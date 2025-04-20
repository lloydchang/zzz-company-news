import csv
import os

def load_news_items(csv_file="aggregated-news.csv"):
    """
    Load news items from the aggregated CSV file
    
    Args:
        csv_file: Path to the CSV file to load
        
    Returns:
        List of news items as dictionaries
    """
    news_items = []
    with open(csv_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            news_items.append(row)
    return news_items

def create_company_mapping():
    """
    Create a mapping of titles to company names from individual company CSV files
    
    Returns:
        Dictionary mapping news titles to company names
    """
    company_mapping = {}
    
    # First, create a mapping of titles to companies from individual CSV files
    for csv_file in os.listdir():
        if (csv_file.startswith("news-") and csv_file.endswith(".csv")):
            company_name = csv_file[5:-4]  # Remove "news-" and ".csv"
            try:
                with open(csv_file, 'r', encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        if "title" in row:
                            company_mapping[row["title"]] = company_name
            except Exception as e:
                print(f"Error reading {csv_file}: {e}")
                
    return company_mapping
