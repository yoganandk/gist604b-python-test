"""
GIST 604B - GeoPandas Spatial Operations
Professional spatial analysis with 15-point structure (7 core functions)

This module demonstrates professional-level implementations of foundational
spatial operations using GeoPandas following a complete GIS workflow:
I/O → Explore → Transform → Operate → Analyze → Visualize

Student: [Your Name]  
Date: [Current Date]
"""

import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import warnings
from typing import Dict, List, Tuple, Union, Optional, Any
from shapely.geometry import Point, LineString, Polygon, MultiPoint, MultiLineString, MultiPolygon
import matplotlib.pyplot as plt
from matplotlib.patches import Patch


# Function 1: Load Spatial Data (2 points)

def load_spatial_data(file_path: Union[str, Path], **kwargs) -> gpd.GeoDataFrame:
    """
    Load spatial data from various vector file formats.
    
    Supports GeoJSON, Shapefile, GeoPackage, and other formats readable by GeoPandas.
    Professional implementation with comprehensive error handling.
    
    Args:
        file_path: Path to the spatial data file
        **kwargs: Additional arguments to pass to gpd.read_file()
        
    Returns:
        GeoDataFrame containing the loaded spatial data
        
    Raises:
        FileNotFoundError: If the file doesn't exist
        ValueError: If the file format is invalid or cannot be read
        
    Example:
        >>> gdf = load_spatial_data('data/cities.geojson')
        >>> print(f"Loaded {len(gdf)} features")
    """
    # TODO: Implement this function
    # Hints:
    # - Convert file_path to Path object
    # - Check if file exists
    # - Use gpd.read_file() to load data
    # - Handle different file formats appropriately
    # - Validate the loaded data is not empty
    raise NotImplementedError("load_spatial_data not yet implemented")


# Function 2: Explore Properties (2 points)

