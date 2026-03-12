"""
GIST 604B - GeoPandas Spatial Operations
Test Suite for 7 Core Functions (15 Points)

This test suite validates implementations of essential spatial operations:
I/O → Explore → Transform → Operate → Analyze → Visualize

Uses real spatial datasets:
- Natural Earth Cities (281 US cities)
- EPA Level III Ecoregions (12 Western US ecoregions)
- National Parks (10 major US national parks)

Test Structure (matching grading):
1. load_spatial_data (2 pts)
2. explore_properties (2 pts)
3. transform_crs (2 pts)
4. geometry_operations (3 pts) - buffer, centroid, area, length, simplify
5. spatial_relationships (2 pts) - intersects, contains, within, distance
6. spatial_joins (2 pts)
7. overlay_and_visualize (2 pts)

Author: GIST 604B Course Team
"""

import pytest
import geopandas as gpd
import pandas as pd
import numpy as np
from pathlib import Path
import tempfile
import json
import warnings
from shapely.geometry import Point, LineString, Polygon
from shapely import wkt
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for testing
import matplotlib.pyplot as plt

# Import the functions to test
from src.spatial_basics import (
    load_spatial_data,
    explore_properties,
    transform_crs,
    geometry_operations,
    spatial_relationships,
    spatial_joins,
    overlay_and_visualize
)


# ============================================================================
# SHARED FIXTURES - Real Data Paths
# ============================================================================

@pytest.fixture(scope="session")
def data_dir():
    """Path to data directory with real datasets."""
    return Path(__file__).parent.parent / "data"


@pytest.fixture(scope="session")
def cities_file(data_dir):
    """Path to Natural Earth cities GeoJSON (281 US cities)."""
    file_path = data_dir / "cities" / "ne_cities_us.geojson"
    if not file_path.exists():
        pytest.skip(f"Cities data file not found: {file_path}")
    return file_path


@pytest.fixture(scope="session")
def ecoregions_file(data_dir):
    """Path to EPA Level III ecoregions GeoJSON (12 Western US ecoregions)."""
    file_path = data_dir / "ecoregions" / "epa_level3_western_us.geojson"
    if not file_path.exists():
        pytest.skip(f"Ecoregions data file not found: {file_path}")
    return file_path


@pytest.fixture(scope="session")
def parks_file(data_dir):
    """Path to National Parks GeoJSON (10 major US national parks)."""
    file_path = data_dir / "protected_areas" / "national_parks_major.geojson"
    if not file_path.exists():
        pytest.skip(f"Parks data file not found: {file_path}")
    return file_path


@pytest.fixture
def cities_gdf(cities_file):
    """Loaded cities GeoDataFrame."""
    return gpd.read_file(cities_file)


@pytest.fixture
def ecoregions_gdf(ecoregions_file):
    """Loaded ecoregions GeoDataFrame."""
    return gpd.read_file(ecoregions_file)


@pytest.fixture
def parks_gdf(parks_file):
    """Loaded parks GeoDataFrame."""
    return gpd.read_file(parks_file)


# ============================================================================
# TEST CLASS 1: Load Spatial Data (2 points)
# ============================================================================

