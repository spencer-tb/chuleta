#!/usr/bin/env python3
"""Generate audio/vocab/<fnv1a(word)>.mp3 (Bon) for every vocab.json word.

Idempotent like gen_audio.py; requires ~/.config/chuleta/elevenlabs.key.
"""
import json
import pathlib
import sys
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, str(pathlib.Path(__file__).parent))
from gen_audio import ROOT, VOICES, api, fnv1a, tts

def main():
    words = [w for w, _ in json.loads((ROOT / "vocab.json").read_text())]
    hashes = [fnv1a(w) for w in words]
    assert len(set(hashes)) == len(hashes), "hash collision in vocab"
    voice_id = next(v["voice_id"] for v in api("/v1/voices")["voices"]
                    if v["name"] == VOICES["es"])
    (ROOT / "audio" / "vocab").mkdir(parents=True, exist_ok=True)
    work = [(ROOT / "audio" / "vocab" / f"{h}.mp3", w)
            for h, w in zip(hashes, words)
            if not (ROOT / "audio" / "vocab" / f"{h}.mp3").exists()]
    print(f"{len(words)} words, {len(work)} clips to generate", flush=True)
    done, failed = 0, []

    def one(job):
        nonlocal done
        dest, word = job
        try:
            dest.write_bytes(tts(voice_id, word))
            done += 1
            if done % 50 == 0:
                print(f"{done}/{len(work)}", flush=True)
        except Exception as e:
            failed.append((word, str(e)[:120]))

    with ThreadPoolExecutor(3) as pool:
        list(pool.map(one, work))
    print(f"generated {done}, failed {len(failed)}")
    for w, err in failed[:8]:
        print("FAILED", w, err)
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
