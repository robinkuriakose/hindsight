# Hindsight

A four-level trading game on real Indian market data. The player gets ₹1,00,000 as 10 bundles and must place all 10 across 6 options, going **long** (up to 4 bundles per option) or **short** (up to 2). Each lock-in runs for two years, shown in six-month steps. After level 4 comes a results page (8 years in). From there the player can hold the level-4 picks till Nov 2026, or start a new scenario.

Live: https://playhindsight.vercel.app · claude.ai preview: https://claude.ai/artifact/FSDDdMzbyrJaNXVq11wPJD

## Files

- `src/template.html`: the whole game (HTML, CSS, JS). `/*__DATA__*/null` is where the data goes. Edit this.
- `pipeline/scenarios.json`: the hand-written scenarios (assets, story, one headline per level).
- `pipeline/build_data.py`: builds `scenarios_built.json` from the raw sources (only needed to change data).
- `pipeline/export_game_data.py`: embeds the data and writes `build/game.html` (not committed).
- `pipeline/build_dist.py`: wraps the game into a full web page in `dist/` with icons and link-preview tags.
- `pipeline/render_public_assets.js`: renders `public/og.png` and the touch icon from the game.
- `public/`: static files copied into `dist/`. `dist/`: what Vercel serves (committed, see `vercel.json`).
- `qa/`: Playwright checks for cut-off text and page overflow. `design/`: card explorations.

Build: `python3 pipeline/export_game_data.py && python3 pipeline/build_dist.py`.
`build_data.py` reads the raw downloads from `$HINDSIGHT_RAW/raw` (default `./raw/raw`); they are not in the repo.

## Shorting rules

- Each bundle is one tenth of the portfolio. A short bundle is backed by one bundle of cash (margin).
- Value of a short bundle = bundle × (2 − price ratio), where price ratio = price now / price at the start of the round.
- If the price ratio reaches 2 at any six-month check, the short is wiped out for good (value 0), even if the price falls back later.
- Per option: up to 4 bundles long or up to 2 short, never both. Fixed deposits can't be shorted.
- A short still counts as one of the 10 bundles, so all 10 must still be placed.
- When the level-4 picks are held to Nov 2026, the wipe-out check runs on every six-month point of the whole hold, so shorts rarely survive.
- Not modelled: borrow fees, dividends, and moves between checks. Real Indian retail investors can short stocks only intraday or through futures.

## Results

- **Best and worst possible**: the exact best and worst split of each round, found by dynamic programming and checked against brute force over all 1,506 (long-only) / the full count shown in-game valid splits. Rounds are independent, so best and worst per round are best and worst overall.
- **Median**: the point-by-point median of 5,000 plays that each pick a uniformly random valid split every level (drawn exactly using counts of completions).
- Also shown: the percentage of those plays you beat, FD and Nifty-alone benchmarks, and where you landed between worst and best.

## Flow

1. **Levels 1-4.** The year shows as a small stamp, `xxxx` → `20xx` → `201x` → full year. A newspaper clipping carries one real headline from that year. From level 2, cards show 2Y / 4Y / 6Y price changes, a sparkline, and invested → current for last round's picks.
2. **Round results**, after each lock-in: the portfolio every six months, the positions table (with wipe-outs flagged), best and worst performer, your best position, and a full list of all eight options showing what one bundle would have earned long and short (with wipe-outs), best first, and where you were invested.
3. **Result**, 8 years after the start.
4. **Hold till Nov 2026** (optional).

## Scenarios (18, random, no repeats until all are played)

| id | Start | Storyline options |
|---|---|---|
| y2k | Jan 2000 | Wipro, HCL Tech, Reliance, ITC, Gold, US Dollar |
| supercycle | Jan 2003 | BHEL, SAIL, Copper, Crude, Silver, Aluminium |
| openroad | Jan 2004 | Maruti, MRF, Ashok Leyland, ONGC, Crude, US Dollar |
| boombust | Jan 2007 | Suzlon, Unitech, RCom, ICICI Bank, TCS, Crude |
| ipo | Mar 2008 | Reliance Power, Reliance, DLF, Gold, Crude, US Dollar |
| telecom | Jan 2009 | RCom, Bharti Airtel, Idea, TCS, Copper, US Dollar |
| scams | Jan 2010 | Unitech, HCC, Hindustan Copper, Bharti Airtel, Silver, Gold |
| credit | Jul 2011 | Bajaj Finance, Eicher, Infosys, SBI, Gold, Crude |
| banks | Jan 2012 | Yes Bank, HDFC Bank, Kotak, PNB, Silver, Euro |
| premium | Jul 2012 | Page, Asian Paints, Titan, Jubilant FoodWorks, Gold, Crude |
| taper | Jan 2013 | Sun Pharma, SBI, Infosys, HUL, US Dollar, Gold |
| goldrush | Jan 2014 | PC Jeweller, Titan, Muthoot, Gold, Silver, Platinum |
| pharma | Jan 2015 | Lupin, Dr. Reddy's, Biocon, Maruti, Crude, Euro |
| power | Jan 2016 | Genus Power, Adani Ent, Tata Power, TCS, Copper, Natural Gas |
| jio | Jul 2016 | Reliance, Bharti Airtel, Idea, Infosys, Gold, US Dollar |
| smallcap | Jan 2017 | Graphite India, Vakrangee, Avanti Feeds, IndiGo, Copper, Gold |
| pandemic | Jan 2018 | Yes Bank, Tanla, Reliance, Deepak Nitrite, Gold, Crude |
| defence | Jul 2018 | HAL, BEL, Cochin Shipyard, Coal India, Gold, Crude |

