import os
import sys
import shutil
import zipfile
import subprocess
import urllib.request
from urllib.parse import urlparse
from dotenv import load_dotenv, find_dotenv

# Configuration
SC_VERSION = "16.20.5" # 16.x is stable and widely used
SC_URL = f"https://github.com/schemacrawler/SchemaCrawler/releases/download/v{SC_VERSION}/schemacrawler-{SC_VERSION}-distribution.zip"
SC_DIR = os.path.join(os.getcwd(), "schemacrawler_dist")
SC_EXECUTABLE = os.path.join(SC_DIR, f"schemacrawler-{SC_VERSION}-distribution", "_schemacrawler", "bin", "schemacrawler.sh")

# Load environment variables
load_dotenv(find_dotenv())

def check_dependencies():
    # Check for Graphviz (dot)
    if shutil.which("dot") is None:
        print("❌ Graphviz ('dot') is not installed.")
        print("👉 Please run: brew install graphviz")
        sys.exit(1)

    # Check for Java
    if shutil.which("java") is None:
        print("❌ Java is not installed.")
        print("👉 Please install Java (required for SchemaCrawler).")
        sys.exit(1)

def setup_schemacrawler():
    # Check if we have the local script
    if os.path.exists(SC_EXECUTABLE):
        os.chmod(SC_EXECUTABLE, 0o755)
        return SC_EXECUTABLE
    
    # Check if global schemacrawler exists
    if shutil.which("schemacrawler"):
        return "schemacrawler"

    print(f"⬇️  SchemaCrawler not found. Downloading v{SC_VERSION}...")
    
    zip_path = os.path.join(os.getcwd(), "schemacrawler.zip")
    
    try:
        # Download
        with urllib.request.urlopen(SC_URL) as response, open(zip_path, 'wb') as out_file:
            shutil.copyfileobj(response, out_file)
        
        print("📦 Extracting SchemaCrawler...")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(SC_DIR)
            
        # Cleanup zip
        os.remove(zip_path)
        
        # Make executable
        os.chmod(SC_EXECUTABLE, 0o755)
        
        print(f"✅ SchemaCrawler installed to {SC_DIR}")
        return SC_EXECUTABLE

    except Exception as e:
        print(f"❌ Failed to download/setup SchemaCrawler: {e}")
        if os.path.exists(zip_path):
            os.remove(zip_path)
        sys.exit(1)

def run_schemacrawler():
    url_str = os.environ.get("TIMESCALE_SERVICE_URL")
    if not url_str:
        print("Error: TIMESCALE_SERVICE_URL not found in .env")
        exit(1)

    # Handle cases where the scheme might be postgresql:// or postgres://
    if url_str.startswith("postgres://"):
        url_str = url_str.replace("postgres://", "postgresql://", 1)

    # Parse URL
    try:
        parsed = urlparse(url_str)
    except Exception as e:
        print(f"Error parsing URL: {e}")
        exit(1)
        
    sc_cmd = setup_schemacrawler()
    
    # Construct SchemaCrawler command
    # Filter to only show our application tables in the public schema
    # Regex matches: public followed by one of our table names
    our_tables = "restaurant_table|customer|staff|reservation|menu_category|menu_item|restaurant_order|order_item|shift|payment"
    table_filter = f"^public\\.({our_tables})$"

    cmd = [
        sc_cmd,
        "--server=postgresql",
        f"--host={parsed.hostname}",
        f"--port={parsed.port or 5432}",
        f"--database={parsed.path.lstrip('/')}",
        f"--user={parsed.username}",
        f"--password={parsed.password}",
        "--command=schema",
        "--output-file=schema.png",
        "--info-level=standard",
        "--table-types=TABLE",     # Only real tables, no views
        f"--grep-tables={table_filter}", # Only our specific tables
    ]

    print("🚀 Generating filtered schema diagram...")
    # Debug print
    debug_cmd = list(cmd)
    debug_cmd[6] = "--password=******"
    print(f"Executing: {' '.join(debug_cmd)}")

    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Schema image generated successfully: ./schema.png")
        else:
            print("❌ Error generating schema:")
            print(result.stderr)
            print(result.stdout)
    except Exception as e:
        print(f"❌ An unexpected error occurred: {e}")

if __name__ == "__main__":
    check_dependencies()
    run_schemacrawler()
