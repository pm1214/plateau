// 耐用年数版のスライドを PowerPoint（.pptx）で作る。文字はすべて編集できるテキスト。
// 使い方: npm install pptxgenjs を済ませてから
//   耐用年数版: node docs/slides/build_pptx.js out/窓の眺望診断_耐用年数版.pptx
//   スコア版　: node docs/slides/build_pptx.js out/窓の眺望診断_スコア版.pptx score
const path = require("path");
const pptxgen = require("pptxgenjs");

const OUT = process.argv[2] || "out/madono_choubou.pptx";
const IMG = (f) => path.join(__dirname, "img", f);
const URL_TOP = "https://pm1214.github.io/plateau/";
// 2つ目の引数に score を付けるとスコア版（window3.html。安定性スコアとベスト5のスライドを追加）
const SCORE = process.argv[3] === "score";
const PAGE = SCORE ? "window3.html" : "window2.html";
const URL_VIEW = URL_TOP + PAGE + "?lat=34.98950&lon=135.75600&floor=7&heading=0&fov=60&years=20";

// テーマ（色とフォント）。PowerPoint の「デザイン」から変えると、全スライドに反映される
const THEME = {
  name: "窓の眺望診断",
  headFontFace: "Yu Gothic",
  bodyFontFace: "Yu Gothic",
  colors: {
    dk1: "1D232B", lt1: "FFFFFF", dk2: "1F2A44", lt2: "F2F5F8",
    accent1: "E66101", // オレンジ：変わりやすい
    accent2: "4393C3", // 青：まだ変わらない
    accent3: "542788", // 濃い紫：耐用年数を超過
    accent4: "A0A8B0", // 灰：判定できない
    accent5: "5AAEE0", // 空
    accent6: "0B6BCB",
    hlink: "0B6BCB", folHlink: "542788",
  },
};

const pres = new pptxgen();
pres.layout = "LAYOUT_16x9"; // 10 x 5.625 インチ
pres.title = SCORE ? "窓の眺望診断（スコア版）" : "窓の眺望診断（耐用年数版）";
pres.author = "ちばりお";
pres.theme = { headFontFace: THEME.headFontFace, bodyFontFace: THEME.bodyFontFace };
const C = pres.SchemeColor;

// ---- レイアウト
pres.defineSlideMaster({
  title: "CONTENT",
  background: { color: C.background1 },
  objects: [
    { placeholder: { options: { name: "title", type: "title", x: 0.5, y: 0.28, w: 9, h: 0.62, fontSize: 24, bold: true, color: C.text1, valign: "middle", margin: 0 }, text: "" } },
    { text: { text: "出典：国土交通省 Project PLATEAU ／ 国税庁「耐用年数（建物）」 ／ 国土地理院", options: { x: 0.5, y: 5.3, w: 7.5, h: 0.22, fontSize: 9, color: C.text2, margin: 0 } } },
  ],
  slideNumber: { x: 9.1, y: 5.28, w: 0.4, h: 0.25, fontSize: 9, color: C.text2, align: "right" },
});
pres.defineSlideMaster({ title: "DARK", background: { color: C.text2 }, objects: [] });

// ---- 部品
const label = (s, text, x, y, w) =>
  s.addText(text, { x, y, w, h: 0.3, fontSize: 12, color: C.text2, margin: 0, isTextBox: true });
const shot = (s, file, x, y, w) =>
  s.addImage({ path: IMG(file), x, y, w, h: (w * 9) / 16, rounding: false,
    shadow: { type: "outer", blur: 6, offset: 2, angle: 90, color: "000000", opacity: 0.25 } });
const card = (s, x, y, w, h, name) =>
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x, y, w, h, rectRadius: 0.08, fill: { color: C.background2 }, line: { color: C.background2 }, objectName: name });
function table(s, rows, x, y, w, colW, opts = {}) {
  s.addTable(
    rows.map((r, i) => r.map((c, j) => ({
      text: String(c),
      options: { bold: i === 0 && opts.header, color: j === 0 || (i === 0 && opts.header) ? C.text2 : C.text1,
        align: j === 0 || opts.left ? "left" : "right", fontSize: opts.fontSize || 14,
        ...(opts.hl && opts.hl(i, j) ? { color: C.accent1, bold: true } : {}) },
    }))),
    { x, y, w, colW, border: { type: "solid", pt: 0.75, color: "D9DEE4" }, margin: [3, 6, 3, 6], rowH: opts.rowH || 0.32 },
  );
}

