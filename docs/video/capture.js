// 動画用の画面を撮る（スコア版 window3.html）
const { chromium } = require('playwright');
(async () => {
  const OUT = process.argv[2];
  const b = await chromium.launch({ args: ['--use-gl=angle','--use-angle=swiftshader','--enable-unsafe-swiftshader'] });
  const p = await b.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 1.5 });
  const errs = []; p.on('pageerror', e => errs.push(e.message));
  const shot = async (name, wait = 1500) => { await p.waitForTimeout(wait); await p.screenshot({ path: `${OUT}/${name}.png`, timeout: 300000 }); console.log('shot', name, new Date().toISOString().slice(11,19)); };
  const idle = (sel) => p.waitForFunction((s) => !document.querySelector(s).disabled, sel, { timeout: 900000 });
  const collapse = async (want) => { const c = await p.evaluate(() => document.querySelector('#panel').classList.contains('collapsed')); if (c !== want) await p.keyboard.press('h'); await p.waitForTimeout(400); };
  await p.goto('http://localhost:8125/window3.html');
  await p.waitForFunction(() => window.app && window.app.tilesets.length === 2, null, { timeout: 120000 });
  await p.waitForTimeout(45000);
  // A: 上から見た色分けの街（パネルを隠す）
  await collapse(true); await shot('A_overview', 3000);
  // B: 年数スライダー 0→40
  await collapse(false);
  await p.evaluate(() => document.querySelector('#years').closest('section').scrollIntoView());
  for (const y of [0, 10, 20, 30, 40]) { await p.fill('#years', String(y)); await p.dispatchEvent('#years', 'input'); await shot(`B_years${String(y).padStart(2,'0')}`, 2500); }
  await p.fill('#years', '20'); await p.dispatchEvent('#years', 'input');
  // C: 東本願寺の窓（数える前）
  await p.evaluate(() => document.querySelector('#panel').scrollTop = 0);
  await p.locator('#presets button').nth(0).click(); await p.waitForTimeout(45000);
  await shot('C_window', 1000);
  // D: 景色を数える（40×25）
  await p.selectOption('#grid', '40x25'); await p.click('#btn-count'); await p.waitForTimeout(3000); await idle('#btn-count');
  await p.evaluate(() => document.querySelector('#result').scrollIntoView()); await shot('D_counted');
  console.log('SCORE', await p.textContent('#score-num'), await p.textContent('#verdict'));
  // E: ベスト5の1位を光らせる
  await p.evaluate(() => document.querySelector('#rank').scrollIntoView({ block: 'center' }));
  await p.locator('#rank tr.row').nth(0).click(); await shot('E_rank', 2500);
  console.log('RANK1', (await p.locator('#rank tr.row').nth(0).innerText()).replace(/\s+/g, ' '));
  await p.locator('#rank tr.row').nth(0).click(); // 光を消す
  // F: 20年後の景色（20×12 で速く）
  await p.selectOption('#grid', '20x12');
  await p.click('#btn-years'); await p.waitForTimeout(3000);
  await p.waitForFunction(() => !document.querySelector('#compare').hidden && !document.querySelector('#btn-compare').disabled, null, { timeout: 900000 });
  await p.evaluate(() => document.querySelector('#compare').scrollIntoView()); await shot('F_future');
  console.log('FUTURE', await p.textContent('#compare-verdict'));
  await p.click('#btn-reset'); await p.waitForTimeout(1000);
  // G: 京都タワーの窓で夕日
  await p.evaluate(() => document.querySelector('#panel').scrollTop = 0);
  await p.locator('#presets button').nth(1).click(); await p.waitForTimeout(40000);
  await p.fill('#sun-date', '2026-11-19'); await p.dispatchEvent('#sun-date', 'change');
  await p.click('#btn-sunset'); await p.waitForTimeout(2000); await idle('#btn-sunset');
  console.log('SUNSET', await p.textContent('#sunset-result'));
  await p.evaluate(() => document.querySelector('#sunset-result').scrollIntoView({ block: 'center' })); await shot('G_sunset_panel');
  await collapse(true);
  for (const m of [930, 950, 970, 990, 1005]) { await p.fill('#sun-time', String(m)); await p.dispatchEvent('#sun-time', 'input'); await shot(`G_sun${m}`, 2500); }
  console.log('ERRS', errs); await b.close();
})();