def explore_properties(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """
    Analyze and extract key spatial properties from a GeoDataFrame.
    
    Provides comprehensive exploration of:
    - Coordinate Reference System (CRS)
    - Spatial bounds (extent)
    - Geometry types present
    - Feature count and basic statistics
    
    Args:
        gdf: Input GeoDataFrame to explore
        
    Returns:
        Dictionary containing spatial properties:
        - 'crs': CRS object or None
        - 'bounds': [minx, miny, maxx, maxy] or empty list
        - 'geometry_types': List of unique geometry types
        - 'feature_count': Number of features
        - 'columns': List of attribute column names
        
    Example:
        >>> props = explore_properties(gdf)
        >>> print(f"CRS: {props['crs']}")
        >>> print(f"Bounds: {props['bounds']}")
        >>> print(f"Geometry types: {props['geometry_types']}")
    """
    # TODO: Implement this function
    # Hints:
    # - Access gdf.crs for coordinate system
    # - Use gdf.total_bounds for extent
    # - Check gdf.geometry.geom_type for geometry types
    # - Count features with len(gdf)
    raise NotImplementedError("explore_properties not yet implemented")


# Function 3: Transform CRS (2 points)

def transform_crs(
    gdf: gpd.GeoDataFrame, 
    target_crs: Union[str, int]
) -> gpd.GeoDataFrame:
    """
    Transform GeoDataFrame to a different coordinate reference system.
    
    Handles CRS transformation with proper validation and error handling.
    Essential for ensuring spatial data alignment and accurate measurements.
    
    Args:
        gdf: Input GeoDataFrame
        target_crs: Target CRS (e.g., 'EPSG:4326', 'EPSG:3857', or EPSG code as int)
        
    Returns:
        New GeoDataFrame in the target CRS
        
    Raises:
        ValueError: If GeoDataFrame has no CRS or target CRS is invalid
        
    Example:
        >>> # Transform to Web Mercator (EPSG:3857)
        >>> gdf_mercator = transform_crs(gdf, 'EPSG:3857')
        >>> print(f"New CRS: {gdf_mercator.crs}")
    """
    # TODO: Implement this function
    # Hints:
    # - Check if gdf has a CRS defined (gdf.crs)
    # - Use gdf.to_crs(target_crs) for transformation
    # - Handle cases where CRS is None
    # - Validate target_crs is valid
    # - Return a copy, not modify original
    raise NotImplementedError("transform_crs not yet implemented")


# Function 4: Geometry Operations (3 points)

def geometry_operations(
    gdf: gpd.GeoDataFrame,
    operation: str = 'buffer',
    **kwargs
) -> Dict[str, Any]:
    """
    Perform fundamental geometry operations on spatial data.
    
    Supports multiple geometric operations:
    - 'buffer': Create buffers around geometries
    - 'centroid': Calculate geometric centers
    - 'area': Calculate polygon areas
    - 'length': Calculate line lengths
    - 'simplify': Generalize geometries
    
    Args:
        gdf: Input GeoDataFrame
        operation: Operation to perform ('buffer', 'centroid', 'area', 'length', 'simplify')
        **kwargs: Operation-specific parameters:
            - buffer: distance (float, required)
            - simplify: tolerance (float, required)
            
    Returns:
        Dictionary containing:
        - 'result': GeoDataFrame with operation results
        - 'statistics': Dictionary of computed statistics
        - 'operation': Name of operation performed
        
    Raises:
        ValueError: If operation is invalid or parameters are missing
        
    Example:
        >>> # Create 1000m buffer
        >>> result = geometry_operations(gdf, 'buffer', distance=1000)
        >>> buffered_gdf = result['result']
        
        >>> # Calculate centroids
        >>> result = geometry_operations(gdf, 'centroid')
        >>> centroids = result['result']
    """
    # TODO: Implement this function
    # Hints:
    # - Support multiple operations with if/elif statements
    # - For buffer: use gdf.geometry.buffer(distance)
    # - For centroid: use gdf.geometry.centroid
    # - For area: use gdf.geometry.area
    # - For length: use gdf.geometry.length
    # - For simplify: use gdf.geometry.simplify(tolerance)
    # - Return results in standardized dictionary format
    raise NotImplementedError("geometry_operations not yet implemented")


# Function 5: Spatial Relationships (2 points)

def spatial_relationships(
    gdf1: gpd.GeoDataFrame,
    gdf2: gpd.GeoDataFrame,
    relationship: str = 'intersects'
) -> Dict[str, Any]:
    """
    Test spatial relationships between two GeoDataFrames.
    
    Supports spatial predicates:
    - 'intersects': Geometries that intersect
    - 'contains': Geometries from gdf1 that contain gdf2
    - 'within': Geometries from gdf1 within gdf2
    - 'distance': Calculate distances between geometries
    - 'nearest': Find nearest features
    
    Args:
        gdf1: First GeoDataFrame
        gdf2: Second GeoDataFrame
        relationship: Type of spatial relationship to test
        
    Returns:
        Dictionary containing:
        - 'relationship': Type of relationship tested
        - 'results': Boolean series or distance measurements
        - 'count': Number of features meeting criteria
        - 'indices': Indices of matching features
        
    Raises:
        ValueError: If inputs are invalid or CRS don't match
        
    Example:
        >>> # Find cities that intersect countries
        >>> result = spatial_relationships(cities, countries, 'intersects')
        >>> print(f"{result['count']} cities intersect countries")
        
        >>> # Calculate distances
        >>> result = spatial_relationships(points, lines, 'distance')
        >>> distances = result['results']
    """
    # TODO: Implement this function
    # Hints:
    # - Validate both GeoDataFrames have CRS defined
    # - Check if CRS match (transform if needed)
    # - For intersects: use gdf1.geometry.intersects(gdf2.geometry)
    # - For contains: use gdf1.geometry.contains(gdf2.geometry)
    # - For within: use gdf1.geometry.within(gdf2.geometry)
    # - For distance: use gdf1.geometry.distance(gdf2.geometry)
    # - For nearest: use spatial indexing (.sindex)
    raise NotImplementedError("spatial_relationships not yet implemented")


# Function 6: Spatial Joins (2 points)

def spatial_joins(
    left_gdf: gpd.GeoDataFrame,
    right_gdf: gpd.GeoDataFrame,
    how: str = 'inner',
    predicate: str = 'intersects'
) -> gpd.GeoDataFrame:
    """
    Join two GeoDataFrames based on spatial relationships.
    
    Combines attribute data from two spatial datasets based on their
    spatial relationship (e.g., points within polygons, lines intersecting areas).
    
    Args:
        left_gdf: Left GeoDataFrame (preserved geometries)
        right_gdf: Right GeoDataFrame (attributes joined)
        how: Type of join ('inner', 'left', 'right')
        predicate: Spatial predicate ('intersects', 'contains', 'within')
        
    Returns:
        Joined GeoDataFrame with combined attributes
        
    Raises:
        ValueError: If inputs are invalid or CRS incompatible
        
    Example:
        >>> # Join cities with their countries
        >>> result = spatial_joins(cities, countries, how='left', predicate='within')
        >>> print(f"Joined {len(result)} features")
    """
    # TODO: Implement this function
    # Hints:
    # - Validate both inputs are GeoDataFrames
    # - Check CRS compatibility
    # - Use gpd.sjoin() for spatial join
    # - Handle CRS mismatch by transforming
    # - Validate result is not empty (for inner joins)
    raise NotImplementedError("spatial_joins not yet implemented")


# Function 7: Overlay and Visualize (2 points)

def overlay_and_visualize(
    gdf1: gpd.GeoDataFrame,
    gdf2: Optional[gpd.GeoDataFrame] = None,
    overlay_how: str = 'intersection',
    save_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """
    Perform overlay operations and create visualizations.
    
    Combines two spatial datasets using geometric overlay operations
    and generates both static and interactive visualizations.
    
    Overlay operations:
    - 'intersection': Areas where both datasets overlap
    - 'union': Combined areas from both datasets
    - 'difference': Areas in gdf1 not in gdf2
    - 'symmetric_difference': Areas in either but not both
    
    Args:
        gdf1: First GeoDataFrame
        gdf2: Second GeoDataFrame (optional for visualization only)
        overlay_how: Type of overlay operation
        save_path: Optional path to save the visualization
        
    Returns:
        Dictionary containing:
        - 'overlay_result': GeoDataFrame with overlay results (if gdf2 provided)
        - 'figure': Matplotlib figure object
        - 'statistics': Dictionary of geometry counts and areas
        
    Raises:
        ValueError: If inputs are invalid or overlay operation fails
        
    Example:
        >>> # Find intersection of two polygon layers
        >>> result = overlay_and_visualize(parks, flood_zones, 'intersection')
        >>> overlay_gdf = result['overlay_result']
        >>> print(f"Intersection area: {overlay_gdf.geometry.area.sum()}")
        
        >>> # Just visualize a single layer
        >>> result = overlay_and_visualize(cities, save_path='cities_map.png')
        >>> plt.show()
    """
    # TODO: Implement this function
    # Hints:
    # - If gdf2 provided, perform overlay with gpd.overlay()
    # - Create visualization with gdf.plot()
    # - Add basemap with contextily if available
    # - For interactive map, use gdf.explore()
    # - Calculate statistics (feature counts, total area)
    # - Save figure if save_path provided
    raise NotImplementedError("overlay_and_visualize not yet implemented")


# Helper Functions (provided for you)

def _validate_crs_compatibility(
    gdf1: gpd.GeoDataFrame, 
    gdf2: gpd.GeoDataFrame
) -> Tuple[bool, str]:
    """
    Check if two GeoDataFrames have compatible CRS.
    
    Returns:
        Tuple of (compatible: bool, message: str)
    """
    if gdf1.crs is None:
        return False, "First GeoDataFrame has no CRS defined"
    if gdf2.crs is None:
        return False, "Second GeoDataFrame has no CRS defined"
    if gdf1.crs != gdf2.crs:
        return False, f"CRS mismatch: {gdf1.crs} vs {gdf2.crs}"
    return True, "CRS compatible"


def _get_appropriate_utm_crs(gdf: gpd.GeoDataFrame) -> str:
    """
    Determine appropriate UTM CRS based on dataset centroid.
    
    Returns:
        EPSG code string for appropriate UTM zone
    """
    try:
        # Get centroid of all geometries
        centroid = gdf.geometry.centroid.unary_union.centroid
        lon, lat = centroid.x, centroid.y
        
        # Calculate UTM zone
        utm_zone = int((lon + 180) // 6) + 1
        
        # Northern or Southern hemisphere
        if lat >= 0:
            epsg_code = 32600 + utm_zone  # UTM North
        else:
            epsg_code = 32700 + utm_zone  # UTM South
            
        return f'EPSG:{epsg_code}'
    except Exception:
        return 'EPSG:3857'  # Web Mercator as fallback


def _calculate_geometry_statistics(gdf: gpd.GeoDataFrame) -> Dict[str, Any]:
    """
    Calculate comprehensive geometry statistics.
    
    Returns:
        Dictionary of statistics including counts, areas, lengths
    """
    stats = {
        'feature_count': len(gdf),
        'geometry_types': gdf.geometry.geom_type.value_counts().to_dict()
    }
    
    # Calculate areas for polygons
    if any(gdf.geometry.geom_type.isin(['Polygon', 'MultiPolygon'])):
        stats['total_area'] = gdf.geometry.area.sum()
        stats['mean_area'] = gdf.geometry.area.mean()
    
    # Calculate lengths for lines
    if any(gdf.geometry.geom_type.isin(['LineString', 'MultiLineString'])):
        stats['total_length'] = gdf.geometry.length.sum()
        stats['mean_length'] = gdf.geometry.length.mean()
    
    return stats
