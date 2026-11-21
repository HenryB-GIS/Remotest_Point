"""Prepare one regional boundary, its open water and surrounding OSM roads."""

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile

import fiona
from pyproj import CRS, Transformer
import shapely
from shapely.geometry import shape
from shapely.ops import transform

from .roads import SURFACE_ROADS


def digest(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def read_region(config, raw):
    path = (raw / config["boundary_file"]).resolve()
    uri = f"zip://{path}" if path.suffix.lower() == ".zip" else str(path)
    with fiona.open(uri, layer=config.get("boundary_layer")) as src:
        project = Transformer.from_crs(src.crs, config["metric_crs"], always_xy=True)
        parts = [shapely.make_valid(shape(f["geometry"])) for f in src]
    return transform(project.transform, shapely.union_all(parts))


def extract(ogr, pbf, layer, where, output, bounds, crs):
    env = os.environ.copy()
    prefix = Path(shutil.which(ogr) or ogr).resolve().parent.parent
    proj = prefix / "share" / "proj"
    if (proj / "proj.db").is_file():
        env["PROJ_DATA"] = str(proj)
    config = Path(__file__).with_name("osmconf.ini")
    # Each invocation reads a geometry layer, never a spatially filtered node layer.
    subprocess.run([ogr, "-f", "GPKG", "-oo", f"CONFIG_FILE={config}",
                    "-spat", *map(str, bounds), "-t_srs", crs, "-where", where,
                    "-nln", layer, str(output), str(pbf), layer], check=True, env=env)


def prepare(config, raw, work, ogr):
    work.mkdir(parents=True, exist_ok=True)
    crs = CRS.from_user_input(config["metric_crs"])
    if not crs.is_projected or any(axis.unit_conversion_factor != 1 for axis in crs.axis_info[:2]):
        raise ValueError("Select a local projected CRS with metre units.")
    boundary = read_region(config, raw)
    buffer_m = config["road_buffer_m"]
    xmin, ymin, xmax, ymax = boundary.bounds
    lonlat = Transformer.from_crs(crs, 4326, always_xy=True)
    bounds = lonlat.transform_bounds(xmin-buffer_m-100, ymin-buffer_m-100,
                                     xmax+buffer_m+100, ymax+buffer_m+100, densify_pts=101)
    classes = ",".join(f"'{c}'" for c in sorted(SURFACE_ROADS | {"track"}))
    water_sql = "natural = 'water' OR waterway = 'riverbank' OR landuse IN ('reservoir', 'basin')"
    stamp = config["osm_date"].replace("-", "")[2:]
    source_files = [raw / f"{country}-{stamp}.osm.pbf" for country in config["extracts"]]
    hashes = {p.name: digest(p) for p in [raw / config["boundary_file"], *source_files]}
    if "sha256" in config and hashes != config["sha256"]:
        raise ValueError("Source files differ from the pinned SHA-256 values.")
    with tempfile.TemporaryDirectory(dir=work) as temporary:
        tmp = Path(temporary)
        water = []
        roads = []
        shapely.prepare(boundary)
        for country, pbf in zip(config["extracts"], source_files):
            roads_file = f"{country}-roads.gpkg"
            print(f"Extracting {country} roads and water", flush=True)
            extract(ogr, pbf, "lines", f"highway IN ({classes})", tmp/roads_file, bounds, crs.to_string())
            roads.append(roads_file)
            water_file = tmp / f"{country}-water.gpkg"
            extract(ogr, pbf, "multipolygons", water_sql, water_file, bounds, crs.to_string())
            with fiona.open(water_file) as src:
                for feature in src:
                    tags = feature["properties"]
                    if tags.get("intermittent") == "yes":
                        continue
                    if tags.get("landuse") == "basin" and tags.get("natural") != "water":
                        continue
                    polygon = shapely.make_valid(shape(feature["geometry"]))
                    if boundary.intersects(polygon):
                        water.append(polygon)
        print(f"Building the land mask from {len(water)} water features", flush=True)
        land = boundary.difference(shapely.union_all(water))
        if land.is_empty or not land.is_valid:
            raise ValueError("Failed to build a valid land mask.")
        (tmp/"land.wkb").write_bytes(land.wkb)
        meta = {"region": config["name"], "metric_crs": crs.to_string(), "roads": roads,
                "road_buffer_m": buffer_m, "tolerance_m": config["tolerance_m"],
                "source_sha256": hashes, "road_bbox_lonlat": bounds,
                "boundary_area_km2": boundary.area/1e6, "land_area_km2": land.area/1e6,
                "water_features_including_overlap": len(water)}
        (tmp/"inputs.json").write_text(json.dumps(meta, indent=2)+"\n", encoding="utf-8")
        for filename in [*roads, "land.wkb", "inputs.json"]:
            (tmp/filename).replace(work/filename)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("region", type=Path)
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    parser.add_argument("--work", type=Path, default=Path("data/working/styria"))
    parser.add_argument("--ogr2ogr", default="ogr2ogr")
    args = parser.parse_args()
    prepare(json.loads(args.region.read_text(encoding="utf-8")), args.raw, args.work, args.ogr2ogr)
