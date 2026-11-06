# PLATEAU AWARD 応募作品（仮）

国土交通省 [Project PLATEAU](https://www.mlit.go.jp/plateau/) の3D都市モデルを使った作品のリポジトリです。
作品の内容はまだ決まっていません。今は、どの作品にも使える次の2つを用意しています。

| フォルダ | 内容 |
| --- | --- |
| `viewer/` | 東京23区の3D都市モデルをブラウザで見るビューア（データ確認用） |
| `tools/` | PLATEAU のデータカタログ検索と、建物の CityGML を GeoJSON・CSV に変換するスクリプト |

作品本体の技術（Web にするか Unity にするか）はまだ決めていません。
ビューアはビルド不要の HTML + JavaScript だけで作っているので、作品の技術とは切り離して使えます。

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

## Unity で使う場合のメモ

- 3Dモデルを Unity に取り込むなら、公式の [PLATEAU SDK for Unity](https://github.com/Project-PLATEAU/PLATEAU-SDK-for-Unity) が便利です。CityGML を直接読み込めます。
- このリポジトリの `tools/` で作った CSV（建物ごとの緯度・経度、高さ、用途、浸水深さ）は、ゲームで使うデータ（敵の出現位置、イベントを起こす建物など）として Unity に読み込めます。

---

## データの出典・ライセンス

- 3D都市モデル: 国土交通省 Project PLATEAU（[PLATEAU のサイトポリシー](https://www.mlit.go.jp/plateau/site-policy/)に従って利用。CC BY 4.0 相当）
  - データカタログ: `https://api.plateauview.mlit.go.jp/datacatalog/plateau-datasets`
- 背景地図: [国土地理院 地理院タイル（淡色地図）](https://maps.gsi.go.jp/development/ichiran.html)
- 3D表示ライブラリ: [CesiumJS](https://cesium.com/platform/cesiumjs/)（Apache License 2.0）
