import json
from pathlib import Path

PROCESSED_DIR = Path(__file__).parent.parent / "data" / "processed"

# Mapping of internal section keys to human-readable labels for context enrichment
SECTION_LABELS = {
    "overview": "Overview",
    "expense_ratio": "Expense Ratio",
    "exit_load": "Exit Load",
    "minimum_investment": "Minimum Investment",
    "benchmark": "Benchmark Index",
    "tax": "Tax Implications",
    "fund_management": "Fund Manager(s)",
    "investment_objective": "Investment Objective",
    "fund_house": "Fund House"
}

def create_chunks():
    input_file = PROCESSED_DIR / "corpus_sections.json"
    if not input_file.exists():
        print(f"Error: {input_file} not found. Run parse.py first.")
        return

    with open(input_file, "r", encoding="utf-8") as f:
        funds = json.load(f)

    all_chunks = []

    for fund in funds:
        fund_id = fund.get("fund_id")
        url = fund.get("url")
        fetch_timestamp = fund.get("fetch_timestamp")
        sections = fund.get("sections", {})
        
        # The overview usually contains the fund name itself, 
        # but let's safely get it for enrichment context.
        fund_name = sections.get("overview", fund_id.replace("-", " ").title())

        for section_key, section_content in sections.items():
            if not section_content or section_content == "N/A":
                continue # Skip empty data
                
            label = SECTION_LABELS.get(section_key, section_key.replace("_", " ").title())
            
            # Construct the context-enriched text
            if section_key == "overview":
                chunk_text = f"Fund Name: {fund_name}. {label}: {section_content}."
            else:
                chunk_text = f"Fund Name: {fund_name}. {label}: {section_content}."
                
            # Create the metadata dictionary
            metadata = {
                "fund_id": fund_id,
                "source_url": url,
                "fetch_timestamp": fetch_timestamp,
                "section": section_key
            }
            
            all_chunks.append({
                "text": chunk_text,
                "metadata": metadata
            })

    output_file = PROCESSED_DIR / "chunks.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_chunks, f, indent=4, ensure_ascii=False)

    print(f"Successfully generated {len(all_chunks)} context-enriched chunks.")
    print(f"Saved to {output_file}")

if __name__ == "__main__":
    create_chunks()
