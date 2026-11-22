"""Re-measure saved pins directly against line segments in the source GeoPackages."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import fiona
from pyproj import Transformer
from shapely import from_wkb
from shapely.geometry import Point

from .roads import SCENARIOS, first_scenario


def squared_segment_distance(px, py, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length2 = dx*dx + dy*dy
    along = ((px-a[0])*dx + (py-a[1])*dy) / length2 if length2 else 0
    along = min(1, max(0, along))
    return (px-a[0]-along*dx)**2 + (py-a[1]-along*dy)**2


def check(work, run_file, comparison_file):
    raw = run_file.read_bytes()
    run = json.loads(raw)
    comparison = json.loads(comparison_file.read_bytes())
    if hashlib.sha256(raw).hexdigest() != comparison["discovery_sha256"]:
        raise ValueError("Comparison cites a different discovery file")
    meta = run["inputs"]
    if meta != json.loads((work/"inputs.json").read_bytes()):
        raise ValueError("Prepared inputs differ from discovery")
    land = from_wkb((work/"land.wkb").read_bytes())
    project = Transformer.from_crs(4326, meta["metric_crs"], always_xy=True).transform
    pins = {k: v["xy"] for k, v in run["winners"].items()}
    pins["reference"] = project(*comparison["reference_lonlat"])
    radius = max(w["upper_bound_m"] for w in run["winners"].values()) + 500
    reports = {}
    for label, (px, py) in pins.items():
        if not land.covers(Point(px, py)):
            raise ValueError(f"{label} is outside the land mask")
        rows = {s: [] for s in SCENARIOS}
        seen = set()
        for roadset in meta["roads"]:
            with fiona.open(work/roadset, layer="lines") as roads:
                for feature in roads.filter(bbox=(px-radius, py-radius, px+radius, py+radius)):
                    tags = dict(feature["properties"])
                    way = int(tags["osm_id"])
                    first, reason = first_scenario(tags)
                    if first is None or way in seen:
                        continue
                    seen.add(way)
                    geom = feature["geometry"]
                    parts = [geom.coordinates] if geom.type == "LineString" else geom.coordinates
                    distance = math.sqrt(min(squared_segment_distance(px, py, a, b)
                                             for part in parts for a, b in zip(part, part[1:])))
                    for scenario in SCENARIOS[SCENARIOS.index(first):]:
                        rows[scenario].append((distance, way, reason, tags))
        reports[label] = {}
        for scenario, hits in rows.items():
            dist, way, reason, tags = min(hits, key=lambda x: x[:2])
            if label == "reference":
                expected = comparison["scenarios"][scenario]["distance_m"]
            else:
                expected = run["winners"][label]["scores_m"][scenario]
            if dist >= radius or abs(dist-expected) > 0.001:
                raise ValueError(f"Distance mismatch at {label} under {scenario}")
            reports[label][scenario] = {"distance_m": round(dist, 3), "way_id": way,
                                        "reason": reason, "tags": {k: tags[k] for k in
                                        ("name", "highway", "tracktype", "smoothness", "surface", "access")
                                        if tags.get(k)}}
    for winner in run["winners"].values():
        if not 0 <= winner["upper_bound_m"] - winner["distance_m"] <= meta["tolerance_m"]:
            raise ValueError("Search bound exceeds the configured tolerance")
    return reports


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--winners", type=Path, required=True)
    parser.add_argument("--comparison", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(check(args.work, args.winners, args.comparison), indent=2))
