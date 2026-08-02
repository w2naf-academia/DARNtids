# Changelog

All notable changes to DARNtids are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this
project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html). While the
major version is `0`, breaking changes increment the **minor** version.

## [0.2.0] - 2026-08-02

### Removed

- **BREAKING**: the `boxcar_filter` parameter has been removed from
  `darntids.more_music.run_music()` (previously defaulted to `True`). Remove the key from any
  configuration dictionary handed to `run_helper.create_music_run_list()`.

  `run_music()` raises `TypeError` with an explanatory message if the key is still present.
  This guard is deliberate: the function accepts `**kwargs`, which would otherwise swallow
  `boxcar_filter` silently, letting a configuration that asked for despeckling run without
  any and produce a plausible-looking but differently-filtered MSTID index.

  When enabled, it called `pyDARNmusic.boxcarFilter()` — a crude in-Python median-filter
  reimplementation that was never used to produce the MSTID index. Salt-and-pepper
  despeckling is performed upstream by the `fitexfilter` binary (A. J. Ribeiro; RST
  `FilterRadarScan`) before this pipeline reads the fitacf. See
  [Stage 0 of the pipeline documentation](docs/pipeline.md#stage-0-upstream-despeckle-prerequisite).

  **Migration**: delete `boxcar_filter` from your config. If you were relying on it being
  `True`, despeckle upstream with `fitexfilter` instead — the two are not equivalent.

### Added

- `hdf5_api` (the MUSIC HDF5 reader) is now installed as an importable top-level module via
  `py-modules`. It was **not shipped at all** in the 0.1.0 distribution, so `import hdf5_api`
  failed after a normal `pip install darntids` and only worked from a source checkout with
  the repository root on `sys.path`.

### Fixed

- `run_DARNtids.py` no longer contains a syntax error. The line setting
  `terminator_fraction_threshold` read `1.0.` (trailing period), which made the script fail
  to parse.
- `[project.urls]` metadata now points at the active `w2naf-academia/DARNtids` repository
  rather than the deprecated `w2naf/DARNtids` mirror.

### Documentation

- Added **Stage 0: Upstream Despeckle** to `docs/pipeline.md`, documenting the `fitexfilter`
  prerequisite, its default parameters (3×3×3 boxcar, threshold 0.4, camping beams combined),
  and the fact that it recomputes the ground-scatter flag the MSTID index depends on.
- `docs/configuration.md` `fitacf_dir` now states that DARNtids performs no despeckling of
  its own and that reproducing the published index requires despeckled input.

## [0.1.0]

Initial packaged release on PyPI.

SuperDARN Traveling Ionospheric Disturbance Analysis Toolkit — the MSTID detection and
classification pipeline supporting Frissell et al. (2016) and subsequent work.
