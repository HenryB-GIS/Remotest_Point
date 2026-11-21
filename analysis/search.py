"""Find the farthest land point for each track rule from a complete regional mask."""

import argparse
import heapq
import json
import math
from pathlib import Path

import fiona
import shapely
from pyproj import Transformer
from shapely.geometry import Point, box, shape
from shapely.ops import nearest_points

from .roads import SCENARIOS, first_scenario


class RoadIndex:
    def __init__(self, geometries, ids):
        if not geometries:
            raise ValueError("The region has no qualifying road lines.")
        self.tree = shapely.STRtree(geometries)
        self.ids = ids

    def distance(self, point):
        idx = self.tree.nearest(point)
        return point.distance(self.tree.geometries[idx])

    def detail(self, point, lonlat):
        indices = self.tree.query_nearest(point)
        idx = min(indices, key=self.ids.__getitem__)
        line = self.tree.geometries[idx]
        foot = nearest_points(point, line)[1]
        return {"distance_m": point.distance(line), "way_id": self.ids[idx],
                "nearest_lonlat": lonlat(foot.x, foot.y)}


def load_roads(work, meta):
    groups = {s: ([], []) for s in SCENARIOS}
    seen = set()
    for path in meta["roads"]:
        with fiona.open(work/path, layer="lines") as src:
            for f in src:
                tags = dict(f["properties"])
                way_id = int(tags["osm_id"])
                if way_id in seen:
                    continue
                first, _ = first_scenario(tags)
                if first is None:
                    continue
                seen.add(way_id)
                groups[first][0].append(shape(f["geometry"]))
                groups[first][1].append(way_id)
    indices = {}
    lines, ids = [], []
    for scenario in SCENARIOS:
        geom, osm_ids = groups.pop(scenario)
        lines.extend(geom)
        ids.extend(osm_ids)
        indices[scenario] = RoadIndex(lines, ids.copy())
    return indices


def maximize(land, roads, tolerance):
    """Bound the maximum over every cell intersecting the input polygon."""
    if land.is_empty or not (math.isfinite(tolerance) and tolerance > 0):
        raise ValueError("A nonempty land polygon and positive tolerance are required.")
    shapely.prepare(land)
    best = land.representative_point()
    lower = roads.distance(best)
    queue = []
    visited = 0
    discarded_bound = lower

    def consider(x0, y0, x1, y1):
        nonlocal best, lower, visited, discarded_bound
        tile = box(x0, y0, x1, y1)
        if not land.intersects(tile):
            return
        visited += 1
        centre = Point((x0+x1)/2, (y0+y1)/2)
        value = roads.distance(centre)
        diagonal = math.hypot(x1-x0, y1-y0)
        upper = value + diagonal/2
        if upper > lower and land.covers(centre):
            if value > lower:
                best, lower = centre, value
        elif upper > lower + tolerance and diagonal <= tolerance:
            # A thin peninsula, hole or boundary cell may contain no grid centre.
            sample = land.intersection(tile).representative_point()
            score = roads.distance(sample)
            if score > lower:
                best, lower = sample, score
        if upper > lower + tolerance:
            heapq.heappush(queue, (-upper, x0, y0, x1, y1))
        else:
            discarded_bound = max(discarded_bound, upper)

    consider(*land.bounds)
    while queue and -queue[0][0] > lower + tolerance:
        _, x0, y0, x1, y1 = heapq.heappop(queue)
        x, y = (x0+x1)/2, (y0+y1)/2
        for left, right in ((x0, x), (x, x1)):
            for bottom, top in ((y0, y), (y, y1)):
                consider(left, bottom, right, top)
    upper = max(lower, discarded_bound, -queue[0][0] if queue else lower)
    return best, upper, visited


def run(work, output):
    meta = json.loads((work/"inputs.json").read_text(encoding="utf-8"))
    land = shapely.from_wkb((work/"land.wkb").read_bytes())
    lonlat = Transformer.from_crs(meta["metric_crs"], 4326, always_xy=True).transform
    print("Indexing the surrounding roads", flush=True)
    indices = load_roads(work, meta)
    winners = {}
    for scenario, roads in indices.items():
        print(f"Searching the complete region under {scenario}", flush=True)
        point, upper, visited = maximize(land, roads, meta["tolerance_m"])
        if upper >= meta["road_buffer_m"]:
            raise ValueError("Increase the road buffer and rebuild the inputs.")
        winners[scenario] = {
            "xy": [point.x, point.y], "lonlat": lonlat(point.x, point.y),
            **roads.detail(point, lonlat), "upper_bound_m": upper,
            "visited_cells": visited, "road_count": len(roads.ids),
            "scores_m": {s: idx.distance(point) for s, idx in indices.items()},
        }
    for fewer, more in zip(SCENARIOS, SCENARIOS[1:]):
        if winners[more]["distance_m"] > winners[fewer]["upper_bound_m"] + 1e-6:
            raise ValueError("Nested networks violate the expected ordering of maxima.")
    report = {"inputs": meta, "winners": winners}
    output.parent.mkdir(parents=True, exist_ok=True)
    temp = output.with_suffix(".tmp")
    temp.write_text(json.dumps(report, indent=2)+"\n", encoding="utf-8")
    temp.replace(output)
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--work", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.work, args.output)["winners"], indent=2))
