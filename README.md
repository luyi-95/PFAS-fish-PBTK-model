# PFAS-fish-PBTK-TD-model

Code repository for PFAS physiologically based toxicokinetic (PBTK) and toxicodynamic (TD) modeling workflows.

This repository contains the R scripts currently used for:

- PFAS PBTK model implementation
- KabsK-related parameter estimation
- TD model fitting and visualization

The repository is organized for manuscript archiving and versioned release. When preparing the paper, cite a tagged GitHub release and, ideally, the Zenodo DOI minted from that release.

## Repository Structure

- `R/TDmodel.R`: TD model fitting workflow
- `R/PBTK_KabsK.R`: PBTK model and KabsK estimation workflow
- `R/New_TP-TKmix.R`: multi-chemical PBTK workflow
- `scripts/run_td_model.R`: convenience launcher for `R/TDmodel.R`
- `scripts/run_pbtk_kabsk.R`: convenience launcher for `R/PBTK_KabsK.R`
- `scripts/run_pbtk_mix.R`: convenience launcher for `R/New_TP-TKmix.R`
- `data/README.md`: notes on data availability
- `results/README.md`: notes on generated outputs
- `requirements-R.txt`: R package dependencies

## Requirements

This project uses R and the following packages:

- `deSolve`
- `FME`
- `DEoptim`
- `ggplot2`
- `gridExtra`
- `minpack.lm`
- `openxlsx`

Install missing packages in R with:

```r
install.packages(c(
  "deSolve",
  "FME",
  "DEoptim",
  "ggplot2",
  "gridExtra",
  "minpack.lm",
  "openxlsx"
))
```

## How To Run

From the repository root:

```r
source("scripts/run_td_model.R")
source("scripts/run_pbtk_kabsk.R")
source("scripts/run_pbtk_mix.R")
```

Or from the command line:

```bash
Rscript scripts/run_td_model.R
Rscript scripts/run_pbtk_kabsk.R
Rscript scripts/run_pbtk_mix.R
```

## Data Availability

No raw experimental datasets are bundled in the current repository snapshot. If manuscript-associated raw data cannot be shared publicly, document access conditions in `data/README.md` and provide example inputs when possible.

## Reproducibility Notes

- Use a tagged release for manuscript submission, for example `v1.0.0-manuscript`.
- Archive the release with Zenodo to mint a DOI.
- Cite the DOI in the manuscript whenever available.

## Citation

See [`CITATION.cff`](CITATION.cff) for software citation metadata.

Suggested placeholder citation before DOI minting:

Lu, Y. (2026). *PFAS-fish-PBTK-TD-model: PFAS PBTK and toxicodynamic modeling scripts* (Version 1.0.0) [Computer software]. GitHub. [https://github.com/luyi-95/PFAS-fish-PBTK-TD-model](https://github.com/luyi-95/PFAS-fish-PBTK-TD-model)

## License

This repository is released under the MIT License. See [`LICENSE`](LICENSE).