class TestLoadSpatialData:
    """Test suite for load_spatial_data function (2 points)."""

    def test_load_geojson_basic(self, cities_file):
        """Test basic GeoJSON loading with real cities data."""
        result = load_spatial_data(cities_file)

        # Should return a GeoDataFrame
        assert isinstance(result, gpd.GeoDataFrame), "Must return GeoDataFrame"

        # Should have expected number of features (281 cities)
        assert len(result) > 250, "Should load ~281 US cities"

        # Should have geometry column
        assert 'geometry' in result.columns, "Must have geometry column"

        # Should have valid geometries
        assert result.geometry.is_valid.all(), "All geometries must be valid"

        # Cities should be Point geometries
        assert all(geom.geom_type == 'Point' for geom in result.geometry), \
            "Cities should all be Point geometries"

    def test_load_polygon_data(self, ecoregions_file):
        """Test loading polygon data (ecoregions)."""
        result = load_spatial_data(ecoregions_file)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 10, "Should load ~12 ecoregions"

        # Ecoregions should be Polygon or MultiPolygon
        geom_types = set(result.geometry.geom_type)
        assert geom_types.issubset({'Polygon', 'MultiPolygon'}), \
            "Ecoregions should be Polygon/MultiPolygon"

    def test_load_with_path_object(self, cities_file):
        """Test loading with Path object instead of string."""
        path_obj = Path(cities_file)
        result = load_spatial_data(path_obj)

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 250

    def test_load_with_string_path(self, cities_file):
        """Test loading with string path."""
        result = load_spatial_data(str(cities_file))

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) > 250

    def test_file_not_found_error(self, data_dir):
        """Test that FileNotFoundError is raised for non-existent files."""
        non_existent_file = data_dir / "does_not_exist.geojson"

        with pytest.raises(FileNotFoundError):
            load_spatial_data(non_existent_file)

    def test_invalid_file_format(self, tmp_path):
        """Test handling of invalid file formats."""
        invalid_file = tmp_path / "invalid.txt"
        with open(invalid_file, 'w') as f:
            f.write("This is not spatial data")

        with pytest.raises(ValueError):
            load_spatial_data(invalid_file)

    def test_crs_preserved(self, cities_file):
        """Test that CRS is preserved when loading."""
        result = load_spatial_data(cities_file)

        assert result.crs is not None, "Loaded data must have CRS"
        # Natural Earth data should be in WGS84 (EPSG:4326)
        assert result.crs.to_epsg() == 4326, "Cities should be in EPSG:4326"


# ============================================================================
# TEST CLASS 2: Explore Properties (2 points)
# ============================================================================

class TestExploreProperties:
    """Test suite for explore_properties function (2 points)."""

    def test_basic_properties_extraction(self, cities_gdf):
        """Test basic property extraction from cities data."""
        result = explore_properties(cities_gdf)

        # Should return a dictionary
        assert isinstance(result, dict), "Must return dictionary"

        # Should have required keys
        required_keys = {'crs', 'bounds', 'geometry_types', 'feature_count'}
        assert required_keys.issubset(set(result.keys())), \
            f"Missing required keys. Expected: {required_keys}, Got: {set(result.keys())}"

    def test_crs_information(self, cities_gdf):
        """Test CRS information extraction."""
        result = explore_properties(cities_gdf)

        assert 'crs' in result
        # Should identify WGS84
        crs_info = str(result['crs'])
        assert '4326' in crs_info or 'WGS 84' in crs_info or 'EPSG:4326' in crs_info, \
            f"Should identify EPSG:4326, got: {crs_info}"

    def test_bounds_calculation(self, cities_gdf):
        """Test spatial bounds calculation."""
        result = explore_properties(cities_gdf)

        assert 'bounds' in result
        bounds = result['bounds']

        # Bounds should be a tuple/list of 4 values (minx, miny, maxx, maxy)
        assert len(bounds) == 4, "Bounds should have 4 values"

        minx, miny, maxx, maxy = bounds
        assert minx < maxx, "minx should be less than maxx"
        assert miny < maxy, "miny should be less than maxy"

        # US cities should be in reasonable coordinate ranges (includes Alaska/Hawaii)
        assert -180 < minx < -65, f"US cities minx should be ~-180 to -65, got {minx}"
        assert 18 < miny < 72, f"US cities miny should be ~18 to 72, got {miny}"
        assert -180 < maxx < -65, f"US cities maxx should be ~-180 to -65, got {maxx}"
        assert 18 < maxy < 72, f"US cities maxy should be ~18 to 72, got {maxy}"

    def test_geometry_types_identification(self, cities_gdf):
        """Test geometry types identification."""
        result = explore_properties(cities_gdf)

        assert 'geometry_types' in result
        geom_types = result['geometry_types']

        # Should find Point geometries
        if isinstance(geom_types, list):
            assert 'Point' in geom_types, "Cities should contain Point geometries"
        elif isinstance(geom_types, dict):
            assert 'Point' in geom_types.keys(), "Cities should contain Point geometries"
        else:
            pytest.fail(f"Unexpected geometry_types format: {type(geom_types)}")

    def test_feature_count(self, cities_gdf):
        """Test feature count reporting."""
        result = explore_properties(cities_gdf)

        assert 'feature_count' in result
        # Should match actual length
        assert result['feature_count'] == len(cities_gdf), \
            f"Feature count mismatch: {result['feature_count']} vs {len(cities_gdf)}"
        assert result['feature_count'] > 250, "Should report ~281 cities"

    def test_polygon_properties(self, ecoregions_gdf):
        """Test property extraction for polygon data."""
        result = explore_properties(ecoregions_gdf)

        assert isinstance(result, dict)
        assert result['feature_count'] > 10

        # Should identify Polygon/MultiPolygon types
        geom_types = result['geometry_types']
        if isinstance(geom_types, list):
            assert any(gt in ['Polygon', 'MultiPolygon'] for gt in geom_types)
        elif isinstance(geom_types, dict):
            assert any(gt in ['Polygon', 'MultiPolygon'] for gt in geom_types.keys())

    def test_empty_geodataframe(self):
        """Test handling of empty GeoDataFrame."""
        empty_gdf = gpd.GeoDataFrame(columns=['geometry'], crs='EPSG:4326')

        result = explore_properties(empty_gdf)

        assert isinstance(result, dict)
        assert result['feature_count'] == 0
        assert len(result['bounds']) == 4  # Should still return bounds (may be NaN/empty)


