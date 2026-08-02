#!/usr/bin/env python3
"""Reference phoneme sequences per card, for on-device pronunciation scoring.

For each card, phonemize the spoken Spanish (same first-variant rule as the
audio) with espeak-ng and tokenize into the wav2vec2 espeak model's vocab.
Output: phonemes.json  { fnv1a(es): { w: [display words], p: [[phones]] } }

The token inventory and strip set MUST match the scorer in index.html.
"""
import json
import pathlib
import re
import subprocess
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from gen_audio import fnv1a, load_deck, speakable  # noqa: E402

VOCAB_URL = ("https://huggingface.co/onnx-community/"
             "wav2vec2-lv-60-espeak-cv-ft-ONNX/resolve/main/vocab.json")
CACHE = pathlib.Path.home() / ".cache" / "vocab-espeak.json"
STRIP = "[ˈˌːˑ̩̪̃͡ ]"


def tokenize(ipa, vocab):
    s = re.sub(STRIP, "", ipa)
    toks, i = [], 0
    while i < len(s):
        for ln in (3, 2, 1):
            c = s[i:i + ln]
            if len(c) == ln and c in vocab:
                toks.append(c)
                i += ln
                break
        else:
            i += 1
    return toks


def main():
    if not CACHE.exists():
        urllib.request.urlretrieve(VOCAB_URL, CACHE)
    vocab = set(json.load(open(CACHE)))
    out, skipped = {}, []
    for es, en in load_deck():
        text = speakable(es, en, "es")
        words = re.sub(r'[¿?¡!.,—:;"]', " ", text).split()
        raw = subprocess.run(["espeak-ng", "-v", "es", "-q", "--ipa", text],
                             capture_output=True, text=True).stdout
        ipa = re.sub(r"\([a-z]{2,3}\)", "", raw).split()  # drop lang-switch tags
        if not words or len(ipa) != len(words):
            skipped.append(es)
            continue
        out[fnv1a(es)] = {"w": words, "p": [tokenize(x, vocab) for x in ipa]}
    (ROOT / "phonemes.json").write_text(
        json.dumps(out, ensure_ascii=False, separators=(",", ":")))
    print(f"{len(out)} cards phonemized, {len(skipped)} skipped")
    for s in skipped:
        print("  skipped:", s)


if __name__ == "__main__":
    main()
