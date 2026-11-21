"""Download the pinned inputs, or verify copies already present."""

import argparse
import json
import shutil
import tempfile
from pathlib import Path
from urllib.request import urlopen

from .prepare import digest


def fetch(config, raw):
    raw.mkdir(parents=True, exist_ok=True)
    urls = {config["boundary_file"]: config["boundary_url"]}
    stamp = config["osm_date"].replace("-", "")[2:]
    for region in config["extracts"]:
        name = f"{region}-{stamp}.osm.pbf"
        urls[name] = f"{config['download_base']}/{region}/{name}"
    for name, url in urls.items():
        target = raw / name
        expected = config["sha256"][name]
        if target.is_file() and digest(target) == expected:
            print(f"Verified {name}")
            continue
        with tempfile.TemporaryDirectory(dir=raw) as tmp:
            staged = Path(tmp) / name
            with urlopen(url, timeout=90) as response, staged.open("wb") as stream:
                shutil.copyfileobj(response, stream)
            if digest(staged) != expected:
                raise ValueError(f"SHA-256 mismatch for {name}")
            staged.replace(target)
        print(f"Downloaded and verified {name}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("region", type=Path)
    parser.add_argument("--raw", type=Path, default=Path("data/raw"))
    args = parser.parse_args()
    fetch(json.loads(args.region.read_text(encoding="utf-8")), args.raw)
