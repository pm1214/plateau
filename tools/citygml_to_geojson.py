#!/usr/bin/env python3
"""PLATEAU 建築物 CityGML → GeoJSON / CSV 変換ツール（標準ライブラリのみ）

建物の「足元の形（フットプリント）」と主な属性（高さ・階数・用途・構造・建築年・
住所・浸水想定など）を取り出して、GeoJSON と CSV にします。
GeoJSON は Web 地図、CSV は Excel や Unity などで読み込む用途を想定しています。

使い方:
  # 3次メッシュコード（8桁）を指定して、ダウンロードから変換まで一気に行う
  python3 tools/citygml_to_geojson.py --mesh 53394611 -o out/53394611_bldg.geojson --csv out/53394611_bldg.csv

  # 緯度経度から、その地点を含むメッシュを自動で選ぶ（例: 東京駅）
  python3 tools/citygml_to_geojson.py --latlon 35.681236 139.767125 -o out/tokyo_station.geojson

  # ダウンロード済み / 任意 URL の .gml を変換
  python3 tools/citygml_to_geojson.py path/to/53394611_bldg_6697_op.gml -o out.geojson

コードの値（用途 413 など）は、CityGML と同じ配布物に含まれるコードリスト
（codelists/*.xml）を使って日本語に変換します（--raw-codes で変換しない）。
"""
from __future__ import annotations

import argparse
import csv
import json
import shutil
import sys
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plateau_catalog import CACHE_DIR, UA, fetch_citygml_index  # noqa: E402
from meshcode import latlon_to_mesh3  # noqa: E402

NS = {
    "core": "http://www.opengis.net/citygml/2.0",
    "bldg": "http://www.opengis.net/citygml/building/2.0",
    "gml": "http://www.opengis.net/gml",
    "gen": "http://www.opengis.net/citygml/generics/2.0",
    "xAL": "urn:oasis:names:tc:ciq:xsdschema:xAL:2.0",
}
GML_ID = f"{{{NS['gml']}}}id"


def q(tag: str) -> str:
    """'bldg:usage' → '{http://...}usage'"""
    prefix, local = tag.split(":")
    return f"{{{NS[prefix]}}}{local}"


# --------------------------------------------------------------------------- 入力


def download(url: str) -> Path:
    CACHE_DIR.mkdir(exist_ok=True)
    name = Path(urllib.parse.urlparse(url).path).name
    dest = CACHE_DIR / "citygml" / name
    if dest.exists():
        return dest
    dest.parent.mkdir(parents=True, exist_ok=True)
    print(f"ダウンロード中: {url}", file=sys.stderr)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    tmp = dest.with_suffix(".part")
    with urllib.request.urlopen(req, timeout=600) as res, tmp.open("wb") as f:
        shutil.copyfileobj(res, f, length=1 << 20)
    tmp.rename(dest)
    return dest


def find_bldg_url(mesh: str) -> str:
    data = fetch_citygml_index(mesh)
    for city in data.get("cities", []):
        for f in city["files"].get("bldg", []):
            if f["code"] == mesh:
                print(f"{city['cityName']} ({city['year']}) の {f['features']} 棟を変換します",
                      file=sys.stderr)
                return f["url"]
    sys.exit(f"メッシュ {mesh} の建築物 CityGML が見つかりませんでした")


# ---------------------------------------------------------------- コードリスト


class CodeLists:
    """codeSpace（../../codelists/Building_usage.xml など）をたどって日本語名を返す。"""

    def __init__(self, gml_location: str, enabled: bool = True):
        self.base = gml_location  # URL またはローカルパス
        self.enabled = enabled
        self.cache: dict[str, dict[str, str]] = {}

    def _load(self, code_space: str) -> dict[str, str]:
        if code_space in self.cache:
            return self.cache[code_space]
        table: dict[str, str] = {}
        try:
            if self.base.startswith("http"):
                url = urllib.parse.urljoin(self.base, code_space)
                local = CACHE_DIR / "codelists" / urllib.parse.quote(url, safe="")
                if not local.exists():
                    local.parent.mkdir(parents=True, exist_ok=True)
                    req = urllib.request.Request(url, headers={"User-Agent": UA})
                    with urllib.request.urlopen(req, timeout=60) as res:
                        local.write_bytes(res.read())
                path = local
            else:
                path = (Path(self.base).parent / code_space).resolve()
            root = ET.parse(path).getroot()
            for d in root.iter(q("gml:Definition")):
                name, desc = d.findtext(q("gml:name")), d.findtext(q("gml:description"))
                if name is not None:
                    table[name.strip()] = (desc or "").strip()
        except Exception as e:  # コードリストが無くても変換は続ける
            print(f"  (コードリスト {code_space} を読めませんでした: {e})", file=sys.stderr)
        self.cache[code_space] = table
        return table

    def decode(self, el: ET.Element | None) -> str | None:
        if el is None or el.text is None:
            return None
        code = el.text.strip()
        cs = el.get("codeSpace")
        if not self.enabled or not cs:
            return code
        return self._load(cs).get(code, code)


