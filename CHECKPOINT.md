# Resume the Styrian pilot

## 1 · Road policy and input specification

The three nested road rules and the dated region configuration are in Git. From the repository root, run `python -m unittest discover -s tests -v` to check the classifier.

The geographical search must cover the entire BEV region, including land along its borders. Search independently for each scenario. Save the winning pins and numerical error bounds before running the optional comparison with Land Steiermark. A preliminary check on an older extract measured distances at the published point only. It supplies no discovery input.

## 2 · Complete-region search and reproducible inputs

All four inputs are downloaded. The region configuration pins their SHA-256 hashes. Six automated tests pass, covering the road rules, a square with a known answer, a nearest road outside the border, a water hole and an added track that moves the optimum to another island.

The preparation, region-wide search and optional post-run comparison are implemented. The three configurations run independently on the same land mask. The README contains the commands for a fresh checkout. The next output is `results/styria-2026-11-01.json`. Check its distance bounds and cross-scores, then inspect `results/styria-comparison.json`. Publish a winning pin after verifying the discovery output.

## 3 — Independent winners and numerical verification · 22 November 2026

The three statewide searches are complete. A second full run reproduced the discovery file byte-for-byte after normalising Windows line endings. The committed discovery SHA-256 is `13b7c9089bc93c1e86178898d8ab97a1de01f40feb41712ece496304791c1013`. The comparison records that hash. Both writers now use LF on every OS.

The default pin scores 4,811.635 m in A and B. Rule C moves the pin 336 m and gives 4,599.069 m. All three statewide upper bounds are within one metre of the corresponding measured maximum. Six unit tests passed. A separate segment-by-segment calculation on the prepared source ways reproduced all 12 pin/rule scores within 1 mm and checked that every pin lies on the land mask. The README identifies the three decisive tracks. The numerical audit tests the calculation against the mapped lines. It cannot establish field conditions.

```sh
python -m analysis.check_pins --work data/working/styria --winners results/styria-2026-11-01.json --comparison results/styria-comparison.json
```

Resume from the saved JSON for presentation work. The next milestone is a public map with each road rule, its measured radius, the nearest way and an optional benchmark pin. The coordinate lookups returned `stirrup.employed.deserters` for A/B and `dangerous.leafy.polkas` for C.

## 4 — Interactive Styria map · 23 November 2026

The map in `docs/index.html` reads geometry exported from the checkpoint 3 results. The A/B/C selector updates the radius, full nearest way, coordinates, three-word address, and BEV link. Under C the orange line identifies the grade-4 way that reduces the score of the original pin. The optional purple diamond shows the benchmark after discovery. The map draws surrounding qualifying roads for the selected rule. The terrain background comes from basemap.at.

To resume, open the repository in GitHub Desktop and read this file from the bottom. To reopen the map locally, open `docs/index.html`. The README gives the export command if the saved results change. Reuse prepared inputs for geometry audits. Rebuild them only when their provenance changes. For a new region, begin with a new specification and blind discovery run.

The classification and statewide-search tests passed again. The imagery review is recorded in the README. Field driveability of the decisive grade-4 section remains unresolved. The publication milestone is a successful test of the public URL on desktop and a narrow screen.

## 5 — Published and verified · 23 November 2026

[Live Styria map](https://henryb-gis.github.io/Remotest_Point/) · [Saved discovery and audit](https://github.com/HenryB-GIS/Remotest_Point/commit/c6152205d87117238e2bbed65687751df9209d78) · [Published map implementation](https://github.com/HenryB-GIS/Remotest_Point/commit/c27eeb39b0cf700f90bf3ed50d3a87c895ba5ebc)

GitHub Pages serves `main` → `/docs`. The desktop browser showed the default 4.812 km result, its map tiles, distance circle and nearest road. On the narrow layout the content width was 375 px with a 348 px map and no horizontal overflow. Selecting C there produced 4.599 km, the grade-4 way link and a 504 m benchmark separation. A local browser check also exercised A, zoom and fit. The BEV topographic link opened at the default pin. A fresh export from the prepared data reproduced the delivered map data byte-for-byte (SHA-256 `315ac7636b2c44c87f40a2f112ebf2a432472249f411cd5c5d6b162ee91e0935`).

**Resume here.** The Styria pilot is published. Its open evidence question is whether the final section of way 81819003 is ordinarily pickup-passable. Evidence about that way can be assessed against the saved A/B/C results. A changed rule or input snapshot calls for a fresh statewide discovery followed by a new comparison. The README contains the commands to run that sequence in another region.

## 6 — Single-track sensitivity and an independent map check · 23 November 2026

The discovery file is unchanged. The two follow-up statewide searches in `results/styria-one-track.json` cite its SHA-256. Adding only way 81819003 to B gave 4,612.954 m and moved the optimum 11.407 km. Removing only that way from C gave 4,695.877 m at a point 181 m from B. The bound widths were 0.933 m and 0.910 m respectively. A segment-by-segment remeasurement reproduced both nearest road IDs and distances within 1 mm. All six existing automated tests passed.

The GIP road layer in the Austrian administrative map follows this OSM track and uses a shared footpath symbol. The reference tile, relevant style excerpt, offsets and rerun commands are saved in the repository. This check supports reporting the default and broad cases separately. Field driveability remains open.

**Resume here.** [The pilot is live](https://henryb-gis.github.io/Remotest_Point/). Use `results/styria-one-track.json` and `results/styria-track-crosscheck.json` for the latest evidence. Both checks are downstream of the frozen discovery. The initial workflow for another region still starts with its land boundary and surrounding roads.
