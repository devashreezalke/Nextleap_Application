import os
import time
import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path

# The 5 HDFC specific URLs from Groww
TARGET_URLS = [
    "https://groww.in/mutual-funds/hdfc-mid-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-large-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-small-cap-fund-direct-growth",
    "https://groww.in/mutual-funds/hdfc-gold-etf-fund-of-fund-direct-plan-growth",
    "https://groww.in/mutual-funds/hdfc-defence-fund-direct-growth"
]

DATA_DIR = Path(__file__).parent.parent / "data"
SNAPSHOTS_DIR = DATA_DIR / "snapshots"
PROCESSED_DIR = DATA_DIR / "processed"

# Headers to mimic a real browser to prevent basic blocking
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def setup_directories():
    """Ensure data directories exist."""
    SNAPSHOTS_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def fetch_html(url: str, fund_id: str) -> str:
    """Fetch HTML from URL or fallback to local snapshot."""
    snapshot_file = SNAPSHOTS_DIR / f"{fund_id}.html"
    
    try:
        print(f"Fetching {url} ...")
        response = requests.get(url, headers=HEADERS, timeout=10)
        response.raise_for_status()
        html_content = response.text
        
        # Save snapshot
        with open(snapshot_file, "w", encoding="utf-8") as f:
            f.write(html_content)
        return html_content
        
    except Exception as e:
        print(f"Failed to fetch {url}: {e}")
        if snapshot_file.exists():
            print(f"Using local snapshot for {fund_id}.")
            with open(snapshot_file, "r", encoding="utf-8") as f:
                return f.read()
        else:
            print(f"No local snapshot available for {fund_id}.")
            return ""

def clean_html(html_content: str) -> BeautifulSoup:
    """Strip out boilerplate (scripts, styles, navs) and return BeautifulSoup object."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Remove unwanted tags
    for element in soup(["script", "style", "nav", "footer", "header", "aside", "svg"]):
        element.decompose()
        
    return soup

def extract_metrics(soup: BeautifulSoup, url: str) -> dict:
    """
    Extract readable text and basic metrics.
    Since DOM structures change, we extract clean text to serve as our RAG corpus.
    """
    # Extract Title (h1)
    title_tag = soup.find("h1")
    title = title_tag.get_text(strip=True) if title_tag else "Unknown Fund"
    
    # Get all text blocks
    text_blocks = []
    for p in soup.find_all(['p', 'div', 'span', 'td', 'th']):
        text = p.get_text(strip=True)
        if len(text) > 20: # filter out very short UI labels
            text_blocks.append(text)
            
    # Join the text to form our chunkable corpus
    corpus_text = "\n".join(text_blocks)
    
    return {
        "title": title,
        "url": url,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "content": corpus_text
    }

def run_scraper():
    setup_directories()
    
    scraped_data = []
    
    for url in TARGET_URLS:
        # Generate a simple fund ID from the URL
        fund_id = url.split("/")[-1]
        
        html = fetch_html(url, fund_id)
        if not html:
            continue
            
        soup = clean_html(html)
        fund_data = extract_metrics(soup, url)
        
        scraped_data.append(fund_data)
        
        # Respect rate limits
        time.sleep(2)
        
    # Save the processed data
    output_file = PROCESSED_DIR / "corpus.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=4, ensure_ascii=False)
        
    print(f"Successfully scraped and processed {len(scraped_data)} funds. Data saved to {output_file}.")

if __name__ == "__main__":
    run_scraper()
