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
