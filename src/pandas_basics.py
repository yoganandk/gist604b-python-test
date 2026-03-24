"""
Pandas Basics for GIS Data Analysis - Student Implementation

Complete the four functions in this file.
Use the notebooks to learn and test each function.

📋 FUNCTIONS TO IMPLEMENT IN THIS FILE:
=====================================
✅ Function 1: load_and_explore_gis_data()     → notebooks/01_function_...
✅ Function 2: filter_environmental_data()     → notebooks/02_function_...
✅ Function 3: calculate_station_statistics()  → notebooks/03_function_...
✅ Function 4: join_station_data()             → notebooks/04_function_...
"""

import pandas as pd
from pathlib import Path
import os


# =============================================================================
# FUNCTION 1: LOAD AND EXPLORE GIS DATA
# =============================================================================

def load_and_explore_gis_data(file_path):
    """
    Load a CSV file and display comprehensive information about the dataset.
    
    This function demonstrates the first step in any data analysis project:
    understanding your data through exploration.
    
    Args:
        file_path (str): Path to the CSV file to load
        
    Returns:
        pandas.DataFrame: The loaded dataset, or None if loading failed
    
    Example:
        >>> stations_df = load_and_explore_gis_data('data/weather_stations.csv')
        Loading data from: data/weather_stations.csv
        Dataset shape: (150, 6) - That's 150 rows and 6 columns!
        ...
    """
    print("=" * 50)
    print("LOADING AND EXPLORING GIS DATA")
    print("=" * 50)
    
    # Step 1: Check if file exists
    if not os.path.exists(file_path):
        print(f"❌ ERROR: File not found: {file_path}")
        print("Please check:")
        print("- Is the file path correct?")
        print("- Are you in the right directory?")
        print("- Does the file exist?")
        return None
    
    print(f"📁 Loading data from: {file_path}")
    
    # Step 2: Load the CSV file
    try:
        df = pd.read_csv(file_path)
        print("✅ File loaded successfully!")
    except Exception as e:
        print(f"❌ ERROR loading file: {e}")
        return None
    
    # Step 3: Show basic dataset information
    print(f"\n📊 DATASET OVERVIEW")
    print(f"Shape: {df.shape} - {df.shape[0]} rows and {df.shape[1]} columns")
    print(f"Columns: {list(df.columns)}")
    
    # Step 4: Show data types
    print(f"\n🔧 DATA TYPES:")
    for col in df.columns:
        print(f"   {col}: {df[col].dtype}")
    
    # Step 5: Show first few rows
    print(f"\n👀 FIRST 5 ROWS:")
    print(df.head())
    
    # Step 6: Show summary statistics
    print(f"\n📈 SUMMARY STATISTICS:")
    print(df.describe())
    
    # Step 7: Check for data quality issues
    print(f"\n🔍 DATA QUALITY CHECK:")
    missing = df.isnull().sum()
    if missing.sum() > 0:
        print("Missing values found:")
        print(missing[missing > 0])
    else:
        print("✅ No missing values")
        
    duplicates = df.duplicated().sum()
    if duplicates > 0:
        print(f"⚠️  Found {duplicates} duplicate rows")
    else:
        print("✅ No duplicate rows")

    print(f"\n🎉 Data exploration complete! Dataset is ready for analysis.")
    
    return df

# =============================================================================
# FUNCTION 2: FILTER ENVIRONMENTAL DATA
# =============================================================================

