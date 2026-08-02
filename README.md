# chuleta 🥩

Spanish flashcards. *Chuleta* is Spain slang for a cheat sheet (literally: pork chop).

## Use

Open `index.html` in a browser. No build, no dependencies.

Two modes:

- **Repasar** — spaced-repetition study. Shows cards that are due, plus at most
  **20 new cards per day** (capping introductions keeps daily sessions short and
  sustainable — bingeing new cards buries you in reviews two days later).
  Say the answer out loud, flip (`space`), then grade yourself: `1` correct, `2` wrong.
- **Explorar** — free browsing: `←` / `→` to navigate, `s` to shuffle.

**Audio-first**: every card has pre-generated studio-quality audio (`audio/`) —
Spanish by *Bon* (young Barcelona/Castilian voice from ElevenLabs, the accent to
imitate) and English by *Brooke* (calm American voice). With **🔊 auto** on
(default), the prompt side plays in its own language when a card appears and the
answer plays on reveal. The 🔊 buttons / `e` replay. After the reveal, **repeat
the Spanish out loud after the voice** (shadowing — see below). If a clip is
missing (new card, audio not regenerated yet) the browser's TTS fills in.

**Scaffold fading** (the 🎓 toggle): in **auto** mode, once a card has 2
successful reviews its prompt becomes **audio-only** (🎧) — you must understand
the spoken Spanish with no text to lean on, which is what real conversation
demands. `t` / *mostrar texto* peeks when your ears fail you. **📖 texto** keeps
text always; **🎧 audio** goes audio-only immediately.

The direction button cycles **Mixto 🎲** (default: each card randomly rolls 75%
EN → ES, 25% ES → EN) → fixed EN → ES → fixed ES → EN. Producing Spanish from English
is harder than recognizing it, so the mix is weighted toward production. Filter by
category in either mode. Progress saves in localStorage.

## How the scheduling works

Grading uses the **SM-2 algorithm** (the same family Anki uses):

- First correct answer → see it again in **1 day**; second → **6 days**; after that the
  interval multiplies by the card's ease factor (~2.5×), so intervals grow 1 → 6 → 15 →
  38 days...
- Get a card **wrong** → its ease drops (it will come back more often from now on), it
  retries later in the same session, and clearing it schedules it for tomorrow.
- Every **correct** answer recovers a little ease (+0.05, up to the 2.5 cap), so a card
  you fumbled early isn't punished forever.
- A card with an interval ≥ 21 days counts as **aprendida**.

Expanding intervals exploit the spacing effect, and self-grading after out-loud recall
exploits the testing effect — the two most robust findings in memory research.

The audio-first design is deliberate too: skills are modality-specific, so if the
goal is *speaking and listening*, practice has to be hearing and saying, not reading
(transfer-appropriate processing). Hearing a native voice builds the word's sound
form (phonological memory), fading the text out forces real speech decoding, and
repeating after the voice is **shadowing** — one of the best-evidenced techniques
for listening comprehension, prosody, and fluency (Hamada 2016+).

## On your phone

The app is a **PWA**: served over HTTPS it can be installed to the home screen and
works offline (`manifest.webmanifest` + `sw.js`; progress stays in that device's
localStorage — there's no sync between devices).

- **iOS Safari**: open the URL → share sheet → *Add to Home Screen*.
- **Android Chrome**: open the URL → menu → *Install app*.

## Roadmap

- **Pronunciation scoring** (next): speak the Spanish answer into the mic, Azure
  Pronunciation Assessment scores it — per-word color coding, tap a word for the
  phoneme-level breakdown, all es-ES.
- **Conversation mode**: questions only, answer out loud like a mock lesson.
- **More cards**: the fastest route to conversation is coverage — ~1,000 highest-
  frequency words ≈ 80% of everyday speech. Grow the deck along a frequency list.

## Add cards

Edit the `DECK` array at the top of the `<script>` in `index.html`:

```js
{ es: "la chuleta", en: "cheat sheet", cat: "Vocabulario", note: "optional extra context" },
```

Then regenerate audio for the new cards only (needs the ElevenLabs key in
`~/.config/chuleta/elevenlabs.key`; existing clips are skipped):

```sh
python3 tools/gen_audio.py
```
