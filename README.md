# Remotest Point

[Open the interactive Styria map](https://henryb-gis.github.io/Remotest_Point/) to compare three definitions of a forestry road and see the route-independent straight-line measurement for each winner.

The independent statewide search places the default Styrian pin at **47.674647° N, 14.011258° E** in the Totes Gebirge. The nearest qualifying road is **4.812 km** away. Distances use the 1 November 2026 road snapshot.

| Forestry-track rule | Winning coordinates (latitude, longitude) | Nearest road | Statewide upper bound |
|---|---|---:|---:|
| A · Require positive track evidence | 47.674647, 14.011258 | 4,811.635 m | 4,812.616 m |
| B · Also count ungraded tracks (default) | 47.674647, 14.011258 | 4,811.635 m | 4,812.616 m |
| C · Also count grades 4–5 | 47.675188, 14.006859 | 4,599.069 m | 4,600.003 m |

Ungraded tracks leave the winner unchanged. Counting rough tracks brings a grade-4 ground track within 4,278 m of the original pin. The new winner lies 336 m west-northwest, where a grade-2 gravel track is nearest. The state's maximum falls by 213 m. Under the default rule the nearest way is a grade-3 gravel track. [Default nearest way](https://www.openstreetmap.org/way/81819022) · [Decisive grade-4 way](https://www.openstreetmap.org/way/81819003) · [Nearest way under C](https://www.openstreetmap.org/way/435056110)

After discovery, we measured the published Land Steiermark point against the same roads. It lies 214 m from our default pin and scores 4,638.629 m, or 173 m less. Possible differences in road definitions, dates and geometry remain unresolved. [Saved discovery](results/styria-2026-11-01.json) · [Benchmark comparison](results/styria-comparison.json)

**Where on Styrian land is the straight-line distance to a mapped, driveable surface road greatest?** The search covers the entire region. Roads across administrative borders count. Distances are measured to road centrelines in metres.

## What counts as a road?

A forestry pickup in ordinary snow-free conditions is our reference vehicle. A private gravel road behind a forestry gate counts. Ownership, access signs and the right to drive there are separate from physical driveability.

| OSM feature | Treatment |
|---|---|
| Ordinary surface roads, links, service roads, driveways, bridges | Count in A, B and C |
| Track rated `excellent` through `very_bad` for smoothness | Count in A, B and C |
| Track with no usable smoothness value and grade 1–3 | Count in A, B and C |
| Track with no usable smoothness or grade | Count in B and C |
| Track with no usable smoothness and grade 4–5 | Count in C |
| `horrible`, `very_horrible` or `impassable` smoothness | Exclude |
| Footpaths, cycleways, steps, bridleways, tunnel interiors, abandoned roads, construction-only roads and road-area polygons | Exclude |

**B is the default.** Each comparison changes one decision about tracks. OSM grade describes surface firmness. The pickup cutoff is a modelling choice and should be validated against decisive tracks. [OSM track](https://wiki.openstreetmap.org/wiki/Tag:highway%3Dtrack) · [Smoothness](https://wiki.openstreetmap.org/wiki/Key:smoothness) · [Track grade](https://wiki.openstreetmap.org/wiki/Key:tracktype)

## Independent search

The inputs are a region polygon, mapped open water, surrounding road extracts and a local metric CRS. The discovery stage searches the region under all three rules and writes its winners. A separate comparison can then score an independently published point. A region can be analysed without a published reference point.

The Styrian input specification selects the BEV boundary dated 1 April 2026 and Geofabrik extracts for Austria, Slovenia and Hungary dated 1 November 2026. A 20 km buffer includes surrounding roads. The project keeps large source files outside Git. [Region specification](regions/styria.json) · [BEV boundary](https://data.bev.gv.at/geonetwork/srv/api/records/2d7b8f24-deb9-42eb-82f2-c7c1c7ff7075) · [Geofabrik](https://download.geofabrik.de/europe.html)

Road and water data © OpenStreetMap contributors, ODbL 1.0. Austrian administrative boundaries © BEV. [OSM attribution and licence](https://www.openstreetmap.org/copyright)

## Reproduce the statewide search

Use Python 3.11 or later and GDAL 3.10 or later with the OSM driver. On Windows, run from a QGIS/OSGeo4W shell or pass the full path to `ogr2ogr.exe` with `--ogr2ogr` on the preparation command.

```sh
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python -m analysis.fetch regions/styria.json --raw data/raw
python -m analysis.prepare regions/styria.json --raw data/raw --work data/working/styria
python -m analysis.search --work data/working/styria --output results/styria-2026-11-01.json
```

The solver starts with the bounding rectangle of all land. It recursively subdivides every cell that could beat the best measured land point. If a cell centre is distance *d* from its nearest road, no point in that cell can exceed *d* plus half its diagonal. The saved upper and lower bounds apply to the **distance**. Several locations can achieve almost the same distance. The default stopping tolerance is 1 metre in the selected projected CRS. Mapping accuracy and projection scale have separate effects.

The land mask subtracts mapped permanent water polygons, including lakes, reservoirs and river areas. The road index retains original line geometry and removes duplicate OSM way IDs across country extracts. The input downloads must cover the entire road buffer. The program also checks that the statewide upper bound falls within that buffer.

For another region, supply its polygon, all surrounding road extracts and a suitable local metric CRS. The boundary layer must contain only the target region or its subdivisions. Check the source coverage and projection scale for each new region. Regions spanning a projection discontinuity need an adapted projection and extraction window.

## Optional benchmark comparison

After saving the winners, run the following command. The comparison records the SHA-256 of the discovery file, the road distance at the reference point, the difference in score and the separation between pins. The search module takes no reference coordinates. [Land Steiermark's published coordinates](https://www.landesentwicklung.steiermark.at/cms/dokumente/12702993_141979497/c3213ffa/Miteinander%20im%20Dialog%202024_MayerWeissenbeck.pdf)

```sh
python -m analysis.compare --work data/working/styria --winners results/styria-2026-11-01.json --lon 14.0135033333333 --lat 47.675835 --output results/styria-comparison.json
```

## Explore or rebuild the map

Open `docs/index.html` in a browser to switch road rules or overlay the published point. The page carries the saved road geometry, pin and measured circle locally. The geographic background loads from basemap.at. GitHub Pages serves the same files from the `/docs` folder of `main`.

```sh
python -m analysis.map_data --work data/working/styria --discovery results/styria-2026-11-01.json --comparison results/styria-comparison.json --output docs/styria-data.js
```

The export verifies discovery provenance and remeasures the saved pins. It constructs the circle in the calculation CRS before converting it for display. It preserves all vertices of the highlighted ways and simplifies surrounding roads for screen display. The geometry is derived from OpenStreetMap, available under ODbL 1.0. Terrain map credit goes to basemap.at. [OpenStreetMap licence](https://www.openstreetmap.org/copyright) · [basemap.at](https://basemap.at/)

## What the checks establish

AI assisted with the implementation, documentation and map. Checks against known-answer geometries, the independent segment calculation, a full replay and the later benchmark comparison are documented in [CHECKPOINT.md](CHECKPOINT.md). A 1 m bound describes the numerical search. The source maps, the pickup interpretation and real-world road conditions each have their own uncertainty.

An inspection of Austrian orthophotos at the three critical footpoints showed vegetation and shadow at the gravel tracks, and broken, partly open ground at the grade-4 way. The photographs did not establish that a pickup can drive that last section. The three-rule sensitivity result therefore remains the appropriate way to report it. [Grade-3 image](https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857/17/45737/70660.jpeg) · [Grade-4 image](https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857/17/45736/70657.jpeg) · [Grade-2 image](https://mapsneu.wien.gv.at/basemap/bmaporthofoto30cm/normal/google3857/17/45753/70619.jpeg)
