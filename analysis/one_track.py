"""Post-discovery statewide sensitivity test for a single C-only OSM way."""

import argparse
import hashlib
import json
import math
from pathlib import Path

from pyproj import Transformer
from shapely import from_wkb

from .search import RoadIndex, load_roads, maximize


def run(work, discovery, way_id):
    raw = discovery.read_bytes()
    original = json.loads(raw)
    meta = json.loads((work / "inputs.json").read_bytes())
    if original["inputs"] != meta:
        raise ValueError("Prepared inputs differ from the saved discovery")
    land = from_wkb((work / "land.wkb").read_bytes())
    project = Transformer.from_crs(meta["metric_crs"], 4326, always_xy=True).transform
    roads = load_roads(work, meta)
    default, broad = roads["B"], roads["C"]
    if way_id in default.ids or way_id not in broad.ids:
        raise ValueError("Select a way counted in C and excluded from B")
    position = broad.ids.index(way_id)
    added = RoadIndex([*default.tree.geometries, broad.tree.geometries[position]],
                      [*default.ids, way_id])
    removed = RoadIndex([*broad.tree.geometries[:position], *broad.tree.geometries[position+1:]],
                        broad.ids[:position]+broad.ids[position+1:])
    cases = {}
    winners = original["winners"]
    for label, network in (("B_plus_way", added), ("C_minus_way", removed)):
        pin, upper, visited = maximize(land, network, meta["tolerance_m"])
        hit = network.detail(pin, project)
        if not (0 <= upper - hit["distance_m"] <= meta["tolerance_m"] and upper < meta["road_buffer_m"]):
            raise ValueError("Invalid statewide search bound")
        if upper < winners["C"]["distance_m"] or hit["distance_m"] > winners["B"]["upper_bound_m"]:
            raise ValueError("Intermediate network violates the nested bounds")
        cases[label] = {"xy": [pin.x, pin.y], "lonlat": project(pin.x, pin.y), **hit,
                        "upper_bound_m": upper, "visited_cells": visited, "road_count": len(network.ids),
                        "pin_separation_m": {s: math.dist((pin.x, pin.y), winners[s]["xy"]) for s in ("B", "C")}}
    return {"discovery_sha256": hashlib.sha256(raw).hexdigest(), "way_id": way_id, "cases": cases}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--discovery", type=Path, required=True)
    parser.add_argument("--way", type=int, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = run(args.work, args.discovery, args.way)
    args.output.parent.mkdir(exist_ok=True, parents=True)
    temp = args.output.with_suffix(".tmp")
    temp.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8", newline="\n")
    temp.replace(args.output)
