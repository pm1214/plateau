# PLATEAU AWARD 応募作品（仮）

国土交通省 [Project PLATEAU](https://www.mlit.go.jp/plateau/) の3D都市モデルを使った作品のリポジトリです。
作品の内容はまだ決まっていません。今は、どの作品にも使える次の2つを用意しています。

| フォルダ | 内容 |
| --- | --- |
| `viewer/` | 東京23区の3D都市モデルをブラウザで見るビューア（データ確認用） |
| `tools/` | PLATEAU のデータカタログ検索と、建物の CityGML を GeoJSON・CSV に変換するスクリプト |

作品本体の技術（Web にするか Unity にするか）はまだ決めていません。
ビューアはビルド不要の HTML + JavaScript だけで作っているので、作品の技術とは切り離して使えます。

## 現在できること・今後の予定

| | 内容 |
| --- | --- |
| できること | 東京23区の3D都市モデルの表示・色分け・属性確認（`viewer/`） |
| | PLATEAU のデータカタログ検索、建物 CityGML の GeoJSON・CSV への変換（`tools/`） |
| | ネットワークなしで動くテストと CI（`tests/`、`.github/workflows/test.yml`） |
| 今後の予定 | 作品の企画を決める（[docs/concept.md](docs/concept.md)。候補を3つ記載） |
| | 1地域・1体験の最小プロトタイプを作る（[docs/prototype-plan.md](docs/prototype-plan.md)） |
| | 作品の形（Web / Unity）を決める。Unity にする場合は [docs/unity-setup.md](docs/unity-setup.md) |
| 未定 | 作品の内容、作品の形、応募部門（応募要項は公式サイトで確認して concept.md に記録する） |

## 資料

| 資料 | 内容 |
| --- | --- |
| [docs/concept.md](docs/concept.md) | 作品企画のひな形と、企画案の候補 |
| [docs/prototype-plan.md](docs/prototype-plan.md) | 最小プロトタイプの開発計画（完了条件つき） |
| [docs/data-management.md](docs/data-management.md) | データ台帳、出典・利用条件、キャッシュ、Git に置くもの／置かないもの |
| [docs/unity-setup.md](docs/unity-setup.md) | Unity ＋ 公式 PLATEAU SDK を導入するときの手順と確認項目 |
| [AGENTS.md](AGENTS.md) | 作業ルール（構成、検証コマンド、コミットしないもの） |
| `.github/ISSUE_TEMPLATE/` | プロトタイプ作業用・不具合報告用の Issue テンプレート |

---

## 応募作品: 窓の眺望診断（`viewer/window.html`）

窓から見える景色を、PLATEAU の建物属性で「中身」まで分解して数えます。企画の詳細は [CLAUDE.md](CLAUDE.md)。

- 対象: 京都駅周辺（下京区・南区の LOD2 建物。京都市のデータには建築年が入っているため）
- 操作: 立ち位置を選ぶ → 階数・向き・画角を決めて「窓から見る」→「景色を数える」
- 結果: 空・地面・建物の割合、用途ごとの割合と棟数、築40年以上の建物が視界に占める割合
- 将来との比較: 建物を消す・箱型の仮の建物を置く →「今と将来を比べる」
- H キーでパネルを隠せます（動画撮影用。隠すと画面全体を数えます）

ローカルで開く:

```bash
python3 -m http.server 8000 -d viewer
```

起動したら http://localhost:8000/window.html を開きます。

- エリア切り替え: `window.html?area=tokyo` で東京駅周辺（建築年がないため、代わりに高さ10m未満の建物の割合を表示）
- 夕日: 日付を選ぶと、窓から夕日（太陽の高さ10°以下）が見える時刻を調べます

- 耐用年数版 `viewer/window2.html`: 建物ごとに「建築年＋耐用年数（国税庁の表の、構造・用途ごとの年数）」で建て替え時期の目安を出し、3D の色分けと「◯年後の景色」（その時期を迎える建物を取り壊した場合）の比較ができます。`window.html` はそのまま残しています。

提出用の資料: スライドの元 `docs/slides/index.html`、台本 `docs/presentation.md`。PDF は `node docs/slides/build.js out/slides.pdf` で書き出します（Playwright が必要）。

注意: 建物の高さは京都駅付近の実測値（63 m）で地面に合わせています。駅から離れて土地の高さが変わるとずれます。建築年が「1」の建物は「不明」として数えます。

---

## 1. ビューア（`viewer/`）

CesiumJS で PLATEAU の 3D Tiles を表示します。Cesium ion のアカウントやトークンは不要です。

- 東京23区を切り替えて表示できる（建物・橋・道路・植生・地下街・都市設備など）
- 建物を色分けできる：高さ／用途／洪水（河川）の浸水深さ／高潮の浸水深さ
- 建物をクリックすると、名称・用途・高さ・階数・浸水想定などの属性を表示
- 時刻を変えて影を確認できる
- URL の `?ward=13104` で最初に表示する区を指定できる（例: 13104 = 新宿区）

### ローカルで起動

```bash
python3 -m http.server 8000 -d viewer
```

起動したら、ブラウザで http://localhost:8000/ を開きます。

### 公開（GitHub Pages）

`main` ブランチに push すると、`.github/workflows/pages.yml` が `viewer/` を GitHub Pages に公開します。
初回だけ、リポジトリの **Settings → Pages → Build and deployment → Source** を「GitHub Actions」にしてください。

---

## 2. データツール（`tools/`）

Python 3.10 以上で動きます。外部ライブラリは使っていません（`pip install` 不要）。

### データカタログの検索 `plateau_catalog.py`

PLATEAU VIEW のデータカタログ API から、3D Tiles・MVT・CityGML の URL を調べます。
カタログは `.cache/` に1日キャッシュします。

```bash
# 東京23区で使えるデータの種類と、それがある区の数（アイデア探し用）
python3 tools/plateau_catalog.py summary --pref 13 --city-prefix 131

# 千代田区の建物の 3D Tiles の URL
python3 tools/plateau_catalog.py list --pref 13 --city 千代田区 --type bldg

# 東京都の全データを CSV に保存
python3 tools/plateau_catalog.py list --pref 13 --csv out/tokyo_datasets.csv

# 地域メッシュ（約1km四方）に含まれる CityGML ファイルの URL
python3 tools/plateau_catalog.py citygml 53394611 --type bldg

# ビューアの区・レイヤー一覧（viewer/data/tokyo-tilesets.json）を最新にする
python3 tools/plateau_catalog.py viewer-json --pref 13 --city-prefix 131 --out viewer/data/tokyo-tilesets.json
```

### 建物 CityGML → GeoJSON / CSV `citygml_to_geojson.py`

建物の足元の形（フットプリント）と主な属性を取り出します。
GeoJSON は Web 地図に、CSV（建物の中心の緯度・経度つき）は Excel や Unity での読み込みに使えます。

```bash
# 緯度経度を指定すると、その地点を含む約1km四方を変換（例: 東京駅）
python3 tools/citygml_to_geojson.py --latlon 35.681236 139.767125 \
  -o out/tokyo_station.geojson --csv out/tokyo_station.csv

# メッシュコードで指定
python3 tools/citygml_to_geojson.py --mesh 53394611 -o out/53394611.geojson
```

取り出す属性は次のとおりです。

- 名称、住所、用途、詳細用途、高さ、地上・地下の階数、建築年、構造、耐火構造、延べ床面積
- 土地利用、用途地域
- 浸水深さの最大値（洪水・津波・高潮・内水）、土砂災害警戒区域かどうか
- LOD2・LOD3 のモデルがあるかどうか

用途などのコード値は、配布データに含まれるコードリストで日本語に変換します。
`--generic` を付けると、自治体独自の属性（`gen:*`）も出力します。

### 緯度経度 ⇔ 地域メッシュ `meshcode.py`

```bash
python3 tools/meshcode.py 35.681236 139.767125   # → 53394611
python3 tools/meshcode.py 53394611               # → そのメッシュの範囲
```

PLATEAU の CityGML は3次メッシュ（約1km四方、8桁）ごとにファイルが分かれています。
1ファイルは数十〜数百 MB あります。ダウンロードしたファイルは `.cache/` に保存し、2回目以降はそれを使います。

---

## 3. テスト

```bash
python3 -m unittest discover -s tests
```

外部 API への接続や都市データのダウンロードはせず、`tests/fixtures/` の小さな手書きデータで確かめます。
GitHub Actions（`.github/workflows/test.yml`）でも、Python 3.10 と 3.13 で同じテストを実行します。
あわせて、ビューアの JavaScript の構文と、5 MB を超えるファイルがコミットされていないかも確認します。

## 既知の問題

現在、把握している未修正の不具合はありません。

---

## Unity で使う場合のメモ

- 3Dモデルを Unity に取り込む場合は、公式の [PLATEAU SDK for Unity](https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unity) の利用を検討しています（未導入）。手順と確認項目は [docs/unity-setup.md](docs/unity-setup.md) にまとめています。
- このリポジトリの `tools/` で作った CSV（建物ごとの緯度・経度、高さ、用途、浸水深さ）は、ゲームで使うデータ（敵の出現位置、イベントを起こす建物など）として Unity に読み込めます。

---

## データの出典・ライセンス

- 3D都市モデル: 国土交通省 Project PLATEAU
  - 利用条件は「[PLATEAU Site Policy](https://www.mlit.go.jp/plateau/site-policy/)『３．著作権について』に拠る」（G空間情報センターのデータセット情報で確認。詳細は [docs/data-management.md](docs/data-management.md)）
  - データカタログ: `https://api.plateauview.mlit.go.jp/datacatalog/plateau-datasets`
- 背景地図: [国土地理院 地理院タイル（淡色地図）](https://maps.gsi.go.jp/development/ichiran.html)
- 3D表示ライブラリ: [CesiumJS](https://cesium.com/platform/cesiumjs/)（Apache License 2.0）
