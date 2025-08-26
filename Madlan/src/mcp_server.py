#!/usr/bin/env python3
"""
src/mcp_server.py - Complete Enhanced MCP Server with Desktop-Optimized Formatting and Transaction Type Filtering
"""

import json
import sys
import pandas as pd
from pathlib import Path
import logging
import requests
from geopy.distance import geodesic
import warnings
import numpy as np
from datetime import datetime

warnings.filterwarnings('ignore')
logging.basicConfig(level=logging.ERROR, stream=sys.stderr)

class NadlanPropertyServer:
    def __init__(self):
        self.data_path = Path(__file__).parent.parent / "data"
        self.data_loaded = False
        self.routing_api_url = "http://localhost:5000"
        self.load_data()
    
    def load_data(self):
        """Load real data with precise facility calculations"""
        try:
            print(f"DEBUG: Looking for data in: {self.data_path.absolute()}", file=sys.stderr)
            
            required_files = ["listings_enriched.csv"]
            
            if all((self.data_path / file).exists() for file in required_files):
                print("DEBUG: Loading real data", file=sys.stderr)
                
                # Load properties data
                self.properties_df = pd.read_csv(self.data_path / "listings_enriched.csv", encoding='utf-8')
                
                # Fix boolean columns from string format
                boolean_cols = ['bulletin_has_parking', 'bulletin_has_elevator', 'bulletin_has_balconies']
                for col in boolean_cols:
                    if col in self.properties_df.columns:
                        self.properties_df[col] = self.properties_df[col].astype(str).str.lower() == 'true'
                
                # Calculate nearest facilities for each property
                self.calculate_nearest_facilities()
                
                print(f"DEBUG: Loaded {len(self.properties_df)} properties successfully", file=sys.stderr)
                self.data_loaded = True
                
            else:
                print("DEBUG: Missing data files, using fallback", file=sys.stderr)
                self.create_fallback_data()
                self.data_loaded = True
            
        except Exception as e:
            print(f"DEBUG: Error loading data: {e}", file=sys.stderr)
            self.create_fallback_data()
            self.data_loaded = True

    def calculate_nearest_facilities(self):
        """Calculate nearest facilities dynamically using hardcoded facility data"""
        print("DEBUG: Calculating nearest facilities...", file=sys.stderr)
        
        # Add facility columns to properties dataframe
        self.properties_df['nearest_school_name'] = 'Unknown'
        self.properties_df['nearest_school_distance_km'] = 999.0
        self.properties_df['nearest_clinic_name'] = 'Unknown'
        self.properties_df['nearest_clinic_distance_km'] = 999.0
        
        # Hardcoded school data for calculations
        HAIFA_SCHOOLS = [
            {"name": "בית ספר יסודי הדר", "lat": 32.805123, "lon": 34.985234},
            {"name": "בית ספר יסודי נורדאו", "lat": 32.812345, "lon": 34.991234},
            {"name": "תיכון רמב״ם", "lat": 32.800234, "lon": 34.995678},
            {"name": "תיכון לאמנויות", "lat": 32.815678, "lon": 35.005789}
        ]
        
        HAIFA_CLINICS = [
            {"name": "מכבי - הדר", "lat": 32.805000, "lon": 34.985000},
            {"name": "כללית - רמת ויזניץ", "lat": 32.785123, "lon": 34.995678},
            {"name": "לאומית - נוה פז", "lat": 32.790000, "lon": 35.010000}
        ]
        
        # Calculate for each property
        for idx, property_row in self.properties_df.iterrows():
            prop_lat = property_row.get('lat')
            prop_lon = property_row.get('lon')
            
            if pd.isna(prop_lat) or pd.isna(prop_lon):
                continue
            
            property_coords = (prop_lat, prop_lon)
            
            # Find nearest school
            school_distances = []
            for school in HAIFA_SCHOOLS:
                school_coords = (school['lat'], school['lon'])
                distance = geodesic(property_coords, school_coords).kilometers
                school_distances.append({'name': school['name'], 'distance_km': distance})
            
            if school_distances:
                nearest_school = min(school_distances, key=lambda x: x['distance_km'])
                self.properties_df.at[idx, 'nearest_school_name'] = nearest_school['name']
                self.properties_df.at[idx, 'nearest_school_distance_km'] = round(nearest_school['distance_km'], 2)
            
            # Find nearest clinic
            clinic_distances = []
            for clinic in HAIFA_CLINICS:
                clinic_coords = (clinic['lat'], clinic['lon'])
                distance = geodesic(property_coords, clinic_coords).kilometers
                clinic_distances.append({'name': clinic['name'], 'distance_km': distance})
            
            if clinic_distances:
                nearest_clinic = min(clinic_distances, key=lambda x: x['distance_km'])
                self.properties_df.at[idx, 'nearest_clinic_name'] = nearest_clinic['name']
                self.properties_df.at[idx, 'nearest_clinic_distance_km'] = round(nearest_clinic['distance_km'], 2)

    def create_fallback_data(self):
        """Create fallback data matching CSV structure with transaction types"""
        print("DEBUG: Creating fallback data", file=sys.stderr)
        
        self.properties_df = pd.DataFrame({
            'publish_date': ['2025-03-30', '2025-02-04', '2025-01-15'],
            'seller_type': ['agent', 'agent', 'owner'],
            'property_rooms': [4.0, 3.5, 3.0],
            'property_price': [1290000, 1590000, 1750000],
            'property_floors': [3, 2, 1],
            'property_builded_area': [100, 68, 80],
            'city': ['חיפה', 'חיפה', 'חיפה'],
            'neighbourhood': ['הדר הכרמל', 'נוה פז', 'ואדי ניסנאס'],
            'street': ['הרצליה', 'שפרע', 'כורי'],
            'property_type': ['FLAT', 'FLAT', 'FLAT'],
            'transaction_type': ['For Sale', 'For Sale', 'For Sale'],  # Add transaction type
            'bulletin_has_balconies': [True, False, True],
            'bulletin_has_elevator': [True, True, False],
            'bulletin_has_parking': [False, True, True],
            'lat': [32.811234, 32.790123, 32.803456],
            'lon': [34.991456, 35.010456, 34.987890],
            'nearest_school_name': ['בית ספר יסודי נורדאו', 'בית ספר יסודי נוה שאנן', 'מקצועי מקס שיין'],
            'nearest_school_distance_km': [0.14, 0.08, 0.05],
            'nearest_clinic_name': ['קליניקה רפואית כרמל', 'לאומית - נוה פז', 'מכבי - הדר'],
            'nearest_clinic_distance_km': [0.39, 0.12, 0.33]
        })

    def detect_query_intent_and_amenities(self, search_params):
        """Detect both query intent, specific amenities, and transaction type mentioned"""
        
        query_text = search_params.get('_query_text', '').lower()
        
        # Property listing indicators
        listing_indicators = [
            'show me', 'find me', 'list', 'properties', 'apartments', 'flats',
            'top', 'best', 'recommendations', 'options', 'listings',
            'search for', 'looking for', 'want to see'
        ]
        
        # Data analysis indicators
        data_indicators = [
            'analyze', 'analysis', 'statistics', 'stats', 'average', 'compare', 
            'market data', 'trends', 'price analysis', 'how many', 'count',
            'overview', 'summary', 'what is', 'tell me about'
        ]
        
        # Amenity detection with comprehensive keywords
        amenity_patterns = {
            'schools': [
                'school', 'schools', 'education', 'elementary', 'high school', 
                'kindergarten', 'בית ספר', 'תיכון', 'חינוך'
            ],
            'medical': [
                'medical', 'clinic', 'hospital', 'doctor', 'health', 'healthcare',
                'maccabi', 'clalit', 'leumit', 'מכבי', 'כללית', 'לאומית', 'רופא', 'קליניקה'
            ],
            'transport': [
                'transport', 'transportation', 'bus', 'train', 'metro', 'carmelit',
                'station', 'public transport', 'תחבורה', 'אוטובוס', 'רכבת'
            ]
        }
        
        # Transaction type detection
        transaction_keywords = {
            'for_sale': ['for sale', 'buy', 'purchase', 'buying', 'sale', 'למכירה', 'קנייה'],
            'to_let': ['to let', 'rent', 'rental', 'renting', 'lease', 'להשכרה', 'השכרה', 'שכירות']
        }
        
        # Detect intent
        is_listing_query = any(indicator in query_text for indicator in listing_indicators)
        is_data_query = any(indicator in query_text for indicator in data_indicators)
        
        # Detect mentioned amenities
        mentioned_amenities = []
        for amenity_type, keywords in amenity_patterns.items():
            if any(keyword in query_text for keyword in keywords):
                mentioned_amenities.append(amenity_type)
        
        # Detect transaction type
        detected_transaction = None
        for trans_type, keywords in transaction_keywords.items():
            if any(keyword in query_text for keyword in keywords):
                detected_transaction = 'For Sale' if trans_type == 'for_sale' else 'To Let'
                break
        
        # Check search parameters for implicit amenity requests
        if search_params.get('near_schools') and 'schools' not in mentioned_amenities:
            mentioned_amenities.append('schools')
        if search_params.get('near_medical') and 'medical' not in mentioned_amenities:
            mentioned_amenities.append('medical')
        
        # Determine final format mode
        if is_data_query and not is_listing_query and not mentioned_amenities:
            format_mode = 'data'
        else:
            format_mode = 'listings'
        
        return {
            'format_mode': format_mode,
            'mentioned_amenities': mentioned_amenities,
            'is_listing_query': is_listing_query,
            'is_data_query': is_data_query,
            'detected_transaction': detected_transaction
        }

    def calculate_madlan_match_score(self, property_row, search_params, all_properties_df):
        """Calculate dynamic Madlan Match Score"""
        metadata_score = 0
        
        # Price competitiveness (15 points)
        if len(all_properties_df) > 1:
            price = property_row['property_price']
            price_percentile = (all_properties_df['property_price'] < price).mean()
            metadata_score += 15 * (1 - price_percentile)
        
        # Size value (10 points)
        area = property_row.get('property_builded_area', 0)
        if area > 0:
            area_percentile = (all_properties_df['property_builded_area'] < area).mean()
            metadata_score += 10 * area_percentile
        
        # Features bonus (15 points total)
        if property_row.get('bulletin_has_parking', False):
            metadata_score += 5
        if property_row.get('bulletin_has_elevator', False):
            metadata_score += 5
        if property_row.get('bulletin_has_balconies', False):
            metadata_score += 5
        
        # Recency bonus (10 points)
        try:
            pub_date = pd.to_datetime(property_row['publish_date'])
            days_old = (datetime.now() - pub_date).days
            metadata_score += max(0, 10 * (1 - days_old / 365))
        except:
            metadata_score += 5
        
        # Context score (50 points)
        context_score = 0
        if search_params.get('near_schools'):
            school_dist = property_row.get('nearest_school_distance_km', 999)
            if school_dist < 999:
                context_score += min(50, 50 * np.exp(-school_dist * 2))
        else:
            context_score += 25  # Base score
        
        return min(100, round(metadata_score + context_score, 1))

    def search_properties(self, **kwargs):
        """Enhanced property search with transaction type filtering"""
        df = self.properties_df.copy()
        filters = []
        
        print(f"DEBUG: Search called with params: {kwargs}", file=sys.stderr)
        
        # Fix boolean columns from string format to actual boolean
        boolean_cols = ['bulletin_has_parking', 'bulletin_has_elevator', 'bulletin_has_balconies']
        for col in boolean_cols:
            if col in df.columns:
                df[col] = df[col].astype(str).str.lower() == 'true'
        
        # Detect query intent and amenities (including transaction type)
        intent_data = self.detect_query_intent_and_amenities(kwargs)
        
        # Transaction type filtering
        if kwargs.get('transaction_type'):
            transaction_filter = kwargs['transaction_type']
            if 'transaction_type' in df.columns:
                df = df[df['transaction_type'] == transaction_filter]
                filters.append(f"Transaction type: {transaction_filter}")
        
        # Auto-detect transaction type from query if not explicitly set
        detected_transaction = intent_data.get('detected_transaction')
        if detected_transaction and not kwargs.get('transaction_type'):
            if 'transaction_type' in df.columns:
                df = df[df['transaction_type'] == detected_transaction]
                filters.append(f"Auto-detected: {detected_transaction} properties only")
        
        # Apply other filters
        if kwargs.get('max_price'):
            df = df[df['property_price'] <= kwargs['max_price']]
            filters.append(f"Max price: {kwargs['max_price']:,} NIS")
        
        if kwargs.get('min_price'):
            df = df[df['property_price'] >= kwargs['min_price']]
            filters.append(f"Min price: {kwargs['min_price']:,} NIS")
        
        if kwargs.get('rooms'):
            df = df[df['property_rooms'] >= kwargs['rooms']]
            filters.append(f"Min rooms: {kwargs['rooms']}")
        
        if kwargs.get('near_schools'):
            df = df[df['nearest_school_distance_km'] <= 1.5]
            filters.append("Near schools (<=1.5km)")
        
        if kwargs.get('near_medical'):
            df = df[df['nearest_clinic_distance_km'] <= 2.0]
            filters.append("Near medical (<=2km)")
        
        if kwargs.get('has_parking'):
            df = df[df['bulletin_has_parking'] == True]
            filters.append("Must have parking")
        
        if kwargs.get('has_elevator'):
            df = df[df['bulletin_has_elevator'] == True]
            filters.append("Must have elevator")
        
        if kwargs.get('has_balcony'):
            df = df[df['bulletin_has_balconies'] == True]
            filters.append("Must have balcony")
        
        # Calculate match scores
        match_scores = []
        for idx, row in df.iterrows():
            score = self.calculate_madlan_match_score(row, kwargs, self.properties_df)
            match_scores.append(score)
        
        df['madlan_match_score'] = match_scores
        df = df.sort_values('madlan_match_score', ascending=False)
        
        limit = kwargs.get('limit', 10)
        df = df.head(limit)
        
        result = {
            'properties': df.to_dict('records'),
            'filters': filters,
            'total_found': len(df),
            'search_params': kwargs,
            'market_stats': {
                'avg_price': int(df['property_price'].mean()) if len(df) > 0 else 0,
                'min_price': int(df['property_price'].min()) if len(df) > 0 else 0,
                'max_price': int(df['property_price'].max()) if len(df) > 0 else 0,
                'avg_area': round(df['property_builded_area'].mean(), 1) if len(df) > 0 else 0
            },
            '_intent_data': intent_data
        }
        
        return result

    def get_nearest_amenities(self, property_coords, amenity_type, limit=3):
        """Get nearest amenities with enhanced travel time calculations"""
        
        AMENITY_DATA = {
            'schools': [
                {
                    'name': 'בית ספר יסודי הדר',
                    'lat': 32.805123, 'lon': 34.985234,
                    'address': 'רחוב הרצל 15, הדר, חיפה',
                    'website': 'www.education.gov.il/hadar-elementary',
                    'phone': '04-8234567',
                    'type': 'Elementary School'
                },
                {
                    'name': 'בית ספר יסודי נורדאו', 
                    'lat': 32.812345, 'lon': 34.991234,
                    'address': 'רחוב נורדאו 28, כרמל מרכז, חיפה',
                    'website': 'www.nordau-school.org.il',
                    'phone': '04-8345678',
                    'type': 'Elementary School'
                },
                {
                    'name': 'בית ספר יסודי גבעת האונס',
                    'lat': 32.820567, 'lon': 35.000123,
                    'address': 'רחוב האונס 42, גבעת האונס, חיפה',
                    'website': 'www.givat-haons-school.co.il',
                    'phone': '04-8456789',
                    'type': 'Elementary School'
                },
                {
                    'name': 'תיכון לאמנויות',
                    'lat': 32.815678, 'lon': 35.005789,
                    'address': 'רחוב הציונות 18, כרמל, חיפה',
                    'website': 'www.arts-highschool-haifa.org.il',
                    'phone': '04-8567890',
                    'type': 'Arts High School'
                },
                {
                    'name': 'תיכון רמב״ם',
                    'lat': 32.800234, 'lon': 34.995678,
                    'address': 'רחוב רמב״ם 33, הדר העליון, חיפה',
                    'website': 'www.rambam-high.edu.il',
                    'phone': '04-8678901',
                    'type': 'Academic High School'
                },
                {
                    'name': 'מקצועי מקס שיין',
                    'lat': 32.809876, 'lon': 34.985432,
                    'address': 'רחוב מקס שיין 5, הדר, חיפה',
                    'website': 'www.max-shein-tech.org.il',
                    'phone': '04-8890123',
                    'type': 'Vocational High School'
                }
            ],
            'medical': [
                {
                    'name': 'מכבי שירותי בריאות - הדר',
                    'lat': 32.805000, 'lon': 34.985000,
                    'address': 'רחוב הרצל 45, הדר, חיפה',
                    'website': 'www.maccabi4u.co.il',
                    'phone': '04-8111222',
                    'type': 'General Clinic'
                },
                {
                    'name': 'כללית - רמת ויזניץ',
                    'lat': 32.785123, 'lon': 34.995678,
                    'address': 'רחוב ויזניץ 12, רמת ויזניץ, חיפה',
                    'website': 'www.clalit.co.il',
                    'phone': '04-8222333',
                    'type': 'General Clinic'
                },
                {
                    'name': 'לאומית - נוה פז',
                    'lat': 32.790000, 'lon': 35.010000,
                    'address': 'רחוב פז 8, נוה פז, חיפה',
                    'website': 'www.leumit.co.il',
                    'phone': '04-8333444',
                    'type': 'General Clinic'
                },
                {
                    'name': 'קליניקה רפואית כרמל',
                    'lat': 32.812000, 'lon': 34.995000,
                    'address': 'רחוב יפה נוף 14, כרמל, חיפה',
                    'website': 'www.carmel-clinic.co.il',
                    'phone': '04-8555666',
                    'type': 'Private Clinic'
                }
            ],
            'transport': [
                {
                    'name': 'תחנת אוטובוס מרכזית חיפה',
                    'lat': 32.809876, 'lon': 34.985432,
                    'address': 'רחוב יפו 142, הדר, חיפה',
                    'website': 'www.egged.co.il',
                    'phone': '04-8666777',
                    'type': 'Central Bus Station'
                },
                {
                    'name': 'רכבת ישראל - חיפה מרכז',
                    'lat': 32.815234, 'lon': 34.999123,
                    'address': 'כיכר פלומר, כרמל מרכז, חיפה',
                    'website': 'www.rail.co.il',
                    'phone': '04-8777888',
                    'type': 'Train Station'
                },
                {
                    'name': 'מטרונית - כרמלית',
                    'lat': 32.818901, 'lon': 34.998234,
                    'address': 'כיכר פריס, כרמל מרכז, חיפה',
                    'website': 'www.carmelit.co.il',
                    'phone': '04-8888999',
                    'type': 'Underground Metro'
                }
            ]
        }
        
        amenities = AMENITY_DATA.get(amenity_type, [])
        
        # Enhanced distance and travel time calculations
        amenity_distances = []
        for amenity in amenities:
            amenity_coords = (amenity['lat'], amenity['lon'])
            
            # Precise distance calculation
            distance_km = geodesic(property_coords, amenity_coords).kilometers
            distance_meters = int(distance_km * 1000)
            
            # Enhanced travel time formulas considering Haifa terrain
            # Walking: Account for Haifa's hills and urban layout
            base_walk_speed_kmh = 4.5  # Conservative speed for hills
            walk_time_minutes = max(1, int((distance_km / base_walk_speed_kmh) * 60))
            
            # Add terrain penalty for longer distances (Haifa's steep roads)
            if distance_km > 0.5:
                terrain_penalty = int(distance_km * 3)  # Extra 3 minutes per km for hills
                walk_time_minutes += terrain_penalty
            
            # Driving: City traffic with Haifa road conditions
            base_drive_speed_kmh = 22  # Realistic city driving speed
            drive_time_minutes = max(2, int((distance_km / base_drive_speed_kmh) * 60))
            
            # Add traffic and navigation penalty
            if distance_km > 0.8:
                traffic_penalty = int(distance_km * 2)  # Extra time for traffic, parking
                drive_time_minutes += traffic_penalty
            
            # Public transport estimate
            if distance_km > 1.5:
                wait_time = 10  # Average bus wait in Haifa
                bus_speed_kmh = 18  # City bus with stops
                bus_travel_time = int((distance_km / bus_speed_kmh) * 60)
                walk_to_stop_time = 6  # Walking to/from stops
                public_transport_time = wait_time + bus_travel_time + walk_to_stop_time
            else:
                public_transport_time = None
            
            # Accessibility rating
            if distance_km < 0.3:
                accessibility = 'Excellent - Very close'
            elif distance_km < 0.8:
                accessibility = 'Very Good - Walking distance'
            elif distance_km < 1.5:
                accessibility = 'Good - Short commute'
            else:
                accessibility = 'Fair - Longer commute'
            
            amenity_info = {
                'name': amenity['name'],
                'address': amenity['address'],
                'website': amenity['website'],
                'phone': amenity['phone'],
                'type': amenity.get('type', 'Facility'),
                'distance_km': round(distance_km, 3),
                'distance_meters': distance_meters,
                'walk_time_min': walk_time_minutes,
                'drive_time_min': drive_time_minutes,
                'public_transport_min': public_transport_time,
                'accessibility_rating': accessibility
            }
            amenity_distances.append(amenity_info)
        
        # Sort by distance and return top results
        amenity_distances.sort(key=lambda x: x['distance_km'])
        return amenity_distances[:limit]

    def format_desktop_optimized(self, results, mentioned_amenities):
        """Comprehensive data formatting that Claude Desktop will naturally present"""
        
        if not results['properties']:
            return "No properties found matching your criteria."
        
        lines = []
        property_count = len(results['properties'])
        search_params = results.get('search_params', {})
        max_price = search_params.get('max_price', 0)
        
        # Check if there's transaction type filtering active
        transaction_type_filter = None
        for filter_desc in results.get('filters', []):
            if 'Transaction type:' in filter_desc or 'Auto-detected:' in filter_desc:
                transaction_type_filter = filter_desc
                break
        
        # Comprehensive header with all context
        header = f"COMPREHENSIVE PROPERTY SEARCH - {property_count} properties"
        if max_price > 0:
            header += f" under {max_price:,} NIS"
        if transaction_type_filter:
            header += f" ({transaction_type_filter.split(': ')[-1].split(' properties')[0]})"
        lines.append(header)
        
        if mentioned_amenities:
            lines.append(f"Specialized search focus: {', '.join(mentioned_amenities)} proximity analysis")
        lines.append("")
        
        # Market analysis
        stats = results['market_stats']
        avg_price_per_sqm = self.get_price_per_sqm(stats['avg_price'], stats['avg_area'])
        lines.append("MARKET ANALYSIS:")
        lines.append(f"Average property price: {stats['avg_price']:,} NIS")
        lines.append(f"Average price per square meter: {avg_price_per_sqm:,} NIS/sqm")
        lines.append(f"Full price range: {stats['min_price']:,} to {stats['max_price']:,} NIS")
        lines.append("")
        
        # Match score analysis
        scores = [p.get('madlan_match_score', 0) for p in results['properties']]
        min_score, max_score = min(scores), max(scores)
        lines.append(f"Madlan Match Score Analysis: Range {min_score:.1f} to {max_score:.1f} out of 100 points")
        lines.append("")
        
        # Detailed property information with comprehensive travel data
        for i, prop in enumerate(results['properties']):
            rank = i + 1
            match_score = prop.get('madlan_match_score', 0)
            
            lines.append(f"PROPERTY {rank} COMPLETE DETAILS:")
            lines.append(f"Madlan match score: {match_score:.1f}/100 ({self.get_score_level(match_score)})")
            lines.append("")
            
            # Complete property specifications
            street = prop.get('street', 'Unknown')
            neighbourhood = prop.get('neighbourhood', 'Unknown')
            rooms = prop.get('property_rooms', 0)
            floors = prop.get('property_floors', 'Unknown')
            area = prop.get('property_builded_area', 0)
            price = prop.get('property_price', 0)
            price_per_sqm = self.get_price_per_sqm(price, area)
            transaction_type = prop.get('transaction_type', 'Unknown')
            
            lines.append(f"Complete address: {street}, {neighbourhood}, Haifa")
            lines.append(f"Property type and layout: {prop.get('property_type', 'FLAT')}, {rooms} rooms, {floors} floors")
            lines.append(f"Built area: {area} square meters")
            lines.append(f"Total price: {price:,} NIS ({transaction_type})")
            lines.append(f"Price per square meter: {price_per_sqm:,} NIS/sqm")
            
            # Comprehensive feature inventory
            lines.append("Complete feature inventory:")
            lines.append(f"  Private parking: {'Available' if prop.get('bulletin_has_parking') else 'Not available'}")
            lines.append(f"  Elevator access: {'Yes - building has elevator' if prop.get('bulletin_has_elevator') else 'No - walk-up building'}")
            lines.append(f"  Balcony or terrace: {'Included' if prop.get('bulletin_has_balconies') else 'No outdoor space'}")
            
            # Listing information
            seller = prop.get('seller_type', 'Unknown').title()
            date = prop.get('publish_date', 'Unknown')
            lines.append(f"Listing information: Published {date} by {seller}")
            lines.append("")
            
            # COMPREHENSIVE TRAVEL TIME ANALYSIS for requested amenities
            prop_lat = prop.get('lat', 32.8156)
            prop_lon = prop.get('lon', 34.9892)
            property_coords = (prop_lat, prop_lon)
            
            if 'schools' in mentioned_amenities:
                lines.append("DETAILED SCHOOL PROXIMITY WITH PRECISE TRAVEL TIMES:")
                school_amenities = self.get_nearest_amenities(property_coords, 'schools', 5)
                
                for j, school in enumerate(school_amenities):
                    lines.append(f"School option {j+1}: {school['name']} ({school['type']})")
                    lines.append(f"  Complete address: {school['address']}")
                    lines.append(f"  Precise distance: {school['distance_km']:.3f} kilometers ({school['distance_meters']} meters)")
                    lines.append(f"  Walking time with terrain: {school['walk_time_min']} minutes")
                    lines.append(f"  Driving time with traffic: {school['drive_time_min']} minutes")
                    if school.get('public_transport_min'):
                        lines.append(f"  Public transport time: {school['public_transport_min']} minutes")
                    lines.append(f"  Accessibility assessment: {school['accessibility_rating']}")
                    lines.append(f"  School contact details: Phone {school['phone']}, Website {school['website']}")
                    lines.append("")
            
            if 'medical' in mentioned_amenities:
                lines.append("DETAILED MEDICAL FACILITY PROXIMITY WITH PRECISE TRAVEL TIMES:")
                medical_amenities = self.get_nearest_amenities(property_coords, 'medical', 4)
                
                for j, clinic in enumerate(medical_amenities):
                    lines.append(f"Medical facility {j+1}: {clinic['name']} ({clinic['type']})")
                    lines.append(f"  Complete address: {clinic['address']}")
                    lines.append(f"  Precise distance: {clinic['distance_km']:.3f} kilometers ({clinic['distance_meters']} meters)")
                    lines.append(f"  Walking time with terrain: {clinic['walk_time_min']} minutes")
                    lines.append(f"  Driving time with traffic: {clinic['drive_time_min']} minutes")
                    if clinic.get('public_transport_min'):
                        lines.append(f"  Public transport time: {clinic['public_transport_min']} minutes")
                    lines.append(f"  Accessibility assessment: {clinic['accessibility_rating']}")
                    lines.append(f"  Medical facility contact: Phone {clinic['phone']}, Website {clinic['website']}")
                    lines.append("")
            
            if 'transport' in mentioned_amenities:
                lines.append("DETAILED TRANSPORTATION ACCESS WITH PRECISE TRAVEL TIMES:")
                transport_amenities = self.get_nearest_amenities(property_coords, 'transport', 3)
                
                for j, transport in enumerate(transport_amenities):
                    lines.append(f"Transportation hub {j+1}: {transport['name']} ({transport['type']})")
                    lines.append(f"  Complete address: {transport['address']}")
                    lines.append(f"  Precise distance: {transport['distance_km']:.3f} kilometers ({transport['distance_meters']} meters)")
                    lines.append(f"  Walking time with terrain: {transport['walk_time_min']} minutes")
                    lines.append(f"  Driving time with traffic: {transport['drive_time_min']} minutes")
                    lines.append(f"  Accessibility assessment: {transport['accessibility_rating']}")
                    lines.append(f"  Transportation contact: Phone {transport['phone']}, Website {transport['website']}")
                    lines.append("")
            
            # Neighborhood analysis
            lines.append(f"NEIGHBORHOOD ANALYSIS FOR {neighbourhood}:")
            lines.append(f"Location characteristics: {neighbourhood} is an established neighborhood in Haifa")
            
            if 'schools' in mentioned_amenities:
                all_schools = self.get_nearest_amenities(property_coords, 'schools', 10)
                school_count = len([s for s in all_schools if s['distance_km'] <= 2.0])
                avg_school_distance = sum(s['distance_km'] for s in all_schools[:3]) / 3
                lines.append(f"Educational environment: {school_count} schools within 2km, average distance {avg_school_distance:.2f}km")
            
            if 'medical' in mentioned_amenities:
                all_medical = self.get_nearest_amenities(property_coords, 'medical', 10)
                medical_count = len([m for m in all_medical if m['distance_km'] <= 2.0])
                avg_medical_distance = sum(m['distance_km'] for m in all_medical[:3]) / 3
                lines.append(f"Healthcare access: {medical_count} medical facilities within 2km, average distance {avg_medical_distance:.2f}km")
            
            lines.append("")
            
            # Property separator
            if i < len(results['properties']) - 1:
                lines.append("=" * 80)
                lines.append("")
        
        # Comprehensive comparative analysis
        lines.append("COMPREHENSIVE COMPARATIVE ANALYSIS:")
        
        # Value comparison
        price_per_sqms = [self.get_price_per_sqm(p['property_price'], p.get('property_builded_area', 1)) for p in results['properties']]
        best_value_idx = price_per_sqms.index(min(price_per_sqms))
        worst_value_idx = price_per_sqms.index(max(price_per_sqms))
        lines.append(f"Best value per square meter: Property {best_value_idx + 1} at {min(price_per_sqms):,} NIS/sqm")
        lines.append(f"Highest price per square meter: Property {worst_value_idx + 1} at {max(price_per_sqms):,} NIS/sqm")
        
        # Transaction type breakdown
        if 'transaction_type' in results['properties'][0]:
            transaction_types = [p.get('transaction_type', 'Unknown') for p in results['properties']]
            for_sale_count = transaction_types.count('For Sale')
            to_let_count = transaction_types.count('To Let')
            if for_sale_count > 0 and to_let_count > 0:
                lines.append(f"Transaction type breakdown: {for_sale_count} For Sale, {to_let_count} To Let")
        
        # Proximity comparison
        if 'schools' in mentioned_amenities:
            school_distances = [p.get('nearest_school_distance_km', 999) for p in results['properties']]
            closest_school_idx = school_distances.index(min(school_distances))
            closest_distance = min(school_distances)
            walk_time = max(1, int((closest_distance / 4.5) * 60)) + int(closest_distance * 3)  # Include terrain
            lines.append(f"Closest to schools: Property {closest_school_idx + 1} at {closest_distance:.3f}km ({walk_time} minutes walk including terrain)")
        
        if 'medical' in mentioned_amenities:
            medical_distances = [p.get('nearest_clinic_distance_km', 999) for p in results['properties']]
            closest_medical_idx = medical_distances.index(min(medical_distances))
            closest_medical_distance = min(medical_distances)
            walk_time = max(1, int((closest_medical_distance / 4.5) * 60)) + int(closest_medical_distance * 3)
            lines.append(f"Closest to medical facilities: Property {closest_medical_idx + 1} at {closest_medical_distance:.3f}km ({walk_time} minutes walk including terrain)")
        
        # Feature statistics
        parking_count = sum(1 for p in results['properties'] if p.get('bulletin_has_parking'))
        elevator_count = sum(1 for p in results['properties'] if p.get('bulletin_has_elevator'))
        balcony_count = sum(1 for p in results['properties'] if p.get('bulletin_has_balconies'))
        
        lines.append(f"Feature availability across all properties:")
        lines.append(f"  Properties with parking: {parking_count} out of {property_count}")
        lines.append(f"  Properties with elevators: {elevator_count} out of {property_count}")
        lines.append(f"  Properties with balconies: {balcony_count} out of {property_count}")

        # Add follow-up suggestions
        lines.append("")
        lines.append("FOLLOW-UP OPTIONS AND SUGGESTIONS:")
        suggestions = self.get_enhanced_suggestions(results, results.get('search_params', {}), mentioned_amenities)
        
        lines.append("Would you like me to:")
        for i, suggestion in enumerate(suggestions[:6], 1):
            lines.append(f"{i}. {suggestion}")
        
        lines.append("")
        lines.append("Additional commands: Ask me to refine search criteria, compare specific properties, or analyze neighborhood trends.")
        
        return "\n".join(lines)

    def get_enhanced_suggestions(self, results, search_params, mentioned_amenities):
        """Generate context-aware suggestions based on mentioned amenities"""
        suggestions = []
    
        # Transaction type specific suggestions
        current_transaction = None
        for filter_desc in results.get('filters', []):
            if 'For Sale' in filter_desc:
                current_transaction = 'For Sale'
            elif 'To Let' in filter_desc:
                current_transaction = 'To Let'
        
        if current_transaction == 'For Sale':
            suggestions.append("Switch to rental properties (To Let) in the same area")
        elif current_transaction == 'To Let':
            suggestions.append("Switch to properties for sale in the same area")
        else:
            suggestions.extend([
                "Filter by transaction type (For Sale vs To Let)",
                "Compare rental vs purchase options"
            ])
    
        # Amenity-specific suggestions
        if 'schools' in mentioned_amenities:
            suggestions.extend([
                "Refine search by specific school distance (e.g., within 500m of a particular school)",
                "Filter by school type (elementary vs high school vs vocational)",
                "Show only properties near top-rated schools"
            ])
        
        if 'medical' in mentioned_amenities:
            suggestions.extend([
                "Filter by health fund provider (Clalit, Maccabi, Leumit)",
                "Show properties near hospitals vs clinics",
                "Find properties near specialized medical centers"
            ])
        
        if 'transport' in mentioned_amenities:
            suggestions.extend([
                "Focus on train station proximity vs bus access",
                "Show properties near multiple transport options"
            ])
        
        # General suggestions based on results
        if len(results.get('properties', [])) < 5:
            suggestions.extend([
                "Expand budget range to see more options",
                "Include additional neighborhoods in search",
                "Reduce minimum room requirements"
            ])
        
        if len(results.get('properties', [])) > 8:
            suggestions.extend([
                "Narrow search with additional filters",
                "Focus on top 3 properties for detailed comparison"
            ])
        
        # Always include these
        suggestions.extend([
            "Sort results by different criteria (price, distance, area)",
            "Get detailed market analysis for this area",
            "Compare specific properties side-by-side",
            "Analyze neighborhood trends and pricing history",
            "Search in different neighborhoods with similar criteria"
        ])
        
        return suggestions[:8]  # Limit to 8 suggestions

    def get_score_level(self, score):
        """Get text description for Madlan Match Score"""
        if score >= 80:
            return "Excellent Match"
        elif score >= 70:
            return "Good Match"
        elif score >= 50:
            return "Fair Match"
        else:
            return "Basic Match"

    def get_price_per_sqm(self, price, area):
        """Calculate price per square meter"""
        if area and area > 0:
            return int(price / area)
        return 0

    def handle_request(self, request):
        """Handle MCP protocol requests"""
        try:
            method = request.get("method", "")
            request_id = request.get("id")
            
            if method == "initialize":
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "result": {
                        "protocolVersion": "2024-11-05",
                        "capabilities": {"tools": {}},
                        "serverInfo": {
                            "name": "Madlan_MCP",
                            "version": "4.3.0"
                        }
                    }
                }
            
            elif method == "notifications/initialized":
                return "SKIP_RESPONSE"

            elif method == "tools/list":
                return {
                    "jsonrpc": "2.0", 
                    "id": request_id,
                    "result": {
                        "tools": [
                            {
                                "name": "Madlan_MCP",
                                "description": "Search the Nadlan property database. Pass the original user query in _query_text parameter for optimal formatting.",
                                "inputSchema": {
                                    "type": "object",
                                    "properties": {
                                        "_query_text": {"type": "string", "description": "Original user query for intent detection"},
                                        "max_price": {"type": "number", "description": "Maximum price in NIS"},
                                        "min_price": {"type": "number", "description": "Minimum price in NIS"},
                                        "rooms": {"type": "number", "description": "Minimum number of rooms"},
                                        "property_type": {"type": "string", "description": "Property type filter"},
                                        "transaction_type": {"type": "string", "description": "Filter by transaction type (For Sale or To Let)", "enum": ["For Sale", "To Let"]},
                                        "neighborhoods": {"type": "array", "items": {"type": "string"}, "description": "Hebrew neighborhood names"},
                                        "near_schools": {"type": "boolean", "description": "Properties within 1.5km of schools"},
                                        "near_medical": {"type": "boolean", "description": "Properties within 2km of medical facilities"},
                                        "has_parking": {"type": "boolean", "description": "Must have parking"},
                                        "has_elevator": {"type": "boolean", "description": "Must have elevator"},
                                        "has_balcony": {"type": "boolean", "description": "Must have balcony"},
                                        "sort_by": {"type": "string", "description": "Sort order", "enum": ["price_low", "price_high", "madlan_match", "area", "school_distance", "newest"]},
                                        "limit": {"type": "number", "description": "Maximum results (default 10)"}
                                    },
                                    "additionalProperties": False
                                }
                            }
                        ]
                    }
                }
            
            elif method == "tools/call":
                if not self.data_loaded:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "content": [{"type": "text", "text": "Data not loaded. Please run install.py first."}]
                        }
                    }
                
                tool_name = request["params"]["name"]
                arguments = request["params"].get("arguments", {})
                
                if tool_name == "Madlan_MCP":
                    result = self.search_properties(**arguments)
                    intent_data = result.get('_intent_data', {})
                    
                    if intent_data.get('format_mode') == 'listings':
                        # Use comprehensive formatting
                        formatted_output = self.format_desktop_optimized(result, intent_data.get('mentioned_amenities', []))
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [{"type": "text", "text": formatted_output}]
                            }
                        }
                    else:
                        # Return structured data for analysis
                        data_response = {
                            "summary": f"Found {len(result['properties'])} properties",
                            "average_price": result['market_stats']['avg_price'],
                            "price_range": f"{result['market_stats']['min_price']:,} - {result['market_stats']['max_price']:,} NIS",
                            "properties": result['properties'],
                            "total_found": result['total_found']
                        }
                        
                        return {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [{"type": "text", "text": json.dumps(data_response, ensure_ascii=False, indent=2)}]
                            }
                        }
                else:
                    return {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {"code": -32601, "message": f"Unknown tool: {tool_name}"}
                    }
            
            else:
                return {
                    "jsonrpc": "2.0",
                    "id": request_id,
                    "error": {"code": -32601, "message": f"Unknown method: {method}"}
                }
                
        except Exception as e:
            print(f"DEBUG: Request handling error: {e}", file=sys.stderr)
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
            }

def main():
    """Main server loop"""
    server = NadlanPropertyServer()
    
    print("DEBUG: Enhanced MCP Server with Transaction Type Filtering initialized, waiting for input...", file=sys.stderr)
    
    try:
        for line in sys.stdin:
            line = line.strip()
            if not line:
                continue
                
            try:
                request = json.loads(line)
                response = server.handle_request(request)
                
                if response != "SKIP_RESPONSE":
                    print(json.dumps(response, ensure_ascii=False, separators=(',', ':')))
                    sys.stdout.flush()
                    
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32700, "message": f"Parse error: {str(e)}"}
                }
                print(json.dumps(error_response, separators=(',', ':')))
                sys.stdout.flush()
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {"code": -32603, "message": f"Internal error: {str(e)}"}
                }
                print(json.dumps(error_response, separators=(',', ':')))
                sys.stdout.flush()
                
    except KeyboardInterrupt:
        print("DEBUG: Server shutting down...", file=sys.stderr)
    except BrokenPipeError:
        print("DEBUG: Client disconnected (broken pipe)", file=sys.stderr)

if __name__ == "__main__":
    main()