# ============================================================================
# TEST CLASS 3: Transform CRS (2 points)
# ============================================================================

class TestTransformCRS:
    """Test suite for transform_crs function (2 points)."""

    def test_transform_to_web_mercator(self, cities_gdf):
        """Test transformation to Web Mercator (EPSG:3857)."""
        result = transform_crs(cities_gdf, 'EPSG:3857')

        # Should return GeoDataFrame
        assert isinstance(result, gpd.GeoDataFrame), "Must return GeoDataFrame"

        # Should have correct target CRS
        assert result.crs.to_epsg() == 3857, "Should transform to EPSG:3857"

        # Should have same number of features
        assert len(result) == len(cities_gdf), "Feature count should be preserved"

        # Coordinates should be different (transformed)
        orig_coords = [(geom.x, geom.y) for geom in cities_gdf.geometry.head(5)]
        new_coords = [(geom.x, geom.y) for geom in result.geometry.head(5)]
        assert orig_coords != new_coords, "Coordinates should change after transformation"

        # Web Mercator coordinates should be much larger
        assert all(abs(x) > 1000 for x, y in new_coords), \
            "Web Mercator X coordinates should be large"

    def test_transform_with_integer_epsg(self, cities_gdf):
        """Test CRS transformation with integer EPSG code."""
        result = transform_crs(cities_gdf, 3857)

        assert isinstance(result, gpd.GeoDataFrame)
        assert result.crs.to_epsg() == 3857

    def test_transform_to_utm(self, cities_gdf):
        """Test transformation to UTM projection."""
        # UTM Zone 11N for Western US (EPSG:32611)
        result = transform_crs(cities_gdf, 'EPSG:32611')

        assert result.crs.to_epsg() == 32611
        assert len(result) == len(cities_gdf)

        # UTM coordinates should be large numbers
        sample_coords = [(geom.x, geom.y) for geom in result.geometry.head(5)]
        assert all(x > 100000 for x, y in sample_coords), \
            "UTM X coordinates should be large"

    def test_no_transformation_needed(self, cities_gdf):
        """Test when data is already in target CRS."""
        # Cities are already in EPSG:4326
        result = transform_crs(cities_gdf, 'EPSG:4326')

        assert result.crs.to_epsg() == 4326
        assert len(result) == len(cities_gdf)

        # Coordinates should be essentially the same
        orig_coords = list(cities_gdf.geometry.head(5))
        new_coords = list(result.geometry.head(5))
        for orig, new in zip(orig_coords, new_coords):
            assert abs(orig.x - new.x) < 1e-9
            assert abs(orig.y - new.y) < 1e-9

    def test_missing_crs_handling(self):
        """Test handling of GeoDataFrame with missing CRS."""
        # Create GeoDataFrame without CRS
        no_crs_gdf = gpd.GeoDataFrame({
            'geometry': [Point(-120, 45), Point(-118, 46)]
        })

        # Should raise ValueError or handle gracefully
        with pytest.raises(ValueError):
            transform_crs(no_crs_gdf, 'EPSG:3857')

    def test_invalid_target_crs(self, cities_gdf):
        """Test handling of invalid target CRS."""
        with pytest.raises((ValueError, Exception)):
            transform_crs(cities_gdf, 'INVALID:9999')

    def test_geometry_validity_preserved(self, ecoregions_gdf):
        """Test that geometries remain valid after transformation."""
        result = transform_crs(ecoregions_gdf, 'EPSG:3857')

        # All geometries should still be valid
        assert result.geometry.is_valid.all(), \
            "All geometries must remain valid after transformation"

        # Should preserve geometry types
        orig_types = set(ecoregions_gdf.geometry.geom_type)
        new_types = set(result.geometry.geom_type)
        assert orig_types == new_types, "Geometry types should be preserved"


