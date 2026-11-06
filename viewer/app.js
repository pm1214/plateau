// PLATEAU 東京ビューア
// - Cesium ion のトークン不要（背景は国土地理院タイル、地形は楕円体）
// - 区とレイヤーの一覧は data/tokyo-tilesets.json（tools/plateau_catalog.py で生成）
/* global Cesium */

const DEFAULT_WARD = "13101"; // 千代田区
const DEFAULT_LAYER_TYPES = ["bldg"];
// PLATEAU の 3D Tiles の高さは楕円体高。地形なし（楕円体）で表示すると
// ジオイド高（東京付近で約 36.7m）ぶん浮いて見えるため、その分だけ下げる。
const GEOID_OFFSET_M = 36.7;

// 3D Tiles の属性名（データの版によって名前が違うので候補を並べる）
const PROP = {
  height: ["計測高さ", "bldg:measuredHeight", "measuredHeight"],
  usage: ["用途", "bldg:usage", "usage"],
};

const $ = (s) => document.querySelector(s);
const status = (msg) => ($("#status").textContent = msg || "");

// ------------------------------------------------------------ Viewer

const viewer = new Cesium.Viewer("cesium", {
  baseLayer: new Cesium.ImageryLayer(
    new Cesium.UrlTemplateImageryProvider({
      url: "https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png",
      minimumLevel: 2,
      maximumLevel: 18,
      credit: new Cesium.Credit("国土地理院", false),
    }),
  ),
  terrainProvider: new Cesium.EllipsoidTerrainProvider(),
  baseLayerPicker: false,
  geocoder: false,
  timeline: false,
  animation: false,
  sceneModePicker: false,
  navigationHelpButton: false,
  fullscreenButton: false,
  infoBox: false,
  selectionIndicator: false,
});
viewer.scene.globe.depthTestAgainstTerrain = true;
viewer.scene.skyAtmosphere.show = true;

// 東京駅周辺から開始
viewer.camera.setView({
  destination: Cesium.Cartesian3.fromDegrees(139.7671, 35.6712, 1200),
  orientation: { heading: 0, pitch: Cesium.Math.toRadians(-35), roll: 0 },
});

// ------------------------------------------------------------ データ

const catalog = await fetch("data/tokyo-tilesets.json").then((r) => r.json());
const params = new URLSearchParams(location.search);
const loaded = new Map(); // layer.id -> Cesium3DTileset
let currentWard = null;

function fmtSize(bytes) {
  if (!bytes) return "";
  return bytes > 1e9 ? `${(bytes / 1e9).toFixed(1)}GB` : `${Math.round(bytes / 1e6)}MB`;
}

function layerLabel(l) {
  const lod = l.lod ? ` LOD${l.lod}` : "";
  const tex = l.type === "bldg" && l.lod === "2" ? (l.texture ? "（テクスチャあり）" : "（白モデル）") : "";
  return `${l.name}${lod}${tex}`;
}

// 建物は「LOD2 白モデル」→「LOD1」の順で軽いものを初期表示
function defaultLayers(city) {
  const bldg = city.layers.filter((l) => l.type === "bldg");
  const pick =
    bldg.find((l) => l.lod === "2" && !l.texture) || bldg.find((l) => l.lod === "1") || bldg[0];
  return new Set(pick ? [pick.id] : []);
}

const wardSel = $("#ward");
for (const c of catalog.cities) {
  wardSel.add(new Option(c.name, c.code));
}
wardSel.value = params.get("ward") || DEFAULT_WARD;
wardSel.addEventListener("change", () => selectWard(wardSel.value, true));

async function addTileset(layer) {
  if (loaded.has(layer.id)) return loaded.get(layer.id);
  status(`読み込み中: ${layerLabel(layer)}`);
  const ts = await Cesium.Cesium3DTileset.fromUrl(layer.url, {
    maximumScreenSpaceError: 16,
  });
  // ジオイド高ぶん下げる
  const center = ts.boundingSphere.center;
  const up = Cesium.Ellipsoid.WGS84.geodeticSurfaceNormal(center, new Cesium.Cartesian3());
  ts.modelMatrix = Cesium.Matrix4.fromTranslation(
    Cesium.Cartesian3.multiplyByScalar(up, -GEOID_OFFSET_M, up),
  );
  ts.plateauLayer = layer;
  watchProps(ts);
  viewer.scene.primitives.add(ts);
  loaded.set(layer.id, ts);
  applyStyle(ts);
  status("");
  return ts;
}