Each scenario also has the Nifty 50 and a 6% FD, for 8 options in all.

## Data sources

- **NSE stocks:** daily NSE bhavcopy closes from github.com/BennyThadikaran/eod2_data.
  - Bonus, split, demerger and rights adjustments come from the NSE MCP `get_corporate_actions` (2005+) and from price jumps (pre-2005).
  - All 53 stocks' last archive closes match the NSE MCP's previous close. Final closes (11 Nov 2026) come from NSE MCP `get_bulk_quote`.
- **Nifty 50:** three NSE-format daily files that agree to 0.0000% on every overlapping day, plus the NSE MCP for the final close.
- **Gold, silver, copper, aluminium, platinum, natural gas, Brent:** World Bank Pink Sheet monthly averages (edition of 3 Nov 2026), converted to INR with FRED USD/INR.
- **USD, EUR:** FRED monthly averages.

## Known limits

- **No pre-2000 scenarios.** There is no verified Nifty 50 history before 2000, and NSE equity trading began in Nov 1994, so the 1992 Harshad Mehta era isn't possible.
- **Price returns only.** Dividends, taxes and costs are ignored.
- **Demergers use the ex-date price-ratio method.**
- **Commodities use monthly averages.** The latest is Oct 2026.
- **Newspaper columns are filler.** The text under each headline is generic newspaper prose that fits any story, so it can't give away the year.

## v5 changes (Revolut-style redesign)

- Dark, card-based UI with a white pill action, mint/coral gains and losses, and a light theme option. The banknote art is gone; the newspaper clipping is the one textured object.
- Six options per round: five storyline assets plus the fixed deposit. The Nifty is no longer always present (see `DROP` in `pipeline/export_game_data.py`).
- The goal is stated up front: finish above the 6% fixed deposit (shown as a target each level) and as high as possible.
- Round screen: smooth six-month chart you can scrub, verdict gauges (vs the FD, and rank among every valid split, computed exactly by enumeration), per-position gain/loss attribution, a peak-and-give-back note, and the exact best and worst split.
- Result screen: gauge vs FD and vs 5,000 random plays, a share grid (one square per bundle, copyable text), best/median/worst, hold till 2026.
- Saved games use new storage keys (`ht4-*`), so older saves are ignored.

## v6 changes (design pass)

- System: Geist at 13/15/17/22/34/64 and weights 400/500/600; Newsreader only for the newspaper headline. Five neutrals; green/red only on money and lines; amber only for shorts. 4pt grid, radii 12 and 20. One 1.75-stroke SVG icon set; no unicode glyphs. All text passes WCAG AA in both themes.
- Copy: "Trade the past. Beat the bank." Numbers are the headlines; no instructional text in the UI.
- Level: money, the bank's target, the headline, then six rows (sparkline, return, − n + stepper) under a Long/Short mode switch. A bottom bar holds a 10-segment allocation bar and one button.
- Round: the number ticks as the chart draws (you vs the bank), then a one-line verdict ("HCL Technologies sank you.") and one ranked list of what ₹10K in each became, with your positions marked by weight. Scrubbing the chart updates the hero number.
- Result: number, the reveal (years and title), one chart (you, the bank, perfect hindsight), the percentile, a square share card, and everything else under Details.
- Saved games use `ht5-*` keys.

## v7 changes (identity and motion)

