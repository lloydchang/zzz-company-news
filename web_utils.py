import time
import random
import requests
from bs4 import BeautifulSoup

# Function to handle rate limiting with exponential backoff
def request_with_retry(url, headers=None, max_retries=3, base_delay=2):
    """
    Make HTTP requests with exponential backoff for rate limiting
    
    Args:
        url: URL to request
        headers: Request headers
        max_retries: Maximum number of retry attempts
        base_delay: Base delay between retries in seconds
        
    Returns:
        Response object or raises exception after max retries
    """
    if headers is None:
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
    
    for attempt in range(max_retries):
        try:
            response = requests.get(url, headers=headers, timeout=15)
            
            # Check if we hit rate limiting (status codes 429, 403, or 503 often indicate rate limiting)
            if response.status_code in (429, 403, 503):
                print(f"Rate limit hit (status code: {response.status_code}), retrying in {base_delay * (2**attempt)} seconds...")
                time.sleep(base_delay * (2**attempt) + random.uniform(0, 1))  # Exponential backoff with jitter
                continue
                
            # Raise exception for other error codes
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            # Check if we've used all retries
            if attempt < max_retries - 1:
                wait_time = base_delay * (2**attempt) + random.uniform(0, 1)
                print(f"Request error: {e}. Retrying in {wait_time:.2f} seconds...")
                time.sleep(wait_time)  # Exponential backoff with jitter
            else:
                # Final attempt failed, re-raise the exception
                raise
    
    # This should not be reached due to the raise in the loop, but just in case
    raise requests.exceptions.RequestException("Max retries exceeded")

def fetch_url_content(url):
    """
    Fetch and extract article content from a URL
    
    Args:
        url: URL to fetch content from
        
    Returns:
        Extracted text content from the URL
    """
    try:
        # Don't process certain problematic URLs
        if "microsoft.com/en-us/investor/" in url:
            return "Microsoft investor relations content is not available for extraction."
        
        # Rotate between different user agents to reduce chance of being rate-limited
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.81 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:94.0) Gecko/20100101 Firefox/94.0',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.0 Mobile/15E148 Safari/604.1'
        ]
        
        headers = {
            'User-Agent': random.choice(user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Referer': 'https://www.google.com/',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'max-age=0',
        }
        
        # Use the retry function for requests with increased max_retries and longer base delay
        response = request_with_retry(url, headers=headers, max_retries=5, base_delay=3)
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Special handling for MSN URLs
        if 'msn.com' in url:
            print(f"Special handling for MSN URL: {url}")
            # Find the main content container in MSN articles
            article_body = soup.find('div', {'class': ['articlecontent', 'mainarticle', 'contentid', 'primary-content']}) or \
                          soup.find('div', {'data-testid': ['article-body', 'content-canvas']}) or \
                          soup.find('article') or \
                          soup.find('div', {'class': 'article-body'})
            
            if article_body:
                # Process only the article content
                for element in article_body.find_all(['script', 'style', 'nav', 'aside']):
                    element.decompose()
                
                # Extract paragraphs from the article body
                paragraphs = article_body.find_all('p')
                if paragraphs:
                    return "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
        
        # Remove script, style, and nav elements for any site
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
            element.decompose()
        
        # Try to find the article content using common selectors
        content_selectors = [
            'article', '.article', '.post-content', '.story', 'main', '#content', '.content',
            '.post', '.entry-content', '.article-content', '.article__content', '.article-body'
        ]
        
        article_content = None
        for selector in content_selectors:
            elements = soup.select(selector)
            for element in elements:
                # Only consider elements with substantial text
                if len(element.get_text(strip=True)) > 150:
                    article_content = element
                    break
            if article_content:
                break
        
        # If no article content found, try to find all paragraphs
        if not article_content:
            paragraphs = soup.find_all('p')
            if paragraphs:
                # Only include paragraphs with reasonable length
                text_paragraphs = [p.get_text(strip=True) for p in paragraphs if len(p.get_text(strip=True)) > 30]
                if text_paragraphs:
                    return "\n\n".join(text_paragraphs[:20])  # Limit to first 20 paragraphs

        # Get text from article content if found
        if article_content:
            # Extract all paragraphs
            paragraphs = article_content.find_all('p')
            if paragraphs:
                return "\n\n".join([p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True)])
            else:
                # Fallback: get all text with paragraph structure
                text = article_content.get_text(separator='\n', strip=True)
                # Clean up white spaces but preserve paragraph structure
                text = '\n\n'.join([' '.join(line.split()) for line in text.split('\n') if line.strip() and len(line) > 30])
                return text
                
        # If no specific content found, use the whole body with cleaning
        body_text = ""
        if soup.body:
            # Get all paragraphs in the body
            paragraphs = soup.body.find_all('p')
            if paragraphs:
                body_text = "\n\n".join([p.get_text(strip=True) for p in paragraphs 
                                      if len(p.get_text(strip=True)) > 30])
        
        # If we still don't have content, use the whole page text as a last resort
        if not body_text:
            text = soup.get_text(separator='\n', strip=True)
            body_text = '\n\n'.join([' '.join(line.split()) for line in text.split('\n') 
                                 if line.strip() and len(line.strip()) > 30])
            
        # Check if we have meaningful content
        if len(body_text) < 100 or len(body_text.split()) < 20:
            print(f"Warning: Extracted content is suspiciously short for {url}")
            # Try a different approach for very short content
            all_text = soup.get_text(separator=' ', strip=True)
            if len(all_text) > 200:
                return all_text[:10000]  # Use raw text as a last resort
            
        # Limit the content length
        return body_text[:10000]
        
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return f"Content extraction failed: {str(e)}"
