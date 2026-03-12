"""
GIST 604B - Rasterio and Remote Sensing Workflows
Professional raster analysis with STAC, COGs, NDVI, and time series workflows

This module demonstrates professional-level implementations of foundational
remote sensing operations using Rasterio and related tools following a
complete raster workflow:

Discover → Read → Calculate → Mask → Summarize

Student: [Your Name]
Date: [Current Date]
"""

from pathlib import Path
from typing import Dict, List, Tuple, Union, Optional, Any

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import rasterio
from pyproj import Transformer
from pystac_client import Client
from rasterio import features
from rasterio.plot import show


# STAC API endpoint
STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


# Function 1: Search STAC Imagery (2 points)

def image_search(
    bbox: List[float],
    date_range: str,
    scene_cloud_tolerance: Union[int, float]
) -> List[Any]:
    """
    Search for Sentinel-2 scenes using a STAC catalog.
    
    Connects to a STAC API and finds imagery intersecting a bounding box
    within a date range and below a cloud cover threshold.
    
    Args:
        bbox: Bounding box as [west, south, east, north]
        date_range: Date range in "YYYY-MM-DD/YYYY-MM-DD" format
        scene_cloud_tolerance: Maximum allowed cloud cover percentage
        
    Returns:
        List of matching STAC items
        
    Raises:
        ValueError: If bbox or date_range is invalid
        
    Example:
        >>> items = image_search(
        ...     [-110.75, 32.27, -110.70, 32.29],
        ...     "2021-07-01/2021-08-01",
        ...     5
        ... )
        >>> print(f"Found {len(items)} scenes")
    """
    # TODO: Implement this function
    # Hints:
    # - Validate bbox has 4 values
    # - Connect to the STAC catalog with Client.open(STAC_URL)
    # - Use catalog.search(...)
    # - Search collection "sentinel-2-l2a"
    # - Filter using bbox, datetime, and eo:cloud_cover
    # - Return list(search.items())
    raise NotImplementedError("image_search not yet implemented")


# Function 2: Read Raster Window (2 points)

def windowed_read(
    url: str,
    bbox: List[float]
) -> Tuple[np.ndarray, Any]:
    """
    Read a raster subset from a cloud-hosted asset using a bounding box.
    
    Performs a windowed read so that only the relevant raster pixels
    are downloaded instead of the entire file.
    
    Args:
        url: Raster asset URL
        bbox: Bounding box as [west, south, east, north]
        
    Returns:
        Tuple containing:
        - pixels: NumPy array of raster values
        - transform: Affine transform for the raster window
        
    Raises:
        ValueError: If bbox is invalid or raster cannot be read
        
    Example:
        >>> pixels, transform = windowed_read(red_url, bbox)
        >>> print(pixels.shape)
    """
    # TODO: Implement this function
    # Hints:
    # - Open the raster with rasterio.open(url)
    # - Transform bbox from EPSG:4326 to the raster CRS using Transformer
    # - Convert transformed coords to pixel row/col using src.index()
    # - Build a rasterio.windows.Window from the pixel coordinates
    # - Read band 1 with src.read(1, window=window)
    # - Get the window transform with src.window_transform(window)
    # - Return pixels and transform
    raise NotImplementedError("windowed_read not yet implemented")


# Function 3: Calculate NDVI (2 points)

def calculate_ndvi(
    red_pixels: np.ndarray,
    nir_pixels: np.ndarray
) -> np.ndarray:
    """
    Calculate NDVI from red and near-infrared band arrays.
    
    NDVI = (NIR - Red) / (NIR + Red)
    
    Args:
        red_pixels: Red band pixel values
        nir_pixels: Near-infrared band pixel values
        
    Returns:
        NumPy array of NDVI values
        
    Raises:
        ValueError: If input arrays do not have matching shape
        
    Example:
        >>> ndvi = calculate_ndvi(red_pixels, nir_pixels)
        >>> print(ndvi.min(), ndvi.max())
    """
    # TODO: Implement this function
    # Hints:
    # - Check that both arrays have the same shape
    # - Convert arrays to float using .astype(float)
    # - Apply the NDVI formula
    # - Return the resulting NumPy array
    raise NotImplementedError("calculate_ndvi not yet implemented")


# Function 4: Mask NDVI by Field (2 points)

