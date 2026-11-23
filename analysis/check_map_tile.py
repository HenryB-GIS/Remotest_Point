"""Compare one OSM way with the GIP road layer in a single basemap.at vector tile."""

import argparse
import gzip
import hashlib
import json
import math
from pathlib import Path

import fiona
from pyproj import CRS, Transformer
from shapely.geometry import box, shape
from shapely.ops import transform, unary_union


def compare(tile, style, road_file, way, z, x, y):
    with fiona.open(road_file, layer="lines") as src:
        feature = next(src.filter(where=f"osm_id = '{way}'"), None)
        if feature is None:
            raise ValueError(f"Way {way} is missing from {road_file.name}")
        road = shape(feature["geometry"])
        crs = CRS(src.crs)
    if not crs.is_projected or crs.axis_info[0].unit_conversion_factor != 1:
        raise ValueError("The road layer must use a projected metric CRS")
    if road.geom_type != "LineString":
        raise ValueError("Select one continuous OSM way")

    mercator = Transformer.from_crs(crs, 3857, always_xy=True).transform
    metric = Transformer.from_crs(3857, crs, always_xy=True).transform
    edge = math.pi * 6378137
    size = 2 * edge / 2**z
    bounds = box(x*size-edge, edge-(y+1)*size, (x+1)*size-edge, edge-y*size)
    if not bounds.covers(transform(mercator, road.buffer(20))):
        raise ValueError("The comparison needs adjacent tiles")

    layer = "GIP_L_GIP_144"
    groups = {}
    with fiona.open(tile, layer=layer, allow_unsupported_drivers=True,
                    X=str(x), Y=str(y), Z=str(z)) as src:
        for feature in src:
            symbol = feature["properties"]["_symbol"]
            groups.setdefault(symbol, []).append(transform(metric, shape(feature["geometry"])))
    geometries = {k: unary_union(v) for k, v in groups.items()}
    if not geometries:
        raise ValueError("No reference road geometry in this tile")
    style_json = json.loads(style.read_bytes())
    samples = [road.interpolate(i) for i in range(0, math.ceil(road.length), 5)]
    samples.append(road.interpolate(1, normalized=True))
    gaps = []
    counts = {}
    for point in samples:
        gap, symbol = min((point.distance(geom), symbol) for symbol, geom in geometries.items())
        gaps.append(gap)
        counts[symbol] = counts.get(symbol, 0) + 1
    classes = {}
    for symbol in counts:
        classes[symbol] = [entry["id"] for entry in style_json["layers"]
                           if entry.get("source-layer") == layer
                           and entry.get("filter") == ["==", "_symbol", symbol]
                           and entry.get("minzoom", 0) <= z < entry.get("maxzoom", 99)]
    data = tile.read_bytes()
    if data.startswith(b"\x1f\x8b"):
        data = gzip.decompress(data)
    return {"way_id": way, "metric_crs": crs.to_string(), "length_m": road.length,
            "tile_url": f"https://mapsneu.wien.gv.at/basemapv/bmapv/3857/tile/{z}/{y}/{x}.pbf",
            "tile_sha256_decoded": hashlib.sha256(data).hexdigest(),
            "style_url": "https://mapsneu.wien.gv.at/basemapvectorneu/root.json",
            "layer": layer, "symbol_labels": classes, "sample_counts_by_nearest_symbol": counts,
            "sample_step_m": 5, "samples": len(samples),
            "samples_within_10_m": sum(d <= 10 for d in gaps),
            "samples_within_20_m": sum(d <= 20 for d in gaps),
            "max_sample_gap_m": max(gaps), "osm_end_gap_m": gaps[-1]}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("tile", "style", "road-file", "output"):
        parser.add_argument("--"+field, type=Path, required=True)
    for field in ("way", "z", "x", "y"):
        parser.add_argument("--"+field, type=int, required=True)
    args = parser.parse_args()
    report = compare(args.tile, args.style, args.road_file, args.way, args.z, args.x, args.y)
    args.output.parent.mkdir(exist_ok=True, parents=True)
    temp = args.output.with_suffix(".tmp")
    temp.write_text(json.dumps(report, indent=2, ensure_ascii=False)+"\n", encoding="utf-8", newline="\n")
    temp.replace(args.output)
