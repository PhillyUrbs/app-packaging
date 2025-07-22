import requests
import time
from pathlib import Path
import json

domain_path = "itninja.com/software"
output_dir = Path("html")
output_dir.mkdir(exist_ok=True)

# Step 1: Fetch all available snapshots
cdx_api = f"http://web.archive.org/cdx/search/cdx?url={domain_path}&output=json&fl=timestamp,original"
response = requests.get(cdx_api)
snapshots = response.json()[1:]  # skip headers

print(f"Found {len(snapshots)} snapshots...")

# Save index
Path("metadata").mkdir(exist_ok=True)
with open("metadata/snapshot_index.json", "w") as f:
    json.dump([{"timestamp": ts, "url": url} for ts, url in snapshots], f, indent=2)

# Step 2: Download each snapshot
for ts, original_url in snapshots:
    archive_url = f"https://web.archive.org/web/{ts}id_/{original_url}"
    output_file = output_dir / f"{ts}.html"

    if output_file.exists():
        continue  # skip if already downloaded

    try:
        res = requests.get(archive_url, timeout=15)
        res.raise_for_status()
        output_file.write_text(res.text, encoding='utf-8')
        print(f"✅ {ts} downloaded")
    except Exception as e:
        print(f"⚠️  {ts} failed: {e}")

    time.sleep(1.5)  # be respectful to archive.org
