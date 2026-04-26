from __future__ import annotations

from fastapi import FastAPI, HTTPException

from geogreen.core.engine import get_city_analysis

app = FastAPI(title="GeoGreen Intelligence Platform", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/analysis/{city_name}")
def city_analysis(city_name: str) -> dict:
    try:
        result = get_city_analysis(city_name)
        return result.__dict__
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