def mask_ndvi_by_field(
    image: Dict[str, Any],
    field_geom: Any
) -> ma.MaskedArray:
    """
    Mask NDVI values to a polygon geometry.
    
    Uses rasterio.features.geometry_mask() to keep NDVI values inside
    a polygon and mask values outside it.
    
    Args:
        image: Scene dictionary containing:
            - 'ndvi': NDVI array
            - 'transform_window': Affine transform
        field_geom: Polygon geometry for masking
        
    Returns:
        MaskedArray of NDVI values inside the polygon
        
    Raises:
        ValueError: If required keys are missing from image
        
    Example:
        >>> masked_ndvi = mask_ndvi_by_field(image, field.geometry)
        >>> print(masked_ndvi.mean())
    """
    # TODO: Implement this function
    # Hints:
    # - Validate image contains 'ndvi' and 'transform_window'
    # - Use features.geometry_mask(...)
    # - Set out_shape to the NDVI array shape
    # - Use the window transform from the image dictionary
    # - Wrap the NDVI array with ma.masked_array(...)
    # - Return the masked NDVI array
    raise NotImplementedError("mask_ndvi_by_field not yet implemented")


# Function 5: Build NDVI Time Series (2 points)

def build_ndvi_time_series(
    images: List[Dict[str, Any]],
    fields: gpd.GeoDataFrame
) -> Dict[Any, Dict[str, List[Any]]]:
    """
    Build mean NDVI through time for each polygon field.
    
    Iterates over multiple raster scenes and multiple field polygons,
    masks NDVI to each field, and calculates mean NDVI values through time.
    
    Args:
        images: List of scene dictionaries
        fields: GeoDataFrame of polygon features
        
    Returns:
        Dictionary keyed by field identifier containing:
        - 'dates': List of date strings
        - 'ndvi': List of mean NDVI values
        
    Raises:
        ValueError: If images list is empty or fields is invalid
        
    Example:
        >>> ts = build_ndvi_time_series(images, fields)
        >>> print(ts.keys())
    """
    # TODO: Implement this function
    # Hints:
    # - Validate inputs
    # - Loop over each field in fields.iterrows()
    # - For each field, loop over each image
    # - Use mask_ndvi_by_field(...) to get masked NDVI
    # - Calculate .mean() for the masked array
    # - Build a dictionary with 'dates' and 'ndvi' lists
    # - Return the completed dictionary
    raise NotImplementedError("build_ndvi_time_series not yet implemented")


# Function 6: Plot NDVI Time Series (2 points)

def plot_ndvi_time_series(
    time_series_data: Dict[Any, Dict[str, List[Any]]],
    title: str = "NDVI Time Series by Field"
) -> plt.Figure:
    """
    Plot NDVI time series for one or more fields.
    
    Creates a line plot showing NDVI values through time for each field
    in the provided time series dictionary.
    
    Args:
        time_series_data: Dictionary returned by build_ndvi_time_series()
        title: Plot title
        
    Returns:
        Matplotlib Figure object
        
    Raises:
        ValueError: If time_series_data is empty
        
    Example:
        >>> fig = plot_ndvi_time_series(ts_data)
        >>> plt.show()
    """
    # TODO: Implement this function
    # Hints:
    # - Validate input is not empty
    # - Create a matplotlib figure and axis
    # - Loop through fields in time_series_data
    # - Plot dates vs NDVI values for each field
    # - Add title, axis labels, legend, and grid
    # - Return the figure
    raise NotImplementedError("plot_ndvi_time_series not yet implemented")


# Helper Functions (provided for you)

def _validate_bbox(bbox: List[float]) -> Tuple[bool, str]:
    """
    Validate that bbox is in [west, south, east, north] format.
    
    Returns:
        Tuple of (valid: bool, message: str)
    """
    if not isinstance(bbox, (list, tuple)):
        return False, "Bounding box must be a list or tuple"

    if len(bbox) != 4:
        return False, "Bounding box must contain exactly 4 values"

    try:
        west, south, east, north = [float(v) for v in bbox]
    except (TypeError, ValueError):
        return False, "Bounding box values must be numeric"

    if west >= east:
        return False, "Bounding box west value must be less than east"

    if south >= north:
        return False, "Bounding box south value must be less than north"

    return True, "Bounding box is valid"


def _validate_image_dict(image: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Validate that an image dictionary contains required raster keys.
    
    Returns:
        Tuple of (valid: bool, message: str)
    """
    required_keys = ["ndvi", "transform_window"]

    if not isinstance(image, dict):
        return False, "Image must be a dictionary"

    missing = [key for key in required_keys if key not in image]
    if missing:
        return False, f"Image dictionary missing required keys: {missing}"

    return True, "Image dictionary is valid"


def _extract_field_id(row: pd.Series) -> Any:
    """
    Extract a field identifier from a GeoDataFrame row.
    
    Prefers the 'area' column if present, otherwise falls back to the row index.
    
    Returns:
        Field identifier
    """
    if "area" in row.index:
        return row["area"]
    return row.name
