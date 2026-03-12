"""
GIST 604B - Rasterio Remote Sensing Workflow
STAC search, windowed raster reads, NDVI calculation, polygon masking,
and NDVI time-series analysis.

This module is different from the pandas and GeoPandas modules.

Instead of being organized entirely around separate standalone functions,
this file supports a larger remote sensing workflow. A few helper functions
are provided as reusable building blocks, and the main workflow is completed
through clearly labeled code sections.

Student: [Your Name]
Date: [Current Date]
"""

from pathlib import Path
from typing import Any, Dict, List, Tuple, Union

import geopandas as gpd
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import numpy.ma as ma
import rasterio
from pyproj import Transformer
from pystac_client import Client
from rasterio import features
from rasterio.plot import show
import planetary_computer


# =============================================================================
# CONFIGURATION
# =============================================================================

STAC_URL = "https://planetarycomputer.microsoft.com/api/stac/v1"


# =============================================================================
# HELPER FUNCTION 1: SEARCH STAC IMAGERY
# =============================================================================

def image_search(
    bbox: List[float],
    date_range: str,
    scene_cloud_tolerance: Union[int, float]
) -> List[Any]:
    """
    Search for Sentinel-2 scenes using a STAC catalog.
    
    Connects to the Microsoft Planetary Computer STAC API and searches
    for Sentinel-2 imagery intersecting a bounding box within a date range
    and below a cloud cover threshold.
    
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
    # - Validate bbox with _validate_bbox()
    # - Connect to the STAC catalog with Client.open(STAC_URL)
    # - Use catalog.search(...)
    # - Search collection "sentinel-2-l2a"
    # - Filter using bbox, datetime, and eo:cloud_cover
    # - Return list(search.items())
    raise NotImplementedError("image_search not yet implemented")


# =============================================================================
# HELPER FUNCTION 2: WINDOWED READ
# =============================================================================

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
    # - Validate bbox with _validate_bbox()
    # - Sign the URL with planetary_computer.sign(url)
    # - Open the raster with rasterio.open(...)
    # - Transform bbox from EPSG:4326 to the raster CRS using Transformer
    # - Convert transformed coords to pixel row/col using src.index()
    # - Build a rasterio.windows.Window from the pixel coordinates
    # - Read band 1 with src.read(1, window=window)
    # - Get the window transform with src.window_transform(window)
    # - Return pixels and transform
    raise NotImplementedError("windowed_read not yet implemented")


# =============================================================================
# HELPER FUNCTION 3: MASK NDVI BY FIELD
# =============================================================================

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
    # - Validate image with _validate_image_dict()
    # - Use features.geometry_mask(...)
    # - Set out_shape to the NDVI array shape
    # - Use the window transform from the image dictionary
    # - Wrap the NDVI array with ma.masked_array(...)
    # - Return the masked NDVI array
    raise NotImplementedError("mask_ndvi_by_field not yet implemented")


# =============================================================================
# WORKFLOW SECTION 1: DEFINE STUDY AREA AND SEARCH SETTINGS
# =============================================================================

# TODO: Define a bounding box for your study area
# Format: [west, south, east, north]
bbox = None

# TODO: Define a short date range for initial exploration
# Example: "2021-07-05/2021-08-02"
date_range = None

# TODO: Define a longer date range for time-series analysis
# Example: "2020-01-01/2021-12-31"
long_date_range = None

# TODO: Define cloud cover threshold
scene_cloud_tolerance = None


# =============================================================================
# WORKFLOW SECTION 2: SEARCH FOR IMAGERY
# =============================================================================

# TODO: Search for imagery using image_search()
# Store the result in a variable named items
items = None

# TODO: Inspect the number of scenes found
# TODO: Print the item IDs and datetimes for a few scenes


# =============================================================================
# WORKFLOW SECTION 3: INSPECT ONE STAC ITEM AND ITS ASSETS
# =============================================================================

# TODO: Select one STAC item from the list
item = None

# TODO: Inspect key properties such as:
# - item.id
# - item.datetime
# - item.bbox
# - item.properties.get("eo:cloud_cover")
# - list(item.assets.keys())

# TODO: Get the asset URLs you will need:
# - red_url from B04
# - nir_url from B08
# - rgb_url from visual
red_url = None
nir_url = None
rgb_url = None


# =============================================================================
# WORKFLOW SECTION 4: READ RASTER WINDOWS
# =============================================================================

# TODO: Use windowed_read() to read:
# - red band pixels
# - NIR band pixels
# Store the outputs in:
# - red_pixels, transform_window
# - nir_pixels, _
red_pixels = None
nir_pixels = None
transform_window = None

# TODO: Print shapes and basic information about the raster subsets


# =============================================================================
# WORKFLOW SECTION 5: CALCULATE NDVI
# =============================================================================

# TODO: Calculate NDVI using the formula:
# (NIR - Red) / (NIR + Red)
# Convert arrays to float first
ndvi = None

# TODO: Print NDVI summary statistics:
# - shape
# - min
# - max
# - mean


# =============================================================================
# WORKFLOW SECTION 6: READ RGB SUBSET FOR VISUALIZATION
# =============================================================================

# TODO: Sign the RGB URL with planetary_computer.sign()
# TODO: Open it with rasterio.open(...)
# TODO: Convert the bbox into a raster window
# TODO: Read bands [1, 2, 3]
# Store the result in rgb_pixels
rgb_pixels = None


# =============================================================================
# WORKFLOW SECTION 7: VISUALIZE RGB AND NDVI
# =============================================================================

# TODO: Create a side-by-side figure showing:
# - RGB subset
# - NDVI image with cmap="RdYlGn"
# Use matplotlib and/or rasterio.plot.show()


# =============================================================================
# WORKFLOW SECTION 8: BUILD A SCENE DICTIONARY
# =============================================================================

# TODO: Build a dictionary for one scene with keys:
# - 'date'
# - 'rgb'
# - 'ndvi'
# - 'transform_window'
image = None


# =============================================================================
# WORKFLOW SECTION 9: LOAD POLYGON DATA
# =============================================================================

# TODO: Load polygon features from neighborhood_samples.geojson
# TODO: Reproject to EPSG:32612
fields = None

# TODO: Print the number of polygons loaded


# =============================================================================
# WORKFLOW SECTION 10: VISUALIZE POLYGONS ON IMAGERY
# =============================================================================

# TODO: Plot the RGB subset
# TODO: Overlay polygon boundaries with GeoPandas


# =============================================================================
# WORKFLOW SECTION 11: MASK NDVI INSIDE ONE POLYGON
# =============================================================================

# TODO: Select one polygon geometry
field_geom = None

# TODO: Use mask_ndvi_by_field(image, field_geom)
masked_ndvi = None

# TODO: Plot the masked NDVI result over the imagery
# TODO: Print the mean NDVI inside the polygon


# =============================================================================
# WORKFLOW SECTION 12: BUILD A LONGER SCENE COLLECTION
# =============================================================================

# TODO: Search imagery again using long_date_range
long_items = None

# TODO: Create an empty list named images
images = []

# TODO: Loop through long_items
# For each item:
# - get red, nir, and visual asset URLs
# - read red and NIR windows with windowed_read()
# - calculate NDVI
# - read the RGB subset
# - append a scene dictionary to images
#
# Each scene dictionary should contain:
# {
#     'date': ...,
#     'rgb': ...,
#     'ndvi': ...,
#     'transform_window': ...
# }


# =============================================================================
# WORKFLOW SECTION 13: ADD MASKED NDVI FOR EACH FIELD
# =============================================================================

# TODO: For each image in images:
# - create a dictionary called ndvi_fields
# - loop through each polygon in fields
# - use mask_ndvi_by_field() to create a masked NDVI array
# - store it using a field identifier as the key
# - save ndvi_fields back into image['ndvi_fields']


# =============================================================================
# WORKFLOW SECTION 14: BUILD TIME-SERIES DATA
# =============================================================================

# TODO: Create an empty dictionary named time_series_data
time_series_data = {}

# TODO: For each field in fields:
# - create a list of dates
# - create a list of mean NDVI values
# - loop through images
# - append image['date']
# - append image['ndvi_fields'][field_id].mean()
# - store in time_series_data[field_id]
#
# Suggested structure:
# {
#     field_id: {
#         'dates': [...],
#         'ndvi': [...]
#     }
# }


# =============================================================================
# WORKFLOW SECTION 15: PLOT NDVI TIME SERIES
# =============================================================================

# TODO: Convert date strings to datetime objects for plotting
# TODO: Create a matplotlib line plot
# TODO: Plot one line per field
# TODO: Add:
# - title
# - x-axis label
# - y-axis label
# - legend
# - grid
# - formatted dates on x-axis


# =============================================================================
# WORKFLOW SECTION 16: WORKFLOW CHECKS
# =============================================================================

# TODO: Add a few print-based checks such as:
# - number of scenes found
# - shape of raster subsets
# - NDVI min/max/mean
# - number of polygons loaded
# - number of fields in time_series_data


# =============================================================================
# HELPER FUNCTIONS (provided for you)
# =============================================================================

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


def _extract_field_id(row) -> Any:
    """
    Extract a field identifier from a GeoDataFrame row.
    
    Prefers the 'area' column if present, otherwise falls back to the row index.
    
    Returns:
        Field identifier
    """
    if "area" in row.index:
        return row["area"]
    return row.name
