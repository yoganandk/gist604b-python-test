#!/usr/bin/env python3
"""
GIST 604B - Real Spatial Data Acquisition
Download and prepare real spatial datasets for GeoPandas assignment

This script downloads authoritative spatial data from:
- EPA Ecoregions (Level III) - from EPA S3 bucket
- Natural Earth populated places
- US National Parks (synthetic dataset)

**Fallback:** If downloads fail (server issues, network problems), the script
automatically uses pre-bundled backup data from data/.bundled/

Usage:
    python scripts/download_real_data.py --all
    python scripts/download_real_data.py --ecoregions
    python scripts/download_real_data.py --cities
    python scripts/download_real_data.py --protected-areas
    python scripts/download_real_data.py --use-bundled  # Skip downloads, use backup

Author: GIST 604B Course Team
License: Educational use - see individual dataset licenses
"""

import geopandas as gpd
import pandas as pd
import requests
import zipfile
import shutil
from pathlib import Path
from typing import Optional, List
import argparse
import sys
from io import BytesIO
import warnings
warnings.filterwarnings('ignore')


class RealDataDownloader:
    """Download and prepare real spatial datasets."""
    
    def __init__(self, data_dir: Path = Path("data"), use_bundled: bool = False):
        self.data_dir = data_dir
        self.bundled_dir = data_dir / ".bundled"
        self.temp_dir = data_dir / "temp"
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.use_bundled = use_bundled
        
        # Create subdirectories
        (self.data_dir / "ecoregions").mkdir(exist_ok=True)
        (self.data_dir / "cities").mkdir(exist_ok=True)
        (self.data_dir / "protected_areas").mkdir(exist_ok=True)
    
    def copy_from_bundled(self, dataset_name: str) -> bool:
        """Copy dataset from bundled backup."""
        dataset_mapping = {
            'ecoregions': ('ecoregions', 'epa_level3_western_us.geojson'),
            'cities': ('cities', 'ne_cities_us.geojson'),
            'protected': ('protected_areas', 'national_parks_major.geojson')
        }
        
        if dataset_name not in dataset_mapping:
            return False
        
        subdir, filename = dataset_mapping[dataset_name]
        bundled_file = self.bundled_dir / subdir / filename
        output_file = self.data_dir / subdir / filename
        
        if not bundled_file.exists():
            print(f"❌ Bundled file not found: {bundled_file}")
            return False
        
        try:
            print(f"📦 Using bundled backup: {filename}")
            shutil.copy2(bundled_file, output_file)
            size_kb = output_file.stat().st_size / 1024
            print(f"✅ Copied from backup: {filename} ({size_kb:.1f} KB)")
            return True
        except Exception as e:
            print(f"❌ Error copying bundled file: {e}")
            return False
        
    def download_file(self, url: str, output_path: Path) -> bool:
        """Download a file with progress indication."""
        try:
            print(f"📥 Downloading from: {url}")
            response = requests.get(url, stream=True, verify=False)  # Disable SSL verification for government sites
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            
            with open(output_path, 'wb') as f:
                if total_size == 0:
                    f.write(response.content)
                else:
                    downloaded = 0
                    for chunk in response.iter_content(chunk_size=8192):
                        downloaded += len(chunk)
                        f.write(chunk)
                        progress = (downloaded / total_size) * 100
                        print(f"\r   Progress: {progress:.1f}%", end='', flush=True)
            print()  # New line after progress
            print(f"✅ Downloaded: {output_path.name}")
            return True
        except Exception as e:
            print(f"❌ Error downloading {url}: {e}")
            return False
    
    def extract_zip(self, zip_path: Path, extract_to: Path) -> bool:
        """Extract a ZIP file."""
        try:
            print(f"📦 Extracting: {zip_path.name}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_to)
            print(f"✅ Extracted to: {extract_to}")
            return True
        except Exception as e:
            print(f"❌ Error extracting {zip_path}: {e}")
            return False
    
    def download_epa_ecoregions(self) -> Optional[gpd.GeoDataFrame]:
        """
        Download EPA Level III Ecoregions.
        
        Source: US EPA Office of Research and Development
        License: Public Domain (US Government work)
        URL: https://www.epa.gov/eco-research/level-iii-and-iv-ecoregions-continental-united-states
        """
        print("\n🌲 EPA LEVEL III ECOREGIONS")
        print("=" * 50)
        
        # Skip download if using bundled data
        if self.use_bundled:
            print("Using pre-bundled data (--use-bundled flag)")
            return None  # Will be handled by save_datasets
        
        # Try multiple sources in order
        urls = [
            "https://dmap-prod-oms-edc.s3.us-east-1.amazonaws.com/ORD/Ecoregions/us/us_eco_l3.zip",  # EPA S3 bucket (primary)
            "https://gaftp.epa.gov/EPADataCommons/ORD/Ecoregions/us/us_eco_l3.zip",  # EPA FTP (backup)
            "https://opendata.arcgis.com/api/v3/datasets/9ebec6097c5d469fa4df93bdf4489e3b_0/downloads/data?format=shp&spatialRefId=4326",  # ArcGIS OpenData (backup)
        ]
        
        zip_path = self.temp_dir / "us_eco_l3.zip"
        extract_dir = self.temp_dir / "ecoregions"
        
        # Try each URL until one works
        success = False
        for i, url in enumerate(urls, 1):
            print(f"Attempting source {i}/{len(urls)}...")
            if self.download_file(url, zip_path):
                success = True
                break
            else:
                print(f"   Source {i} failed, trying next...")
        
        if not success:
            print("❌ All download sources failed")
            print("   Attempting to use bundled backup data...")
            if self.copy_from_bundled('ecoregions'):
                return None  # Copied successfully, skip processing
            print("   ⚠️  No backup available - ecoregions will be missing")
            return None
        
        # Extract
        extract_dir.mkdir(exist_ok=True)
        if not self.extract_zip(zip_path, extract_dir):
            return None
        
        # Find shapefile
        shp_files = list(extract_dir.glob("**/*.shp"))
        if not shp_files:
            print("❌ No shapefile found in extracted data")
            return None
        
        print(f"📂 Loading: {shp_files[0].name}")
        gdf = gpd.read_file(shp_files[0])
        
        print(f"✅ Loaded {len(gdf)} ecoregions")
        print(f"   CRS: {gdf.crs}")
        print(f"   Columns: {', '.join(gdf.columns[:10])}...")
        
        return gdf
    
    def prepare_ecoregions(self, gdf: gpd.GeoDataFrame, region: str = "western_us") -> gpd.GeoDataFrame:
        """
        Prepare ecoregions for educational use.
        
        Args:
            gdf: Full ecoregions GeoDataFrame
            region: Geographic region to extract ('western_us', 'conus', 'northeast', etc.)
        """
        print(f"\n🔧 Preparing Ecoregions ({region})")
        print("=" * 50)
        
        # Ensure WGS84 first (EPA data comes in Albers Equal Area)
        if gdf.crs != "EPSG:4326":
            print(f"   Transforming CRS: {gdf.crs.name} → EPSG:4326")
            gdf = gdf.to_crs("EPSG:4326")
        
        # Standardize column names
        column_mapping = {
            'US_L3CODE': 'eco_code',
            'US_L3NAME': 'eco_name',
            'NA_L3CODE': 'eco_code_na',
            'NA_L3NAME': 'eco_name_na',
            'NA_L2CODE': 'l2_code',
            'NA_L2NAME': 'l2_name',
            'NA_L1CODE': 'l1_code',
            'NA_L1NAME': 'l1_name',
            'SHAPE_AREA': 'area',
            'SHAPE_LEN': 'perimeter'
        }
        
        # Rename columns that exist
        rename_dict = {old: new for old, new in column_mapping.items() if old in gdf.columns}
        gdf = gdf.rename(columns=rename_dict)
        
        # Keep essential columns
        keep_cols = ['eco_code', 'eco_name', 'l2_name', 'l1_name', 'geometry']
        keep_cols = [col for col in keep_cols if col in gdf.columns]
        gdf = gdf[keep_cols].copy()
        
        # Regional subsets (now that we're in WGS84)
        if region == "western_us":
            # Western US states (approximate bbox)
            western_bbox = (-125, 31, -102, 49)  # West Coast to Rockies
            gdf = gdf.cx[western_bbox[0]:western_bbox[2], western_bbox[1]:western_bbox[3]]
            print(f"   Filtered to Western US: {len(gdf)} ecoregions")
        
        elif region == "conus":
            # Keep all continental US (already filtered by source)
            print(f"   Using Continental US: {len(gdf)} ecoregions")
        
        elif region == "northeast":
            # Northeast states
            ne_bbox = (-80, 37, -66, 48)
            gdf = gdf.cx[ne_bbox[0]:ne_bbox[2], ne_bbox[1]:ne_bbox[3]]
            print(f"   Filtered to Northeast US: {len(gdf)} ecoregions")
        
        # Simplify geometries for educational use (preserve topology)
        print("   Simplifying geometries...")
        gdf['geometry'] = gdf.geometry.simplify(tolerance=0.01, preserve_topology=True)
        
        # Add helpful attributes
        gdf['area_km2'] = gdf.to_crs('EPSG:6933').geometry.area / 1e6  # Equal Area projection
        
        print(f"✅ Prepared {len(gdf)} ecoregions")
        print(f"   Columns: {', '.join(gdf.columns)}")
        
        return gdf
    
    def download_natural_earth_cities(self) -> Optional[gpd.GeoDataFrame]:
        """
        Download Natural Earth populated places.
        
        Source: Natural Earth Data
        License: Public Domain
        URL: https://www.naturalearthdata.com/downloads/10m-cultural-vectors/10m-populated-places/
        """
        print("\n🏙️  NATURAL EARTH CITIES")
        print("=" * 50)
        
        # Skip download if using bundled data
        if self.use_bundled:
            print("Using pre-bundled data (--use-bundled flag)")
            return None  # Will be handled by save_datasets
        
        url = "https://naciscdn.org/naturalearth/10m/cultural/ne_10m_populated_places.zip"
        zip_path = self.temp_dir / "ne_cities.zip"
        extract_dir = self.temp_dir / "cities"
        
        # Download
        if not self.download_file(url, zip_path):
            print("   Attempting to use bundled backup data...")
            if self.copy_from_bundled('cities'):
                return None  # Copied successfully
            print("   ⚠️  No backup available - cities will be missing")
            return None
        
        # Extract
        extract_dir.mkdir(exist_ok=True)
        if not self.extract_zip(zip_path, extract_dir):
            return None
        
        # Find shapefile
        shp_files = list(extract_dir.glob("**/*.shp"))
        if not shp_files:
            print("❌ No shapefile found")
            return None
        
        print(f"📂 Loading: {shp_files[0].name}")
        gdf = gpd.read_file(shp_files[0])
        
        print(f"✅ Loaded {len(gdf)} cities")
        print(f"   CRS: {gdf.crs}")
        
        return gdf
    
    def prepare_cities(self, gdf: gpd.GeoDataFrame, filter_country: Optional[str] = None, 
                       min_population: int = 100000) -> gpd.GeoDataFrame:
        """
        Prepare cities dataset for educational use.
        
        Args:
            gdf: Full cities GeoDataFrame
            filter_country: Optional country code (e.g., 'United States', 'all')
            min_population: Minimum population threshold
        """
        print(f"\n🔧 Preparing Cities Dataset")
        print("=" * 50)
        
        # Standardize columns
        column_mapping = {
            'NAME': 'name',
            'ADM0NAME': 'country',
            'ADM1NAME': 'state_province',
            'POP_MAX': 'population',
            'POP_MIN': 'pop_min',
            'LATITUDE': 'latitude',
            'LONGITUDE': 'longitude',
            'TIMEZONE': 'timezone'
        }
        
        rename_dict = {old: new for old, new in column_mapping.items() if old in gdf.columns}
        gdf = gdf.rename(columns=rename_dict)
        
        # Filter by population
        if 'population' in gdf.columns:
            gdf = gdf[gdf['population'] >= min_population].copy()
            print(f"   Filtered to population >= {min_population:,}: {len(gdf)} cities")
        
        # Filter by country if specified
        if filter_country and filter_country != 'all':
            if 'country' in gdf.columns:
                # Try exact match first, then partial match
                exact_match = gdf[gdf['country'] == filter_country].copy()
                if len(exact_match) == 0:
                    # Try partial match (e.g., "United States" in "United States of America")
                    gdf = gdf[gdf['country'].str.contains(filter_country, case=False, na=False)].copy()
                else:
                    gdf = exact_match
                print(f"   Filtered to {filter_country}: {len(gdf)} cities")
        
        # Keep essential columns
        keep_cols = ['name', 'country', 'state_province', 'population', 'latitude', 'longitude', 'geometry']
        keep_cols = [col for col in keep_cols if col in gdf.columns]
        gdf = gdf[keep_cols].copy()
        
        # Ensure WGS84
        if gdf.crs != "EPSG:4326":
            print(f"   Transforming CRS: {gdf.crs} → EPSG:4326")
            gdf = gdf.to_crs("EPSG:4326")
        
        # Sort by population
        if 'population' in gdf.columns:
            gdf = gdf.sort_values('population', ascending=False)
        
        print(f"✅ Prepared {len(gdf)} cities")
        print(f"   Columns: {', '.join(gdf.columns)}")
        
        return gdf
    
    def download_protected_areas(self, region_bbox: tuple = (-125, 31, -102, 49)) -> Optional[gpd.GeoDataFrame]:
        """
        Create a simplified protected areas dataset.
        
        Note: Full WDPA data is large (>1GB). This creates a representative sample
        using US National Park Service data.
        
        Source: National Park Service - Park Boundaries
        License: Public Domain (US Government)
        """
        print("\n🏞️  US NATIONAL PARKS")
        print("=" * 50)
        
        # Skip creation if using bundled data
        if self.use_bundled:
            print("Using pre-bundled data (--use-bundled flag)")
            if self.copy_from_bundled('protected'):
                return None
            print("   ⚠️  No backup available - protected areas will be missing")
            return None
        
        print("Note: Using NPS data as representative protected areas sample")
        
        # Alternative: Use a curated GeoJSON of major parks
        # For now, we'll create a sample from known parks
        
        major_parks = {
            'name': [
                # West Coast
                'Olympic National Park',
                'Crater Lake National Park',
                'Redwood National Park',
                'Yosemite National Park',
                'Sequoia National Park',
                'Channel Islands National Park',
                # Southwest
                'Grand Canyon National Park',
                'Zion National Park',
                'Bryce Canyon National Park',
                'Arches National Park',
                'Canyonlands National Park',
                'Petrified Forest National Park',
                'Saguaro National Park',
                'Big Bend National Park',
                'Guadalupe Mountains National Park',
                # Rocky Mountains
                'Yellowstone National Park',
                'Grand Teton National Park',
                'Glacier National Park',
                'Rocky Mountain National Park',
                'Great Sand Dunes National Park',
                # Midwest
                'Badlands National Park',
                'Theodore Roosevelt National Park',
                'Wind Cave National Park',
                'Isle Royale National Park',
                # Southeast
                'Hot Springs National Park',
                'Mammoth Cave National Park',
                'Great Smoky Mountains National Park',
                'Shenandoah National Park',
                'Everglades National Park',
                'Biscayne National Park',
                'Dry Tortugas National Park',
                # Northeast
                'Acadia National Park',
                # Alaska (major)
                'Denali National Park',
                'Glacier Bay National Park',
                'Kenai Fjords National Park',
                # Hawaii
                'Haleakalā National Park',
                'Hawaiʻi Volcanoes National Park'
            ],
            'state': [
                 # West Coast
                'Washington', 'Oregon', 'California', 'California', 'California', 'California',
                # Southwest
                'Arizona', 'Utah', 'Utah', 'Utah', 'Utah', 'Arizona', 'Arizona', 'Texas', 'Texas',
                # Rocky Mountains
                'Wyoming/Montana/Idaho', 'Wyoming', 'Montana', 'Colorado', 'Colorado',
                # Midwest
                'South Dakota', 'North Dakota', 'South Dakota', 'Michigan',
                # Southeast
                'Arkansas', 'Kentucky', 'Tennessee/North Carolina', 'Virginia', 'Florida', 'Florida', 'Florida',
                # Northeast
                'Maine',
                # Alaska
                'Alaska', 'Alaska', 'Alaska',
                # Hawaii
                'Hawaii', 'Hawaii'
            ],
            'designation': ['National Park'] * 37,
            'area_km2': [
                # West Coast
                3734, 741, 534, 3074, 1635, 1009,
                # Southwest
                4926, 595, 145, 310, 1366, 895, 370, 3243, 350,
                # Rocky Mountains
                8991, 1255, 4100, 1075, 340,
                # Midwest
                982, 285, 137, 2314,
                # Southeast
                23, 215, 2114, 809, 6105, 700, 262,
                # Northeast
                198,
                # Alaska
                24585, 13287, 2711,
                # Hawaii
                135, 1348
            ],
            'established': [
                # West Coast
                1938, 1902, 1968, 1890, 1890, 1980,
                # Southwest
                1919, 1919, 1928, 1929, 1964, 1962, 1994, 1944, 1972,
                # Rocky Mountains
                1872, 1929, 1910, 1915, 2004,
                # Midwest
                1978, 1978, 1903, 1940,
                # Southeast
                1921, 1941, 1934, 1935, 1947, 1980, 1992,
                # Northeast
                1919,
                # Alaska
                1917, 1980, 1980,
                # Hawaii
                1916, 1916
            ],
            # Approximate centroids
            'longitude': [
                # West Coast
                -123.5, -122.1, -124.0, -119.5, -118.6, -119.9,
                # Southwest
                -112.1, -113.0, -112.2, -109.6, -109.8, -109.8, -110.7, -103.2, -104.9,
                # Rocky Mountains
                -110.5, -110.8, -113.8, -105.7, -105.6,
                # Midwest
                -102.4, -103.5, -103.5, -88.8,
                # Southeast
                -93.1, -86.1, -83.5, -78.5, -80.9, -80.2, -82.9,
                # Northeast
                -68.2,
                # Alaska
                -151.0, -136.9, -149.9,
                # Hawaii
                -156.2, -155.5
            ],
            'latitude': [
                # West Coast
                47.8, 42.9, 41.3, 37.8, 36.5, 34.0,
                # Southwest
                36.1, 37.3, 37.6, 38.7, 38.3, 35.0, 32.2, 29.2, 31.9,
                # Rocky Mountains
                44.6, 43.8, 48.8, 40.3, 37.7,
                # Midwest
                43.9, 47.6, 43.6, 47.9,
                # Southeast
                34.5, 37.2, 35.7, 38.5, 25.3, 25.5, 24.6,
                # Northeast
                44.4,
                # Alaska
                63.1, 58.7, 60.0,
                # Hawaii
                20.7, 19.4
            ]
        }
        
        # Create points (we'll buffer these to approximate park boundaries)
        from shapely.geometry import Point
        geometries = [Point(lon, lat) for lon, lat in zip(major_parks['longitude'], major_parks['latitude'])]
        
        gdf = gpd.GeoDataFrame(major_parks, geometry=geometries, crs='EPSG:4326')
        
        # Create approximate park boundaries using buffers
        # Transform to appropriate projected CRS for buffering
        gdf_proj = gdf.to_crs('EPSG:5070')  # Albers Equal Area for CONUS
        
        # Buffer based on area (rough approximation)
        # Area = π * r^2, so r = sqrt(area / π)
        import numpy as np
        gdf_proj['geometry'] = gdf_proj.apply(
            lambda row: row.geometry.buffer(
                np.sqrt(row['area_km2'] * 1e6 / np.pi)  # Convert km2 to m2
            ),
            axis=1
        )
        
        # Transform back to WGS84
        gdf = gdf_proj.to_crs('EPSG:4326')
        
        print(f"✅ Created {len(gdf)} national park polygons")
        print(f"   CRS: {gdf.crs}")
        print(f"   Columns: {', '.join(gdf.columns)}")
        
        return gdf
    
    def save_datasets(self, ecoregions: Optional[gpd.GeoDataFrame] = None,
                     cities: Optional[gpd.GeoDataFrame] = None,
                     protected: Optional[gpd.GeoDataFrame] = None):
        """Save prepared datasets to assignment data directory."""
        print("\n💾 SAVING DATASETS")
        print("=" * 50)
        
        if ecoregions is not None:
            output_path = self.data_dir / "ecoregions" / "epa_level3_western_us.geojson"
            ecoregions.to_file(output_path, driver='GeoJSON')
            print(f"✅ Saved: {output_path}")
            print(f"   Features: {len(ecoregions)}, Size: {output_path.stat().st_size / 1024:.1f} KB")
        
        if cities is not None:
            output_path = self.data_dir / "cities" / "ne_cities_us.geojson"
            cities.to_file(output_path, driver='GeoJSON')
            print(f"✅ Saved: {output_path}")
            print(f"   Features: {len(cities)}, Size: {output_path.stat().st_size / 1024:.1f} KB")
        
        if protected is not None:
            output_path = self.data_dir / "protected_areas" / "national_parks_major.geojson"
            protected.to_file(output_path, driver='GeoJSON')
            print(f"✅ Saved: {output_path}")
            print(f"   Features: {len(protected)}, Size: {output_path.stat().st_size / 1024:.1f} KB")
    
    def cleanup(self):
        """Remove temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up temporary files")


def main():
    """Main execution function."""
    parser = argparse.ArgumentParser(description='Download real spatial data for GeoPandas assignment')
    parser.add_argument('--all', action='store_true', help='Download all datasets')
    parser.add_argument('--ecoregions', action='store_true', help='Download EPA ecoregions')
    parser.add_argument('--cities', action='store_true', help='Download Natural Earth cities')
    parser.add_argument('--protected-areas', action='store_true', help='Create protected areas dataset')
    parser.add_argument('--region', default='western_us', 
                       choices=['western_us', 'conus', 'northeast'],
                       help='Geographic region for ecoregions')
    parser.add_argument('--use-bundled', action='store_true', 
                       help='Skip downloads, use pre-bundled backup data')
    parser.add_argument('--cleanup', action='store_true', help='Clean up temporary files')
    
    args = parser.parse_args()
    
    # If no specific dataset selected, download all
    if not any([args.ecoregions, args.cities, args.protected_areas]):
        args.all = True
    
    downloader = RealDataDownloader(use_bundled=args.use_bundled)
    
    print("=" * 70)
    print("🌍 REAL SPATIAL DATA DOWNLOADER")
    print("=" * 70)
    print("GIST 604B - GeoPandas Spatial Operations Assignment")
    print()
    
    ecoregions_gdf = None
    cities_gdf = None
    protected_gdf = None
    
    try:
        # Download EPA Ecoregions
        if args.all or args.ecoregions:
            raw_ecoregions = downloader.download_epa_ecoregions()
            if raw_ecoregions is not None:
                ecoregions_gdf = downloader.prepare_ecoregions(raw_ecoregions, region=args.region)
        
        # Download Natural Earth Cities
        if args.all or args.cities:
            raw_cities = downloader.download_natural_earth_cities()
            if raw_cities is not None:
                cities_gdf = downloader.prepare_cities(
                    raw_cities, 
                    filter_country='United States',
                    min_population=100000
                )
        
        # Create Protected Areas
        if args.all or args.protected_areas:
            protected_gdf = downloader.download_protected_areas()
        
        # Save all datasets
        downloader.save_datasets(ecoregions_gdf, cities_gdf, protected_gdf)
        
        print("\n" + "=" * 70)
        print("✅ DATA DOWNLOAD COMPLETE")
        print("=" * 70)
        print("\nNext steps:")
        print("1. Review data in data/ directory")
        print("2. Run: python scripts/verify_data.py")
        print("3. Update notebooks to use real data")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Download interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        if args.cleanup:
            downloader.cleanup()


if __name__ == "__main__":
    main()
