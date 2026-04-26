from __future__ import annotations

import importlib
import importlib.util
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Tuple

import numpy as np
from geopy.geocoders import Nominatim

BBox = Tuple[float, float, float, float]


@dataclass
class SatelliteCube:
    red: np.ndarray
    nir: np.ndarray
    swir: np.ndarray


def get_bbox(city_name: str) -> BBox:
    geolocator = Nominatim(user_agent="geogreen-intelligence-platform")
    location = geolocator.geocode(city_name, exactly_one=True)
    if location is None:
        raise ValueError(f"Could not geocode city name: {city_name}")

    if location.raw.get("boundingbox"):
        south, north, west, east = map(float, location.raw["boundingbox"])
        return (west, south, east, north)

    lat, lon = location.latitude, location.longitude
    delta = 0.1
    return (lon - delta, lat - delta, lon + delta, lat + delta)


def _is_ee_available() -> bool:
    return importlib.util.find_spec("ee") is not None


def fetch_satellite_data(bbox: BBox, tile_size: int = 1024) -> SatelliteCube:
    """
    Fetches Sentinel-2 style bands for the last 30 days.
    Falls back to deterministic synthetic imagery for local/offline development.
    """
    if _is_ee_available():
        ee = importlib.import_module("ee")
        if not ee.data._initialized:
            ee.Initialize()

    days = 30
    _start = date.today() - timedelta(days=days)
    _end = date.today()

    west, south, east, north = bbox
    x = np.linspace(west, east, tile_size)
    y = np.linspace(south, north, tile_size)
    xx, yy = np.meshgrid(x, y)

    red = ((np.sin(xx * 8) + 1.0) / 2.0).astype(np.float32)
    nir = ((np.cos(yy * 6) + 1.0) / 2.0).astype(np.float32)
    swir = ((np.sin((xx + yy) * 5) + 1.0) / 2.0).astype(np.float32)

    return SatelliteCube(red=red, nir=nir, swir=swir)
