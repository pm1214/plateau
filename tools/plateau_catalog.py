#!/usr/bin/env python3
"""PLATEAU データカタログ取得ツール（標準ライブラリのみ）

PLATEAU VIEW のデータカタログ API から、都市ごとの 3D Tiles / MVT / CityGML の
URL を集めて一覧にします。

使い方:
  # 東京23区の建築物モデル（3D Tiles）を一覧表示
  python3 tools/plateau_catalog.py list --pref 13 --city-prefix 131 --type bldg

  # CSV に保存
  python3 tools/plateau_catalog.py list --pref 13 --type bldg --csv out/tokyo_bldg.csv

  # 東京都で使えるデータ種別を集計（アイデア探し用）
  python3 tools/plateau_catalog.py summary --pref 13

  # ビューア用の一覧 JSON（viewer/data/tokyo-tilesets.json）を作り直す
  python3 tools/plateau_catalog.py viewer-json --pref 13 --city-prefix 131 \
      --out viewer/data/tokyo-tilesets.json

  # 3次メッシュ（8桁）または区市町村コードで CityGML ファイルの URL を調べる
  python3 tools/plateau_catalog.py citygml 53394611
  python3 tools/plateau_catalog.py citygml 53394611 --type bldg
"""
from __future__ import annotations

import argparse
import collections
import csv
import json
import sys
import time
import urllib.request
from pathlib import Path

API_BASE = "https://api.plateauview.mlit.go.jp/datacatalog"
CATALOG_URL = f"{API_BASE}/plateau-datasets"
CACHE_DIR = Path(__file__).resolve().parent.parent / ".cache"
CACHE_TTL_SEC = 24 * 60 * 60

# データ種別コード（type_en）と日本語名の対応（主なもの）
TYPE_NAMES = {
    "bldg": "建築物",
    "tran": "道路",
    "rwy": "鉄道",
    "trk": "徒歩道",
    "squr": "広場",
    "wwy": "航路",
    "brid": "橋梁",
    "tun": "トンネル",
    "cons": "その他の構造物",
    "frn": "都市設備",
    "ubld": "地下街",
    "unf": "地下埋設物",
    "veg": "植生",
    "wtr": "水部",
    "luse": "土地利用",
    "lsld": "土砂災害警戒区域",
    "urf": "都市計画決定情報",
    "fld": "洪水浸水想定区域",
    "tnm": "津波浸水想定",
    "htd": "高潮浸水想定区域",
    "ifld": "内水浸水想定区域",
    "rfld": "ため池浸水想定区域",
    "area": "区域",
    "gen": "汎用都市オブジェクト",
    "dem": "地形",
}

UA = "plateau-award-tools/0.1"


def http_get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as res:
        return res.read()


def load_catalog(refresh: bool = False) -> dict:
    """データカタログ全体（約10MB）を取得する。1日キャッシュする。"""
    CACHE_DIR.mkdir(exist_ok=True)
    cache = CACHE_DIR / "plateau-datasets.json"
    if not refresh and cache.exists() and time.time() - cache.stat().st_mtime < CACHE_TTL_SEC:
        return json.loads(cache.read_text(encoding="utf-8"))
    print(f"カタログを取得中: {CATALOG_URL}", file=sys.stderr)
    data = http_get(CATALOG_URL)
    cache.write_bytes(data)
    return json.loads(data)


def filter_datasets(items, pref=None, city=None, city_prefix=None, types=None, fmt=None):
    for x in items:
        if pref and x.get("pref_code") != pref.zfill(2):
            continue
        if city and city not in (x.get("city_code"), x.get("city")):
            continue
        if city_prefix and not (x.get("city_code") or "").startswith(city_prefix):
            continue
        if types and x.get("type_en") not in types:
            continue
        if fmt and (x.get("format") or "").lower() != fmt.lower():
            continue
        yield x


def cmd_list(args):
    cat = load_catalog(args.refresh)
    items = cat["datasets"] if args.all_years else cat["latest_datasets"]
    rows = list(
        filter_datasets(items, args.pref, args.city, args.city_prefix, args.type, args.format)
    )
    cols = ["id", "city_code", "city", "type_en", "type", "name", "format", "lod", "texture",
            "year", "file_size", "url"]
    if args.csv:
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as f:
            w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} 件を {out} に保存しました", file=sys.stderr)
    elif args.json:
        json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)
    else:
        for r in rows:
            lod = f"LOD{r['lod']}" if r.get("lod") else ""
            tex = "texture" if r.get("texture") else ""
            print(f"{r['city_code']}\t{r['city']}\t{r['type_en']}\t{r['format']}\t{lod}\t{tex}\t{r['url']}")
        print(f"-- {len(rows)} 件", file=sys.stderr)


