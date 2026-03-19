"""
Unit Tests for Pandas Basics Assignment
=======================================

This file contains professional unit tests using pytest to verify that your
pandas functions work correctly.

Learning Objectives:
- Understand how unit tests work in professional development
- Learn pytest framework and assertions
- Practice test-driven development (TDD) principles
- See how to test data analysis functions

Run these tests with:
    pytest tests/test_pandas_basics.py -v

Individual test class:
    pytest tests/test_pandas_basics.py::TestLoadAndExploreGISData -v

Individual test method:
    pytest tests/test_pandas_basics.py::TestLoadAndExploreGISData::test_loads_csv_successfully -v

Debug failing tests:
    pytest tests/test_pandas_basics.py::TestLoadAndExploreGISData::test_loads_csv_successfully --pdb
"""

import pytest
import pandas as pd
import numpy as np
import os
import tempfile
import shutil
from pathlib import Path

# Import the functions we want to test
import sys
sys.path.insert(0, 'src')

try:
    from pandas_basics import (
        load_and_explore_gis_data,
        filter_environmental_data,
        calculate_station_statistics,
        join_station_data
    )
except ImportError as e:
    pytest.fail(f"Cannot import functions from src.pandas_basics: {e}")


# ==============================================================================
# PYTEST FIXTURES - Reusable test data
# ==============================================================================

@pytest.fixture
def sample_stations_csv(tmp_path):
    """
    Create a temporary CSV file with sample station data.

    This is a pytest 'fixture' - a way to create reusable test data.
    The tmp_path fixture automatically creates a temporary directory.
    """
    csv_data = """station_id,station_name,latitude,longitude,elevation_m,station_type
STN_001,Central Park,40.7829,-73.9654,35,meteorological
STN_002,Times Square,40.7580,-73.9855,10,air_quality
STN_003,Brooklyn Bridge,40.7061,-73.9969,25,meteorological
STN_004,Queens Plaza,40.7505,-73.9370,15,air_quality
STN_005,Staten Island,40.5795,-74.1502,45,meteorological"""

    csv_file = tmp_path / "test_stations.csv"
    csv_file.write_text(csv_data)
    return str(csv_file)


@pytest.fixture
def sample_stations_df():
    """Create a sample stations DataFrame for testing."""
    return pd.DataFrame({
        'station_id': ['STN_001', 'STN_002', 'STN_003', 'STN_004', 'STN_005'],
        'station_name': ['Central Park', 'Times Square', 'Brooklyn Bridge', 'Queens Plaza', 'Staten Island'],
        'latitude': [40.7829, 40.7580, 40.7061, 40.7505, 40.5795],
        'longitude': [-73.9654, -73.9855, -73.9969, -73.9370, -74.1502],
        'elevation_m': [35, 10, 25, 15, 45],
        'station_type': ['meteorological', 'air_quality', 'meteorological', 'air_quality', 'meteorological']
    })


@pytest.fixture
def sample_readings_df():
    """Create a sample temperature readings DataFrame for testing."""
    np.random.seed(42)  # For reproducible test data
    return pd.DataFrame({
        'station_id': ['STN_001'] * 4 + ['STN_002'] * 4 + ['STN_003'] * 2,
        'date': ['2023-01-15', '2023-01-16', '2023-01-17', '2023-01-18'] * 2 + ['2023-01-15', '2023-01-16'],
        'temperature_c': [20.0, 35.0, 25.0, 5.0, 22.0, 18.0, 24.0, 27.0, 19.0, 21.0],
        'humidity_percent': [60.0, 45.0, 65.0, 50.0, 62.0, 55.0, 70.0, 75.0, 58.0, 63.0],
        'data_quality': ['good', 'poor', 'good', 'good', 'good', 'good', 'good', 'fair', 'good', 'good']
    })


# ==============================================================================
# UNIT TESTS FOR EACH FUNCTION
# ==============================================================================

class TestLoadAndExploreGISData:
    """
    Test class for load_and_explore_gis_data function.

    Grouping related tests in classes is a pytest best practice.
    """

    def test_loads_csv_successfully(self, sample_stations_csv):
        """Test that function can load a CSV file and return a DataFrame."""
        result = load_and_explore_gis_data(sample_stations_csv)

        # Assert that we get a pandas DataFrame
        assert isinstance(result, pd.DataFrame), "Function should return a pandas DataFrame"

        # Assert correct dimensions
        assert len(result) == 5, "Should load 5 rows of data"
        assert len(result.columns) == 6, "Should have 6 columns"

    def test_has_correct_columns(self, sample_stations_csv):
        """Test that loaded DataFrame has the expected columns."""
        result = load_and_explore_gis_data(sample_stations_csv)

        expected_columns = ['station_id', 'station_name', 'latitude', 'longitude', 'elevation_m', 'station_type']
        assert list(result.columns) == expected_columns, f"Columns should be {expected_columns}"

    def test_handles_missing_file_gracefully(self):
        """Test that function handles missing files appropriately."""
        result = load_and_explore_gis_data('nonexistent_file.csv')

        # Function should return None for missing files
        assert result is None, "Should return None for missing files"

    def test_data_types_are_correct(self, sample_stations_csv):
        """Test that numeric columns are loaded as numeric types."""
        result = load_and_explore_gis_data(sample_stations_csv)

        # Check that numeric columns are actually numeric
        assert pd.api.types.is_numeric_dtype(result['latitude']), "Latitude should be numeric"
        assert pd.api.types.is_numeric_dtype(result['longitude']), "Longitude should be numeric"
        assert pd.api.types.is_numeric_dtype(result['elevation_m']), "Elevation should be numeric"


