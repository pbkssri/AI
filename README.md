# GeoGreen Intelligence Platform

GeoGreen is an **AI-powered environmental intelligence platform** for on-demand city-level analysis.

## MVP scope
- City input (starting with Bangalore)
- Tree density estimation
- Land classification (trees, cropland, urban, barren)
- Environmental KPI generation
- API-first architecture with FastAPI

## Architecture
```
Frontend Dashboard
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

## Run locally
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn geogreen.api.main:app --reload
```

## API
- `GET /health`
- `GET /analysis/{city_name}`

Example:
```bash
curl http://127.0.0.1:8000/analysis/Bangalore
```

## Implementation notes
- The core abstraction is `get_city_analysis(city_name: str)` in `geogreen/core/engine.py`.
- Development mode currently builds deterministic synthetic raster bands, while keeping the Google Earth Engine integration point in place.
- NDVI and KPI logic is implemented in `geogreen/core/processing.py`.