function removeTileset(id) {
  const ts = loaded.get(id);
  if (!ts) return;
  viewer.scene.primitives.remove(ts); // remove で destroy される
  loaded.delete(id);
}

async function selectWard(code, fly) {
  const city = catalog.cities.find((c) => c.code === code) || catalog.cities[0];
  currentWard = city;
  for (const id of [...loaded.keys()]) removeTileset(id);

  const on = defaultLayers(city);
  const box = $("#layers");
  box.replaceChildren();
  // 種類ごとにまとめて表示（建物を先頭に）
  const order = (l) => (DEFAULT_LAYER_TYPES.includes(l.type) ? 0 : 1);
  for (const l of [...city.layers].sort((a, b) => order(a) - order(b))) {
    const label = document.createElement("label");
    const cb = document.createElement("input");
    cb.type = "checkbox";
    cb.checked = on.has(l.id);
    cb.addEventListener("change", async () => {
      if (cb.checked) await addTileset(l).catch(showError);
      else removeTileset(l.id);
    });
    const size = document.createElement("span");
    size.className = "size";
    size.textContent = fmtSize(l.size);
    label.append(cb, document.createTextNode(layerLabel(l)), size);
    box.append(label);
  }

  const first = await Promise.all(city.layers.filter((l) => on.has(l.id)).map(addTileset)).catch(
    showError,
  );
  if (fly && first?.[0]) {
    viewer.flyTo(first[0], {
      // 区全体だと遠すぎるので、最大 3km くらいの距離から見下ろす
      offset: new Cesium.HeadingPitchRange(
        0,
        Cesium.Math.toRadians(-35),
        Math.min(first[0].boundingSphere.radius * 1.2, 3000),
      ),
    });
  }
  const url = new URL(location.href);
  url.searchParams.set("ward", city.code);
  history.replaceState(null, "", url);
}

function showError(e) {
  console.error(e);
  status(`読み込みに失敗しました: ${e.message || e}`);
}

// ------------------------------------------------------------ 色分け

const USAGE_COLORS = [
  ["業務施設", "#4e79a7"],
  ["商業施設", "#f28e2b"],
  ["宿泊施設", "#b07aa1"],
  ["商業系複合施設", "#ff9da7"],
  ["住宅", "#59a14f"],
  ["共同住宅", "#8cd17d"],
  ["店舗等併用住宅", "#edc948"],
  ["店舗等併用共同住宅", "#d4a6c8"],
  ["官公庁施設", "#e15759"],
  ["文教厚生施設", "#76b7b2"],
  ["運輸倉庫施設", "#9c755f"],
  ["工場", "#79706e"],
];
const HEIGHT_STOPS = [
  [200, "#b2182b"],
  [100, "#ef8a62"],
  [60, "#fddbc7"],
  [31, "#d1e5f0"],
  [10, "#67a9cf"],
  [0, "#2166ac"],
];
const FLOOD_STOPS = [
  [5, "#dc7adc"],
  [3, "#ff91a0"],
  [0.5, "#ffb7b7"],
  [0.01, "#f7f5a9"],
];

function findProp(ts, candidates, test) {
  // 読み込まれたタイルの属性名から候補を探す
  const names = ts.plateauPropNames;
  if (!names) return candidates[0];
  return candidates.find((c) => names.has(c)) || [...names].find((n) => test?.(n));
}

function stopsCondition(prop, stops, unknownColor = "#cccccc") {
  const v = `Number(\${feature['${prop}']})`;
  return {
    conditions: [
      [`\${feature['${prop}']} === undefined || \${feature['${prop}']} === null`, `color('${unknownColor}')`],
      ...stops.map(([min, color]) => [`${v} >= ${min}`, `color('${color}')`]),
      ["true", `color('${unknownColor}')`],
    ],
  };
}