# ------------------------------------------------------------------- 形状


def parse_poslist(text: str) -> list[list[float]]:
    """EPSG:6697 の posList（緯度 経度 高さ）→ GeoJSON 座標（経度, 緯度）"""
    v = [float(t) for t in text.split()]
    return [[round(v[i + 1], 8), round(v[i], 8)] for i in range(0, len(v) - 2, 3)]


def polygon_coords(poly: ET.Element) -> list | None:
    rings = []
    for tag in ("gml:exterior", "gml:interior"):
        for ring in poly.findall(q(tag)):
            pl = ring.find(f".//{q('gml:posList')}")
            if pl is not None and pl.text:
                rings.append(parse_poslist(pl.text))
    return rings or None


def footprint(b: ET.Element) -> dict | None:
    # 1) LOD0 の屋根形状 / 足元形状（平面の多角形）
    for tag in ("bldg:lod0RoofEdge", "bldg:lod0FootPrint"):
        el = b.find(q(tag))
        if el is not None:
            polys = [c for p in el.iter(q("gml:Polygon")) if (c := polygon_coords(p))]
            if polys:
                return ({"type": "Polygon", "coordinates": polys[0]} if len(polys) == 1
                        else {"type": "MultiPolygon", "coordinates": polys})
    # 2) LOD1 立体の底面（高さが最小の面）
    solid = b.find(q("bldg:lod1Solid"))
    if solid is not None:
        best, best_z = None, float("inf")
        for p in solid.iter(q("gml:Polygon")):
            pl = p.find(f".//{q('gml:posList')}")
            if pl is None or not pl.text:
                continue
            z = [float(t) for t in pl.text.split()[2::3]]
            if max(z) - min(z) < 0.01 and z[0] < best_z:
                best, best_z = p, z[0]
        if best is not None:
            return {"type": "Polygon", "coordinates": polygon_coords(best)}
    return None


def centroid(geom: dict) -> tuple[float, float]:
    ring = geom["coordinates"][0] if geom["type"] == "Polygon" else geom["coordinates"][0][0]
    pts = ring[:-1] if len(ring) > 1 and ring[0] == ring[-1] else ring
    return (sum(p[0] for p in pts) / len(pts), sum(p[1] for p in pts) / len(pts))


# ------------------------------------------------------------------- 属性


def to_num(s: str | None):
    if s is None:
        return None
    try:
        f = float(s)
    except ValueError:
        return s
    # PLATEAU では不明値に -9999 / 9999（階数など）を使うことがある
    if abs(f) >= 9999:
        return None
    return int(f) if f.is_integer() and "." not in s else f


def first(b: ET.Element, local: str) -> ET.Element | None:
    """名前空間（uro のバージョン違い）を問わず、ローカル名で最初の要素を探す。"""
    for el in b.iter():
        if el.tag.endswith("}" + local):
            return el
    return None


def risk_list(b: ET.Element, local: str, codes: CodeLists) -> list[dict]:
    out = []
    for el in b.iter():
        if not el.tag.endswith("}" + local):
            continue
        item = {}
        for c in el:
            key = c.tag.split("}")[1]
            item[key] = to_num(c.text.strip()) if key == "depth" and c.text else codes.decode(c)
        out.append(item)
    return out


