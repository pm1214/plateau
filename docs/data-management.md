# データ管理

> 使うデータの出どころ・条件・保存場所を記録します。
> **出典や利用条件は、確認できた事実だけを書き、確認日を添えます。確認できていないものは「未確認」と書きます。**

---

## 1. データ台帳（ひな形）

使うデータを1行ずつ追加します。下の行は、このリポジトリで実際に使ったデータの記録です。

| データ | 対象地域 | データ年度 / 仕様 | 形式 | 配信元 URL | 取得日 | 座標系 | 保存先 | 備考 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| データカタログ（全国の一覧） | 全国 | — | JSON | `https://api.plateauview.mlit.go.jp/datacatalog/plateau-datasets` | 2026-11-06 | — | `.cache/plateau-datasets.json`（Git 管理外） | 約 10 MB。ツールが1日キャッシュする |
| 東京23区の 3D Tiles 一覧（ビューア用） | 東京23区 | `latest`（年度は固定されていない） | JSON | 上のカタログから生成 | 2026-11-06 | — | `viewer/data/tokyo-tilesets.json`（Git 管理） | 23区・204レイヤー。`generated_at` に生成日 |
| 建築物 CityGML（東京駅周辺） | 3次メッシュ `53394611` | 2025年度 / 標準製品仕様書 第5.0版 | CityGML | `https://api.plateauview.mlit.go.jp/datacatalog/citygml/m:53394611` で URL を取得 | 2026-11-06 | EPSG:6697（緯度・経度・標高） | `.cache/citygml/`（Git 管理外） | 約 166 MB、1022 棟。千代田区と中央区の両方の配布物に、このメッシュのファイルが入っている（ツールは最初に見つかった千代田区のものを使う） |
| 背景地図（淡色地図） | 全国 | — | 画像タイル | `https://cyberjapandata.gsi.go.jp/xyz/pale/{z}/{x}/{y}.png` | ビューア表示時に毎回 | Web メルカトル | 保存しない | ズーム 2〜18 を使う |
| 建築物 CityGML（錦糸町） | 3次メッシュ `53394635` | 2025年度 / 第5.0版 | CityGML | `https://api.plateauview.mlit.go.jp/datacatalog/citygml/m:53394635` で URL を取得（墨田区の配布物） | 2026-11-08 | EPSG:6697 | `.cache/citygml/`（Git 管理外） | 約 66 MB、2,323 棟 |
| 建築物 CityGML（下北沢） | 3次メッシュ `53393593` | 2025年度 / 第5.0版 | CityGML | `https://api.plateauview.mlit.go.jp/datacatalog/citygml/m:53393593` で URL を取得（世田谷区の配布物） | 2026-11-08 | EPSG:6697 | `.cache/citygml/`（Git 管理外） | 約 74 MB、4,903 棟 |
| （追加するデータ） | | | | | | | | |

### 座標系・高さについて確認できたこと

- 建築物 CityGML のファイルには `srsName="http://www.opengis.net/def/crs/EPSG/0/6697"` と書かれており、座標は「緯度 経度 高さ」の順。
  `tools/citygml_to_geojson.py` は GeoJSON の「経度, 緯度」の順に並べ替えている。
- データカタログの 3D Tiles の項目には `"crs": "JGD2011"` と書かれているものがある。
- ビューアでは、地形なし（楕円体）で表示すると建物が浮くため、`viewer/app.js` で 36.7 m 下げている。
  これは東京付近のジオイド高に合わせた**実測での調整**で、公式資料で確かめた値ではない。東京以外では合わない可能性がある。

### データについて確認できたこと（2026-11-08）

- 東京23区の 2025 年度の建築物 CityGML（上の3メッシュ）には、建築年・延べ床面積の要素が入っていない。
- 構造は `uro:buildingStructureType` ではなく、`uro:KeyValuePairAttribute` のキー 100「建物構造コード」として入っている（コードリスト `KeyValuePairAttribute_key100.xml`: 11 耐火構造、12 準防火造、21 防火造、22 木造、0 調査時不明、99 不明）。今の `tools/citygml_to_geojson.py` はこれを取り出していない。
- 道路モデル（`tran`）は道路の面（`tran:Road` と `tran:TrafficArea` のポリゴン）で、道の中心線やネットワークは含まれていない（`53394635` の `tran` ファイルで確認）。
- 洪水・高潮の浸水想定区域モデル（`fld`・`htd`）の 2025 年度版は、データカタログの `datasets` には墨田区・江東区・世田谷区などがあるが、`latest_datasets` には23区の分が入っていない。ビューア用の一覧は `latest_datasets` から作っているため、ビューアには浸水区域のレイヤーが出ない。
- 植生モデル（`veg`）は23区のうち9区にある（中央区・千代田区・台東区・墨田区・新宿区・江東区・渋谷区・港区・豊島区）。

## 2. 出典・利用条件

