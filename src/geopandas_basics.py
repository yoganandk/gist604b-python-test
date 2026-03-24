"""
GeoPandas Spatial Operations - Student Implementation

Complete the seven functions in this file.
Use the notebooks to learn and test each function.

📋 FUNCTIONS TO IMPLEMENT IN THIS FILE:
=====================================
✅ Function 1: load_spatial_data()        → notebooks/geopandas/01_function_...
✅ Function 2: explore_properties()       → notebooks/geopandas/02_function_...
✅ Function 3: transform_crs()            → notebooks/geopandas/03_function_...
✅ Function 4: geometry_operations()      → notebooks/geopandas/04_function_...
✅ Function 5: spatial_relationships()    → notebooks/geopandas/05_function_...
✅ Function 6: spatial_joins()            → notebooks/geopandas/06_function_...
✅ Function 7: overlay_and_visualize()    → notebooks/geopandas/07_function_...
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


# Function 1: Load Spatial Data

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
    # Convert to Path object for consistent handling
    file_path = Path(file_path)
    
    # Check if file exists
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    # Try to load the spatial data
    try:
        gdf = gpd.read_file(file_path, **kwargs)
    except Exception as e:
        raise ValueError(f"Cannot read spatial data from {file_path}: {str(e)}")
    
    return gdf


# Function 2: Explore Properties

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
    properties = {}
    
    # Extract CRS (handle empty GeoDataFrames without geometry column)
    try:
        properties['crs'] = gdf.crs
    except AttributeError:
        # Empty GeoDataFrame without geometry column has no CRS
        properties['crs'] = None
    
    # Extract bounds (total_bounds returns [minx, miny, maxx, maxy])
    if len(gdf) > 0:
        bounds = gdf.total_bounds
        properties['bounds'] = bounds.tolist()
    else:
        properties['bounds'] = [np.nan, np.nan, np.nan, np.nan]
    
    # Extract geometry types
    if len(gdf) > 0:
        geometry_types = gdf.geometry.geom_type.unique().tolist()
    else:
        geometry_types = []
    properties['geometry_types'] = geometry_types
    
    # Feature count
    properties['feature_count'] = len(gdf)
    
    # Column information
    properties['columns'] = gdf.columns.tolist()
    
    # Additional useful properties
    try:
        properties['has_valid_geometries'] = gdf.geometry.is_valid.all() if len(gdf) > 0 else True
    except AttributeError:
        # No geometry column
        properties['has_valid_geometries'] = True
    
    return properties


# Function 3: Transform CRS

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
    # Check if input has CRS
    if gdf.crs is None:
        raise ValueError("Input GeoDataFrame has no CRS defined. Cannot transform.")
    
    # Validate target CRS by trying to transform
    try:
        result = gdf.to_crs(target_crs)
    except Exception as e:
        raise ValueError(f"Invalid target CRS '{target_crs}': {str(e)}")
    
    return result


# Function 4: Geometry Operations

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
    valid_operations = ['buffer', 'centroid', 'area', 'length', 'simplify']
    
    if operation not in valid_operations:
        raise ValueError(f"Invalid operation '{operation}'. Must be one of: {valid_operations}")
    
    result_dict = {
        'operation': operation,
        'statistics': {}
    }
    
    if operation == 'buffer':
        if 'distance' not in kwargs:
            raise ValueError("Buffer operation requires 'distance' parameter")
        
        distance = kwargs['distance']
        result_gdf = gdf.copy()
        result_gdf.geometry = gdf.geometry.buffer(distance)
        
        result_dict['result'] = result_gdf
        result_dict['statistics']['buffer_distance'] = distance
        result_dict['statistics']['feature_count'] = len(result_gdf)
        
    elif operation == 'centroid':
        result_gdf = gdf.copy()
        result_gdf.geometry = gdf.geometry.centroid
        
        result_dict['result'] = result_gdf
        result_dict['statistics']['feature_count'] = len(result_gdf)
        
    elif operation == 'area':
        result_gdf = gdf.copy()
        areas = gdf.geometry.area
        result_gdf['area'] = areas
        
        result_dict['result'] = result_gdf
        result_dict['statistics']['total_area'] = areas.sum()
        result_dict['statistics']['mean_area'] = areas.mean()
        result_dict['statistics']['min_area'] = areas.min()
        result_dict['statistics']['max_area'] = areas.max()
        
    elif operation == 'length':
        result_gdf = gdf.copy()
        lengths = gdf.geometry.length
        result_gdf['length'] = lengths
        
        result_dict['result'] = result_gdf
        result_dict['statistics']['total_length'] = lengths.sum()
        result_dict['statistics']['mean_length'] = lengths.mean()
        result_dict['statistics']['min_length'] = lengths.min()
        result_dict['statistics']['max_length'] = lengths.max()
        
    elif operation == 'simplify':
        if 'tolerance' not in kwargs:
            raise ValueError("Simplify operation requires 'tolerance' parameter")
        
        tolerance = kwargs['tolerance']
        result_gdf = gdf.copy()
        result_gdf.geometry = gdf.geometry.simplify(tolerance)
        
        result_dict['result'] = result_gdf
        result_dict['statistics']['tolerance'] = tolerance
        result_dict['statistics']['feature_count'] = len(result_gdf)
    
    return result_dict


# Function 5: Spatial Relationships

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
    # Validate inputs
    if not isinstance(gdf1, gpd.GeoDataFrame) or not isinstance(gdf2, gpd.GeoDataFrame):
        raise ValueError("Both inputs must be GeoDataFrames")
    
    # Check CRS compatibility
    if gdf1.crs != gdf2.crs:
        raise ValueError(
            f"CRS mismatch: gdf1 has {gdf1.crs}, gdf2 has {gdf2.crs}. "
            "Transform to same CRS before testing relationships."
        )
    
    # Validate relationship type
    valid_relationships = ['intersects', 'contains', 'within', 'distance', 'nearest']
    if relationship not in valid_relationships:
        raise ValueError(
            f"Invalid relationship '{relationship}'. "
            f"Must be one of: {', '.join(valid_relationships)}"
        )
    
    result = {'relationship': relationship}
    
    if relationship == 'intersects':
        # Test which geometries from gdf1 intersect any geometry in gdf2
        intersects_any = gdf1.geometry.apply(
            lambda geom: gdf2.geometry.intersects(geom).any()
        )
        result['results'] = intersects_any
        result['count'] = int(intersects_any.sum())
        result['indices'] = intersects_any[intersects_any].index.tolist()
        
    elif relationship == 'contains':
        # Test which geometries from gdf1 contain any geometry from gdf2
        contains_any = gdf1.geometry.apply(
            lambda geom: gdf2.geometry.within(geom).any()
        )
        result['results'] = contains_any
        result['count'] = int(contains_any.sum())
        result['indices'] = contains_any[contains_any].index.tolist()
        
    elif relationship == 'within':
        # Test which geometries from gdf1 are within any geometry from gdf2
        within_any = gdf1.geometry.apply(
            lambda geom: gdf2.geometry.contains(geom).any()
        )
        result['results'] = within_any
        result['count'] = int(within_any.sum())
        result['indices'] = within_any[within_any].index.tolist()
        
    elif relationship == 'distance':
        # Calculate minimum distance (convert to metric CRS first)
        gdf1_proj = gdf1.to_crs('EPSG:5070')  # Albers Equal Area
        gdf2_proj = gdf2.to_crs('EPSG:5070')
        
        min_distances_m = gdf1_proj.geometry.apply(
            lambda geom: gdf2_proj.geometry.distance(geom).min()
        )
        min_distances_km = min_distances_m / 1000  # Convert to km
        result['results'] = min_distances_km
        result['distances'] = min_distances_km
        result['count'] = len(min_distances_km)
        result['mean_distance'] = float(min_distances_km.mean())
        result['units'] = 'kilometers'
        
    elif relationship == 'nearest':
        # Find nearest feature (using metric CRS for accurate distances)
        gdf1_proj = gdf1.to_crs('EPSG:5070')
        gdf2_proj = gdf2.to_crs('EPSG:5070')
        
        nearest_indices = []
        nearest_distances = []
        
        for geom1 in gdf1_proj.geometry:
            distances = gdf2_proj.geometry.distance(geom1)
            nearest_idx = distances.idxmin()
            nearest_dist_km = distances.min() / 1000  # Convert to km
            nearest_indices.append(nearest_idx)
            nearest_distances.append(nearest_dist_km)
        
        result['results'] = nearest_indices
        result['nearest_indices'] = nearest_indices
        result['nearest_distances'] = nearest_distances
        result['count'] = len(nearest_indices)
        result['units'] = 'kilometers'
    
    return result


# Function 6: Spatial Joins

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
    # Validate inputs
    if not isinstance(left_gdf, gpd.GeoDataFrame) or not isinstance(right_gdf, gpd.GeoDataFrame):
        raise ValueError("Both inputs must be GeoDataFrames")
    
    # Check CRS compatibility
    if left_gdf.crs != right_gdf.crs:
        raise ValueError(
            f"CRS mismatch: left has {left_gdf.crs}, right has {right_gdf.crs}. "
            "Transform to same CRS before joining."
        )
    
    # Validate parameters
    valid_how = ['inner', 'left', 'right']
    if how not in valid_how:
        raise ValueError(f"Invalid 'how' parameter '{how}'. Must be one of: {', '.join(valid_how)}")
    
    valid_predicates = ['intersects', 'contains', 'within']
    if predicate not in valid_predicates:
        raise ValueError(f"Invalid 'predicate' parameter '{predicate}'. Must be one of: {', '.join(valid_predicates)}")
    
    # Perform spatial join
    result = gpd.sjoin(left_gdf, right_gdf, how=how, predicate=predicate)
    
    return result


# Function 7: Overlay and Visualize

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
    result = {}
    
    # If gdf2 is provided, perform overlay operation
    if gdf2 is not None:
        # Validate inputs
        if not isinstance(gdf1, gpd.GeoDataFrame) or not isinstance(gdf2, gpd.GeoDataFrame):
            raise ValueError("Both inputs must be GeoDataFrames")
        
        # Check CRS compatibility
        if gdf1.crs != gdf2.crs:
            raise ValueError(
                f"CRS mismatch: gdf1 has {gdf1.crs}, gdf2 has {gdf2.crs}. "
                "Transform to same CRS before overlay."
            )
        
        # Validate overlay operation
        valid_operations = ['intersection', 'union', 'difference', 'symmetric_difference']
        if overlay_how not in valid_operations:
            raise ValueError(
                f"Invalid overlay operation '{overlay_how}'. "
                f"Must be one of: {', '.join(valid_operations)}"
            )
        
        # Perform overlay
        overlay_result = gpd.overlay(gdf1, gdf2, how=overlay_how)
        result['overlay_result'] = overlay_result
        
        # Calculate statistics
        stats = {
            'operation': overlay_how,
            'input1_count': len(gdf1),
            'input2_count': len(gdf2),
            'output_count': len(overlay_result),
        }
        
        # Calculate areas if geometry is polygons and result is not empty
        if len(overlay_result) > 0:
            geom_type = overlay_result.geometry.geom_type.iloc[0]
            if geom_type in ['Polygon', 'MultiPolygon']:
                # Use projected CRS for area calculation if in geographic CRS
                if overlay_result.crs and overlay_result.crs.is_geographic:
                    overlay_proj = overlay_result.to_crs('EPSG:6933')  # Equal Area
                    total_area_km2 = overlay_proj.geometry.area.sum() / 1e6
                else:
                    total_area_km2 = overlay_result.geometry.area.sum() / 1e6
                stats['total_area_km2'] = float(total_area_km2)
        
        result['statistics'] = stats
        
        # Create visualization
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        if len(overlay_result) > 0:
            overlay_result.plot(ax=ax, alpha=0.7, edgecolor='black', cmap='viridis')
        else:
            # Plot original datasets if overlay is empty
            gdf1.plot(ax=ax, alpha=0.5, edgecolor='red')
            gdf2.plot(ax=ax, alpha=0.5, edgecolor='blue')

            legend_elements = [
                Patch(facecolor='none', edgecolor='red', label='GDF1'),
                Patch(facecolor='none', edgecolor='blue', label='GDF2')
            ]
            ax.legend(handles=legend_elements)
        ax.set_title(f"Overlay Result: {overlay_how.title()}", fontsize=14)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        plt.tight_layout()
        
    else:
        # Visualization only (no overlay)
        result['statistics'] = {
            'feature_count': len(gdf1),
            'geometry_types': gdf1.geometry.geom_type.unique().tolist()
        }
        
        # Create visualization
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        gdf1.plot(ax=ax, alpha=0.7, edgecolor='black', cmap='viridis')
        ax.set_title("Spatial Data Visualization", fontsize=14)
        ax.set_xlabel('Longitude')
        ax.set_ylabel('Latitude')
        plt.tight_layout()
    
    result['figure'] = fig
    
    # Save figure if path provided
    if save_path:
        save_path = Path(save_path)
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        result['saved_path'] = str(save_path)
    
    return result


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
