# Copilot Instructions for ITNinja Software Archive

## Overview
This repository archives snapshots of the ITNinja.com/software page using the Wayback Machine. The project is structured to download, parse, and store data from archived snapshots.

### Key Components
- **`metadata/`**: Contains metadata files like `snapshot_index.json` (timestamps and URLs of snapshots).
- **`html/`**: Stores raw HTML files downloaded from the Wayback Machine.
- **`extracted/`**: Contains parsed data extracted from the HTML files.
- **`scrape.py`**: Main script for downloading snapshots and saving them to the `html/` directory.
- **`dedupe_api_response.py`**: Script to deduplicate snapshot data, keeping only the latest version of each URL.

## Developer Workflows
### Running the Scraper
1. Ensure Python 3.10+ is installed.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the scraper:
   ```bash
   python scrape.py
   ```
   - Use `--retry-failed` to retry previously failed downloads.

### Deduplicating Snapshots
1. Run the deduplication script:
   ```bash
   python dedupe_api_response.py
   ```
   - This will create a deduplicated version of `api_response.json` in `metadata/deduped_api_response.json`.

## Project-Specific Conventions
- **File Naming**: HTML files are saved in a folder structure based on the timestamp (`YYYY/MM/DD`) and retain their original filenames.
- **Error Handling**: Failed downloads are logged in `metadata/failed_downloads.json`.
- **Retry Logic**: Use the `--retry-failed` flag to reattempt failed downloads.

## Integration Points
- **Wayback Machine CDX API**: Used to fetch snapshot metadata.
- **BeautifulSoup**: Used for parsing HTML files (install with `pip install beautifulsoup4`).

## Examples
### Adding a New Feature
To add a feature for extracting additional metadata from HTML files:
1. Modify `scrape.py` to include parsing logic using BeautifulSoup.
2. Save extracted data to the `extracted/` directory.

### Debugging
- Check `metadata/failed_downloads.json` for failed snapshots.
- Use `print` statements to debug API responses or parsing logic.

## Key Files
- `scrape.py`: Main script for downloading and processing snapshots.
- `dedupe_api_response.py`: Handles deduplication of snapshot data.
- `metadata/snapshot_index.json`: Index of all snapshots.
- `metadata/failed_downloads.json`: Logs of failed downloads.

## Notes
- Ensure all scripts are run from the root directory of the repository.
- Use Python 3.10+ for compatibility.

Feel free to update this document as the project evolves.
