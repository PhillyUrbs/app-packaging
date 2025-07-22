from bs4 import BeautifulSoup
from pathlib import Path
import json

html_dir = Path("html")
output_file = Path("extracted/app_links.json")
output_file.parent.mkdir(exist_ok=True)

all_links = {}

for html_file in html_dir.glob("*.html"):
    soup = BeautifulSoup(html_file.read_text(encoding='utf-8'), "html.parser")
    links = sorted(set(
        a['href'] for a in soup.find_all('a', href=True)
        if '/software/' in a['href'] and a['href'].count('/') >= 3
    ))
    all_links[html_file.stem] = links
    print(f"{html_file.name}: {len(links)} links extracted")

output_file.write_text(json.dumps(all_links, indent=2))