def attributes(b: ET.Element, codes: CodeLists, with_generic: bool) -> dict:
    a: dict = {"gml_id": b.get(GML_ID)}
    bid = first(b, "buildingID")
    a["building_id"] = bid.text.strip() if bid is not None and bid.text else None
    a["name"] = b.findtext(q("gml:name"))
    a["class"] = codes.decode(b.find(q("bldg:class")))
    a["usage"] = codes.decode(b.find(q("bldg:usage")))
    a["detailed_usage"] = codes.decode(first(b, "detailedUsage"))
    a["measured_height"] = to_num(b.findtext(q("bldg:measuredHeight")))
    a["storeys_above"] = to_num(b.findtext(q("bldg:storeysAboveGround")))
    a["storeys_below"] = to_num(b.findtext(q("bldg:storeysBelowGround")))
    a["year_of_construction"] = to_num(b.findtext(q("bldg:yearOfConstruction")))
    a["structure"] = codes.decode(first(b, "buildingStructureType"))
    a["fireproof"] = codes.decode(first(b, "fireproofStructureType"))
    a["total_floor_area"] = to_num((first(b, "totalFloorArea") or ET.Element("x")).text)
    a["address"] = next((el.text for el in b.iter(q("xAL:LocalityName")) if el.text), None)
    a["land_use"] = codes.decode(first(b, "landUseType"))
    a["districts_zones"] = codes.decode(first(b, "districtsAndZonesType"))

    # 災害リスク（建物ごとの浸水深さなど）
    flood = risk_list(b, "RiverFloodingRiskAttribute", codes)
    tsunami = risk_list(b, "TsunamiRiskAttribute", codes)
    hightide = risk_list(b, "HighTideRiskAttribute", codes)
    inland = risk_list(b, "InlandFloodingRiskAttribute", codes)
    landslide = risk_list(b, "LandSlideRiskAttribute", codes)

    def max_depth(lst):
        d = [x["depth"] for x in lst if isinstance(x.get("depth"), (int, float))]
        return max(d) if d else None

    a["flood_depth_max"] = max_depth(flood)
    a["tsunami_depth_max"] = max_depth(tsunami)
    a["hightide_depth_max"] = max_depth(hightide)
    a["inland_flood_depth_max"] = max_depth(inland)
    a["landslide_risk"] = bool(landslide)
    a["flood_risks"] = flood or None  # 河川ごとの詳細（GeoJSON のみ）

    lod = first(b, "lodType")
    a["lod_type"] = lod.text.strip() if lod is not None and lod.text else None
    a["has_lod2"] = b.find(q("bldg:lod2Solid")) is not None
    a["has_lod3"] = b.find(q("bldg:lod3Solid")) is not None or b.find(q("bldg:lod3MultiSurface")) is not None

    if with_generic:
        for g in b.findall(q("gen:stringAttribute")) + b.findall(q("gen:measureAttribute")):
            a[f"gen:{g.get('name')}"] = (g.findtext(q("gen:value")) or "").strip() or None
    return a


# ------------------------------------------------------------------- 本体


def iter_buildings(path: Path):
    ctx = ET.iterparse(path, events=("start", "end"))
    _, root = next(ctx)
    member = q("core:cityObjectMember")
    for ev, el in ctx:
        if ev == "end" and el.tag == member:
            for b in el.findall(q("bldg:Building")):
                yield b
            root.clear()  # メモリ節約（大きなファイルでも一定量で処理）


def convert(path: Path, codes: CodeLists, with_generic: bool, bbox=None):
    for b in iter_buildings(path):
        geom = footprint(b)
        if geom is None:
            continue
        lon, lat = centroid(geom)
        if bbox and not (bbox[0] <= lon <= bbox[2] and bbox[1] <= lat <= bbox[3]):
            continue
        props = attributes(b, codes, with_generic)
        props["lon"], props["lat"] = round(lon, 7), round(lat, 7)
        yield {"type": "Feature", "geometry": geom, "properties": props}


CSV_SKIP = {"flood_risks"}


def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    src = p.add_mutually_exclusive_group(required=True)
    src.add_argument("input", nargs="?", help=".gml のパス または URL")
    src.add_argument("--mesh", help="3次メッシュコード（8桁）")
    src.add_argument("--latlon", nargs=2, type=float, metavar=("LAT", "LON"),
                     help="この地点を含む3次メッシュを変換")
    p.add_argument("-o", "--out", help="出力 GeoJSON（省略時は標準出力）")
    p.add_argument("--csv", help="重心座標つきの CSV も出力")
    p.add_argument("--bbox", nargs=4, type=float, metavar=("W", "S", "E", "N"),
                   help="経度緯度の範囲で絞り込み")
    p.add_argument("--generic", action="store_true", help="汎用属性（gen:*）も含める")
    p.add_argument("--raw-codes", action="store_true", help="コード値を日本語に変換しない")
    args = p.parse_args(argv)

    if args.latlon:
        args.mesh = latlon_to_mesh3(*args.latlon)
        print(f"メッシュコード: {args.mesh}", file=sys.stderr)
    location = find_bldg_url(args.mesh) if args.mesh else args.input
    path = download(location) if location.startswith("http") else Path(location)
    codes = CodeLists(location, enabled=not args.raw_codes)

    features = list(convert(path, codes, args.generic, args.bbox))
    fc = {"type": "FeatureCollection",
          "name": path.stem,
          "attribution": "出典: 国土交通省 Project PLATEAU",
          "features": features}

    if args.out:
        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json.dumps(fc, ensure_ascii=False), encoding="utf-8")
        print(f"{len(features)} 棟を {out} に保存しました", file=sys.stderr)
    else:
        json.dump(fc, sys.stdout, ensure_ascii=False)

    if args.csv:
        cols: list[str] = []
        for f in features:
            for k in f["properties"]:
                if k not in cols and k not in CSV_SKIP:
                    cols.append(k)
        out = Path(args.csv)
        out.parent.mkdir(parents=True, exist_ok=True)
        with out.open("w", newline="", encoding="utf-8-sig") as fh:
            w = csv.DictWriter(fh, fieldnames=cols, extrasaction="ignore")
            w.writeheader()
            for f in features:
                w.writerow(f["properties"])
        print(f"CSV を {out} に保存しました", file=sys.stderr)


if __name__ == "__main__":
    main()
