# `data/interim/`

Intermediate transformed data — between raw pulls and the final master JSON. These files are derived from `data/raw/` via `src/transform/` scripts.

Public-registry-derived intermediates only. AVA-derived and IQVIA-derived intermediates are excluded by `.gitignore` (they would expose confidential underlying data).

## Refresh

To regenerate, re-run the relevant `src/transform/` script after refreshing the corresponding raw data.