function styleFor(mode, ts) {
  if (ts.plateauLayer.type !== "bldg" || mode === "default") return undefined;
  if (mode === "height") {
    const p = findProp(ts, PROP.height, (n) => n.includes("高さ"));
    return new Cesium.Cesium3DTileStyle({ color: stopsCondition(p, HEIGHT_STOPS) });
  }
  if (mode === "usage") {
    const p = findProp(ts, PROP.usage, (n) => n === "用途" || n.endsWith(":usage"));
    return new Cesium.Cesium3DTileStyle({
      color: {
        conditions: [
          ...USAGE_COLORS.map(([u, c]) => [`\${feature['${p}']} === '${u}'`, `color('${c}')`]),
          ["true", "color('#d9d9d9')"],
        ],
      },
    });
  }
  if (mode === "flood" || mode === "hightide") {
    // 浸水深の属性は「<河川名>_<規模>_浸水深」「高潮浸水想定_<名称>_浸水深」のように
    // 想定ごとに分かれているので、該当する属性すべての最大値で色を付ける
    const names = [...(ts.plateauPropNames || [])].filter((n) => n.endsWith("_浸水深"));
    const isTide = (n) => n.startsWith("高潮");
    const isOther = (n) => n.startsWith("津波") || n.startsWith("内水");
    const props = names.filter((n) => (mode === "hightide" ? isTide(n) : !isTide(n) && !isOther(n)));
    if (props.length === 0) return new Cesium.Cesium3DTileStyle({ color: "color('#e6e6e6')" });
    const val = (n) => `(\${feature['${n}']} === undefined ? 0 : Number(\${feature['${n}']}))`;
    const expr = props.map(val).reduce((a, b) => `max(${a}, ${b})`);
    return new Cesium.Cesium3DTileStyle({
      defines: { depth: expr },
      color: {
        conditions: [
          ...FLOOD_STOPS.map(([min, color]) => [`\${depth} >= ${min}`, `color('${color}')`]),
          ["true", "color('#e6e6e6')"],
        ],
      },
    });
  }
  return undefined;
}

let styleMode = "default";

function applyStyle(ts) {
  ts.style = styleFor(styleMode, ts);
}

function renderLegend() {
  const lg = $("#legend");
  lg.replaceChildren();
  const rows =
    styleMode === "height"
      ? HEIGHT_STOPS.map(([m, c]) => [c, `${m}m 以上`])
      : styleMode === "usage"
        ? [...USAGE_COLORS.map(([u, c]) => [c, u]), ["#d9d9d9", "その他・不明"]]
        : styleMode === "flood" || styleMode === "hightide"
          ? [...FLOOD_STOPS.map(([m, c]) => [c, `${m}m 以上`]), ["#e6e6e6", "想定なし"]]
          : [];
  for (const [color, text] of rows) {
    const i = document.createElement("i");
    i.style.background = color;
    const s = document.createElement("span");
    s.textContent = text;
    lg.append(i, s);
  }
}

for (const r of document.querySelectorAll("input[name=style]")) {
  r.addEventListener("change", () => {
    styleMode = r.value;
    loaded.forEach(applyStyle);
    renderLegend();
  });
}

// 読み込んだタイルから属性名を集める（色分けで使う属性名を決めるため）
function watchProps(ts) {
  ts.tileLoad.addEventListener((tile) => {
    const content = tile.content;
    if (!content || content.featuresLength === 0) return;
    const names = (ts.plateauPropNames ||= new Set());
    const before = names.size;
    for (const n of content.getFeature(0).getPropertyIds()) names.add(n);
    if (names.size !== before) applyStyle(ts);
  });
}
// ------------------------------------------------------------ 建物を選ぶ

let highlighted = null;
const handler = new Cesium.ScreenSpaceEventHandler(viewer.scene.canvas);
handler.setInputAction((ev) => {
  if (highlighted) {
    highlighted.feature.color = highlighted.color;
    highlighted = null;
  }
  const picked = viewer.scene.pick(ev.position);
  if (!(picked instanceof Cesium.Cesium3DTileFeature)) {
    $("#info").hidden = true;
    return;
  }
  highlighted = { feature: picked, color: Cesium.Color.clone(picked.color) };
  picked.color = Cesium.Color.fromCssColorString("#ffd400");
  showInfo(picked);
}, Cesium.ScreenSpaceEventType.LEFT_CLICK);