# ============================================================================
# TEST CLASS 4: Geometry Operations (3 points)
# ============================================================================

class TestGeometryOperations:
    """Test suite for geometry_operations function (3 points)."""

    def test_buffer_operation(self, cities_gdf):
        """Test buffer operation with distance parameter."""
        # Project to UTM for metric buffer (1000m = 1km)
        cities_utm = cities_gdf.to_crs('EPSG:32611')  # UTM Zone 11N

        result = geometry_operations(cities_utm, operation='buffer', distance=1000)

        # Should return dictionary
        assert isinstance(result, dict), "Must return dictionary"

        # Should have required keys
        assert 'result' in result, "Must have 'result' key"
        assert 'operation' in result, "Must have 'operation' key"

        # Result should be GeoDataFrame
        buffered = result['result']
        assert isinstance(buffered, gpd.GeoDataFrame), "Result must be GeoDataFrame"

        # Should have same number of features
        assert len(buffered) == len(cities_utm), "Feature count should be preserved"

        # Buffered geometries should be polygons
        assert all(geom.geom_type in ['Polygon', 'MultiPolygon'] 
                   for geom in buffered.geometry), \
            "Buffered points should become polygons"

    def test_centroid_operation(self, ecoregions_gdf):
        """Test centroid calculation on polygons."""
        result = geometry_operations(ecoregions_gdf, operation='centroid')

        assert isinstance(result, dict)
        assert 'result' in result

        centroids = result['result']
        assert isinstance(centroids, gpd.GeoDataFrame)
        assert len(centroids) == len(ecoregions_gdf)

        # Centroids should be points
        assert all(geom.geom_type == 'Point' for geom in centroids.geometry), \
            "Centroids must be Point geometries"

    def test_area_operation(self, ecoregions_gdf):
        """Test area calculation on polygons."""
        # Project to UTM for accurate area calculation
        ecoregions_utm = ecoregions_gdf.to_crs('EPSG:32611')

        result = geometry_operations(ecoregions_utm, operation='area')

        assert isinstance(result, dict)
        assert 'result' in result
        assert 'statistics' in result, "Should include statistics"

        areas_gdf = result['result']
        assert isinstance(areas_gdf, gpd.GeoDataFrame)

        # Should have area information (either as column or in statistics)
        stats = result['statistics']
        assert 'total_area' in stats or 'mean_area' in stats or 'areas' in stats, \
            "Should provide area statistics"

    def test_length_operation(self):
        """Test length calculation on lines."""
        # Create simple line data
        lines = gpd.GeoDataFrame({
            'name': ['Line1', 'Line2'],
            'geometry': [
                LineString([(-120, 45), (-119, 45)]),
                LineString([(-118, 46), (-117, 46)])
            ]
        }, crs='EPSG:4326')

        # Project to UTM for metric length
        lines_utm = lines.to_crs('EPSG:32611')

        result = geometry_operations(lines_utm, operation='length')

        assert isinstance(result, dict)
        assert 'result' in result

        # Should include length information
        assert 'statistics' in result, "Should include length statistics"

    def test_simplify_operation(self, ecoregions_gdf):
        """Test geometry simplification."""
        result = geometry_operations(ecoregions_gdf, operation='simplify', tolerance=0.01)

        assert isinstance(result, dict)
        assert 'result' in result

        simplified = result['result']
        assert isinstance(simplified, gpd.GeoDataFrame)
        assert len(simplified) == len(ecoregions_gdf)

        # Simplified geometries should have fewer vertices
        # (hard to test precisely, but should at least work)
        assert simplified.geometry.is_valid.all(), \
            "Simplified geometries must be valid"

    def test_invalid_operation(self, cities_gdf):
        """Test handling of invalid operation."""
        with pytest.raises(ValueError):
            geometry_operations(cities_gdf, operation='invalid_operation')

    def test_missing_required_parameter(self, cities_gdf):
        """Test handling of missing required parameters."""
        # Buffer requires distance parameter
        with pytest.raises((ValueError, TypeError)):
            geometry_operations(cities_gdf, operation='buffer')  # No distance


