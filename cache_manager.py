import json
import os
import time
import random

def load_cache(cache_file="news_cache.json"):
    """
    Load the article content cache from a JSON file
    
    Args:
        cache_file: Path to the cache file
        
    Returns:
        Dictionary containing cached article content
    """
    cached_news_data = {}
    if os.path.exists(cache_file):
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached_news_data = json.load(f)
            print(f"Loaded {len(cached_news_data)} cached articles")
        except Exception as e:
            print(f"Error loading cache: {e}")
    return cached_news_data

def save_cache(cached_news_data, cache_file="news_cache.json"):
    """
    Save the article content cache to a JSON file
    
    Args:
        cached_news_data: Dictionary containing article content to cache
        cache_file: Path to the cache file
    """
    try:
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cached_news_data, f, ensure_ascii=False, indent=2)
        print(f"Saved {len(cached_news_data)} articles to cache")
    except Exception as e:
        print(f"Error saving cache: {e}")

def prepare_news_data(news_items, cached_news_data, fetch_url_content):
    """
    Prepare news data for JavaScript, fetching full content where needed
    
    Args:
        news_items: List of news items as dictionaries
        cached_news_data: Dictionary of cached article content
        fetch_url_content: Function to fetch content from URLs
        
    Returns:
        List of news items with full content and a updated cache dictionary
    """
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
        
        # Check if we already have the content in cache
        cache_key = f"{url}_{title}"
        if cache_key in cached_news_data and cached_news_data[cache_key].get("full_content"):
            content = cached_news_data[cache_key]["full_content"]
            # Verify the cached content is substantial
            if content and len(content) > 100 and not content.startswith("Content extraction failed"):
                print(f"Using cached content for: {title}")
                article_data["full_content"] = content
                article_data["extraction_status"] = "cached"
            else:
                print(f"Cached content for '{title}' seems inadequate. Re-fetching...")
                article_data["extraction_status"] = "cache_inadequate"
        
        # Only fetch content if we have a real URL and it's not adequately cached
        if (article_data["extraction_status"] != "cached" and 
            url and url != "#" and url.startswith("http")):
            try:
                print(f"Fetching content from {url}")
                content = fetch_url_content(url)
                
                # Verify the fetched content is substantial
                if content and len(content) > 100:
                    article_data["full_content"] = content
                    article_data["extraction_status"] = "success"
                    # Update the cache with new content
                    cached_news_data[cache_key] = article_data
                else:
                    print(f"Warning: Fetched content for '{title}' is too short or empty")
                    article_data["extraction_status"] = "content_too_short"
                    article_data["full_content"] = f"Note: Content could not be properly extracted from this source. Using summary instead.\n\n{article_data['body']}"
                
                # Polite delay to avoid hammering websites
                time.sleep(random.uniform(1.5, 4))
            except Exception as e:
                print(f"Error processing URL {url}: {e}")
                article_data["extraction_status"] = "error"
                article_data["full_content"] = f"Error extracting content: {str(e)}"
        
        news_data_for_js.append(article_data)
    
    return news_data_for_js, cached_news_data
