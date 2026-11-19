// docs/slides/index.html を PDF に書き出す（16:9・1ページ1スライド）
// 使い方: node docs/slides/build.js [出力先.pdf] [元の HTML（省略時は index.html）]
//   例: node docs/slides/build.js out/slides2.pdf index2.html
// Playwright（Chromium）が必要。
const path = require("path");
const { chromium } = require("playwright");

(async () => {
  const out = process.argv[2] || "out/slides.pdf";
  const src = "file://" + path.resolve(__dirname, process.argv[3] || "index.html");
  const browser = await chromium.launch();
  const page = await browser.newPage();
  await page.goto(src, { waitUntil: "load" });
  await page.pdf({ path: out, preferCSSPageSize: true, printBackground: true });
  await browser.close();
  console.log("saved", out);
})();