def cmd_summary(args):
    cat = load_catalog(args.refresh)
    rows = list(filter_datasets(cat["latest_datasets"], args.pref, args.city, args.city_prefix))
    by_type = collections.defaultdict(set)
    for r in rows:
        by_type[(r["type_en"], r.get("format"))].add(r["city"])
    print(f"{'種別':<6}{'名称':<14}{'形式':<10}{'都市数':>6}")
    for (t, f), cities in sorted(by_type.items(), key=lambda kv: -len(kv[1])):
        print(f"{t:<6}{TYPE_NAMES.get(t, '?'):<14}{f or '':<10}{len(cities):>6}")


def cmd_viewer_json(args):
    """ビューアの区選択メニューに使う 3D Tiles 一覧を作る。"""
    cat = load_catalog(args.refresh)
    rows = filter_datasets(cat["latest_datasets"], args.pref, args.city, args.city_prefix,
                           fmt="3D Tiles")
    cities: dict[str, dict] = {}
    for r in rows:
        c = cities.setdefault(r["city_code"], {"code": r["city_code"], "name": r["city"],
                                               "layers": []})
        c["layers"].append({
            "id": r["id"],
            "type": r["type_en"],
            # 「建築物モデル（千代田区）」→「建築物モデル」のように末尾の都市名を落とす
            "name": r["name"].removesuffix(f"（{r['city']}）"),
            "lod": r.get("lod"),
            "texture": bool(r.get("texture")),
            "size": r.get("file_size"),
            "url": r["url"],
        })
    out = {
        "source": CATALOG_URL,
        "generated_at": time.strftime("%Y-%m-%d"),
        "cities": sorted(cities.values(), key=lambda c: c["code"]),
    }
    p = Path(args.out)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    n = sum(len(c["layers"]) for c in out["cities"])
    print(f"{len(out['cities'])} 都市 / {n} レイヤーを {p} に保存しました", file=sys.stderr)


def fetch_citygml_index(condition: str) -> dict:
    """CityGML ファイル一覧 API。condition は区市町村コード(5桁) か メッシュ(m:XXXXXXXX)。"""
    if condition.isdigit() and len(condition) in (6, 8, 10):
        condition = f"m:{condition}"
    return json.loads(http_get(f"{API_BASE}/citygml/{condition}"))


def cmd_citygml(args):
    data = fetch_citygml_index(args.condition)
    for city in data.get("cities", []):
        groups = [(t, fs) for t, fs in sorted(city["files"].items())
                  if not args.type or t in args.type]
        if not groups:
            continue
        print(f"# {city['cityCode']} {city['cityName']} ({city['year']}, 仕様 {city['spec']})")
        for t, files in groups:
            for f in files:
                mb = f["fileSize"] / 1e6
                print(f"{t}\t{f['code']}\tLOD{f['maxLod']}\t{f['features']}件\t{mb:.1f}MB\t{f['url']}")


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--refresh", action="store_true", help="キャッシュを使わずにカタログを取り直す")
    sub = p.add_subparsers(dest="cmd", required=True)

    def add_filters(sp):
        sp.add_argument("--pref", help="都道府県コード（例: 13 = 東京都）")
        sp.add_argument("--city", help="区市町村コード または 名前（例: 13101 / 千代田区）")
        sp.add_argument("--city-prefix", help="区市町村コードの前方一致（例: 131 = 東京23区）")

    sp = sub.add_parser("list", help="データセットを一覧表示")
    add_filters(sp)
    sp.add_argument("--type", nargs="*", help="種別コード（例: bldg fld）")
    sp.add_argument("--format", help="形式（3D Tiles / MVT など）")
    sp.add_argument("--all-years", action="store_true", help="最新版以外（過去年度）も含める")
    sp.add_argument("--csv", help="CSV ファイルに保存")
    sp.add_argument("--json", action="store_true", help="JSON で出力")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("summary", help="データ種別ごとに使える都市数を集計")
    add_filters(sp)
    sp.set_defaults(func=cmd_summary)

    sp = sub.add_parser("viewer-json", help="ビューア用の 3D Tiles 一覧 JSON を作る")
    add_filters(sp)
    sp.add_argument("--out", default="viewer/data/tokyo-tilesets.json")
    sp.set_defaults(func=cmd_viewer_json)

    sp = sub.add_parser("citygml", help="CityGML ファイルの URL を調べる")
    sp.add_argument("condition", help="区市町村コード(5桁) または 地域メッシュコード(6/8/10桁)")
    sp.add_argument("--type", nargs="*", help="種別コードで絞り込み（例: bldg）")
    sp.set_defaults(func=cmd_citygml)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