# ============================================================================
# TEST CLASS 5: Spatial Relationships (2 points)
# ============================================================================

class TestSpatialRelationships:
    """Test suite for spatial_relationships function (2 points)."""

    def test_intersects_relationship(self, cities_gdf, ecoregions_gdf):
        """Test intersects relationship between cities and ecoregions."""
        # Ensure same CRS
        cities = cities_gdf.head(50)  # Use subset for faster testing
        ecoregions = ecoregions_gdf

        result = spatial_relationships(cities, ecoregions, relationship='intersects')

        # Should return dictionary
        assert isinstance(result, dict), "Must return dictionary"

        # Should have required keys
        assert 'relationship' in result, "Must have 'relationship' key"
        assert 'count' in result, "Must have 'count' key"
        assert result['relationship'] == 'intersects', "Should record relationship type"

        # Some cities should intersect ecoregions
        assert result['count'] >= 0, "Count should be non-negative"

    def test_contains_relationship(self, ecoregions_gdf, cities_gdf):
        """Test contains relationship (ecoregions contain cities)."""
        ecoregions = ecoregions_gdf.head(5)
        cities = cities_gdf.head(20)

        result = spatial_relationships(ecoregions, cities, relationship='contains')

        assert isinstance(result, dict)
        assert 'relationship' in result
        assert result['relationship'] == 'contains'
        assert 'count' in result

    def test_within_relationship(self, cities_gdf, ecoregions_gdf):
        """Test within relationship (cities within ecoregions)."""
        cities = cities_gdf.head(20)
        ecoregions = ecoregions_gdf.head(5)

        result = spatial_relationships(cities, ecoregions, relationship='within')

        assert isinstance(result, dict)
        assert 'relationship' in result
        assert result['relationship'] == 'within'

    def test_distance_calculation(self, cities_gdf):
        """Test distance calculation between features."""
        # Take two small subsets for pairwise distance
        cities_west = cities_gdf.head(10)
        cities_east = cities_gdf.tail(10)

        result = spatial_relationships(cities_west, cities_east, relationship='distance')

        assert isinstance(result, dict)
        assert 'relationship' in result
        assert result['relationship'] == 'distance'

        # Should have distance results
        assert 'results' in result or 'distances' in result, \
            "Should provide distance measurements"

    def test_crs_mismatch_handling(self, cities_gdf, ecoregions_gdf):
        """Test handling of CRS mismatches."""
        # Transform one dataset to different CRS
        cities_mercator = cities_gdf.to_crs('EPSG:3857')

        # Function should either:
        # 1. Handle CRS mismatch by transforming, or
        # 2. Raise ValueError
        try:
            result = spatial_relationships(cities_mercator, ecoregions_gdf, 
                                          relationship='intersects')
            # If it succeeds, should return valid result
            assert isinstance(result, dict)
        except ValueError as e:
            # Or it should raise ValueError about CRS mismatch
            assert 'crs' in str(e).lower() or 'coordinate' in str(e).lower()

    def test_invalid_relationship_type(self, cities_gdf, ecoregions_gdf):
        """Test handling of invalid relationship type."""
        with pytest.raises(ValueError):
            spatial_relationships(cities_gdf, ecoregions_gdf, 
                                relationship='invalid_relationship')


