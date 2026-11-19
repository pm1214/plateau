# AGENTS.md — このリポジトリで作業する人・AI エージェント向けのルール

PLATEAU AWARD 応募作品の制作リポジトリです。作品の内容と作品の形（Web / Unity）は**未定**です。
企画は [docs/concept.md](docs/concept.md)、開発計画は [docs/prototype-plan.md](docs/prototype-plan.md) を見てください。

## 構成

| パス | 内容 |
| --- | --- |
| `viewer/` | CesiumJS（cdnjs から読み込み）の都市モデルビューア。ビルド不要の HTML / CSS / JS。GitHub Pages で公開する |
| `viewer/data/tokyo-tilesets.json` | ビューアの区・レイヤー一覧。`tools/plateau_catalog.py viewer-json` で生成し、Git で管理する |
| `tools/` | Python 標準ライブラリだけで動くツール（カタログ検索・CityGML 変換・メッシュコード） |
| `tests/` | `unittest` のテスト。`tests/fixtures/` は手書きの小さなテストデータ |
| `docs/` | 企画・計画・データ管理・Unity 導入の資料 |
| `.github/workflows/pages.yml` | `main` の `viewer/` を GitHub Pages に公開 |
| `.github/workflows/test.yml` | テスト・JS 構文チェック・大きなファイルのチェック（外部 API に接続しない） |
| `.github/ISSUE_TEMPLATE/` | プロトタイプ作業用・不具合報告用の Issue テンプレート |

Unity プロジェクトはまだありません。作るときは [docs/unity-setup.md](docs/unity-setup.md) に従います。

## 起動・検証コマンド

リポジトリのルートで実行します。Python 3.10 以上。外部ライブラリのインストールは不要です。

```bash
# テスト（ネットワーク不要）
python3 -m unittest discover -s tests

# Python の構文チェック
python3 -m py_compile tools/*.py

# ビューアの JS 構文チェック（トップレベル await があるので .mjs として検査）
cp viewer/app.js /tmp/app.mjs && node --check /tmp/app.mjs

# ローカルで起動 → http://localhost:8000/（入り口）、/window.html・/window2.html（作品）、/explore.html（データ確認用）
python3 -m http.server 8000 -d viewer
```

ネットワークが必要なコマンド（PLATEAU の配信サーバーに接続する）:

```bash
python3 tools/plateau_catalog.py summary --pref 13 --city-prefix 131
python3 tools/citygml_to_geojson.py --mesh 53394611 -o out/53394611_bldg.geojson --csv out/53394611_bldg.csv
```

## 生成物の保存先

| 生成物 | 保存先 | Git |
| --- | --- | --- |
| ダウンロードしたカタログ・CityGML・コードリスト | `.cache/` | 管理しない |
| 変換結果（GeoJSON・CSV） | `out/` | 管理しない |
| ビューア用の一覧 JSON | `viewer/data/` | 管理する（更新したら差分を確認） |
| 一時ファイル | OS の一時フォルダ、または作業用のスクラッチ領域 | 管理しない |

## 守ること

1. **既存の変更を保護する。** 作業を始める前に `git status` と `git diff` で未コミットの変更を確認する。
   自分が作っていない変更を、元に戻したり、上書きしたり、勝手にコミットに含めたりしない。
   `git reset --hard`・`git checkout -- <file>`・`git clean`・`git stash drop`・force push は、依頼がない限りしない。
2. **秘密情報をコミットしない。** API キー・トークン・パスワード・`.env` はリポジトリに入れない。
3. **巨大な都市データをコミットしない。** CityGML・3D Tiles・ZIP・Unity の取り込み結果などは Git に入れない。
   CI は 5 MB を超えるファイルがあると失敗する。詳しくは [docs/data-management.md](docs/data-management.md)。
4. **Git worktree を作らない。** 今のクラウド環境はタスクごとに隔離されているので、明示的な依頼がなければ worktree は作らず、今のチェックアウトで作業する。
5. **実行していない検証を成功扱いしない。** 報告では「実行して成功」「実行して失敗」「実行していない（理由）」を分けて書く。
   テストを通すために、テストを消す・スキップする・期待値を不具合に合わせて書き換えることはしない。
6. **不具合を見つけたら報告する。** 依頼の範囲外の不具合は、勝手に直さず報告する（テストでは `expectedFailure` と理由のコメントで記録してよい）。
7. **事実と推測を分ける。** 応募要項（年度・締切・審査基準）、データの利用条件、Unity・SDK のバージョンは、確認した情報だけを書き、出典と確認日を添える。
8. **外部依存は最小限にする。** `tools/` は標準ライブラリのみ、`viewer/` はビルド不要を保つ。追加が必要なら理由を書く。
9. **ビューアを公開している仕組みを壊さない。** `viewer/` のパス構成と `pages.yml` を変えるときは、公開への影響を確認する。

## 既知の問題

現在、把握している未修正の不具合はありません。
見つけた不具合を範囲外として残すときは、テストに `expectedFailure` と理由のコメントを付けて記録し、ここに書きます。
修正したら `expectedFailure` を外してください（外さないと「想定外の成功」としてテストが失敗します）。
