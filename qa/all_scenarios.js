const { chromium } = require('playwright');
(async () => { const b = await chromium.launch(); const found = new Set();
  for (const w of [320, 360, 375, 390]) {
    const p = await b.newPage({ viewport: { width: w, height: 800 } }); await p.goto('file://' + require('path').resolve(__dirname, '../build/game.html') + ''); await p.waitForTimeout(300);
    const r = await p.evaluate(() => { const out = [];
      for (const s of DATA.scenarios) for (let L = 1; L <= 4; L++) {
        const rounds = []; for (let k = 0; k < L - 1; k++) { const d = LEVEL_IDX[k]; rounds.push({ level: k + 1, d, value: 100000, alloc: extremeAlloc(s, d, d + 4, true) }); }
        S = { screen: 'level', sid: s.id, level: L, value: 100000, alloc: new Array(6).fill(0), rounds, mode: 'long' }; render();
        document.querySelectorAll('#app .nt, #app .ds, #app .mast, #app .kick, #app .sub, #app .label').forEach(el => { if (getComputedStyle(el).display === 'none') return; if (el.scrollWidth > el.clientWidth + 1) out.push(el.textContent.trim().slice(0, 40)); });
        if (document.documentElement.scrollWidth > innerWidth) out.push('PAGE OVERFLOW ' + s.id);
      } return [...new Set(out)]; });
    console.log(w, r.length ? r : 'clean'); await p.close();
  } await b.close(); })();
