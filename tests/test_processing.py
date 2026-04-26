import numpy as np

from geogreen.core.data_fetcher import SatelliteCube
from geogreen.core.processing import compute_ndvi, estimate_tree_density, segment_vegetation


def test_ndvi_range_and_shape() -> None:
    cube = SatelliteCube(
        red=np.array([[0.2, 0.3], [0.4, 0.1]], dtype=np.float32),
        nir=np.array([[0.8, 0.6], [0.5, 0.9]], dtype=np.float32),
        swir=np.array([[0.1, 0.2], [0.3, 0.4]], dtype=np.float32),
    )
    ndvi = compute_ndvi(cube)
    assert ndvi.shape == (2, 2)
    assert np.all(ndvi <= 1.0)
    assert np.all(ndvi >= -1.0)


def test_vegetation_mask_threshold() -> None:
    ndvi = np.array([[0.1, 0.31], [0.7, 0.29]])
    mask = segment_vegetation(ndvi)
    assert mask.tolist() == [[False, True], [True, False]]


def test_tree_density_estimation() -> None:
    classified = np.array([[1, 1], [3, 4]], dtype=np.uint8)
    assert estimate_tree_density(classified) == 0.5
