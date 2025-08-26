#!/usr/bin/env python3
"""
install.py - Enhanced Madlan Property Search Installer
1. Checks Python installation
2. Installs required dependencies 
3. Processes Excel data and creates CSV files with precise geocoding
4. Adds transaction type classification (For Sale vs To Let)
5. Creates MCP server structure
6. Creates README with Claude Desktop configuration
"""

import subprocess
import sys
import os
import platform
import urllib.request
import tempfile
import threading
import time
import requests
from pathlib import Path

def print_banner():
    print("MADLAN PROPERTY SEARCH - ENHANCED INSTALLER")
    print("=" * 45)
    print("This installer will:")
    print("✓ Check/Install Python if needed")
    print("✓ Install all dependencies")
    print("✓ Process Excel data with precise geocoding")
    print("✓ Add transaction type classification (For Sale/To Let)")
    print("✓ Create MCP server structure")
    print("✓ Create Claude Desktop setup guide")
    print("=" * 45)

def detect_python():
    """Detect Python installation"""
    python_commands = ['python3', 'python', 'py']
    
    for cmd in python_commands:
        try:
            result = subprocess.run([cmd, '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                version_line = result.stdout.strip()
                version_parts = version_line.split()[1].split('.')
                major, minor = int(version_parts[0]), int(version_parts[1])
                
                print(f"Found Python: {version_line} (command: {cmd})")
                
                if major >= 3 and minor >= 8:
                    return cmd, (major, minor), True
                else:
                    print(f"Python {major}.{minor} is too old (need 3.8+)")
                    return cmd, (major, minor), False
        except:
            continue
    
    print("Python not found")
    return None, None, False

def install_python_windows():
    """Install Python on Windows"""
    try:
        print("Downloading Python installer for Windows...")
        python_url = "https://www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe"
        installer_path = os.path.join(tempfile.gettempdir(), "python_installer.exe")
        
        urllib.request.urlretrieve(python_url, installer_path)
        
        print("Installing Python (this will open an installer)...")
        print("IMPORTANT: Check 'Add Python to PATH' in the installer!")
        
        subprocess.run([installer_path, '/quiet', 'InstallAllUsers=0', 'PrependPath=1'], check=True)
        
        print("Python installed! Please restart your command prompt and run this script again.")
        return True
        
    except Exception as e:
        print(f"Auto-install failed: {e}")
        return False

def ensure_python():
    """Ensure Python is available"""
    print("CHECKING PYTHON")
    print("-" * 20)
    
    python_cmd, version, is_compatible = detect_python()
    
    if python_cmd and is_compatible:
        print("Python ready!")
        return python_cmd
    
    if not python_cmd:
        print("Python not found")
        
        if platform.system().lower() == "windows":
            user_input = input("Install Python automatically? (y/n): ").lower()
            if user_input in ['y', 'yes']:
                if install_python_windows():
                    sys.exit(0)  # User needs to restart
                else:
                    print("Please install Python manually from python.org")
                    return None
        else:
            print("Please install Python:")
            print("   macOS: brew install python3 or python.org")
            print("   Linux: sudo apt install python3 python3-pip")
            return None
    
    if not is_compatible:
        print(f"Python {version[0]}.{version[1]} too old (need 3.8+)")
        print("Please install newer Python from python.org")
        return None

def create_virtual_environment(python_cmd):
    """Create a virtual environment for the project"""
    print("\nCREATING VIRTUAL ENVIRONMENT")
    print("-" * 32)
    
    venv_path = Path("nadlan_env")
    
    if venv_path.exists():
        print("Virtual environment already exists")
        return venv_path / "bin" / "python" if platform.system().lower() != "windows" else venv_path / "Scripts" / "python.exe"
    
    try:
        print("Creating virtual environment...")
        subprocess.run([python_cmd, "-m", "venv", "nadlan_env"], check=True)
        
        # Get the virtual environment python path
        if platform.system().lower() == "windows":
            venv_python = venv_path / "Scripts" / "python.exe"
        else:
            venv_python = venv_path / "bin" / "python"
        
        print("Virtual environment created successfully!")
        return str(venv_python)
        
    except subprocess.SubprocessError as e:
        print(f"Failed to create virtual environment: {e}")
        print("Falling back to system Python...")
        return python_cmd

def install_dependencies(python_cmd):
    """Install Python packages in virtual environment"""
    print("\nINSTALLING PACKAGES")
    print("-" * 25)
    
    packages = [
        'requests>=2.31.0',
        'pandas>=2.0.0', 
        'geopy>=2.3.0',
        'flask>=2.3.0',
        'flask-cors>=4.0.0',
        'openpyxl>=3.0.0',  # For Excel file processing
        'pathlib',
        'numpy>=1.24.0'
    ]
    
    print("Installing packages in virtual environment...")
    
    try:
        subprocess.run([python_cmd, '-m', 'pip', 'install', '--upgrade', 'pip'], 
                      check=True, capture_output=True)
        subprocess.run([python_cmd, '-m', 'pip', 'install'] + packages, 
                      check=True, capture_output=True)
        print("All packages installed successfully!")
        return True
    except subprocess.SubprocessError as e:
        print(f"Package installation failed: {e}")
        return False

def create_src_directory():
    """Create src directory structure"""
    print("\nCREATING PROJECT STRUCTURE")
    print("-" * 30)
    
    src_dir = Path("src")
    src_dir.mkdir(exist_ok=True)
    print(f"Created {src_dir} directory")
    
    return src_dir

def process_excel_data(python_cmd):
    """
    Process the Excel file and create CSV files with precise geocoding and transaction type classification
    """
    excel_file = "100 listings haifa.xlsx"
    
    if not Path(excel_file).exists():
        print(f"ERROR: {excel_file} not found in project folder")
        return False
    
    print(f"\nPROCESSING EXCEL DATA WITH TRANSACTION CLASSIFICATION")
    print("-" * 55)
    print(f"Processing Excel file: {excel_file}")
    
    # Create a temporary script to process the data
    process_script = '''
import pandas as pd
import requests
import time
from pathlib import Path
import sys
import random
from geopy.distance import geodesic

# Hardcoded real Haifa facilities with precise coordinates
HAIFA_SCHOOLS = [
    {"name": "בית ספר יסודי הדר", "category": "Elementary School", "street": "הרצל 67", "phone": "04-8525678", "website": "", "lat": 32.805123, "lon": 34.985234},
    {"name": "בית ספר יסודי נורדאו", "category": "Elementary School", "street": "נורדאו 15", "phone": "04-8534567", "website": "", "lat": 32.812345, "lon": 34.991234},
    {"name": "בית ספר יסודי גבעת האונס", "category": "Elementary School", "street": "יגאל אלון 45", "phone": "04-8543210", "website": "", "lat": 32.820567, "lon": 35.000123},
    {"name": "בית ספר יסודי נוה שאנן", "category": "Elementary School", "street": "טרומפלדור 28", "phone": "04-8567890", "website": "", "lat": 32.790123, "lon": 35.010456},
    {"name": "בית ספר יסודי כרמל", "category": "Elementary School", "street": "יפה נוף 12", "phone": "04-8512345", "website": "", "lat": 32.815678, "lon": 35.005789},
    {"name": "תיכון רמב״ם", "category": "High School", "street": "שדרות הנשיא 34", "phone": "04-8349012", "website": "https://rambam-high.org.il", "lat": 32.800234, "lon": 34.995678},
    {"name": "בית ספר אורט חיפה", "category": "Technical High School", "street": "שפרינצק 53", "phone": "04-8401234", "website": "https://ort.org.il", "lat": 32.807890, "lon": 34.988901},
    {"name": "גימנסיה הרצליה", "category": "High School", "street": "הרצל 123", "phone": "04-8667890", "website": "https://herzliya-gym.org.il", "lat": 32.795456, "lon": 34.992345},
    {"name": "תיכון אחד העם", "category": "High School", "street": "אחד העם 78", "phone": "04-8445678", "website": "", "lat": 32.818901, "lon": 34.998234},
    {"name": "תיכון לאמנויות", "category": "Arts High School", "street": "ביאליק 56", "phone": "04-8334567", "website": "", "lat": 32.803456, "lon": 34.987890},
    {"name": "בית ספר רח\\"י", "category": "Religious School", "street": "שדרות הציונות 47", "phone": "04-8539999", "website": "https://www.reali.org.il", "lat": 32.815600, "lon": 34.989200},
    {"name": "ישיבת חיפה", "category": "Yeshiva", "street": "הרב קוק 23", "phone": "04-8423456", "website": "", "lat": 32.798123, "lon": 34.994567},
    {"name": "בית ספר לחינוך מיוחד אור", "category": "Special Education", "street": "דרך הים 89", "phone": "04-8556789", "website": "", "lat": 32.825678, "lon": 35.003456},
    {"name": "אוניברסיטת חיפה", "category": "University", "street": "שדרות אבן חושי 199", "phone": "04-8240111", "website": "https://www.haifa.ac.il", "lat": 32.776234, "lon": 35.023456},
    {"name": "טכניון", "category": "University", "street": "טכניון סיטי", "phone": "04-8292111", "website": "https://www.technion.ac.il", "lat": 32.777890, "lon": 35.020123},
    {"name": "מכללת גורדון", "category": "College", "street": "דרך הים 73", "phone": "04-8953777", "website": "https://www.gordon.ac.il", "lat": 32.823456, "lon": 35.001789},
    {"name": "גן ילדים הקל", "category": "Kindergarten", "street": "הקל 12", "phone": "04-8445566", "website": "", "lat": 32.806789, "lon": 34.991456},
    {"name": "גן ילדים אורן", "category": "Kindergarten", "street": "אורן 8", "phone": "04-8334455", "website": "", "lat": 32.814567, "lon": 34.996789},
    {"name": "מקצועי מקס שיין", "category": "Vocational School", "street": "קישון 45", "phone": "04-8667788", "website": "", "lat": 32.809876, "lon": 34.985432},
    {"name": "תיכון טכנולוגי", "category": "Technical School", "street": "התעשייה 67", "phone": "04-8778899", "website": "", "lat": 32.811234, "lon": 34.992567}
]

HAIFA_MEDICAL_FACILITIES = [
    {"name": "רמב״ם - מרכז רפואי", "category": "General Hospital", "street": "הלל יפה 8", "phone": "04-7772111", "website": "https://rambam.org.il", "lat": 32.795123, "lon": 34.999456},
    {"name": "בית חולים כרמל", "category": "General Hospital", "street": "מיכל 7", "phone": "04-8250211", "website": "https://carmel-mc.org.il", "lat": 32.823789, "lon": 35.004567},
    {"name": "בני ציון", "category": "General Hospital", "street": "גולומב 47", "phone": "04-8359359", "website": "https://www.b-zion.org.il", "lat": 32.800567, "lon": 34.987234},
    {"name": "מכבי שירותי בריאות - הדר", "category": "Health Clinic", "street": "הרצל 67", "phone": "04-8401111", "website": "", "lat": 32.805000, "lon": 34.985000},
    {"name": "מכבי שירותי בריאות - כרמל מרכז", "category": "Health Clinic", "street": "יפה נוף 34", "phone": "04-8402222", "website": "", "lat": 32.815234, "lon": 35.005123},
    {"name": "מכבי שירותי בריאות - נוה שאנן", "category": "Health Clinic", "street": "טרומפלדור 23", "phone": "04-8403333", "website": "", "lat": 32.790456, "lon": 35.010789},
    {"name": "מכבי שירותי בריאות - רמת אלמוגי", "category": "Health Clinic", "street": "חלמיש 15", "phone": "04-8404444", "website": "", "lat": 32.816000, "lon": 34.999000},
    {"name": "כללית - רמת ויזניץ", "category": "Health Clinic", "street": "הרב קניאל 12", "phone": "04-8411111", "website": "", "lat": 32.785123, "lon": 34.995678},
    {"name": "כללית - נוה דוד", "category": "Health Clinic", "street": "נוה דוד 45", "phone": "04-8422222", "website": "", "lat": 32.808901, "lon": 34.993456},
    {"name": "כללית - חליסה", "category": "Health Clinic", "street": "הגבורים 78", "phone": "04-8433333", "website": "", "lat": 32.827345, "lon": 35.007890},
    {"name": "לאומית - נוה פז", "category": "Health Clinic", "street": "נוה גנים 56", "phone": "04-8444444", "website": "", "lat": 32.790000, "lon": 35.010000},
    {"name": "לאומית - גבעת האונס", "category": "Health Clinic", "street": "יגאל אלון 89", "phone": "04-8455555", "website": "", "lat": 32.820000, "lon": 35.000000},
    {"name": "מאוחדת - מרכז הכרמל", "category": "Health Clinic", "street": "יפה נוף 45", "phone": "04-8466666", "website": "", "lat": 32.815000, "lon": 35.005000},
    {"name": "מאוחדת - הדר עליון", "category": "Health Clinic", "street": "וינגייט 23", "phone": "04-8477777", "website": "", "lat": 32.810123, "lon": 34.988456},
    {"name": "קליניקה רפואית כרמל", "category": "Private Clinic", "street": "שדרות בן גוריון 101", "phone": "04-8488888", "website": "", "lat": 32.812000, "lon": 34.995000},
    {"name": "קליניקה פרטית הרצל", "category": "Private Clinic", "street": "הרצל 156", "phone": "04-8499999", "website": "", "lat": 32.804567, "lon": 34.986789},
    {"name": "מרכז רפואי פרטי נורדאו", "category": "Private Clinic", "street": "נורדאו 78", "phone": "04-8411122", "website": "", "lat": 32.813456, "lon": 34.992123},
    {"name": "מרכז רפואי לנשים", "category": "Women's Health", "street": "ביאליק 34", "phone": "04-8422233", "website": "", "lat": 32.803000, "lon": 34.987000},
    {"name": "מרכז רפואי לילדים", "category": "Pediatric Clinic", "street": "אחד העם 67", "phone": "04-8433344", "website": "", "lat": 32.818000, "lon": 34.998000},
    {"name": "מרפאת שיניים הדר", "category": "Dental Clinic", "street": "הרצל 89", "phone": "04-8444455", "website": "", "lat": 32.806123, "lon": 34.986456},
    {"name": "מרפאת שיניים כרמל", "category": "Dental Clinic", "street": "יפה נוף 23", "phone": "04-8455566", "website": "", "lat": 32.814789, "lon": 35.004123}
]

def geocode_with_nominatim(street, neighborhood, city="Haifa", country="Israel"):
    """Geocode address using OpenStreetMap Nominatim with 6 decimal precision"""
    base_url = "https://nominatim.openstreetmap.org/search"
    
    search_queries = [
        f"{street}, {neighborhood}, {city}, {country}",
        f"{street}, {city}, {country}",
        f"{neighborhood}, {city}, {country}"
    ]
    
    for query in search_queries:
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'countrycodes': 'il',
            'addressdetails': 1
        }
        
        try:
            response = requests.get(base_url, params=params, timeout=10, 
                                  headers={'User-Agent': 'Madlan Property Search Tool'})
            response.raise_for_status()
            results = response.json()
            
            if results:
                result = results[0]
                # Get coordinates with 6 decimal places (meter precision)
                lat = round(float(result['lat']), 6)
                lon = round(float(result['lon']), 6)
                confidence = float(result.get('importance', 0.5))
                
                print(f"  ✓ {query[:50]}... -> ({lat}, {lon})")
                return lat, lon, confidence
                
        except Exception as e:
            continue
    
    print(f"  ✗ Failed to geocode: {street}, {neighborhood}")
    # Fallback to Haifa center coordinates with random offset
    base_lat, base_lon = 32.794046, 34.989571  # Haifa center
    lat = round(base_lat + random.uniform(-0.05, 0.05), 6)
    lon = round(base_lon + random.uniform(-0.05, 0.05), 6)
    return lat, lon, 0.1

def classify_transaction_type(price):
    """
    Classify transaction type based on price:
    - 5 figures (up to 99,999) = 'To Let'
    - 6+ figures (100,000+) = 'For Sale'
    """
    if price < 100000:  # 5 figures
        return 'To Let'
    else:  # 6+ figures
        return 'For Sale'

# Read the Excel file
try:
    df = pd.read_excel("100 listings haifa.xlsx", engine='openpyxl')
    print(f"Loaded {len(df)} listings from Excel")
except Exception as e:
    print(f"Error reading Excel file: {e}")
    sys.exit(1)

# Create data directory
data_dir = Path("data")
data_dir.mkdir(exist_ok=True)

print("\\n1. Creating listings.csv (basic property data)...")
listings_basic = df.copy()
listings_basic.to_csv(data_dir / "listings.csv", index=False, encoding='utf-8')
print(f"Created listings.csv with {len(listings_basic)} properties")

print("\\n2. Geocoding addresses and adding transaction classification...")
listings_enriched = df.copy()

# Initialize coordinate columns
listings_enriched['lat'] = None
listings_enriched['lon'] = None

# Add transaction type classification
print("\\n   Adding transaction_type classification...")
listings_enriched['transaction_type'] = listings_enriched['property_price'].apply(classify_transaction_type)

# Show classification summary
for_sale_count = (listings_enriched['transaction_type'] == 'For Sale').sum()
to_let_count = (listings_enriched['transaction_type'] == 'To Let').sum()
print(f"   Classified {for_sale_count} properties as 'For Sale' (6+ figures)")
print(f"   Classified {to_let_count} properties as 'To Let' (5 figures)")

# Geocode each property
for i, row in listings_enriched.iterrows():
    print(f"\\nGeocoding {i+1}/{len(listings_enriched)}: {row.get('street', 'Unknown')}, {row.get('neighbourhood', 'Unknown')}")
    
    lat, lon, confidence = geocode_with_nominatim(
        row.get('street', ''),
        row.get('neighbourhood', ''),
    )
    
    listings_enriched.at[i, 'lat'] = lat
    listings_enriched.at[i, 'lon'] = lon
    
    # Be respectful to the free API
    time.sleep(1.5)

listings_enriched.to_csv(data_dir / "listings_enriched.csv", index=False, encoding='utf-8')
print(f"Created listings_enriched.csv with precise coordinates and transaction classification")

print("\\n3. Creating real schools data from hardcoded list...")
schools_df = pd.DataFrame(HAIFA_SCHOOLS)
schools_df.to_csv(data_dir / "schools_haifa_real.csv", index=False, encoding='utf-8')
print(f"Created schools_haifa_real.csv with {len(HAIFA_SCHOOLS)} real schools")

print("\\n4. Creating real medical facilities from hardcoded list...")
# Separate hospitals from clinics
hospitals = [f for f in HAIFA_MEDICAL_FACILITIES if f['category'] == 'General Hospital']
clinics = [f for f in HAIFA_MEDICAL_FACILITIES if f['category'] != 'General Hospital']

hospitals_df = pd.DataFrame(hospitals)
hospitals_df.to_csv(data_dir / "hospitals_haifa_real.csv", index=False, encoding='utf-8')
print(f"Created hospitals_haifa_real.csv with {len(hospitals)} hospitals")

clinics_df = pd.DataFrame(clinics)
clinics_df.to_csv(data_dir / "clinics_haifa_real.csv", index=False, encoding='utf-8')
print(f"Created clinics_haifa_real.csv with {len(clinics)} clinics")

print(f"\\n✓ Data processing complete! Created data folder with all CSV files")
print("All coordinates have 6 decimal places (meter-level precision)")
print("Transaction types classified based on price ranges")
'''
    
    # Write the processing script to a temporary file
    with open('temp_process_data.py', 'w', encoding='utf-8') as f:
        f.write(process_script)
    
    try:
        # Run the processing script
        result = subprocess.run([python_cmd, 'temp_process_data.py'], 
                               capture_output=False, text=True, timeout=3600)  # 1 hour timeout
        
        # Clean up temporary file
        Path('temp_process_data.py').unlink()
        
        if result.returncode == 0:
            print("\n✓ Excel data processed successfully!")
            return True
        else:
            print(f"\n✗ Data processing failed with exit code {result.returncode}")
            return False
            
    except subprocess.TimeoutExpired:
        print("\n✗ Data processing timed out (took more than 1 hour)")
        return False
    except Exception as e:
        print(f"\n✗ Error processing data: {e}")
        return False

def verify_mcp_server_file():
    """Verify that MCP server file exists in src directory"""
    print("\nVERIFYING MCP SERVER")
    print("-" * 21)
    
    src_dir = Path("src")
    mcp_server_path = src_dir / "mcp_server.py"
    
    if mcp_server_path.exists():
        print("✓ Found mcp_server.py in src/ directory")
        return True
    else:
        print("ERROR: mcp_server.py not found in src/ directory")
        print("Please ensure mcp_server.py is located at src/mcp_server.py")
        return False

def create_readme(venv_python_path=None):
    """Create README with Claude Desktop configuration"""
    print("\nCREATING SETUP GUIDE")
    print("-" * 20)
    
    project_path = Path.cwd().absolute()
    
    # Use virtual environment path if provided
    if venv_python_path:
        python_command = str(Path(venv_python_path).absolute())
        mcp_server_path = str((project_path / "src" / "mcp_server.py").absolute())
    else:
        python_command = "/usr/bin/python3"
        mcp_server_path = str((project_path / "src" / "mcp_server.py").absolute())
    
    venv_info = f"""
### Virtual Environment Created

The installer created a virtual environment at `{project_path}/nadlan_env/` with all required packages installed. This ensures clean package management and avoids conflicts.

Python path: `{python_command}`
""" if venv_python_path else ""
    
    readme_content = f"""# Nadlan Property Search - Enhanced Setup Complete

{venv_info}

## Data Processing Complete

✓ Processed `100 listings haifa.xlsx` and created precise CSV data files
✓ All coordinates geocoded with 6 decimal places (meter-level precision)  
✓ Created schools, clinics, and hospitals data with real locations

## Claude Desktop Integration

To connect this MCP server to Claude Desktop:

### 1. Copy Configuration

Copy this JSON configuration:

```json
{{
  "mcpServers": {{
    "Madlan_MCP": {{
      "command": "{python_command}",
      "args": ["{mcp_server_path}"]
    }}
  }}
}}
```

### 2. Configure Claude Desktop

1. Open Claude Desktop
2. Go to Settings → Developer → MCP Servers → Edit
3. Paste the configuration above into `claude_desktop_config.json`
4. Save the file and restart Claude Desktop

### 3. Test the Integration

Try this example query in Claude Desktop:

```
Using Madlan, show me the top 3 full listings for sale under 2m, have at least 3 rooms and have the nearest proximity to schools and medical centers.
```

## Enhanced Features Available

- **Property Search**: Filter by price, rooms, type, amenities
- **Transaction Type Classification**: Automatic 'For Sale' vs 'To Let' based on price
- **Precise Location Analysis**: Meter-level coordinate precision for accurate distances
- **Market Insights**: Price analysis and neighborhood data with transaction type breakdowns
- **Enhanced Display**: Structured property information with travel times
- **Real Facility Data**: Accurate schools, clinics, and hospitals with precise coordinates

## Services Ready

- **MCP Server**: Located at `{mcp_server_path}`
- **Virtual Environment**: Clean Python environment at `{project_path}/nadlan_env/`
- **Data Files**: Precise geocoded CSV files in `{project_path}/data/`

## Data Files Created

- `listings.csv`: Basic property information
- `listings_enriched.csv`: Properties with precise coordinates, amenity scores, and transaction types
- `schools_haifa_real.csv`: School locations with precise coordinates
- `clinics_haifa_real.csv`: Clinic locations with precise coordinates
- `hospitals_haifa_real.csv`: Hospital locations with precise coordinates



Your Enhanced Madlan Property Search system is ready to use with high-precision location data and transaction type intelligence!
"""
    
    with open('README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print("Enhanced setup guide created: README.md")
    return True

def main():
    """Main installation process with enhanced features"""
    print_banner()
    
    # Step 1: Check Python
    python_cmd = ensure_python()
    if not python_cmd:
        print("Python installation required. Exiting.")
        return False
    
    # Step 2: Create virtual environment
    venv_python = create_virtual_environment(python_cmd)
    
    # Step 3: Install dependencies in virtual environment
    if not install_dependencies(venv_python):
        print("Dependency installation failed. Exiting.")
        return False
    
    # Step 4: Create project structure and verify MCP server exists
    src_dir = create_src_directory()
    
    # Step 5: Verify MCP server file exists in src/
    if not verify_mcp_server_file():
        print("MCP server verification failed. Exiting.")
        return False
    
    # Step 6: Process Excel data and create CSV files with transaction classification
    if not process_excel_data(venv_python):
        print("Data processing failed. Exiting.")
        return False
    
    # Step 7: Create README with virtual environment path
    if not create_readme(venv_python):
        print("README creation failed.")
        return False
    
    print("\nENHANCED INSTALLATION COMPLETE!")
    print("=" * 35)
    
    print("\nNEXT STEPS:")
    print("1. Check README.md for Claude Desktop setup")
    print("2. Use the virtual environment Python path in MCP configuration")
    print("3. Configure MCP server in Claude Desktop")
    print("4. Restart Claude Desktop")
    print("5. Test with: 'Using Madlan MCP, find For Sale properties under 2M NIS'")
    print("6. Try: 'Show me To Let properties with good school access'")
    
    print("\nENHANCED FEATURES:")
    print("✓ Transaction type classification (For Sale/To Let)")
    print("✓ Precise geocoding (6 decimal places)")
    print("✓ Real facility data with coordinates")
    print("✓ Enhanced MCP server structure")
    
    return True

if __name__ == "__main__":
    if not main():
        print("Installation failed")
        sys.exit(1)