class TestFilterEnvironmentalData:
    """Test class for filter_environmental_data function."""

    def test_filters_by_temperature_range(self, sample_readings_df):
        """Test that function correctly filters by temperature range."""
        result = filter_environmental_data(sample_readings_df, min_temp=15, max_temp=30, quality='good')

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"

        # All temperatures should be within range
        if not result.empty:
            assert all(result['temperature_c'] >= 15), "All temperatures should be >= 15"
            assert all(result['temperature_c'] <= 30), "All temperatures should be <= 30"

    def test_filters_by_quality(self, sample_readings_df):
        """Test that function correctly filters by data quality."""
        result = filter_environmental_data(sample_readings_df, min_temp=0, max_temp=50, quality='good')

        if not result.empty:
            assert all(result['data_quality'] == 'good'), "All records should have 'good' quality"

    def test_returns_correct_count(self, sample_readings_df):
        """Test that filtering returns expected number of rows."""
        # With our test data: temp 15-30 AND quality='good' should keep specific rows
        result = filter_environmental_data(sample_readings_df, min_temp=15, max_temp=30, quality='good')

        # Count manually: temp 20,25,22,18,24,27,19,21 AND quality 'good'
        # Expected: 20,25,22,18,24,19,21 (7 rows)
        expected_count = 7
        assert len(result) == expected_count, f"Should return {expected_count} rows after filtering"

    def test_handles_empty_dataframe(self):
        """Test function with empty DataFrame."""
        empty_df = pd.DataFrame()
        result = filter_environmental_data(empty_df, min_temp=15, max_temp=30, quality='good')

        assert isinstance(result, pd.DataFrame), "Should return DataFrame even for empty input"
        assert result.empty, "Result should be empty for empty input"

    def test_handles_missing_columns(self):
        """Test function handles DataFrames missing required columns."""
        bad_df = pd.DataFrame({'wrong_column': [1, 2, 3]})
        result = filter_environmental_data(bad_df, min_temp=15, max_temp=30, quality='good')

        # Function should handle this gracefully (return empty DataFrame or raise informative error)
        assert isinstance(result, pd.DataFrame), "Should return DataFrame"
        assert result.empty, "Should return empty DataFrame when required columns are missing"


class TestCalculateStationStatistics:
    """Test class for calculate_station_statistics function."""

    def test_groups_by_station(self, sample_readings_df):
        """Test that function correctly groups data by station."""
        result = calculate_station_statistics(sample_readings_df)

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"

        # Should have one row per unique station
        unique_stations = sample_readings_df['station_id'].nunique()
        assert len(result) == unique_stations, f"Should have {unique_stations} rows (one per station)"

    def test_has_required_columns(self, sample_readings_df):
        """Test that result has all required statistical columns."""
        result = calculate_station_statistics(sample_readings_df)

        required_columns = ['station_id', 'reading_count', 'avg_temperature']
        for col in required_columns:
            assert col in result.columns, f"Result should contain column '{col}'"

    def test_calculations_are_correct(self, sample_readings_df):
        """Test that statistical calculations are mathematically correct."""
        result = calculate_station_statistics(sample_readings_df)

        # Test STN_001 specifically
        stn_001_data = sample_readings_df[sample_readings_df['station_id'] == 'STN_001']
        stn_001_result = result[result['station_id'] == 'STN_001']

        if not stn_001_result.empty:
            expected_avg_temp = round(stn_001_data['temperature_c'].mean(), 1)
            actual_avg_temp = stn_001_result['avg_temperature'].iloc[0]
            assert actual_avg_temp == expected_avg_temp, f"Average temperature calculation incorrect. Expected {expected_avg_temp}, got {actual_avg_temp}"

    def test_reading_count_correct(self, sample_readings_df):
        """Test that reading count is calculated correctly."""
        result = calculate_station_statistics(sample_readings_df)

        # STN_001 should have 4 readings in our test data
        stn_001_result = result[result['station_id'] == 'STN_001']
        if not stn_001_result.empty:
            expected_count = 4
            actual_count = stn_001_result['reading_count'].iloc[0]
            assert actual_count == expected_count, f"Reading count should be {expected_count}, got {actual_count}"


