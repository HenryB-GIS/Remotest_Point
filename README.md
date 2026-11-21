# Remotest Point

This shows a region's point that is farthest from the road network.

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

See [CHECKPOINT.md](CHECKPOINT.md) for the latest verified result and the next reproducible step.