def filter_environmental_data(df, min_temp=15, max_temp=30, quality="good"):
    """
    Filter environmental data based on temperature range and data quality.
    
    This function demonstrates how to apply multiple filtering conditions
    to clean and prepare environmental data for analysis.
    
    Args:
        df (pandas.DataFrame): Environmental data with temperature and quality columns
        min_temp (float): Minimum acceptable temperature in Celsius (default: 15)
        max_temp (float): Maximum acceptable temperature in Celsius (default: 30)
        quality (str): Required data quality level (default: "good")
        
    Returns:
        pandas.DataFrame: Filtered data meeting all specified conditions
    
    Example:
        >>> filtered_df = filter_environmental_data(readings_df, min_temp=20, max_temp=30, quality='good')
        Original data: 1000 rows
        After filtering: 247 rows (24.7% of data retained)
        Filters applied:
          - Temperature: 20.0°C to 30.0°C
          - Data quality: good
    """
    
    print("=" * 50)
    print("FILTERING ENVIRONMENTAL DATA")
    print("=" * 50)
    
    # Input validation
    if df is None or df.empty:
        print("❌ ERROR: Empty or None DataFrame provided")
        return pd.DataFrame()
    
    # Check for required columns
    required_columns = ['temperature_c', 'data_quality']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ ERROR: Missing required columns: {missing_columns}")
        print(f"📋 Available columns: {list(df.columns)}")
        return pd.DataFrame()
    
    original_count = len(df)
    print(f"📊 Starting with {original_count} rows of environmental data")
    
    # Show filtering criteria
    print(f"\n🎯 FILTERING CRITERIA:")
    print(f"   Temperature range: {min_temp}°C to {max_temp}°C")
    print(f"   Data quality: '{quality}'")
    
    # Check if quality level exists
    available_qualities = df['data_quality'].unique()
    if quality not in available_qualities:
        print(f"\n⚠️  WARNING: Quality level '{quality}' not found in data")
        print(f"📋 Available quality levels: {list(available_qualities)}")
        print("🔄 Returning original data without quality filtering...")
        quality_filter = pd.Series([True] * len(df), index=df.index)  # No filtering
    else:
        quality_filter = df['data_quality'] == quality
    
    # Apply all filters
    print(f"\n🔍 APPLYING FILTERS...")
    
    # Temperature range filter
    temp_filter = (df['temperature_c'] >= min_temp) & (df['temperature_c'] <= max_temp)
    temp_filtered_count = temp_filter.sum()
    temp_removed = original_count - temp_filtered_count
    print(f"   🌡️  Temperature filter: kept {temp_filtered_count}, removed {temp_removed} rows")
    
    # Quality filter
    quality_filtered_count = quality_filter.sum()
    quality_removed = original_count - quality_filtered_count
    print(f"   🏷️  Quality filter: kept {quality_filtered_count}, removed {quality_removed} rows")
    
    # Combined filter
    combined_filter = temp_filter & quality_filter
    filtered_df = df[combined_filter].copy()
    
    final_count = len(filtered_df)
    total_removed = original_count - final_count
    removal_pct = (total_removed / original_count) * 100 if original_count > 0 else 0
    
    print(f"\n📈 FILTERING RESULTS:")
    print(f"   Original dataset: {original_count} rows")
    print(f"   After filtering: {final_count} rows kept")
    print(f"   Total removed: {total_removed} rows ({removal_pct:.1f}%)")
    
    # Show statistics of filtered data
    if not filtered_df.empty:
        print(f"\n📊 FILTERED DATA SUMMARY:")
        print(f"   Temperature range: {filtered_df['temperature_c'].min():.1f}°C to {filtered_df['temperature_c'].max():.1f}°C")
        print(f"   Average temperature: {filtered_df['temperature_c'].mean():.1f}°C")
        print(f"   Quality distribution: {dict(filtered_df['data_quality'].value_counts())}")
    else:
        print(f"\n⚠️  WARNING: No data remains after filtering!")
        print(f"   Consider relaxing your filtering criteria.")
    
    print(f"\n✅ Filtering complete! Ready for analysis.")
    
    return filtered_df


# =============================================================================
# FUNCTION 3: CALCULATE STATION STATISTICS
# =============================================================================

def calculate_station_statistics(df):
    """
    Calculate station statistics
    
    This function groups temperature readings by weather station and calculates
    summary statistics (average temperature, number of readings, etc.) for each
    station.
    
    Args:
        df (pandas.DataFrame): Environmental readings data with 'station_id', 'temperature_c' and 'humidity_percent' columns
    
    Returns:
        pandas.DataFrame: Statistics for each station with columns:
            - station_id: The weather station identifier
            - avg_temperature: Average temperature for this station
            - avg_humidity: Average humidity for this station
            - reading_count: Number of readings from this station
    
    Example:
        >>> stats_df = calculate_station_statistics(readings_df)
        Calculating statistics for 5 unique stations...
        Statistics calculated:
          - Total readings analyzed: 1000
          - Stations with data: 5
          - Average readings per station: 200.0
    """
    
    # Print header
    print("=" * 50)
    print("CALCULATING STATION STATISTICS")
    print("=" * 50)
    
    # Input validation
    if df is None or len(df) == 0:
        print("❌ ERROR: DataFrame is empty or None")
        return pd.DataFrame()
    
    # Check for required columns
    required_columns = ['station_id', 'temperature_c', 'humidity_percent']
    missing_columns = [col for col in required_columns if col not in df.columns]
    
    if missing_columns:
        print(f"❌ ERROR: Missing required columns: {missing_columns}")
        print(f"Available columns: {list(df.columns)}")
        return pd.DataFrame()
    
    # Print input data summary
    print(f"Processing {len(df):,} temperature readings...")
    
    # Get unique stations
    unique_stations = df['station_id'].unique()
    print(f"Found {len(unique_stations)} weather stations: {list(unique_stations)}")
    
    # Group data by station
    grouped = df.groupby('station_id')
    
    # Calculate statistics
    avg_temperature = grouped['temperature_c'].mean().round(1)
    avg_humidity = grouped['humidity_percent'].mean().round(1)
    reading_count = grouped.size()
    
    # Create summary DataFrame
    summary = pd.DataFrame({
        'station_id': avg_temperature.index,
        'avg_temperature': avg_temperature.values,
        'avg_humidity': avg_humidity.values,
        'reading_count': reading_count.values
    })
    
    # Print summary of results
    print(f"\nTemperature range across all stations: {summary['avg_temperature'].min():.1f}°C to {summary['avg_temperature'].max():.1f}°C")
    print(f"Humidity range across all stations: {summary['avg_humidity'].min():.1f}% to {summary['avg_humidity'].max():.1f}%")
    print(f"Total readings processed: {summary['reading_count'].sum():,}")
    print(f"Average readings per station: {summary['reading_count'].mean():.0f}")
    
    # Find temperature extremes
    hottest_station = summary.loc[summary['avg_temperature'].idxmax()]
    coolest_station = summary.loc[summary['avg_temperature'].idxmin()]
    
    print(f"\nHottest station: {hottest_station['station_id']} (avg: {hottest_station['avg_temperature']:.1f}°C)")
    print(f"Coolest station: {coolest_station['station_id']} (avg: {coolest_station['avg_temperature']:.1f}°C)")
    
    print("\nStation statistics calculated successfully!")
    
    return summary


