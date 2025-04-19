import csv
import html
import datetime
import os
import json
import requests
from bs4 import BeautifulSoup
import time
import random

# Read the CSV file
news_items = []
with open("aggregated-news.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        news_items.append(row)

# Better company detection - create a mapping first
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

# Generate HTML content
html_content = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f5f5f5;
        }
        h1 {
            color: #333;
            text-align: center;
            margin-bottom: 30px;
        }
        .news-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 20px;
        }
        .news-card {
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
            padding: 20px;
            transition: transform 0.2s ease;
        }
        .news-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        }
        .news-title {
            font-size: 18px;
            margin-top: 0;
        }
        .news-source {
            color: #666;
            font-size: 14px;
            margin-bottom: 10px;
        }
        .company-tag {
            display: inline-block;
            background-color: #e0f7fa;
            color: #006064;
            padding: 3px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .news-date {
            color: #888;
            font-size: 12px;
            margin-top: 10px;
        }
        .timestamp {
            text-align: center;
            color: #999;
            font-size: 12px;
            margin-top: 40px;
        }
        a {
            color: #0066cc;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
        }
        /* Image thumbnail styles */
        .news-image {
            margin-bottom: 15px;
            max-height: 180px;
            overflow: hidden;
            border-radius: 6px;
        }
        .news-image img {
            width: 100%;
            height: 180px;
            object-fit: cover;
            display: block;
            transition: transform 0.3s ease;
        }
        .news-card:hover .news-image img {
            transform: scale(1.05);
        }
        
        /* Chatbot styles */
        .chatbot-container {
            position: fixed;
            top: 20px;
            right: 20px;
            width: 350px;
            height: calc(100vh - 40px);
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            z-index: 1000;
            transition: transform 0.3s ease, opacity 0.3s ease;
            transform: translateX(110%);
            opacity: 0;
            overflow: hidden;
        }
        
        .chatbot-container.active {
            transform: translateX(0);
            opacity: 1;
        }
        
        .chatbot-header {
            background-color: #0066cc;
            color: white;
            padding: 15px;
            border-radius: 10px 10px 0 0;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        
        .chatbot-title {
            font-weight: bold;
            margin: 0;
        }
        
        .chatbot-messages {
            flex: 1;
            padding: 15px;
            overflow-y: auto;
            display: flex;
            flex-direction: column;
            max-height: calc(100vh - 140px);
        }
        
        .message {
            margin-bottom: 10px;
            max-width: 80%;
            padding: 10px 15px;
            border-radius: 18px;
            line-height: 1.4;
        }
        
        .user-message {
            align-self: flex-end;
            background-color: #0066cc;
            color: white;
        }
        
        .bot-message {
            align-self: flex-start;
            background-color: #f1f1f1;
        }
        
        .chatbot-input {
            display: flex;
            padding: 10px;
            border-top: 1px solid #e0e0e0;
        }
        
        .chatbot-input input {
            flex: 1;
            padding: 10px 15px;
            border: 1px solid #ddd;
            border-radius: 20px;
            outline: none;
        }
        
        .chatbot-input button {
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 20px;
            padding: 10px 15px;
            margin-left: 10px;
            cursor: pointer;
        }
        
        .chat-toggle-button {
            position: fixed;
            bottom: 20px;
            right: 20px;
            width: 60px;
            height: 60px;
            background-color: #0066cc;
            color: white;
            border: none;
            border-radius: 50%;
            display: none;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            z-index: 1001;
            opacity: 1;
            visibility: visible;
        }
        
        @keyframes pulse {
            0% { transform: scale(1); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
            50% { transform: scale(1.05); box-shadow: 0 8px 16px rgba(0,0,0,0.3); }
            100% { transform: scale(1); box-shadow: 0 4px 8px rgba(0,0,0,0.2); }
        }
        
        .chat-toggle-button {
            animation: pulse 2s infinite;
        }
        
        .chat-toggle-button:hover {
            background-color: #0055bb;
        }

        .source-citation {
            font-size: 12px;
            color: #666;
            margin-top: 5px;
            font-style: italic;
        }
    </style>
</head>
<body>
    <div class="news-grid">
"""

# Add each news item to the HTML
for item in news_items:
    company = html.escape(str(item.get("company", "")))
    title = html.escape(str(item.get("title", "No title")))
    url = html.escape(str(item.get("url", "#")))
    source = html.escape(str(item.get("source", "Unknown source")))
    body = html.escape(str(item.get("body", "No description available")))
    date = html.escape(str(item.get("date", "")))
    image = html.escape(str(item.get("image", "")))
    
    company_tag = f'<span class="company-tag">{company}</span>' if company else ''
    image_html = f'<div class="news-image"><img src="{image}" alt="{title}"></div>' if image and image != "None" else ''
    
    if "No news" in title:
        title_html = f'<h3 class="news-title">No news</h3>'
        date_html = ""
    else:
        title_html = f'<h3 class="news-title"><a href="{url}" target="_blank">{title}</a></h3>'
        date_html = f'<div class="news-date">{date}</div>'
    
    html_content += f"""
    <div class="news-card">
        {company_tag}
        {image_html}
        {title_html}
        <div class="news-source">{source}</div>
        <p>{body}</p>
        {date_html}
    </div>
    """

# Function to fetch content from URLs - improved to handle different sites better
def fetch_url_content(url):
    try:
        if "microsoft.com/en-us/investor/" in url:
            return "Microsoft investor relations content is not available for extraction."
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        if 'msn.com' in url:
            print(f"Special handling for MSN URL: {url}")
            article_body = soup.find('div', {'class': ['articlecontent', 'mainarticle', 'contentid', 'primary-content']}) or \
                          soup.find('div', {'data-testid': ['article-body', 'content-canvas']}) or \
                          soup.find('article') or \
                          soup.find('div', {'class': 'article-body'})
            
            if article_body:
                for element in article_body.find_all(['script', 'style', 'nav', 'aside']):
                    element.decompose()
                
                paragraphs = article_body.find_all('p')
                if paragraphs:
                    return "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
            element.decompose()
        
        content_selectors = [
            'article', '.article', '.post-content', '.story', 'main', '#content', '.content',
            '.post', '.entry-content', '.article-content', '.article__content', '.article-body'
        ]
        
        article_content = None
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                if len(element.get_text(strip=True)) > 150:
                    article_content = element
                    break
            if article_content:
                break
        
        if not article_content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                text_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30]
                if text_paragraphs:
                    return "\n\n".join(text_paragraphs[:20])

        if article_content:
            paragraphs = article_content.find_all('p')
            if paragraphs:
                return "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            else:
                text = article_content.get_text(separator='\n', strip=True)
                text = '\n\n'.join([' '.join(line.split()) for line in text.split('\n') if line.strip() and len(line) > 30])
                return text
                
        body_text = ""
        if soup.body:
            paragraphs = soup.body.find_all('p')
            if paragraphs:
                body_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs 
                                      if len(p.get_text(strip=True)) > 30])
        
        if not body_text:
            text = soup.get_text(separator='\n', strip=True)
            body_text = '\n\n'.join([' '.join(line.split()) for line in text.split('\n') 
                                 if line.strip() and len(line.strip()) > 30])
            
        if len(body_text) < 100 or len(body_text.split()) < 20:
            print(f"Warning: Extracted content is suspiciously short for {url}")
            all_text = soup.get_text(separator=' ', strip=True)
            if len(all_text) > 200:
                return all_text[:10000]
            
        return body_text[:10000]
        
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return f"Content extraction failed: {str(e)}"

# Load cached data if it exists
cached_news_data = {}
cache_file = "news_cache.json"
if os.path.exists(cache_file):
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            cached_news_data = json.load(f)
        print(f"Loaded {len(cached_news_data)} cached articles")
    except Exception as e:
        print(f"Error loading cache: {e}")

# Prepare news data for the chatbot with URL content - with better error handling
news_data_for_js = []
for item in news_items:
    url = str(item.get("url", "#"))
    title = str(item.get("title", "No title"))
    
    article_data = {
        "company": str(item.get("company", "")),
        "title": title,
        "url": url,
        "source": str(item.get("source", "Unknown source")),
        "body": str(item.get("body", "No description available")),
        "date": str(item.get("date", "")),
        "full_content": "",
        "extraction_status": "not_attempted"
    }
    
    cache_key = f"{url}_{title}"
    if cache_key in cached_news_data and cached_news_data[cache_key].get("full_content"):
        content = cached_news_data[cache_key]["full_content"]
        if content and len(content) > 100 and not content.startswith("Content extraction failed"):
            print(f"Using cached content for: {title}")
            article_data["full_content"] = content
            article_data["extraction_status"] = "cached"
        else:
            print(f"Cached content for '{title}' seems inadequate. Re-fetching...")
            article_data["extraction_status"] = "cache_inadequate"
    
    if (article_data["extraction_status"] != "cached" and 
        url and url != "#" and url.startswith("http")):
        try:
            print(f"Fetching content from {url}")
            content = fetch_url_content(url)
            
            if content and len(content) > 100:
                article_data["full_content"] = content
                article_data["extraction_status"] = "success"
                cached_news_data[cache_key] = article_data
            else:
                print(f"Warning: Fetched content for '{title}' is too short or empty")
                article_data["extraction_status"] = "content_too_short"
                article_data["full_content"] = f"Note: Content could not be properly extracted from this source. Using summary instead.\n\n{article_data['body']}"
            
            time.sleep(random.uniform(1.5, 4))
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            article_data["extraction_status"] = "error"
            article_data["full_content"] = f"Error extracting content: {str(e)}"
    
    news_data_for_js.append(article_data)

# Save updated cache
try:
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cached_news_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(cached_news_data)} articles to cache")
except Exception as e:
    print(f"Error saving cache: {e}")

current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
html_content += f"""
    </div>
    <p class="timestamp">Last updated: {current_time}</p>
</body>
</html>
"""

# Write the HTML file
with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML dashboard created successfully!")
