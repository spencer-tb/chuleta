#!/usr/bin/env python3
"""Generate per-card TTS audio via ElevenLabs.

Writes audio/es/<fnv1a(es)>.mp3 (voice: chuleta-Bon) and audio/en/<fnv1a(es)>.mp3
(voice: chuleta-Brooke) for every card in the DECK inside index.html, plus
audio/manifest.json mapping hash -> card text. Idempotent: existing files are
skipped, so growing the deck only generates the new cards.

API key is read from ~/.config/chuleta/elevenlabs.key (never in the repo).
"""
import json
import pathlib
import re
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
KEY = (pathlib.Path.home() / ".config/chuleta/elevenlabs.key").read_text().strip()
MODEL = "eleven_multilingual_v2"
FMT = "mp3_44100_96"
VOICES = {"es": "chuleta-Bon", "en": "chuleta-Brooke"}
CONCURRENCY = 3


def fnv1a(s: str) -> str:
    # Must match the JS implementation in index.html.
    h = 0x811C9DC5
    for b in s.encode("utf-8"):
        h ^= b
        h = (h * 0x01000193) & 0xFFFFFFFF
    return format(h, "08x")


def load_deck():
    html = (ROOT / "index.html").read_text()
    body = re.search(r"const DECK = \[(.*?)\n\];", html, re.S).group(1)
    cards = []
    for m in re.finditer(r'\{ es: "((?:[^"\\]|\\.)*)", en: "((?:[^"\\]|\\.)*)"', body):
        cards.append((m.group(1).replace('\\"', '"'), m.group(2).replace('\\"', '"')))
    return cards


def speakable(text: str, lang: str) -> str:
    t = text.replace("y/o", "o").replace("and/or", "or")
    if lang == "es":
        t = re.sub(r"[()]", "", t)  # "(yo) trabajo" -> "yo trabajo"
    else:
        t = re.sub(r"\s*\([^)]*\)", "", t)  # drop gloss asides: "I like (it)" -> "I like"
    t = t.replace(" / ", ", ").replace("/", ", ")
    return re.sub(r"\s+", " ", t).strip(" -—")


def api(path):
    req = urllib.request.Request("https://api.elevenlabs.io" + path, headers={"xi-api-key": KEY})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read())


def tts(voice_id: str, text: str) -> bytes:
    req = urllib.request.Request(
        f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}?output_format={FMT}",
        data=json.dumps({"text": text, "model_id": MODEL}).encode(),
        headers={"xi-api-key": KEY, "Content-Type": "application/json"},
    )
    last = None
    for attempt in range(5):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = f"{e.code}: {e.read().decode()[:200]}"
            if e.code not in (429,) and e.code < 500:
                raise RuntimeError(last)
        except Exception as e:  # timeouts, resets
            last = repr(e)
        time.sleep(2 * (attempt + 1))
    raise RuntimeError(f"retries exhausted: {last}")


def main():
    cards = load_deck()
    hashes = [fnv1a(es) for es, _ in cards]
    assert len(cards) >= 300, f"deck extraction looks wrong: {len(cards)} cards"
    assert len(set(hashes)) == len(hashes), "fnv1a hash collision — rename a card"

    voice_ids = {}
    for v in api("/v1/voices")["voices"]:
        for lang, name in VOICES.items():
            if v["name"] == name:
                voice_ids[lang] = v["voice_id"]
    assert set(voice_ids) == {"es", "en"}, f"voices missing from lab: {voice_ids}"

    manifest, work = {}, []
    for (es, en), h in zip(cards, hashes):
        manifest[h] = {"es": es, "en": en}
        for lang, text in (("es", es), ("en", en)):
            dest = ROOT / "audio" / lang / f"{h}.mp3"
            if not dest.exists():
                work.append((dest, voice_ids[lang], speakable(text, lang)))

    (ROOT / "audio").mkdir(exist_ok=True)
    (ROOT / "audio" / "es").mkdir(exist_ok=True)
    (ROOT / "audio" / "en").mkdir(exist_ok=True)
    (ROOT / "audio" / "manifest.json").write_text(
        json.dumps(manifest, ensure_ascii=False, indent=1))

    print(f"{len(cards)} cards, {len(work)} clips to generate", flush=True)
    done, failed = 0, []

    def one(job):
        nonlocal done
        dest, vid, text = job
        try:
            audio = tts(vid, text)
            dest.write_bytes(audio)
        except Exception as e:
            failed.append((dest.name, str(e)))
            return
        done += 1
        if done % 20 == 0:
            print(f"{done}/{len(work)}", flush=True)

    with ThreadPoolExecutor(CONCURRENCY) as pool:
        list(pool.map(one, work))

    print(f"generated {done}, failed {len(failed)}")
    for name, err in failed[:10]:
        print("FAILED", name, err)
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
