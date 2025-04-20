#!/usr/bin/env python3
"""
Main entry point for the news HTML dashboard generator.
This script coordinates the overall process of generating the HTML dashboard.
"""

import os
import datetime
from data_loader import load_news_items, create_company_mapping
from web_utils import fetch_url_content
from cache_manager import load_cache, save_cache, prepare_news_data
from html_generator import generate_html_head_and_styles, generate_news_items_html, generate_chatbot_html
from js_generator import generate_chatbot_js

def main():
    """
    Main function that coordinates the process of generating the HTML dashboard
    """
    print("Starting HTML dashboard generation...")
    
    # Step 1: Load news items from CSV
    news_items = load_news_items()
    print(f"Loaded {len(news_items)} news items")
    
    # Step 2: Create company mapping
    company_mapping = create_company_mapping()
    print(f"Created mapping for {len(company_mapping)} titles to companies")
    
    # Step 3: Load cache
    cached_news_data = load_cache()
    
    # Step 4: Prepare news data for JavaScript, fetching full content where needed
    news_data_for_js, updated_cache = prepare_news_data(news_items, cached_news_data, fetch_url_content)
    
    # Step 5: Save updated cache
    save_cache(updated_cache)
    
    # Step 6: Generate HTML content
    html_content = generate_html_head_and_styles()
    html_content += generate_news_items_html(news_items)
    html_content += generate_chatbot_html(news_data_for_js)
    
    # Insert the JavaScript before the closing </script> tag
    js_code = generate_chatbot_js()
    html_content = html_content.replace('</script>', f'{js_code}\n    </script>')
    
    # Step 7: Write the HTML file
    with open("index.html", "w", encoding="utf-8") as file:
        file.write(html_content)
    
    print("HTML dashboard created successfully!")

if __name__ == "__main__":
    main()
