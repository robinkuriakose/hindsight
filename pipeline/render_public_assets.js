// Renders the share preview (og.png, 1200x630) and the home-screen icon (apple-touch-icon.png, 180x180)
// from build/game.html. Run after export_game_data.py:  NODE_PATH=$(npm root -g) node pipeline/render_public_assets.js
const { chromium } = require('playwright'); const path = require('path');
const ROOT = path.resolve(__dirname, '..'), PUB = path.join(ROOT, 'public');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 1200, height: 630 }, deviceScaleFactor: 1 });
  await p.addInitScript(() => { try { localStorage.clear(); } catch (e) {} });
  await p.goto('file://' + path.join(ROOT, 'build', 'game.html')); await p.waitForTimeout(1200);
  await p.addStyleTag({ content: `.steps, .split p.x13, .dock, .top .ib { display: none !important; }
    .page { padding-bottom: 0 !important; } .split.center { min-height: 570px !important; padding-top: 0 !important; grid-template-columns: minmax(0,1fr) 440px !important; gap: 64px !important; }
    .card { transition: none !important; }` });
  await p.waitForTimeout(300); await p.screenshot({ path: path.join(PUB, 'og.png') });
  const q = await b.newPage({ viewport: { width: 180, height: 180 }, deviceScaleFactor: 1 });
  await q.setContent(`<body style="margin:0;background:#09090b;display:grid;place-items:center;height:180px"><svg width="120" height="120" viewBox="0 0 24 24" fill="none" stroke="#8b74ff" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M4.6 13.2A7.6 7.6 0 1 0 7 6.4"/><path d="M3.8 3.6v4.2H8"/><circle cx="12" cy="12" r="1.9" fill="#8b74ff" stroke="none"/></svg></body>`);
  await q.screenshot({ path: path.join(PUB, 'apple-touch-icon.png') });
  await b.close(); console.log('wrote public/og.png and public/apple-touch-icon.png');
})();
