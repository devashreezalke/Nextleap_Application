import os
import time
import requests
from pathlib import Path

TARGET_URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
]

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def fetch_all():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    for url in TARGET_URLS:
        fund_id = url.split("/")[-1]
        output_path = RAW_DIR / f"{fund_id}.html"
        
        try:
            print(f"Fetching {url}...")
            response = requests.get(url, headers=HEADERS, timeout=10)
            response.raise_for_status()
            
            # Save raw HTML with fetch timestamp metadata inside a header comment
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            content = f"<!-- FETCH_TIMESTAMP: {timestamp} | URL: {url} -->\n" + response.text
            
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
                
            print(f"Saved to {output_path}")
            
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            
        time.sleep(2) # rate limit

if __name__ == "__main__":
    fetch_all()
