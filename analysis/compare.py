"""Compare saved independent winners with an optional lon/lat reference."""

import argparse
import hashlib
import json
from pathlib import Path

from pyproj import Transformer
from shapely.geometry import Point

from .search import load_roads


def compare(work, run_file, lon, lat):
    saved = run_file.read_bytes()
    report = json.loads(saved)
    meta = json.loads((work/"inputs.json").read_text(encoding="utf-8"))
    if meta != report["inputs"]:
        raise ValueError("The prepared inputs differ from those of the saved run.")
    to_xy = Transformer.from_crs(4326, meta["metric_crs"], always_xy=True).transform
    lonlat = Transformer.from_crs(meta["metric_crs"], 4326, always_xy=True).transform
    reference = Point(to_xy(lon, lat))
    data = {}
    for scenario, roads in load_roads(work, meta).items():
        winner = report["winners"][scenario]
        details = roads.detail(reference, lonlat)
        data[scenario] = {**details, "separation_from_winner_m": reference.distance(Point(winner["xy"])),
                          "winner_advantage_m": winner["distance_m"]-details["distance_m"]}
    return {"discovery_sha256": hashlib.sha256(saved).hexdigest(),
            "reference_lonlat": [lon, lat], "scenarios": data}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--winners", type=Path, required=True)
    parser.add_argument("--lon", type=float, required=True)
    parser.add_argument("--lat", type=float, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = compare(args.work, args.winners, args.lon, args.lat)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    print(json.dumps(report, indent=2))
