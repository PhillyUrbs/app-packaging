import json
from pathlib import Path

# Load the API response file
input_file = Path("metadata/api_response.json")
output_file = Path("metadata/deduped_api_response.json")

with open(input_file, "r") as f:
    data = json.load(f)

# Skip the header row
header, *rows = data

# Create a dictionary to store the latest snapshot for each URL
latest_snapshots = {}

for timestamp, url in rows:
    if url not in latest_snapshots or timestamp > latest_snapshots[url]:
        latest_snapshots[url] = timestamp

# Prepare the deduplicated data
deduped_data = [header] + [[ts, url] for url, ts in latest_snapshots.items()]

# Save the deduplicated data to a new file
with open(output_file, "w") as f:
    json.dump(deduped_data, f, indent=2)

print(f"Deduplicated data saved to {output_file}")
