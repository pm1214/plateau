const { chromium } = require('playwright');
(async () => {
  const OUT = process.argv[2];
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  await p.goto('http://localhost:8125/window3.html?lat=34.99050&lon=135.76250&floor=10&heading=220&fov=60&years=20');
  await p.waitForFunction(() => window.app && window.app.tilesets.length === 2, null, { timeout: 120000 });
  await p.waitForTimeout(40000);
  await p.evaluate(() => { const d = document.querySelector('#sun-date'); d.value = '2026-11-19'; d.dispatchEvent(new Event('change')); });
  await p.keyboard.press('h'); await p.waitForTimeout(500);
  for (const m of [930, 950, 970, 990, 1005]) {
    // パネルを隠したままでも動かせるように、値を直接入れて input を送る
    await p.evaluate((m) => { const s = document.querySelector('#sun-time'); s.value = m; s.dispatchEvent(new Event('input')); }, m);
    await p.waitForTimeout(2500);
    await p.screenshot({ path: `${OUT}/G_sun${m}.png`, timeout: 300000 }); console.log('shot', m);
  }
  await b.close();
})();