# ============================================================================
# TEST CLASS 6: Spatial Joins (2 points)
# ============================================================================

class TestSpatialJoins:
    """Test suite for spatial_joins function (2 points)."""

    def test_inner_join_intersects(self, cities_gdf, ecoregions_gdf):
        """Test inner spatial join with intersects predicate."""
        cities = cities_gdf.head(50)  # Subset for faster testing

        result = spatial_joins(cities, ecoregions_gdf, 
                             how='inner', predicate='intersects')

        # Should return GeoDataFrame
        assert isinstance(result, gpd.GeoDataFrame), "Must return GeoDataFrame"

        # Should have features (cities that intersect ecoregions)
        assert len(result) > 0, "Should have at least some joined features"

        # Should preserve left geometry (cities)
        assert all(geom.geom_type == 'Point' for geom in result.geometry), \
            "Should preserve left (cities) geometry"

        # Should have columns from both datasets
        # (exact column names vary, but should have more columns than original)
        assert len(result.columns) >= len(cities.columns), \
            "Should have attributes from both datasets"

    def test_left_join(self, cities_gdf, ecoregions_gdf):
        """Test left spatial join."""
        cities = cities_gdf.head(30)

        result = spatial_joins(cities, ecoregions_gdf, 
                             how='left', predicate='within')

        assert isinstance(result, gpd.GeoDataFrame)

        # Left join should preserve all left features
        assert len(result) >= len(cities), \
            "Left join should preserve all left features"

    def test_within_predicate(self, cities_gdf, ecoregions_gdf):
        """Test spatial join with 'within' predicate."""
        cities = cities_gdf.head(40)

        result = spatial_joins(cities, ecoregions_gdf, 
                             how='inner', predicate='within')

        assert isinstance(result, gpd.GeoDataFrame)
        assert len(result) >= 0  # May have zero results, that's OK

    def test_join_preserves_crs(self, cities_gdf, ecoregions_gdf):
        """Test that spatial join preserves CRS of left GeoDataFrame."""
        cities = cities_gdf.head(20)

        result = spatial_joins(cities, ecoregions_gdf, 
                             how='inner', predicate='intersects')

        assert result.crs is not None, "Result must have CRS"
        assert result.crs == cities.crs, "Should preserve left CRS"

    def test_crs_compatibility_check(self, cities_gdf, ecoregions_gdf):
        """Test handling of CRS mismatches."""
        cities_mercator = cities_gdf.head(20).to_crs('EPSG:3857')

        # Should either handle transformation or raise error
        try:
            result = spatial_joins(cities_mercator, ecoregions_gdf, 
                                 how='inner', predicate='intersects')
            assert isinstance(result, gpd.GeoDataFrame)
        except ValueError as e:
            assert 'crs' in str(e).lower() or 'coordinate' in str(e).lower()

    def test_invalid_predicate(self, cities_gdf, ecoregions_gdf):
        """Test handling of invalid spatial predicate."""
        with pytest.raises(ValueError):
            spatial_joins(cities_gdf, ecoregions_gdf, 
                        how='inner', predicate='invalid_predicate')


# ============================================================================
# TEST CLASS 7: Overlay and Visualize (2 points)
# ============================================================================

