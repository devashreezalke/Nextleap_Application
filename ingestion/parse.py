import os
import json
import re
from pathlib import Path
from bs4 import BeautifulSoup

RAW_DIR = Path(__file__).parent.parent / "data" / "raw"
PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

def extract_sections(html_content: str) -> dict:
    """Extract scheme-specific content into structured sections."""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # 1. Parse JSON data from Next.js state (Groww stores structured data here)
    script_tag = soup.find('script', id='__NEXT_DATA__')
    mf_data = {}
    if script_tag and script_tag.string:
        try:
            next_data = json.loads(script_tag.string)
            mf_data = next_data.get('props', {}).get('pageProps', {}).get('mfServerSideData', {})
        except json.JSONDecodeError:
            pass

    # 2. Extract specific sections as requested
    sections = {
        "overview": mf_data.get("scheme_name", ""),
        "expense_ratio": str(mf_data.get("expense_ratio", "N/A")) + "%" if mf_data.get("expense_ratio") else "N/A",
        "exit_load": mf_data.get("exit_load", "N/A"),
        "minimum_investment": f"Lumpsum: {mf_data.get('min_investment_amount', 'N/A')}, SIP: {mf_data.get('min_sip_investment', 'N/A')}",
        "benchmark": mf_data.get("benchmark_name", "N/A"),
        "fund_house": mf_data.get("fund_house", "N/A"),
        "investment_objective": mf_data.get("description", "N/A"),
        "tax": "N/A",
        "fund_management": "N/A"
    }

    # Format fund management
    managers = mf_data.get("fund_manager_details", [])
    if managers:
        sections["fund_management"] = ", ".join([m.get("name", "Unknown") for m in managers])
    elif mf_data.get("fund_manager"):
        sections["fund_management"] = mf_data.get("fund_manager")
        
    # Tax implications are often in 'stats' or 'analysis' or text
    # Fallback to BeautifulSoup text extraction for tax if not found in JSON
    tax_header = soup.find(string=re.compile("Tax Implication", re.I))
    if tax_header and tax_header.parent:
        tax_container = tax_header.parent.find_next_sibling()
        if tax_container:
            sections["tax"] = tax_container.get_text(separator=" ", strip=True)
            
    # If the JSON data is completely empty (site changed), do fallback extraction
    if not mf_data:
        title_tag = soup.find("h1")
        sections["overview"] = title_tag.get_text(strip=True) if title_tag else "Unknown Fund"
        
        # General stripping of chrome
        for element in soup(["script", "style", "nav", "footer", "header", "aside", "svg"]):
            element.decompose()
        
        text_blocks = [p.get_text(strip=True) for p in soup.find_all(['p', 'div', 'span']) if len(p.get_text(strip=True)) > 20]
        sections["overview"] += "\n" + "\n".join(text_blocks[:5]) # just take first few text blocks

    return sections

def parse_all():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    if not RAW_DIR.exists():
        print("Raw directory not found. Please run fetch.py first.")
        return
        
    all_funds = []
    
    for html_file in RAW_DIR.glob("*.html"):
        with open(html_file, "r", encoding="utf-8") as f:
            content = f.read()
            
        # Extract timestamp and URL from the comment we added in fetch.py
        timestamp_match = re.search(r"<!-- FETCH_TIMESTAMP: (.*?) \| URL: (.*?) -->", content)
        timestamp = timestamp_match.group(1) if timestamp_match else "Unknown"
        url = timestamp_match.group(2) if timestamp_match else "Unknown"
        
        sections = extract_sections(content)
        
        fund_data = {
            "fund_id": html_file.stem,
            "url": url,
            "fetch_timestamp": timestamp,
            "sections": sections
        }
        
        all_funds.append(fund_data)
        print(f"Parsed {html_file.name}")
        
    output_path = PROCESSED_DIR / "corpus_sections.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(all_funds, f, indent=4, ensure_ascii=False)
        
    print(f"Saved extracted sections for {len(all_funds)} funds to {output_path}")

if __name__ == "__main__":
    parse_all()