// ================================================================ 1. 表紙
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addImage({ path: IMG("sunset.jpg"), x: 0, y: 0, w: 10, h: 5.625 });
  s.addShape(pres.shapes.RECTANGLE, { x: 0, y: 2.6, w: 10, h: 3.025, fill: { color: "000000", transparency: 45 }, line: { color: "000000", transparency: 100 }, objectName: "文字の下の影" });
  s.addText("PLATEAU AWARD 2026 一般部門 ／ ちばりお", { x: 0.5, y: 2.85, w: 7, h: 0.35, fontSize: 14, color: "FFFFFF", margin: 0, isTextBox: true });
  s.addText("窓の眺望診断", { x: 0.5, y: 3.2, w: 7, h: 0.9, fontSize: 44, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
  s.addText("その景色、あと何年もちますか？ — PLATEAU の建物属性で、窓から見える景色の「中身」と変わりやすさを数える",
    { x: 0.5, y: 4.15, w: 6.8, h: 0.9, fontSize: 15, color: "FFFFFF", margin: 0, valign: "top", isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 7.75, y: 3.0, w: 1.85, h: 2.2, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, objectName: "QR の台紙" });
  s.addImage({ path: IMG("qr.png"), x: 7.95, y: 3.12, w: 1.45, h: 1.45 });
  s.addText("今すぐ試せます\npm1214.github.io/plateau", { x: 7.8, y: 4.6, w: 1.75, h: 0.5, fontSize: 9, color: "1D232B", align: "center", margin: 0, isTextBox: true });
  s.addNotes("窓から見える景色を、PLATEAU の建物データで分解して、何年後にどれだけ変わりうるかを数えるツールです。");
}

// ================================================================ 2. 課題
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("眺望は「買う前に自分で確かめる」しかない", { placeholder: "title" });
  const items = [
    ["変わる", "マンションの眺望は、周りの建て替えで将来変わることがある"],
    ["守られない", "景観の街・京都の眺望景観創生条例でも、守るのは決められた視点場からの眺め。マンションの窓は対象外"],
    ["数えない", "今あるサービスは景色を「見せる」だけ。景色の中身や変わりやすさは数えない"],
  ];
  items.forEach(([h, t], i) => {
    const x = 0.5 + i * 3.08;
    card(s, x, 1.15, 2.85, 2.35, `課題${i + 1}`);
    s.addText(String(i + 1), { x: x + 0.25, y: 1.3, w: 0.6, h: 0.6, fontSize: 30, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(h, { x: x + 0.25, y: 1.9, w: 2.4, h: 0.4, fontSize: 18, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.25, y: 2.3, w: 2.4, h: 1.1, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
  s.addText([{ text: "→ ", options: { color: C.accent1, bold: true } },
    { text: "景色を建物1棟ずつに分解し、建て替えで変わりやすい景色かどうかを数値で示す", options: { bold: true } }],
    { x: 0.5, y: 3.85, w: 9, h: 0.5, fontSize: 15, color: C.text1, margin: 0, isTextBox: true });
}

// ================================================================ 3. ひとことで
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("窓の眺望診断とは", { placeholder: "title" });
  shot(s, "life_count.jpg", 0.5, 1.1, 5.2);
  s.addText("20年後までに", { x: 6.0, y: 1.15, w: 3.5, h: 0.45, fontSize: 20, bold: true, color: C.text1, margin: 0, isTextBox: true });
  s.addText([{ text: "37", options: { fontSize: 66, bold: true, color: C.accent1 } }, { text: " %", options: { fontSize: 28, bold: true, color: C.accent1 } }],
    { x: 6.0, y: 1.6, w: 3.5, h: 1.1, margin: 0, isTextBox: true });
  s.addText("の景色が、建物の耐用年数を迎える\n（うち、今すでに超えている建物 24%）", { x: 6.0, y: 2.75, w: 3.5, h: 0.8, fontSize: 14, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  s.addText("京都駅の北・東本願寺の近く、7階の窓から北を見た例。\n点の色：濃い紫＝超過、オレンジ＝20年後までに超過、青＝まだ超えない、灰＝判定できない、白＝空",
    { x: 6.0, y: 3.7, w: 3.5, h: 1.0, fontSize: 10, color: C.text2, margin: 0, valign: "top", isTextBox: true });
}

// ================================================================ 4. 使い方
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("3ステップで、窓の景色を診断", { placeholder: "title" });
  const steps = [
    ["窓を決める", "地図で窓の位置をクリックし、階数・向き・画角をスライダーで決める（目線の高さ＝階数×3 m）"],
    ["景色を数える", "空・地面・建物の割合、用途ごとの棟数、◯年後までに耐用年数を迎える建物が視界に占める割合"],
    ["将来と比べる", "その時期を迎える建物を取り壊した場合と今を比べる。建物を消す・箱を置く操作もできる"],
  ];
  steps.forEach(([h, t], i) => {
    const x = 0.5 + i * 3.08;
    card(s, x, 1.2, 2.85, 2.6, `手順${i + 1}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.4, w: 0.55, h: 0.55, fill: { color: C.accent1 }, line: { color: C.accent1 }, objectName: `番号${i + 1}` });
    s.addText(String(i + 1), { x: x + 0.25, y: 1.4, w: 0.55, h: 0.55, fontSize: 18, bold: true, color: "FFFFFF", align: "center", valign: "middle", margin: 0, isTextBox: true });
    s.addText(h, { x: x + 0.25, y: 2.1, w: 2.4, h: 0.4, fontSize: 17, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.25, y: 2.5, w: 2.4, h: 1.2, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
  s.addText("ブラウザだけで動く1枚の HTML（CesiumJS）。PLATEAU の 3D Tiles を読み込み、建物ごとの属性をその場で集計する。リンクで同じ景色を共有できる。",
    { x: 0.5, y: 4.1, w: 9, h: 0.6, fontSize: 13, color: C.text2, margin: 0, isTextBox: true });
}

// ================================================================ 5. しくみ
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("景色を 1,000 個の点で「数える」", { placeholder: "title" });
  s.addText([
    { text: "画面を格子（40×25）に区切り、1点ずつ何が見えるかを調べる", options: { bullet: true, breakLine: true } },
    { text: "建物に当たった点 → その建物の ID・用途・構造・建築年・高さを記録", options: { bullet: true, breakLine: true } },
    { text: "当たらない点 → 視線が地面に届けば「地面」、届かなければ「空」", options: { bullet: true, breakLine: true } },
    { text: "棟数は建物 ID で重複を除いて数える", options: { bullet: true } },
  ], { x: 0.5, y: 1.2, w: 4.9, h: 2.8, fontSize: 15, color: C.text1, paraSpaceAfter: 10, valign: "top", isTextBox: true });
  card(s, 5.7, 1.2, 3.8, 2.8, "PLATEAU だからできること");
  s.addText("PLATEAU だからできること", { x: 5.95, y: 1.35, w: 3.4, h: 0.4, fontSize: 16, bold: true, color: C.accent1, margin: 0, isTextBox: true });
  s.addText([
    { text: "建物1棟ずつに ID・用途・構造・高さ・階数・建築年がある", options: { bullet: true, breakLine: true } },
    { text: "建物単位で表示・非表示を切り替えられる", options: { bullet: true, breakLine: true } },
    { text: "オープンデータなので、数えて集計できる", options: { bullet: true } },
  ], { x: 5.95, y: 1.8, w: 3.4, h: 2.0, fontSize: 14, color: C.text1, paraSpaceAfter: 8, valign: "top", isTextBox: true });
}

// ================================================================ 6. 結果の例
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("結果の例：東本願寺の近く・7階・北向き", { placeholder: "title" });
  shot(s, "life_count.jpg", 0.5, 1.1, 5.2);
  table(s, [
    ["空", "45%"], ["地面", "2%"], ["建物", "53%"],
    ["耐用年数を超過", "視界の 24%"], ["20年後までに超過", "視界の 13%"],
    ["まだ超えない", "視界の 1%"], ["判定できない", "視界の 15%"],
  ], 6.0, 1.15, 3.5, [2.0, 1.5], { hl: (i) => i === 4 });
}

// ================================================================ スコア版：安定性スコアとベスト5
if (SCORE) {
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("景色の安定性スコアと、視界を占める建物", { placeholder: "title" });
  shot(s, "score.jpg", 0.5, 1.1, 5.2);
  card(s, 6.0, 1.1, 3.5, 1.3, "安定性スコア");
  s.addText([{ text: "63", options: { fontSize: 44, bold: true, color: C.accent1 } }, { text: " 点", options: { fontSize: 18, bold: true, color: C.accent1 } }],
    { x: 6.2, y: 1.15, w: 1.6, h: 0.9, margin: 0, valign: "middle", isTextBox: true });
  s.addText("やや変わりやすい景色", { x: 7.55, y: 1.35, w: 1.9, h: 0.5, fontSize: 12, bold: true, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
  s.addText("100 −（20年後までに耐用年数を迎える建物が視界に占める割合）。80点以上・50点以上の3段階は目安", { x: 6.2, y: 1.95, w: 3.15, h: 0.4, fontSize: 9, color: C.text2, margin: 0, isTextBox: true });
  s.addText("視界を占める建物 ベスト3", { x: 6.0, y: 2.55, w: 3.5, h: 0.3, fontSize: 13, bold: true, color: C.text1, margin: 0, isTextBox: true });
  table(s, [
    ["1 店舗等併用住宅", "木造 1912→1934", "5%"],
    ["2 住宅", "木造 2012→2034", "4%"],
    ["3 住宅", "木造 1998→2020", "3%"],
  ], 6.0, 2.9, 3.5, [1.45, 1.55, 0.5], { fontSize: 10, rowH: 0.3, left: true });
  s.addText("数字は「建築年→建て替え目安の年」。行をクリックすると、その建物が3Dで光る。どの建物が眺望を左右しているかがわかる。", { x: 6.0, y: 4.15, w: 3.5, h: 0.6, fontSize: 10, color: C.text2, margin: 0, valign: "top", isTextBox: true });
}

// ================================================================ 7. 建物ごとの寿命
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("建物ごとの「寿命の目安」で、街の将来を見る", { placeholder: "title" });
  shot(s, "life_overview.jpg", 0.5, 1.1, 5.2);
  s.addText("建て替え時期の目安＝建築年＋耐用年数", { x: 6.0, y: 1.1, w: 3.5, h: 0.35, fontSize: 12, bold: true, color: C.text1, margin: 0, isTextBox: true });
  table(s, [["構造", "住宅", "事務所", "ホテル"], ["木造", "22年", "24年", "17年"], ["鉄骨造", "34年", "38年", "29年"], ["RC造", "47年", "50年", "39年"]],
    6.0, 1.55, 3.5, [1.1, 0.8, 0.8, 0.8], { header: true, fontSize: 11, rowH: 0.3 });
  s.addText("RC造＝鉄筋コンクリート造。耐用年数は国税庁「耐用年数（建物）」の、構造・用途ごとの年数。\n色：濃い紫＝今すでに超過、オレンジ＝20年後までに超過、青＝まだ超えない、灰＝判定できない",
    { x: 6.0, y: 3.15, w: 3.5, h: 1.2, fontSize: 10, color: C.text2, margin: 0, valign: "top", isTextBox: true });
}

// ================================================================ 8. 将来シナリオの意味（改善案1）
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("「20年後の景色」は、何を表しているか", { placeholder: "title" });
  const cols = [
    ["今", "いま見えている景色", C.accent2],
    ["20年後（このツール）", "耐用年数を迎えた建物が、すべて取り壊されて空き地になった場合。空がいちばん広がる「最大ケース」", C.accent1],
    ["20年後（現実）", "多くは同じくらいか、より高い建物に建て替わる。空は、このツールの数字より増えにくい", C.accent3],
  ];
  cols.forEach(([h, t, col], i) => {
    const x = 0.5 + i * 3.08;
    card(s, x, 1.2, 2.85, 2.5, `シナリオ${i + 1}`);
    s.addShape(pres.shapes.OVAL, { x: x + 0.25, y: 1.4, w: 0.3, h: 0.3, fill: { color: col }, line: { color: col }, objectName: `シナリオ${i + 1}の印` });
    s.addText(h, { x: x + 0.65, y: 1.35, w: 2.1, h: 0.4, fontSize: 13, bold: true, color: C.text1, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.25, y: 1.9, w: 2.4, h: 1.7, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
  s.addText("つまり、このツールの「20年後の空」は、景色が開ける方向の上限。それでも空がほとんど増えないなら、その窓の眺望は「古い建物が多いから将来開ける」とは言えない。",
    { x: 0.5, y: 3.95, w: 9, h: 0.75, fontSize: 14, bold: true, color: C.text1, margin: 0, isTextBox: true });
}

// ================================================================ 9. 45%→46%（改善案2：図解）
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("発見：古い家がなくなっても、空はほとんど増えない", { placeholder: "title" });
  shot(s, "life_future.jpg", 0.5, 1.1, 4.3);
  // 断面の図解：窓 → 手前の古い家 → 奥の寿命の長い建物 → 空
  const gx = 5.1, gy = 1.15;
  s.addShape(pres.shapes.RECTANGLE, { x: gx, y: gy + 2.05, w: 4.4, h: 0.04, fill: { color: "8A8F96" }, line: { color: "8A8F96" }, objectName: "地面" });
  s.addShape(pres.shapes.RECTANGLE, { x: gx, y: gy + 0.75, w: 0.35, h: 1.3, fill: { color: C.background2 }, line: { color: "8A8F96" }, objectName: "自分の建物" });
  s.addText("窓", { x: gx - 0.05, y: gy + 0.45, w: 0.5, h: 0.3, fontSize: 11, bold: true, color: C.text1, align: "center", margin: 0, isTextBox: true });
  s.addShape(pres.shapes.RECTANGLE, { x: gx + 0.95, y: gy + 1.35, w: 0.9, h: 0.7, fill: { color: C.accent1, transparency: 55 }, line: { color: C.accent1, dashType: "dash" }, objectName: "手前の古い家（取り壊し）" });
  s.addText("手前の古い家\n（取り壊し）", { x: gx + 0.75, y: gy + 0.75, w: 1.3, h: 0.55, fontSize: 10, color: C.accent1, align: "center", margin: 0, isTextBox: true });
  s.addShape(pres.shapes.RECTANGLE, { x: gx + 2.4, y: gy + 0.55, w: 1.1, h: 1.5, fill: { color: C.accent2 }, line: { color: C.accent2 }, objectName: "奥の寿命の長い建物" });
  s.addText("奥の寿命の\n長い建物", { x: gx + 2.3, y: gy + 0.0, w: 1.3, h: 0.55, fontSize: 10, color: C.accent2, align: "center", margin: 0, isTextBox: true });
  s.addShape(pres.shapes.LINE, { x: gx + 0.35, y: gy + 0.85, w: 2.05, h: 0.45, line: { color: C.text1, width: 1.5, endArrowType: "triangle" }, objectName: "視線" });
  s.addText("視線は、奥の建物に当たる", { x: gx + 0.4, y: gy + 2.15, w: 3.5, h: 0.3, fontSize: 11, color: C.text2, margin: 0, isTextBox: true });
  table(s, [["", "今", "20年後"], ["空", "45%", "46%"], ["地面", "2%", "10%"], ["見える建物", "56棟", "43棟"]],
    5.1, 3.75, 4.4, [1.6, 1.4, 1.4], { header: true, fontSize: 13, rowH: 0.3, hl: (i, j) => i === 1 && j === 2 });
}

// ================================================================ 10. 夕日
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("もうひとつの眺望：夕日は見える？", { placeholder: "title" });
  shot(s, "sunset.jpg", 0.5, 1.1, 5.2);
  s.addText("日付を選ぶと、日の入り前の太陽の方向に視線を飛ばし、建物に隠れるかを調べる", { x: 6.0, y: 1.1, w: 3.5, h: 0.8, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  card(s, 6.0, 2.0, 3.5, 1.3, "夕日の結果");
  s.addText([{ text: "11月18日：", options: { bold: true } }, { text: "15:55〜16:45 ごろ見える", options: { bold: true, color: C.accent1, breakLine: true } },
    { text: "日の入り 16:50 ごろ（南西）" }], { x: 6.2, y: 2.1, w: 3.1, h: 1.1, fontSize: 14, color: C.text1, margin: 0, valign: "middle", isTextBox: true });
  s.addText("京都タワーを望む10階・南西向きの窓。夏至（6/21）は日の入りが北西になり、この窓からは見えない。山の影は含まない。",
    { x: 6.0, y: 3.45, w: 3.5, h: 1.0, fontSize: 10, color: C.text2, margin: 0, valign: "top", isTextBox: true });
}

// ================================================================ 11. なぜ京都か
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("なぜ京都か：データによって数えられるものが違う", { placeholder: "title" });
  s.addText([
    { text: "建て替え時期の目安には、建物ごとの建築年と構造が必要", options: { bullet: true, breakLine: true } },
    { text: "京都駅周辺：72% の建物に建築年がある（2,634棟中 1,892棟）。構造は 74% にある", options: { bullet: true, breakLine: true } },
    { text: "東京23区（2025年度データ、調べた3地域）：建築年は 0%", options: { bullet: true, breakLine: true } },
    { text: "東京では代わりに「高さ10m未満の低い建物」の割合を出す", options: { bullet: true } },
  ], { x: 0.5, y: 1.15, w: 4.7, h: 3.2, fontSize: 14, color: C.text1, paraSpaceAfter: 10, valign: "top", isTextBox: true });
  shot(s, "tokyo.jpg", 5.5, 1.15, 4.0);
  s.addText("東京・八重洲 12階・西向き（ビルの谷間）：空 23%・建物 49%", { x: 5.5, y: 3.55, w: 4.0, h: 0.5, fontSize: 10, color: C.text2, margin: 0, isTextBox: true });
}

// ================================================================ 12. 既存との違い
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("景色を「見せる」から「数える」へ", { placeholder: "title" });
  table(s, [
    ["作品・サービス", "できること", "窓の眺望診断との違い"],
    ["PLATEAU Window（PLATEAU AWARD 2022 受賞）", "窓からの景色を、日時・天候つきで再現して見せる", "景色を建物ごとに数え、建て替えによる変わりやすさを示す。夕日も見えるか・何時までを判定"],
    ["Google の写実的な3D地図", "写真のような3D表示", "建物ごとの属性がない。3D Tiles から抽出・派生したデータの利用は規約で制限"],
    ["Shadowmap", "日照と影", "景色の構成と、建て替えによる変化が中心"],
  ], 0.5, 1.15, 9, [2.4, 2.6, 4.0], { header: true, fontSize: 12, rowH: 0.7, left: true });
}

// ================================================================ 13. これから
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("これから：眺望の「寿命」を予測する", { placeholder: "title" });
  const next = [
    ["建て替え後の高さ", "用途地域の制限などから、建て替え後の高さを見積もり、空が減る場合も示す"],
    ["実際の変化と比べる", "年度の違う PLATEAU データを比べ、景色が実際にどう変わってきたかを示す"],
    ["逆方向の眺望", "自分の窓が、周りのどの建物から見えるかを数える"],
    ["ほかの都市へ", "建築年・構造が整備された都市へ広げ、内見・購入前のチェックに使う"],
  ];
  next.forEach(([h, t], i) => {
    const x = 0.5 + (i % 2) * 4.6, y = 1.15 + Math.floor(i / 2) * 1.75;
    card(s, x, y, 4.4, 1.55, `これから${i + 1}`);
    s.addText(h, { x: x + 0.25, y: y + 0.15, w: 3.9, h: 0.4, fontSize: 16, bold: true, color: C.accent1, margin: 0, isTextBox: true });
    s.addText(t, { x: x + 0.25, y: y + 0.6, w: 3.9, h: 0.85, fontSize: 13, color: C.text1, margin: 0, valign: "top", isTextBox: true });
  });
}

// ================================================================ 14. 限界と出典
{
  const s = pres.addSlide({ masterName: "CONTENT" });
  s.addText("限界と出典", { placeholder: "title" });
  s.addText([
    { text: "目線の高さは「階数×3 m」と仮定（窓の位置はデータにない）", options: { bullet: true, breakLine: true } },
    { text: "高さは京都駅付近の実測値で地面に合わせており、離れると誤差が出る", options: { bullet: true, breakLine: true } },
    { text: "耐用年数は税金の計算のための年数で、実際の寿命や建て替え計画ではない", options: { bullet: true, breakLine: true } },
    { text: "鉄骨造は骨格材4mm超、軽量鉄骨造は3〜4mm、文教厚生施設・用途不明は住宅用として年数を当てた", options: { bullet: true, breakLine: true } },
    { text: "構造が不明な建物は判定できない（京都駅周辺の約26%）", options: { bullet: true, breakLine: true } },
    { text: "太陽の位置は近似式。山の影は含まない", options: { bullet: true } },
  ], { x: 0.5, y: 1.1, w: 5.3, h: 3.9, fontSize: 12, color: C.text1, paraSpaceAfter: 6, valign: "top", isTextBox: true });
  card(s, 6.1, 1.1, 3.4, 3.0, "出典");
  s.addText([
    { text: "出典・使用技術", options: { bold: true, color: C.accent1, breakLine: true } },
    { text: "3D都市モデル：国土交通省 Project PLATEAU（京都市・東京都千代田区・中央区）", options: { bullet: true, breakLine: true } },
    { text: "耐用年数：国税庁「耐用年数（建物／建物附属設備）」", options: { bullet: true, breakLine: true } },
    { text: "背景地図：国土地理院 地理院タイル", options: { bullet: true, breakLine: true } },
    { text: "3D表示：CesiumJS", options: { bullet: true } },
  ], { x: 6.3, y: 1.25, w: 3.0, h: 2.75, fontSize: 11, color: C.text1, paraSpaceAfter: 6, valign: "top", isTextBox: true });
}

// ================================================================ 15. 試してみる
{
  const s = pres.addSlide({ masterName: "DARK" });
  s.addText("ブラウザで、すぐに試せます", { x: 0.5, y: 0.5, w: 9, h: 0.7, fontSize: 30, bold: true, color: "FFFFFF", margin: 0, isTextBox: true });
  s.addShape(pres.shapes.ROUNDED_RECTANGLE, { x: 0.5, y: 1.5, w: 2.2, h: 2.2, rectRadius: 0.08, fill: { color: "FFFFFF" }, line: { color: "FFFFFF" }, objectName: "QR の台紙" });
  s.addImage({ path: IMG("qr.png"), x: 0.65, y: 1.65, w: 1.9, h: 1.9 });
  s.addText([
    { text: SCORE ? "入り口（元の版・耐用年数版・スコア版を選べる）" : "入り口（元の版・耐用年数版を選べる）", options: { bold: true, breakLine: true } },
    { text: URL_TOP, options: { hyperlink: { url: URL_TOP }, color: "9FD0FF", breakLine: true } },
    { text: " ", options: { breakLine: true } },
    { text: "例の窓（東本願寺の近く・7階・北向き）をそのまま開く", options: { bold: true, breakLine: true } },
    { text: URL_VIEW, options: { hyperlink: { url: URL_VIEW }, color: "9FD0FF", fontSize: 10 } },
  ], { x: 3.0, y: 1.5, w: 6.5, h: 2.2, fontSize: 14, color: "FFFFFF", margin: 0, valign: "top", isTextBox: true });
  s.addText("パソコンのブラウザ（Chrome・Edge など）向け。「おすすめの窓」ボタンで、京都タワーを望む窓や東京駅の窓にも切り替えられます。",
    { x: 0.5, y: 4.2, w: 9, h: 0.6, fontSize: 13, color: "DDE3EA", margin: 0, isTextBox: true });
}

(async () => {
  await pres.writeFile({ fileName: OUT });
  // テーマの色を書き込む（PPTX_SKILL に apply_theme.js のある場所を指定したときだけ。なくても開ける）
  if (process.env.PPTX_SKILL) {
    const { applyTheme } = require(process.env.PPTX_SKILL + "/scripts/apply_theme.js");
    await applyTheme(OUT, THEME);
  }
  console.log("saved", OUT);
})();
