# GeoGreen Intelligence Platform

GeoGreen is an **AI-powered environmental intelligence platform** for on-demand city-level analysis.

## MVP scope
- City input (starting with Bangalore)
- Tree density estimation
- Land classification (trees, cropland, urban, barren)
- Environmental KPI generation
- API + interactive UI dashboard (same FastAPI app)

## Architecture
```
Frontend Dashboard (served at /)
  ↓
FastAPI API Layer
  ↓
Core Engine
  ├── Data Fetcher (GEE / Sentinel-2)
  ├── NDVI Processor
  ├── Segmentation
  ├── Classification
  ├── Density Estimator
  └── KPI Engine
```

## Run locally (single command flow)
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn geogreen.api.main:app --reload
```

Then open:
- UI Dashboard: `http://127.0.0.1:8000/`
- API Health: `http://127.0.0.1:8000/health`
- Analysis API: `http://127.0.0.1:8000/analysis/Bangalore`

## What you get in the UI
- Search bar for city input
- KPI cards:
  - Tree count estimate
  - Tree density
  - Urban %, Cropland %, Barren %
- Environmental insight scores:
  - Heat Impact Index
  - Water Retention Index
  - Green Coverage Score
  - Climate Risk Indicator
  - Urban Stress Score
- Land-distribution visual bars (tree/crop/urban/barren)

## Implementation notes
- The core abstraction is `get_city_analysis(city_name: str)` in `geogreen/core/engine.py`.
- Development mode currently builds deterministic synthetic raster bands, while keeping the Google Earth Engine integration point in place.
- NDVI and KPI logic is implemented in `geogreen/core/processing.py`.