# =============================================================================
# FUNCTION 4: JOIN STATION DATA
# =============================================================================

def join_station_data(stations_df, readings_df):
    """
    Join sensor readings with station metadata
    
    This function joins station information (name, location) with temperature readings.
    You'll add station details (like station name and coordinates) to each temperature reading.
    
    Args:
        stations_df (pandas.DataFrame): Station information with 'station_id', 'station_name', 
                                       'latitude', 'longitude', etc.
        readings_df (pandas.DataFrame): Temperature readings with 'station_id', 'date', 
                                       'temperature_c', etc.
    
    Returns:
        pandas.DataFrame: Combined dataset with readings AND station information
    
    Example:
        >>> joined_df = join_station_data(stations_df, readings_df)
        Joining station information with readings...
        Stations table: 5 stations
        Readings table: 1000 readings
        Joined table: 1000 rows with station details added!
    """
    
    print("=" * 50)
    print("JOINING STATION DATA")
    print("=" * 50)
    
    # Input validation
    if readings_df is None or len(readings_df) == 0:
        print("❌ ERROR: Readings DataFrame is empty or None")
        return pd.DataFrame()
    
    if stations_df is None or len(stations_df) == 0:
        print("❌ ERROR: Stations DataFrame is empty or None") 
        return pd.DataFrame()
    
    # Check for required join key
    if 'station_id' not in readings_df.columns:
        print("❌ ERROR: 'station_id' column missing from readings data")
        return pd.DataFrame()
    
    if 'station_id' not in stations_df.columns:
        print("❌ ERROR: 'station_id' column missing from stations data")
        return pd.DataFrame()
    
    # Print input summary
    print(f"Input data:")
    print(f"  Readings: {len(readings_df)} rows, {len(readings_df.columns)} columns")
    print(f"  Stations: {len(stations_df)} rows, {len(stations_df.columns)} columns")
    
    # Analyze join keys
    readings_stations = set(readings_df['station_id'].unique())
    metadata_stations = set(stations_df['station_id'].unique())
    
    print(f"\nJoin analysis:")
    print(f"  Stations in readings: {len(readings_stations)}")
    print(f"  Stations in metadata: {len(metadata_stations)}")
    print(f"  Stations in both: {len(readings_stations & metadata_stations)}")
    
    if readings_stations - metadata_stations:
        print(f"  ⚠️ Readings without metadata: {readings_stations - metadata_stations}")
    if metadata_stations - readings_stations:
        print(f"  ℹ️ Metadata without readings: {metadata_stations - readings_stations}")
    
    # Perform left join to keep all readings
    print(f"\nPerforming LEFT JOIN (keeping all readings)...")
    result = pd.merge(readings_df, stations_df, on='station_id', how='left')
    
    # Validate results
    missing_metadata_count = result['station_name'].isna().sum()
    complete_records = len(result) - missing_metadata_count
    
    print(f"\nJoin results:")
    print(f"  Total records: {len(result)}")
    print(f"  Complete records: {complete_records}")
    print(f"  Records with missing metadata: {missing_metadata_count}")
    print(f"  Data completeness: {100*complete_records/len(result):.1f}%")
    
    print("\n✅ Station data join completed successfully!")
    
    return result


# =============================================================================
# HELPER FUNCTIONS (You don't need to modify these - they're provided!)
# =============================================================================

def _check_required_columns(df, required_columns, data_name="DataFrame"):
    """
    Helper function to check if required columns exist in a DataFrame.
    
    Args:
        df (pandas.DataFrame): DataFrame to check
        required_columns (list): List of required column names
        data_name (str): Name to use in error messages
    
    Returns:
        tuple: (bool, list) - (all_present, missing_columns)
    """
    if df is None or df.empty:
        return False, required_columns
    
    missing = [col for col in required_columns if col not in df.columns]
    return len(missing) == 0, missing


def _format_number(value, decimals=1):
    """
    Helper function to format numbers for display.
    
    Args:
        value: Number to format
        decimals (int): Number of decimal places
    
    Returns:
        str: Formatted number
    """
    try:
        return f"{float(value):.{decimals}f}"
    except (ValueError, TypeError):
        return str(value)
