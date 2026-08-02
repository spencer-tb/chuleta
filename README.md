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

**Audio**: the 🔊 button (or `e`) pronounces the Spanish with the browser's Spanish
voice. With **🔊 auto** on (default), the Spanish is spoken whenever it's revealed —
hearing the word builds its sound form, which is what your inner voice rehearses.
Audio never plays before you answer, so it can't give the answer away.

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

## On your phone

The app is a **PWA**: served over HTTPS it can be installed to the home screen and
works offline (`manifest.webmanifest` + `sw.js`; progress stays in that device's
localStorage — there's no sync between devices).

- **iOS Safari**: open the URL → share sheet → *Add to Home Screen*.
- **Android Chrome**: open the URL → menu → *Install app*.

## Roadmap

- **Voice mode**: record yourself saying the phrase (Web Speech API), compare against
  the target — start with recognized-text matching, later real pronunciation scoring.
- **Conversation mode**: questions only, answer out loud like a mock lesson.
- **More cards**: the fastest route to conversation is coverage — ~1,000 highest-
  frequency words ≈ 80% of everyday speech. Grow the deck along a frequency list.

## Add cards

Edit the `DECK` array at the top of the `<script>` in `index.html`:

```js
{ es: "la chuleta", en: "cheat sheet", cat: "Vocabulario", note: "optional extra context" },
```
