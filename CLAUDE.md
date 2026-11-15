# Hindsight: working notes for Claude Code

A single-page trading game on real Indian market data, live at https://playhindsight.vercel.app.
No framework, no server: one HTML file with the data embedded. README.md has the game rules and data sources.

## Change → ship
1. Edit `src/template.html` (all HTML, CSS and JS live there; data is injected at `/*__DATA__*/null`).
2. Build: `python3 pipeline/export_game_data.py && python3 pipeline/build_dist.py`
   - If the homepage look changed, also refresh the link preview: `NODE_PATH=$(npm root -g) node pipeline/render_public_assets.js`, then rerun `build_dist.py`.
3. Check: `NODE_PATH=$(npm root -g) node qa/all_scenarios.js` (cut-off text, 320–390px, all 18 scenarios) and
   `NODE_PATH=$(npm root -g) node qa/overflow_matrix.js` (page overflow, 8 widths × 2 themes). Both must be clean.
   Look at screenshots at 390 and 1440 in dark and light before calling a visual change done.
4. Commit `src/` and `dist/` together. Push a branch for a Vercel preview; `main` is production.

`dist/` is generated: never hand-edit it. `build/` is scratch and not committed.

## Design rules the owner has set
- Fonts: Geist (UI) and Newsreader (upright serif, clue and verdicts only). Don't change typography unless asked.
- Homepage tagline: Geist Regular 48/56, −2.24px tracking; subline 22/29 in #85858F. Mobile scales down.
- Colour: dark #09090b base, violet brand (#8b74ff, CTA #6548ee), green gain / red loss, amber shorts. Light theme mirrors it.
- Chart line is green above the bank (FD) line and red below, flipping on each crossing; the background glow follows.
- Pills: "[your return] vs the bank's [bank return]", each coloured by its own sign.
- Home card: Onyx glow, black with soft grey left-pointing chevrons and India dots (Survey of India, via DataMeet) over a violet glow; light theme has its own token set (`--c*`).
- Copy the owner gives is a direction, not final text. Keep copy short. Push back or ask before building if something looks off.
- Quality bar is Apple/Revolut: no text truncation, no layout shift, motion with intent (std .2,0,0,1 250ms; emph .3,0,0,1 450ms).

## Gotchas
- The page also runs as a claude.ai artifact (`build/game.html`); there it saves the share image through the `downloads` capability. On the hosted site it downloads a PNG.
- Satoshi was tried and dropped; Satoshi has no ₹ glyph.
- Data rebuilds (`pipeline/build_data.py`) need the raw NSE/World Bank/FRED downloads, which are not in the repo.
