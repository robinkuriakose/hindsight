const { chromium } = require('playwright');
const CHECK = () => {
  const vw = innerWidth, bad = [];
  if (document.documentElement.scrollWidth > vw) bad.push(`page scrollWidth ${document.documentElement.scrollWidth} > ${vw}`);
  document.querySelectorAll('#app *').forEach(el => {
    if (el.closest('svg') || el.closest('.sr') || el.closest('.odo') || el.closest('details:not([open])')) return;
    const r = el.getBoundingClientRect(); if (!r.width || !r.height) return;
    if (r.right > vw + 0.5 || r.left < -0.5) { if (!el.closest('.chart.bleed') && !el.matches('.top')) bad.push(`edge: ${el.className || el.tagName} [${Math.round(r.left)},${Math.round(r.right)}]`); }
    const cs = getComputedStyle(el);
    if (el.scrollWidth > el.clientWidth + 1 && cs.textOverflow !== 'ellipsis' && !el.matches('.scroll, .chart, .tbl, .tbl *, .poster, .pgrid *') && cs.overflowX !== 'auto' && el.children.length === 0 || (el.matches('.num, .years, .mast, .kick, .legend, .label, .sub, .ctl, .alloc') && el.scrollWidth > el.clientWidth + 1))
      bad.push(`clip: ${el.className || el.tagName} "${(el.textContent || '').trim().slice(0, 30)}" ${el.scrollWidth}>${el.clientWidth}`);
  });
  document.querySelectorAll('#app .nt, #app .ds').forEach(el => { if (el.closest(".prices") || el.closest(".ret") || el.closest(".ret2") || getComputedStyle(el).display === "none" || el.closest('details:not([open])')) return; if (el.scrollWidth > el.clientWidth + 1 && innerWidth >= 360) bad.push(`ellipsis: "${el.textContent.trim()}"`); });
  return [...new Set(bad)].slice(0, 8);
};
(async () => {
  const b = await chromium.launch(); let fails = 0;
  for (const theme of ['dark', 'light']) for (const w of [320, 360, 375, 390, 430, 768, 1024, 1440]) for (const mode of ['best', 'worst']) {
    const ctx = await b.newContext({ viewport: { width: w, height: 800 }, reducedMotion: 'reduce' });
    await ctx.addInitScript(t => localStorage.setItem('ht-theme', JSON.stringify(t)), theme);
    const p = await ctx.newPage(); const errs = []; p.on('pageerror', e => errs.push(e.message));
    await p.goto('file://' + require('path').resolve(__dirname, '../build/game.html') + ''); await p.waitForTimeout(300);
    const res = {}; const chk = async n => { const r = await p.evaluate(CHECK); if (r.length) res[n] = r; };
    await chk('intro'); await p.click('[data-act="new"]'); await p.waitForTimeout(150); await chk('level1');
    for (let L = 1; L <= 4; L++) {
      await p.evaluate(m => { const d = LEVEL_IDX[S.level - 1]; S.alloc = extremeAlloc(sc(), d, d + 4, m === 'best'); render(); }, mode);
      await chk('level' + L); if (L === 2) { await p.click('#bet [data-act="open"][data-i="0"]'); await p.waitForTimeout(80); await chk('sheet'); await p.keyboard.press('Escape'); }
      await p.click('[data-act="lock"]'); await p.waitForTimeout(120); await chk('round' + L); await p.click('[data-act="next"]'); await p.waitForTimeout(120);
    }
    await chk('result'); await p.click('summary'); await chk('result-details'); await p.click('[data-act="hold"]'); await p.waitForTimeout(150); await chk('hold');
    const big = await p.evaluate(() => document.querySelector('#heroNum').getAttribute('aria-label'));
    if (Object.keys(res).length || errs.length) { fails++; console.log(theme, w, mode, big, JSON.stringify(res), errs); }
    else if (w === 320 || w === 1440) console.log('ok', theme, w, mode, 'hold =', big);
    await ctx.close();
  }
  console.log('failing combos:', fails); await b.close();
})();