class TestJoinStationData:
    """Test class for join_station_data function."""

    def test_joins_dataframes_successfully(self, sample_stations_df, sample_readings_df):
        """Test that function successfully joins two DataFrames."""
        result = join_station_data(sample_stations_df, sample_readings_df)

        assert isinstance(result, pd.DataFrame), "Should return a DataFrame"

        # Should have same number of rows as readings (left join behavior)
        assert len(result) == len(sample_readings_df), \
            f"Result should have {len(sample_readings_df)} rows (same as readings)"

    def test_adds_station_columns(self, sample_stations_df, sample_readings_df):
        """Test that join adds columns from stations DataFrame."""
        result = join_station_data(sample_stations_df, sample_readings_df)

        # Should have columns from both DataFrames
        original_columns = set(sample_readings_df.columns)
        new_columns = set(result.columns) - original_columns

        assert len(new_columns) > 0, "Should add new columns from stations data"
        assert 'station_name' in result.columns, "Should add station_name column"
        assert 'latitude' in result.columns, "Should add latitude column"

    def test_preserves_all_readings(self, sample_stations_df, sample_readings_df):
        """Test that all readings are preserved in the join."""
        result = join_station_data(sample_stations_df, sample_readings_df)

        # All original station_ids should still be present
        original_station_ids = set(sample_readings_df['station_id'])
        result_station_ids = set(result['station_id'])

        assert original_station_ids == result_station_ids, \
            "All original station IDs should be preserved"

    def test_handles_empty_dataframes(self):
        """Test function behavior with empty DataFrames."""
        empty_df = pd.DataFrame()
        stations_df = pd.DataFrame({'station_id': ['STN_001'], 'name': ['Test']})

        result = join_station_data(stations_df, empty_df)
        assert isinstance(result, pd.DataFrame), "Should handle empty DataFrames gracefully"


# ==============================================================================
# INTEGRATION TESTS - Test functions working together
# ==============================================================================

class TestIntegration:
    """Integration tests that verify functions work together correctly."""

    def test_full_workflow(self, sample_stations_csv, tmp_path):
        """Test complete workflow from loading to saving data."""
        # Step 1: Load data
        stations_df = load_and_explore_gis_data(sample_stations_csv)
        assert stations_df is not None, "Should load stations data"

        # Step 2: Create some readings data for testing
        readings_df = pd.DataFrame({
            'station_id': ['STN_001', 'STN_002', 'STN_003'],
            'temperature_c': [22.0, 25.0, 18.0],
            'humidity_percent': [65.0, 70.0, 60.0],
            'data_quality': ['good', 'good', 'good']
        })

        # Step 3: Filter the data
        filtered_df = filter_environmental_data(readings_df, min_temp=15, max_temp=30, quality='good')
        assert not filtered_df.empty, "Should have filtered data"

        # Step 4: Join with stations
        joined_df = join_station_data(stations_df, filtered_df)
        assert len(joined_df) > 0, "Should have joined data"
        assert 'station_name' in joined_df.columns, "Should have station names after join"

        # Step 5: Calculate statistics
        stats_df = calculate_station_statistics(filtered_df)
        assert len(stats_df) > 0, "Should calculate statistics"


# ==============================================================================
# PYTEST CONFIGURATION AND HELPERS
# ==============================================================================

def test_imports_work():
    """Basic test to ensure all required imports are working."""
    import pandas as pd
    import numpy as np
    assert pd.__version__ is not None, "Pandas should be installed and working"
    assert np.__version__ is not None, "NumPy should be installed and working"


# Custom pytest markers for different types of tests
pytestmark = pytest.mark.filterwarnings("ignore::RuntimeWarning")


# ==============================================================================
# LEARNING NOTES FOR STUDENTS
# ==============================================================================

"""
🎓 LEARNING NOTES: Understanding These Tests

1. **Pytest Fixtures**:
   - Functions decorated with @pytest.fixture create reusable test data
   - tmp_path fixture automatically creates temporary directories for testing

2. **Test Organization**:
   - Tests grouped in classes by function they test
   - Each test function starts with "test_"
   - Descriptive test names explain what is being tested

3. **Assert Statements**:
   - assert condition, "error message if condition fails"
   - These are the actual tests - they pass or fail based on conditions

4. **Test Types**:
   - Unit tests: Test individual functions in isolation
   - Integration tests: Test functions working together
   - Edge case tests: Test with unusual inputs (empty data, missing files)

5. **Running Tests**:
   - pytest tests/ : Run all tests
   - pytest tests/test_pandas_basics.py::TestLoadAndExploreGISData : Run specific class
   - pytest tests/ -v : Verbose output
   - pytest tests/ -s : Show print statements
   - pytest tests/ --pdb : Drop into debugger on failure

6. **Professional Benefits**:
   - Catch bugs early in development
   - Ensure code works as expected
   - Make refactoring safer
   - Document expected behavior
   - Industry standard practice

Keep these tests passing as you implement your functions!
"""