class TestOverlayAndVisualize:
    """Test suite for overlay_and_visualize function (2 points)."""

    def test_intersection_overlay(self, ecoregions_gdf, parks_gdf):
        """Test intersection overlay between two polygon layers."""
        # Use subsets for faster testing
        ecoregions = ecoregions_gdf.head(5)
        parks = parks_gdf.head(5)

        result = overlay_and_visualize(ecoregions, parks, 
                                      overlay_how='intersection')

        # Should return dictionary
        assert isinstance(result, dict), "Must return dictionary"

        # Should have overlay result
        assert 'overlay_result' in result, "Must have 'overlay_result' key"

        overlay_result = result['overlay_result']
        assert isinstance(overlay_result, gpd.GeoDataFrame), \
            "Overlay result must be GeoDataFrame"

        # Intersection should have some features (or zero if no overlap)
        assert len(overlay_result) >= 0, "Should return overlay result"

    def test_union_overlay(self, ecoregions_gdf, parks_gdf):
        """Test union overlay operation."""
        ecoregions = ecoregions_gdf.head(3)
        parks = parks_gdf.head(3)

        result = overlay_and_visualize(ecoregions, parks, 
                                      overlay_how='union')

        assert isinstance(result, dict)
        assert 'overlay_result' in result

        overlay_result = result['overlay_result']
        assert isinstance(overlay_result, gpd.GeoDataFrame)

    def test_difference_overlay(self, ecoregions_gdf, parks_gdf):
        """Test difference overlay operation."""
        ecoregions = ecoregions_gdf.head(3)
        parks = parks_gdf.head(3)

        result = overlay_and_visualize(ecoregions, parks, 
                                      overlay_how='difference')

        assert isinstance(result, dict)
        assert 'overlay_result' in result

        overlay_result = result['overlay_result']
        assert isinstance(overlay_result, gpd.GeoDataFrame)

    def test_visualization_only(self, cities_gdf):
        """Test visualization without overlay (single layer)."""
        cities = cities_gdf.head(50)

        result = overlay_and_visualize(cities, gdf2=None)

        # Should return dictionary
        assert isinstance(result, dict)

        # Should have figure object
        assert 'figure' in result, "Should create visualization"

        # Close figure to free memory
        if 'figure' in result and result['figure'] is not None:
            plt.close(result['figure'])

    def test_statistics_included(self, ecoregions_gdf, parks_gdf):
        """Test that statistics are included in results."""
        ecoregions = ecoregions_gdf.head(3)
        parks = parks_gdf.head(3)

        result = overlay_and_visualize(ecoregions, parks, 
                                      overlay_how='intersection')

        # Should include statistics
        assert 'statistics' in result, "Should include statistics"

        stats = result['statistics']
        assert isinstance(stats, dict), "Statistics should be dictionary"

    def test_save_visualization(self, cities_gdf, tmp_path):
        """Test saving visualization to file."""
        cities = cities_gdf.head(30)
        save_path = tmp_path / "test_map.png"

        result = overlay_and_visualize(cities, gdf2=None, save_path=save_path)

        assert isinstance(result, dict)

        # File should be created
        assert save_path.exists(), "Visualization file should be saved"

        # Clean up
        if 'figure' in result and result['figure'] is not None:
            plt.close(result['figure'])

    def test_invalid_overlay_operation(self, ecoregions_gdf, parks_gdf):
        """Test handling of invalid overlay operation."""
        with pytest.raises(ValueError):
            overlay_and_visualize(ecoregions_gdf, parks_gdf, 
                                overlay_how='invalid_operation')

    def test_crs_compatibility(self, cities_gdf, ecoregions_gdf):
        """Test handling of CRS compatibility in overlays."""
        cities_mercator = cities_gdf.head(10).to_crs('EPSG:3857')
        ecoregions = ecoregions_gdf.head(3)

        # Should either handle CRS mismatch or raise error
        try:
            # Note: overlay requires polygon/polygon, so buffer cities first
            cities_buffered = cities_mercator.copy()
            cities_buffered.geometry = cities_buffered.geometry.buffer(1000)

            result = overlay_and_visualize(cities_buffered, ecoregions, 
                                          overlay_how='intersection')
            assert isinstance(result, dict)
        except (ValueError, Exception) as e:
            # Expected if CRS mismatch not handled
            assert 'crs' in str(e).lower() or 'coordinate' in str(e).lower() or \
                   'overlay' in str(e).lower()


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestIntegrationWorkflows:
    """Integration tests combining multiple functions."""

    def test_complete_workflow(self, cities_file, ecoregions_file):
        """Test complete workflow: Load → Explore → Transform → Join → Visualize."""

        # Step 1: Load data
        cities = load_spatial_data(cities_file)
        ecoregions = load_spatial_data(ecoregions_file)
        assert isinstance(cities, gpd.GeoDataFrame)
        assert isinstance(ecoregions, gpd.GeoDataFrame)

        # Step 2: Explore properties
        cities_props = explore_properties(cities)
        eco_props = explore_properties(ecoregions)
        assert cities_props['feature_count'] > 250
        assert eco_props['feature_count'] > 10

        # Step 3: Transform to common projection (UTM)
        cities_utm = transform_crs(cities.head(50), 'EPSG:32611')
        eco_utm = transform_crs(ecoregions, 'EPSG:32611')
        assert cities_utm.crs.to_epsg() == 32611
        assert eco_utm.crs.to_epsg() == 32611

        # Step 4: Spatial join
        joined = spatial_joins(cities_utm, eco_utm, 
                             how='inner', predicate='within')
        assert isinstance(joined, gpd.GeoDataFrame)

        # Step 5: Visualize (without saving)
        result = overlay_and_visualize(joined, gdf2=None)
        assert 'figure' in result

        # Clean up
        if result['figure'] is not None:
            plt.close(result['figure'])

    def test_buffer_and_overlay_workflow(self, cities_file, parks_file):
        """Test workflow: Load → Transform → Buffer → Overlay."""

        # Load data
        cities = load_spatial_data(cities_file)
        parks = load_spatial_data(parks_file)

        # Transform to UTM for buffering
        cities_utm = transform_crs(cities.head(20), 'EPSG:32611')
        parks_utm = transform_crs(parks.head(5), 'EPSG:32611')

        # Buffer cities to create polygons
        buffer_result = geometry_operations(cities_utm, 
                                           operation='buffer', 
                                           distance=5000)
        cities_buffered = buffer_result['result']

        # Overlay buffered cities with parks
        overlay_result = overlay_and_visualize(cities_buffered, parks_utm, 
                                              overlay_how='intersection')
        assert 'overlay_result' in overlay_result

        # Clean up
        if 'figure' in overlay_result and overlay_result['figure'] is not None:
            plt.close(overlay_result['figure'])