- Identity: "editorial fintech". Serif italic wordmark with a rewind mark, brand indigo, and an ambient glow behind each screen that turns green or red with how you're doing against the bank. The game's verdicts are set as newspaper headlines.
- Motion: odometer numbers that roll digit by digit; hidden year digits spin while two years pass, and newly revealed digits roll in; the result years roll into place; view transitions between screens, with the hero number gliding between them. All of it is off under reduced motion.
- Level: fixed 72px rows with short names, one return column (2Y/4Y/6Y switch) and a stepper. Tap a name for a bottom sheet with its price history (in %, so prices don't give away the year), returns and controls. The clue is a paper card with the hidden year in its masthead.
- Round: four six-month beats; the number rolls to each stop as the line reaches it.
- Result: the reveal, you vs the bank, a histogram of 5,000 random plays with you marked, and a 4:5 share poster.
- Desktop: two columns. Glass top and bottom bars on phones.

## v8 changes (Apple-bar pass)

- Fixed: the page now declares a mobile viewport and disables double-tap zoom, so phones lay it out at their real width. Money figures shrink to fit their column (44px on phones, never below 24px).
- Visual reset: no gradient blobs or coloured glows; no italics; sans wordmark. Type 13/15/17/20/28/44. Three radii (10/14/22), squircle corners where supported. One gain/loss style. Graphite intro card and share poster.
- Charts run edge to edge with the legend above. The reveal uses one curve: a quadratic ease-in for 30% of 2.4s, then a long quintic ease-out with no overshoot. The hero number follows the line, and the end point lands with a halo and a light haptic before the verdict appears.
- Level rows: the return sits on the name line, descriptions are shortened to fit (full text in the detail sheet), and below 360px wide the row reflows instead of truncating.
- Result: the price table became rows that fit; the share poster is a real 1080×1350 PNG (Share image where supported, otherwise Save image).
- QA: `qa/overflow_matrix.js` plays perfect and worst games at 8 widths in both themes and fails on any overflow, clipping or truncation; `qa/all_scenarios.js` renders every scenario and round at phone widths. Run with `NODE_PATH=$(npm root -g) node qa/<file>`.

## v10 changes

- Colour: the light behind each screen follows the outcome. Indigo while you place bets; on results it turns green when you are ahead of the bank and coral when you trail. The three lights sit in different places and crossfade, drifting slowly and moving gently with scroll.
- Chart: the whole line takes the colour of where it is right now against the bank (green above, red below) and the light flips with it. Each crossing slows the draw for a beat so the flip registers.
- Long and short: one position control per option, from short 2 to long 4. − below zero opens a short; the label under the number says LONG, SHORT or NONE. The mode tab is gone.
- Copy: "Everyone’s a genius in hindsight. Prove it." The result opens with a verdict: You made it / Close, but the bank won / You broke it.
- Home card and share poster: indigo light with fine topographic contour lines; on desktop the card lifts and a soft light follows the pointer.
- Top bar: fades to black instead of a hard strip.
- Desktop: asset details open inline under the row; Details sits below both columns in three columns.

### v12–v14
- Level rows: the return % is its own column, centred on the stepper; long descriptions wrap instead of truncating.
- Home: headline plus a one-line explainer ("Real prices from 2000 to 2026. You get the headlines, not the hindsight."); more space under the top bar.
- Home card: Onyx glow (black, grey left-pointing chevrons, India dots in lavender over a violet glow). Year reads 20__.
- Share card keeps its contour lines on the same onyx base; the square legend moved behind an (i) explainer and off the image.
- Result: the multiple is coloured against the bank, and close results get extra precision (1.588× vs 1.594×, full rupees).
- Round reveal: table and verdict appear when the line lands; the year spins for 2s and lands on its own.
- Detail tiles show Last 2Y, Low and High instead of repeating "since start". Section labels align with the page edge.
- Desktop: level columns centred against each other; histogram moved to the left column on the result.

### v15
- Homepage tagline in Geist Regular: headline 48/56 with -2.24px tracking, subline 22/29 in #85858F (from the Figma "Tagline" frame); no dividers between the four steps.
- Pills read "[your return] vs the bank's [bank return]", each pill coloured by its own sign, with the detail on a second line.
- Home card chevrons toned down (lower opacity, darker greys) so the India map leads.
- Sources note the map credit and that the game is not investment advice.
- Save image downloads a PNG on a hosted page; inside an embedding viewer without the downloads capability the button is hidden.

## Hosting
Vercel, from the `main` branch of this repo. `vercel.json` tells Vercel to serve `dist/` as-is (no build step there) and sets the headers.
Branches other than `main` get preview URLs. Workflow: edit `src/template.html`, run the build, run QA, commit `src/` and `dist/` together.

Before wider promotion: the game shows derived NSE closing prices, World Bank Pink Sheet and FRED series, and a Survey of India outline via DataMeet. Check each source's terms for public or commercial use, and keep the "not investment advice" note in Sources.

### v16–v18
- Pills read "[your return] vs the bank's [bank return]", each coloured by its own sign, with the detail on a second line.
- Home card: chevrons toned down; light-mode card (white base, violet dots) driven by `--c*` tokens.
- Theme switch on every screen, next to exit.
- Desktop level: the left column stays put (sticky, centred in the viewport) when a row opens on the right.
