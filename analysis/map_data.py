"""Export the measured map geometry for a static, dependency-free web viewer."""

import argparse
import hashlib
import json
import math
from pathlib import Path

import fiona
from pyproj import Transformer
from shapely.geometry import box, shape

from .check_pins import check
from .roads import SCENARIOS, first_scenario


WORLD = 256 * 2**13


def pixel(lon, lat):
    return ((lon + 180) * WORLD / 360,
            (1 - math.asinh(math.tan(math.radians(lat))) / math.pi) * WORLD / 2)


def lines(geom):
    if geom.geom_type == "LineString" and not geom.is_empty:
        yield geom
    elif hasattr(geom, "geoms"):
        for part in geom.geoms:
            yield from lines(part)


def export(work, discovery, comparison, output):
    raw = discovery.read_bytes()
    run = json.loads(raw)
    ref = json.loads(comparison.read_bytes())
    if ref["discovery_sha256"] != hashlib.sha256(raw).hexdigest():
        raise ValueError("Comparison and discovery differ")
    meta = run["inputs"]
    if meta != json.loads((work / "inputs.json").read_bytes()):
        raise ValueError("Prepared inputs differ from discovery")
    winners = run["winners"]
    centre = winners["B"]
    to_lonlat = Transformer.from_crs(meta["metric_crs"], 4326, always_xy=True).transform
    origin = pixel(*centre["lonlat"])

    def point(lonlat):
        x, y = pixel(*lonlat)
        return [round(x - origin[0], 2), round(y - origin[1], 2)]

    def path(line):
        coords = [point(to_lonlat(*p[:2])) for p in line.coords]
        return "M" + " ".join(f"{x:g},{y:g}" for x, y in coords)

    pins = {}
    for rule, winner in winners.items():
        x, y = winner["xy"]
        radius = winner["distance_m"]
        ring = []
        for i in range(145):
            angle = i * 2 * math.pi / 144
            ring.append(point(to_lonlat(x + radius * math.cos(angle), y + radius * math.sin(angle))))
        pins[rule] = {k: winner[k] for k in ("lonlat", "way_id", "distance_m", "upper_bound_m")}
        pins[rule].update(pin=point(winner["lonlat"]), foot=point(winner["nearest_lonlat"]),
                          ring=ring, reference=ref["scenarios"][rule])

    x, y = centre["xy"]
    extent = 2.1 * max(w["distance_m"] for w in winners.values())
    window = box(x - extent, y - extent, x + extent, y + extent)
    context = {s: [] for s in SCENARIOS}
    important = {w["way_id"] for w in winners.values()}
    important.update(v["way_id"] for v in ref["scenarios"].values())
    rough_at_default = check(work, discovery, comparison)["B"]["C"]
    important.add(rough_at_default["way_id"])
    highlighted = {}
    seen = set()
    for filename in meta["roads"]:
        with fiona.open(work / filename, layer="lines") as roads:
            for feature in roads.filter(bbox=window.bounds):
                tags = feature["properties"]
                rule, _ = first_scenario(tags)
                way = int(tags["osm_id"])
                if rule is None or way in seen:
                    continue
                seen.add(way)
                geom = shape(feature["geometry"])
                if way in important:
                    highlighted[way] = {"path": "".join(map(path, lines(geom))),
                                        "grade": tags["tracktype"], "surface": tags["surface"]}
                simple = geom.intersection(window).simplify(18)
                context[rule].extend(map(path, lines(simple)))
    if highlighted.keys() != important:
        raise ValueError("Missing nearest road geometry")
    data = {"origin": origin, "reference": point(ref["reference_lonlat"]), "winners": pins,
            "roads": highlighted, "context": {s: "".join(v) for s, v in context.items()},
            "rough_at_default": rough_at_default,
            "discovery_sha256": ref["discovery_sha256"]}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("const atlas = " + json.dumps(data, separators=(",", ":"), allow_nan=False)
                      + ";\n", encoding="utf-8", newline="\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    for field in ("work", "discovery", "comparison", "output"):
        parser.add_argument("--" + field, type=Path, required=True)
    args = parser.parse_args()
    export(args.work, args.discovery, args.comparison, args.output)