function flatten(value, prefix, out) {
  if (value === null || value === undefined || value === "") return;
  if (typeof value === "object") {
    for (const [k, v] of Object.entries(value)) flatten(v, prefix ? `${prefix} / ${k}` : k, out);
  } else {
    out.push([prefix, value]);
  }
}

// クリックしたときに上に出す主な項目（[表示名, 属性名の候補...]）
const SUMMARY = [
  ["名称", "gml:name"],
  ["住所", "bldg:address"],
  ["用途", "bldg:usage"],
  ["詳細用途", "uro:BuildingDetailAttribute / 0 / uro:detailedUsage"],
  ["高さ (m)", "bldg:measuredHeight"],
  ["地上階数", "bldg:storeysAboveGround"],
  ["地下階数", "bldg:storeysBelowGround"],
  ["建築年", "bldg:yearOfConstruction"],
  ["構造", "uro:BuildingDetailAttribute / 0 / uro:buildingStructureType"],
  ["耐火構造", "uro:BuildingDetailAttribute / 0 / uro:fireproofStructureType"],
  ["用途地域", "uro:BuildingDetailAttribute / 0 / uro:districtsAndZonesType"],
  ["建物ID", "uro:BuildingIDAttribute / 0 / uro:buildingID"],
];

function showInfo(feature) {
  const rows = [];
  for (const id of feature.getPropertyIds()) {
    let v = feature.getProperty(id);
    if (typeof v === "string" && /^[[{]/.test(v)) {
      try {
        v = JSON.parse(v);
      } catch {
        /* そのまま */
      }
    }
    // 中身の「attributes」は元の CityGML 属性をまとめた JSON なので、先頭の名前を省く
    flatten(v, id === "attributes" ? "" : id, rows);
  }
  const all = new Map(rows);
  const summary = SUMMARY.map(([label, key]) => [label, all.get(key)]).filter(
    ([, v]) => v !== undefined && v !== "" && v !== 9999 && v !== -9999,
  );
  // 浸水想定（洪水・高潮・津波など）の深さ
  for (const [k, v] of rows) {
    const m = k.match(/uro:(\w+)RiskAttribute \/ (\d+) \/ uro:depth$/);
    if (!m) continue;
    const desc = all.get(k.replace("uro:depth", "uro:description")) || m[1];
    const scale = all.get(k.replace("uro:depth", "uro:scale"));
    summary.push([`浸水深 ${desc}${scale ? `（${scale}）` : ""}`, `${v} m`]);
  }

  fillTable($("#info-table"), summary);
  fillTable($("#info-all"), rows.filter(([k]) => !k.endsWith("_code") && !k.endsWith("_uom")));
  $("#info").hidden = false;
}

function fillTable(table, rows) {
  table.replaceChildren();
  for (const [k, v] of rows) {
    const tr = table.insertRow();
    const th = document.createElement("th");
    th.textContent = k;
    tr.append(th);
    tr.insertCell().textContent = String(v);
  }
}

// ------------------------------------------------------------ 影・時刻

const hour = $("#hour");
function setHour() {
  const h = Number(hour.value);
  const d = new Date();
  // 日本時間の h 時（UTC+9）
  d.setUTCHours(Math.floor(h) - 9, Math.round((h % 1) * 60), 0, 0);
  viewer.clock.currentTime = Cesium.JulianDate.fromDate(d);
  $("#hour-label").textContent = `${Math.floor(h)}:${String(Math.round((h % 1) * 60)).padStart(2, "0")}`;
}
$("#shadows").addEventListener("change", (e) => {
  viewer.shadows = e.target.checked;
  viewer.scene.globe.enableLighting = e.target.checked;
  hour.disabled = !e.target.checked;
  setHour();
});
hour.addEventListener("input", setHour);
setHour();

$("#toggle-panel").addEventListener("click", () => $("#panel").classList.toggle("collapsed"));

// ------------------------------------------------------------ 開始

// デバッグ用（ブラウザのコンソールから window.app.viewer などで触れる）
window.app = { viewer, loaded, catalog };
await selectWard(wardSel.value, false);
