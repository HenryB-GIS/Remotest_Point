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
