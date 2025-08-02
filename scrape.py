import argparse
import requests
import time
from pathlib import Path
import json
from urllib.parse import urlparse

# Parse command-line arguments
parser = argparse.ArgumentParser(description="Download snapshots from Wayback Machine.")
parser.add_argument("--retry-failed", action="store_true", help="Retry failed downloads.")
args = parser.parse_args()

domain_path = "itninja.com/software*"  # Updated to include wildcard for recursion
output_dir = Path("html")
output_dir.mkdir(exist_ok=True)

# Step 1: Fetch all available snapshots
cdx_api = f"http://web.archive.org/cdx/search/cdx?url={domain_path}&output=json&fl=timestamp,original"

# Check if the API response file already exists
api_response_file = Path("metadata/deduped_api_response.json")
if api_response_file.exists():
    print("Loading snapshots from saved API response file...")
    with open(api_response_file, "r") as f:
        snapshots = json.load(f)[1:]  # skip headers
else:
    print(f"Fetching snapshots from: {cdx_api}")
    response = requests.get(cdx_api)

    # Debugging: Check the API response
    if response.status_code != 200:
        print(f"⚠️  API request failed with status code {response.status_code}")
        print(f"Response content: {response.text}")
        exit(1)

    snapshots = response.json()[1:]  # skip headers

    # Debugging: Check if snapshots are empty
    if not snapshots:
        print("⚠️  No snapshots found. Verify the domain_path and API query.")
        exit(1)

    print(f"Found {len(snapshots)} snapshots...")

    # Save API response to a file
    api_response_file.write_text(response.text, encoding='utf-8')

# Load failed downloads if retry-failed is not passed
failed_downloads_file = Path("metadata/failed_downloads.json")
failed_downloads = set()
if failed_downloads_file.exists() and not args.retry_failed:
    with open(failed_downloads_file, "r") as f:
        failed_downloads = {json.loads(line)["timestamp"] for line in f}

# Save index
Path("metadata").mkdir(exist_ok=True)
with open("metadata/snapshot_index.json", "w") as f:
    json.dump([{"timestamp": ts, "url": url} for ts, url in snapshots], f, indent=2)

# Define the number of retries as a variable
MAX_RETRIES = 4  # Number of retries before a download is deemed a failure

# Step 2: Download each snapshot
for index, (ts, original_url) in enumerate(snapshots, start=1):
    if ts in failed_downloads:
        print(f"Skipping previously failed snapshot: {ts}")
        continue

    print(f"Processing record {index} / {len(snapshots)}")  # Add progress output

    archive_url = f"https://web.archive.org/web/{ts}id_/{original_url}"

    # Parse timestamp to create folder structure
    year, month, day = ts[:4], ts[4:6], ts[6:8]
    output_subdir = output_dir / year / month / day
    output_subdir.mkdir(parents=True, exist_ok=True)

    # Extract original filename and retain extension
    parsed_url = urlparse(original_url)
    original_filename = Path(parsed_url.path).name or "index.html"
    if not Path(original_filename).suffix:  # Default to .html if no extension
        original_filename += ".html"
    output_file = output_subdir / original_filename

    if output_file.exists():
        continue  # skip if already downloaded

    retries = MAX_RETRIES  # Use the variable for retries
    while retries > 0:
        try:
            res = requests.get(archive_url, timeout=15)
            if res.status_code == 429:  # Too Many Requests
                print("⚠️  API limit reached. Waiting for 60 seconds...")
                time.sleep(60)
                continue
            res.raise_for_status()
            output_file.write_text(res.text, encoding='utf-8')
            print(f"✅ {ts} downloaded to {output_file}")
            break
        except requests.exceptions.RequestException as e:
            print(f"⚠️  {ts} failed: {e}")
            retries -= 1
            if retries > 0:
                print(f"Retrying {ts}... ({retries} retries left)")
                time.sleep(20)  # Wait before retrying
            else:
                print(f"❌ {ts} permanently failed after {MAX_RETRIES} attempts.")
                # Log the failure in real time
                with open(failed_downloads_file, "a") as f:
                    json.dump({"timestamp": ts, "url": original_url, "error": str(e)}, f)
                    f.write("\n")
                break

    time.sleep(4)  # Adjusted to 4 seconds to stay within 15 requests per minute