# ============================================================================
# EDGE CASES
# ============================================================================

class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_empty_geodataframe(self):
        """Test functions with empty GeoDataFrame."""
        empty_gdf = gpd.GeoDataFrame(columns=['geometry'], crs='EPSG:4326')

        # Explore properties
        props = explore_properties(empty_gdf)
        assert props['feature_count'] == 0

        # Transform CRS
        transformed = transform_crs(empty_gdf, 'EPSG:3857')
        assert len(transformed) == 0
        assert transformed.crs.to_epsg() == 3857

    def test_single_feature(self):
        """Test functions with single feature."""
        single_gdf = gpd.GeoDataFrame({
            'name': ['Single'],
            'geometry': [Point(-120, 45)]
        }, crs='EPSG:4326')

        props = explore_properties(single_gdf)
        assert props['feature_count'] == 1

        transformed = transform_crs(single_gdf, 'EPSG:3857')
        assert len(transformed) == 1

    def test_very_small_geometries(self):
        """Test handling of very small geometries."""
        tiny_gdf = gpd.GeoDataFrame({
            'name': ['Tiny'],
            'geometry': [Point(-120.0000001, 45.0000001)]
        }, crs='EPSG:4326')

        props = explore_properties(tiny_gdf)
        assert props['feature_count'] == 1

        transformed = transform_crs(tiny_gdf, 'EPSG:3857')
        assert transformed.geometry.is_valid.all()
