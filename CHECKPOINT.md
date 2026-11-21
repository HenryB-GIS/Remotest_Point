# Resume the Styrian pilot

## 1 · Road policy and input specification

The three nested road rules and the dated region configuration are in Git. From the repository root, run `python -m unittest discover -s tests -v` to check the classifier.

The geographical search must cover the entire BEV region, including land along its borders. Search independently for each scenario. Save the winning pins and numerical error bounds before running the optional comparison with Land Steiermark. A preliminary check on an older extract measured distances at the published point only. It supplies no discovery input.

## 2 · Complete-region search and reproducible inputs

All four inputs are downloaded. The region configuration pins their SHA-256 hashes. Six automated tests pass, covering the road rules, a square with a known answer, a nearest road outside the border, a water hole and an added track that moves the optimum to another island.

The preparation, region-wide search and optional post-run comparison are implemented. The three configurations run independently on the same land mask. The README contains the commands for a fresh checkout. The next output is `results/styria-2026-11-01.json`. Check its distance bounds and cross-scores, then inspect `results/styria-comparison.json`. Publish a winning pin after verifying the discovery output.
