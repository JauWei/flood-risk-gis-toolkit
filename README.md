# Flood Risk GIS Toolkit | Python 洪氾風險示範工具

[![Python tests](https://github.com/JauWei/flood-risk-gis-toolkit/actions/workflows/tests.yml/badge.svg)](https://github.com/JauWei/flood-risk-gis-toolkit/actions/workflows/tests.yml)

A small, reproducible **Python software development project** for grid-based flood-risk **screening and education**. Includes a documented algorithm, synthetic example dataset, unit tests, CLI, CSV output and GeoJSON point output suitable for inspection in QGIS.

> **Important:** This is an illustrative index, **not** an official flood hazard map, rainfall-runoff model, hydrodynamic simulation, or engineering design tool. Input coordinates are arbitrary planar grid coordinates, **not WGS84 longitude/latitude**. The GeoJSON points must not be overlaid onto real-world basemaps without an appropriate real-world coordinate reference and transformation. No claims about real flood depths or return periods can be inferred.

## What the code does

1. Read a CSV containing `cell_id, x, y, elevation_m, slope_deg, rainfall_mm, impervious_pct, population`.
2. Apply min–max normalization **within the provided dataset** (constant series normalize to zero).
3. Calculate a transparent illustrative hazard index:

   `hazard = (1 - norm(elevation) + 1 - norm(slope) + norm(rainfall) + norm(impervious)) / 4`

4. Calculate vulnerability `norm(population)` and `risk = hazard × vulnerability`.
5. Classify `low` (<0.3), `medium` (0.3–<0.6), `high` (≥0.6), using illustrative, **not calibrated** thresholds.
6. Write `outputs/risk_results.csv` and `outputs/risk_points.geojson`.

**Limitations:** low slope is used as a heuristic for local accumulation, not a flow routing calculation. No DEM hydrology, SCS-CN, TWI, drainage network, exposure model calibration, observed flood validation, or uncertainty quantification is implemented. Comparisons across datasets with different min/max values are not meaningful without a shared calibration.

## Quick start

Python 3.9+ required; no runtime third-party dependencies.

```bash
python -m pip install -e .
python -m floodrisk --input data/sample_cells.csv --output outputs/risk_results.csv --geojson outputs/risk_points.geojson
python -m unittest discover -s tests -v
```

Expected output: `Analyzed 100 cells` plus counts of risk classes. See `outputs/` for pre-generated example outputs.

## Data

`data/sample_cells.csv` contains **100 synthetic grid cells** generated with a fixed random seed. They do **not** describe Taichung or any real location. `x, y` are abstract grid coordinates.

## QGIS usage

For tabular inspection, import `outputs/risk_results.csv` as a table. To visualize the GeoJSON points, load `outputs/risk_points.geojson` as a vector layer **without assigning a real geographic CRS**. For real georeferenced GIS workflows, replace the synthetic data with a correctly referenced dataset and explicitly handle CRS and spatial data conversion. Do not assume these arbitrary coordinates are latitude/longitude.

## Project structure

```text
src/floodrisk/        Core algorithm and command-line interface
data/                 Synthetic reproducible sample data
tests/                Python unit tests
outputs/              Generated CSV and GeoJSON examples
.github/workflows/    Automated CI test workflow
```

## Developer / contact

JauWei — [GitHub profile](https://github.com/JauWei) · [Portfolio](https://jauwei.github.io/)

MIT licensed. Contributions and feedback are welcome.