| 対象 | 確認できた事実 | 確認日 | 確認した場所 | 未確認の点 |
| --- | --- | --- | --- | --- |
| PLATEAU 3D都市モデル | G空間情報センターのデータセット「plateau-13101-chiyoda-ku-2025」の情報では、ライセンスは「PLATEAU Site Policy『３．著作権について』に拠る」（`https://www.mlit.go.jp/plateau/site-policy/`）。説明文に「商用利用も含め、どなたでも無償で自由にご利用いただけます。」とある | 2026-11-08 | `https://www.geospatial.jp/ckan/api/3/action/package_show?id=plateau-13101-chiyoda-ku-2025` | サイトポリシー本文（出典表記の書き方、加工時の表示など）は未確認。他の都市・年度のデータも同じ条件かは未確認 |
| 地理院タイル（背景地図） | — | — | — | 利用条件・出典表記の書き方は未確認（国土地理院の利用規約を確認すること） |
| CesiumJS 1.120.0（cdnjs から読み込み） | Apache License 2.0 で配布されているライブラリ | — | — | 配信元（cdnjs）の利用条件は未確認 |

作品に入れる出典表記（案。上の未確認の点を確認してから確定する）:

```
出典: 国土交通省 Project PLATEAU（3D都市モデル）
背景地図: 国土地理院
```

## 3. 再取得の方法とキャッシュ方針

| データ | 再取得の方法 | キャッシュ |
| --- | --- | --- |
| データカタログ | `python3 tools/plateau_catalog.py --refresh summary --pref 13` | `.cache/plateau-datasets.json`（24時間で自動更新） |
| ビューア用一覧 | `python3 tools/plateau_catalog.py viewer-json --pref 13 --city-prefix 131 --out viewer/data/tokyo-tilesets.json` | なし（Git で管理し、更新したら差分を確認してコミット） |
| 建築物 CityGML | `python3 tools/citygml_to_geojson.py --mesh <メッシュコード> ...` が自動でダウンロード | `.cache/citygml/<ファイル名>`。同じ名前のファイルがあれば再ダウンロードしない |
| コードリスト | 変換時に自動で取得 | `.cache/codelists/` |
| 変換結果（GeoJSON・CSV） | 上のコマンドで作り直せる | `out/`（Git 管理外） |

- `.cache/` と `out/` は消しても、コマンドで作り直せる。
- 配信元のデータが更新されると、同じコマンドでも結果が変わることがある。作品で使ったデータは、台帳に取得日を残す。
- CityGML のファイルは1つで数十〜数百 MB ある（例: 東京駅周辺を含む2次メッシュ `533946` の地形 `dem` は約 360 MB、高潮浸水想定 `htd` は約 560 MB）。必要なメッシュ・種類だけを取る。

## 4. Git に置くもの／置かないもの

| 置く | 置かない |
| --- | --- |
| ソースコード（`tools/`・`viewer/`・`tests/`） | `.cache/`（ダウンロードしたカタログ・CityGML・コードリスト） |
| 小さな設定・一覧データ（`viewer/data/tokyo-tilesets.json` など） | `out/`（変換結果。作り直せる） |
| テスト用の小さな手書きデータ（`tests/fixtures/`） | 配信元からそのまま取った CityGML・3D Tiles・FBX・OBJ・ZIP |
| 資料（`docs/`） | API キー・トークン・パスワード・`.env` |
| | Unity の生成物（`Library/` など。[unity-setup.md](unity-setup.md)） |

CI（`.github/workflows/test.yml`）は、5 MB を超えるファイルがコミットされていると失敗します。

## 5. 小さな検証用データ・大容量モデル・Git LFS の使い分け

| 種類 | 目安 | 置き場所 | 方針 |
| --- | --- | --- | --- |
| 検証用の小さなデータ | 数 KB〜数百 KB | `tests/fixtures/` | 手で書くか、本物から必要な部分だけ抜き出す。架空データならそう書く。CI はこれだけで動くようにする |
| 作品で使う変換済みデータ | 数 MB まで | 作品のフォルダ（未定） | 作り直すコマンドを README か台帳に書いてからコミットする |
| 大容量モデル（CityGML・3D Tiles・Unity に取り込んだメッシュやテクスチャ） | 5 MB 超 | Git の外（`.cache/` やローカル） | 配信元から再取得できるものはコミットしない。手順だけ残す |
| 作品に必須で再取得できない大きなファイル（自作の 3D モデル・音・動画など） | 5 MB 超 | Git LFS | 必要になった時点で導入を決める。**今は Git LFS を設定していない** |

Git LFS を導入する場合の注意:

- 導入するかは、必要なファイルが出てきてから決める（容量や転送量の上限は GitHub の最新の案内を確認する）。
- 導入するときは `git lfs track "<パターン>"` で対象を決め、`.gitattributes` をコミットする。
- PLATEAU から再取得できるデータは、LFS にも入れない。
