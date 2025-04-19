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
            top: 20px; /* Changed from bottom to top */
            right: 20px;
            width: 350px;
            height: calc(100vh - 40px); /* Changed to take up almost full viewport height */
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            z-index: 1000;
            transition: transform 0.3s ease, opacity 0.3s ease;
            transform: translateX(110%); /* Changed from translateY to translateX */
            opacity: 0;
            overflow: hidden; /* Added to ensure no overflow */
        }
        
        .chatbot-container.active {
            transform: translateX(0); /* Changed from translateY to translateX */
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
            max-height: calc(100vh - 140px); /* Added to ensure scrolling works properly */
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
            display: none; /* Changed from flex to none to hide initially */
            justify-content: center;
            align-items: center;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            z-index: 1001;
            opacity: 1;
            visibility: visible;
        }
        
        /* Adding a pulsing animation to make the chat button more noticeable */
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
    # Convert all values to strings to avoid NoneType errors
    company = html.escape(str(item.get("company", "")))
    title = html.escape(str(item.get("title", "No title")))
    url = html.escape(str(item.get("url", "#")))
    source = html.escape(str(item.get("source", "Unknown source")))
    body = html.escape(str(item.get("body", "No description available")))
    date = html.escape(str(item.get("date", "")))
    image = html.escape(str(item.get("image", "")))
    
    # Only add company tag if we found a valid company name
    company_tag = f'<span class="company-tag">{company}</span>' if company else ''
    
    # Add image HTML if an image URL exists
    image_html = f'<div class="news-image"><img src="{image}" alt="{title}"></div>' if image and image != "None" else ''
    
    # Check if the title contains "No news" and adjust the title rendering accordingly
    if "No news" in title:
        title_html = f'<h3 class="news-title">No news</h3>'
        date_html = "" # Don't show date for "No news" entries
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
        # Don't process certain problematic URLs
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
        
        # Add timeout to prevent hanging on problematic sites
        response = requests.get(url, headers=headers, timeout=15)
        response.raise_for_status()
        
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

# Save updated cache
try:
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cached_news_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(cached_news_data)} articles to cache")
except Exception as e:
    print(f"Error saving cache: {e}")

# Complete the HTML document with proper escaping of JavaScript template literals
current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
html_content += f"""
    </div>
    <p class="timestamp">Last updated: {current_time}</p>
    
    <!-- Chatbot UI - Added title attribute and more visible text -->
    <button class="chat-toggle-button" title="Open Chat Assistant">💬</button>
    <div class="chatbot-container">
        <div class="chatbot-header">
            <span class="chatbot-title">News Assistant</span>
            <span class="close-chat" style="cursor: pointer;">✕</span>
        </div>
        <div class="chatbot-messages">
            <div class="message bot-message">
                Hi! I'm your news assistant. Ask me anything about the news articles on this page.
            </div>
        </div>
        <div class="chatbot-input">
            <input type="text" placeholder="Ask a question...">
            <button>Send</button>
        </div>
    </div>
    
    <script>
        // Store news data for the chatbot
        const newsData = {json.dumps(news_data_for_js)};
        
        // Debug flag - set to true to see debug info in console
        const DEBUG = true;
        
        // Chatbot functionality
        document.addEventListener('DOMContentLoaded', () => {{
            const chatToggle = document.querySelector('.chat-toggle-button');
            const chatContainer = document.querySelector('.chatbot-container');
            const closeChat = document.querySelector('.close-chat');
            const chatInput = document.querySelector('.chatbot-input input');
            const sendButton = document.querySelector('.chatbot-input button');
            const messagesContainer = document.querySelector('.chatbot-messages');
            
            // Automatically open the chatbot on page load
            setTimeout(() => {{
                chatContainer.classList.add('active');
                chatToggle.style.display = 'none';
                chatInput.focus(); // Focus on the input field
            }}, 1000); // Short delay to ensure page has loaded
            
            // Toggle chat open/close
            chatToggle.addEventListener('click', () => {{
                chatContainer.classList.add('active');
                chatToggle.style.display = 'none';
                chatInput.focus();
            }});
            
            closeChat.addEventListener('click', () => {{
                chatContainer.classList.remove('active');
                setTimeout(() => {{
                    chatToggle.style.display = 'flex'; // Show toggle button after transition
                }}, 300);
            }});
            
            // Send message function
            function sendMessage() {{
                const question = chatInput.value.trim();
                if (!question) return;
                
                // Add user message to chat
                addMessage(question, 'user');
                chatInput.value = '';
                
                // Check if this is a follow-up response
                if (handleFollowUp(question)) {{
                    // If it was handled as a follow-up, we're done
                    return;
                }}
                
                // Otherwise process as a new query
                conversationState.currentQuery = question;
                conversationState.mode = 'showing_results';
                conversationState.currentArticleIndex = 0;
                processQuery(question);
            }}
            
            // Add message to chat
            function addMessage(text, sender) {{
                const message = document.createElement('div');
                message.classList.add('message');
                message.classList.add(sender + '-message');
                message.textContent = text;
                messagesContainer.appendChild(message);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }}
            
            // Add message with citation
            function addMessageWithCitation(text, citation) {{
                const messageContainer = document.createElement('div');
                
                const message = document.createElement('div');
                message.classList.add('message');
                message.classList.add('bot-message');
                message.textContent = text;
                
                const citationElement = document.createElement('div');
                citationElement.classList.add('source-citation');
                citationElement.textContent = 'Source: ' + citation;
                
                messageContainer.appendChild(message);
                messageContainer.appendChild(citationElement);
                messagesContainer.appendChild(messageContainer);
                messagesContainer.scrollTop = messagesContainer.scrollHeight;
            }}
            
            // Enhanced RAG implementation with full content
            function processQuery(question) {{
                // Convert question to lowercase for case-insensitive matching
                const lowerQuestion = question.toLowerCase();
                
                if (DEBUG) {{
                    console.log('Processing query:', question);
                    console.log('Available articles:', newsData.length);
                }}
                
                // Check if it's a direct company name query
                const isCompanyQuery = lowerQuestion.split(' ').length <= 3;
                
                // First check if the query is just a company name, and if that company exists in our data
                if (isCompanyQuery) {{
                    // Get a list of all unique company names in our data
                    const allCompanies = [...new Set(newsData.map(article => article.company.toLowerCase()))];
                    console.log('All companies:', allCompanies);
                    
                    // Check if any company exactly matches the query
                    const exactCompanyMatch = allCompanies.find(company => 
                        company.toLowerCase() === lowerQuestion.trim()
                    );
                    
                    // Check for partial but valid company name matches (exact word boundaries)
                    // This prevents "Partum Health" from matching with "Fort Health" just because both have "Health"
                    const validPartialMatch = allCompanies.some(company => {
                        // Split both into words and check for substantial overlap
                        const companyWords = company.toLowerCase().split(/\s+/);
                        const queryWords = lowerQuestion.toLowerCase().trim().split(/\s+/);
                        
                        // Exact match
                        if (company.toLowerCase() === lowerQuestion.toLowerCase().trim()) {
                            return true;
                        }
                        
                        // Only consider it a match if:
                        // 1. Company fully contains the query as a complete phrase
                        if (company.toLowerCase().includes(lowerQuestion.toLowerCase().trim())) {
                            return true;
                        }
                        
                        // 2. Query fully contains the company name as a complete phrase
                        if (lowerQuestion.toLowerCase().trim().includes(company.toLowerCase())) {
                            return true;
                        }
                        
                        // 3. For multi-word company names, require matching at least 2 words in sequence
                        // or the first word exactly (for distinctive first words)
                        if (companyWords.length > 1) {
                            // Check if first word matches exactly (like "Partum" in "Partum Health")
                            if (queryWords.includes(companyWords[0]) && companyWords[0].length > 3) {
                                return true;
                            }
                            
                            // Check for 2+ consecutive words matching
                            const companyPhrase = companyWords.join(' ');
                            const queryPhrase = queryWords.join(' ');
                            
                            // Find any 2-word phrases that match
                            for (let i = 0; i < companyWords.length - 1; i++) {
                                const phrase = companyWords[i] + ' ' + companyWords[i+1];
                                if (queryPhrase.includes(phrase)) {
                                    return true;
                                }
                            }
                        }
                        
                        return false;
                    });
                    
                    // Only consider it a company match if exact or valid partial match
                    const companyExists = exactCompanyMatch !== undefined || validPartialMatch;
                    
                    if (!companyExists) {{
                        // If we're searching for a specific company and it doesn't exist in our data
                        addMessage(`I'm sorry, I don't have any news articles about "${question}". Would you like information about another company?`, 'bot');
                        conversationState.mode = 'initial';
                        return; // Exit early, don't search for partial matches
                    }}
                }}
                
                // Improved keyword extraction
                let keywords = [];
                
                // First extract quoted phrases
                const quoteRegex = /"([^"]+)"/g;
                let quoteMatch;
                while ((quoteMatch = quoteRegex.exec(question)) !== null) {{
                    keywords.push(quoteMatch[1].toLowerCase());
                }}
                
                // Then extract individual important words (excluding common stop words)
                const stopWords = new Set([
                    'a', 'an', 'the', 'and', 'or', 'but', 'is', 'are', 'was', 'were', 
                    'to', 'of', 'in', 'on', 'at', 'by', 'for', 'with', 'about', 'from',
                    'these', 'those', 'this', 'that', 'have', 'has', 'had', 'do', 'does',
                    'did', 'can', 'could', 'will', 'would', 'should', 'may', 'might'
                ]);
                
                const wordKeywords = lowerQuestion
                    .replace(/[^a-zA-Z0-9 ]/g, ' ')
                    .split(' ')
                    .filter(word => word.length > 2 && !stopWords.has(word.toLowerCase()));
                    
                keywords = [...keywords, ...wordKeywords];
                
                if (DEBUG) {{
                    console.log('Extracted keywords:', keywords);
                }}
                
                // Search for relevant articles
                let relevantArticles = [];
                newsData.forEach(article => {{
                    let score = 0;
                    const title = article.title.toLowerCase();
                    const body = article.body.toLowerCase();
                    const fullContent = article.full_content ? article.full_content.toLowerCase() : '';
                    const company = article.company.toLowerCase();
                    
                    // Direct company name match in query - highest priority
                    if (company && lowerQuestion.includes(company)) {{
                        score += 15; // Highest boost for company name match in question
                    }}
                    
                    // Exact match for company name - highest priority (added fix)
                    if (company && lowerQuestion.trim() === company) {{
                        score += 30; // Super high boost for exact company name match
                    }}
                    
                    // Prioritize company names that start with the same phrase (added fix)
                    if (company && lowerQuestion.trim().startsWith(company)) {{
                        score += 25; // Very high priority for company name at start
                    }}
                    if (company && company.startsWith(lowerQuestion.trim())) {{
                        score += 20; // High priority if company starts with query
                    }}
                    
                    // IMPORTANT FIX: Penalize different company matches when searching for a specific company
                    // This prevents "Fort Health" from matching when searching for "Partum Health"
                    if (isCompanyQuery && company && !company.includes(lowerQuestion) && !lowerQuestion.includes(company)) {{
                        // Check if first words match - if they don't, heavily penalize
                        const companyFirstWord = company.split(' ')[0].toLowerCase();
                        const queryFirstWord = lowerQuestion.trim().split(' ')[0].toLowerCase();
                        
                        if (companyFirstWord !== queryFirstWord) {{
                            score -= 50; // Strong penalty for different company first words
                        }}
                    }}
                    
                    // Check for direct question matches in content
                    if (fullContent && fullContent.includes(lowerQuestion)) {{
                        score += 10; // Large boost for exact question match
                    }}
                    
                    // Check if keywords are in title, body or full content
                    keywords.forEach(keyword => {{
                        // Check for company name match with keywords
                        if (company && keyword.length > 2 && company === keyword) {{
                            score += 18; // Extremely high boost for exact keyword match
                        }}
                        else if (company && keyword.length > 2 && company.includes(keyword)) {{
                            score += 5; // Reduced from 12 to 5 - partial matches shouldn't be weighted too heavily
                        }}
                        if (company && keyword.length > 2 && keyword.includes(company)) {{
                            score += 10; // Boost if keyword contains company name
                        }}
                        
                        // Check for exact matches in content
                        if (title.includes(keyword)) score += 5;  // Title matches are weighted highly
                        if (body.includes(keyword)) score += 3;   // Summary matches are important
                        
                        if (fullContent) {{
                            // For longer keywords (phrases), boost the score even more
                            if (keyword.length > 10 && fullContent.includes(keyword)) {{
                                score += 8;
                            }} else if (fullContent.includes(keyword)) {{
                                score += 2;  // Full content matches
                            }}
                            
                            // Count occurrences for additional scoring
                            const keywordRegex = new RegExp(keyword, 'gi');
                            const occurrences = (fullContent.match(keywordRegex) || []).length;
                            score += Math.min(occurrences, 5) * 0.5; // Cap at 2.5 points from occurrences
                        }}
                    }});
                    
                    // Special handling for specific question types
                    if (lowerQuestion.includes('who') || lowerQuestion.includes('person')) {{
                        // Person entity detection
                        const nameRegex = /([A-Z][a-z]+ [A-Z][a-z]+)/g;
                        const names = fullContent ? (fullContent.match(nameRegex) || []) : [];
                        if (names.length > 0) score += 2;
                    }}
                    
                    if (score > 0) {{
                        if (DEBUG) {{
                            console.log(`Article: ${{article.title}}, Score: ${{score}}`);
                        }}
                        relevantArticles.push({{...article, score}});
                    }}
                }});
                
                // Sort by relevance
                relevantArticles.sort((a, b) => b.score - a.score);
                
                // Store in conversation state
                conversationState.relevantArticles = relevantArticles;
                conversationState.currentArticleIndex = 0;
                
                if (DEBUG) {{
                    console.log('Relevant articles found:', relevantArticles.length);
                    if (relevantArticles.length > 0) {{
                        console.log('Top article:', relevantArticles[0].title);
                        console.log('Top score:', relevantArticles[0].score);
                    }}
                }}
                
                // Generate response based on findings
                if (relevantArticles.length > 0) {{
                    const mostRelevant = relevantArticles[0];
                    let response = "";
                    
                    // Extract the most relevant snippet from full content if available
                    let informativeSnippet = '';
                    if (mostRelevant.full_content) {{
                        const fullContent = mostRelevant.full_content;
                        
                        // Improved paragraph extraction
                        // First split by clear paragraph breaks
                        const paragraphs = fullContent.split(/\\n+/)
                            .filter(p => p.trim().length > 50);
                        
                        // If no paragraphs found, create them from sentences
                        let foundRelevantSnippet = false;
                        
                        // First look for paragraphs containing multiple keywords
                        for (const paragraph of paragraphs) {{
                            const lowerPara = paragraph.toLowerCase();
                            const matchedKeywords = keywords.filter(kw => lowerPara.includes(kw));
                            
                            if (matchedKeywords.length >= 2) {{
                                informativeSnippet = paragraph.trim().substring(0, 300) + '...';
                                foundRelevantSnippet = true;
                                break;
                            }}
                        }}
                        
                        // If no multi-keyword paragraph, look for any keyword match
                        if (!foundRelevantSnippet) {{
                            for (const paragraph of paragraphs) {{
                                if (keywords.some(keyword => paragraph.toLowerCase().includes(keyword))) {{
                                    informativeSnippet = paragraph.trim().substring(0, 300) + '...';
                                    foundRelevantSnippet = true;
                                    break;
                                }}
                            }}
                        }}
                        
                        // If still no good paragraph found, just take an interesting part of the content
                        if (!foundRelevantSnippet && fullContent.length > 0) {{
                            // If we have substantial content, try to find the most interesting part
                            if (fullContent.length > 500) {{
                                // Look for a part that might be from the middle of the article
                                const middleStart = Math.floor(fullContent.length / 3);
                                const middleContent = fullContent.substring(middleStart, middleStart + 500);
                                const sentences = middleContent.split(/[.!?] /).filter(s => s.length > 30);
                                
                                if (sentences.length > 0) {{
                                    informativeSnippet = sentences[0].trim() + '...';
                                }} else {{
                                    informativeSnippet = fullContent.substring(0, 300) + '...';
                                }}
                            }} else {{
                                informativeSnippet = fullContent.substring(0, 300) + '...';
                            }}
                        }}
                    }}
                    
                    // Generate different responses based on question type
                    if (lowerQuestion.includes('what') && lowerQuestion.includes('company')) {{
                        response = `Based on the news, ${{mostRelevant.company}} has been mentioned in relation to: "${{mostRelevant.title}}"`;
                    }} else if (lowerQuestion.includes('latest') || lowerQuestion.includes('recent')) {{
                        response = `The latest news I found is: "${{mostRelevant.title}}". ${{mostRelevant.body.substring(0, 150)}}...`;
                    }} else if (informativeSnippet) {{
                        // Use the full content snippet for detailed answers
                        response = `According to ${{mostRelevant.source}}: "${{informativeSnippet}}"`;
                    }} else {{
                        response = `I found this relevant information: "${{mostRelevant.title}}". ${{mostRelevant.body.substring(0, 150)}}...`;
                    }}
                    
                    addMessageWithCitation(response, `${{mostRelevant.source}}, ${{mostRelevant.date}} - ${{mostRelevant.url}}`);
                    
                    // If there are more relevant articles, mention them
                    if (relevantArticles.length > 1) {{
                        setTimeout(() => {{
                            addMessage(`I also found ${{relevantArticles.length - 1}} more articles that might be relevant. Would you like to know more about any specific topic?`, 'bot');
                            conversationState.mode = 'offering_more'; // Set mode to offering more articles
                        }}, 1000);
                    }}
                }} else {{
                    addMessage(`I couldn't find any information about that in the current news articles. Could you try asking something else?`, 'bot');
                    conversationState.mode = 'initial'; // Reset mode
                }}
            }}
            
            // Conversation state to track dialogue context
            const conversationState = {{
                mode: 'initial', // 'initial', 'showing_results', 'offering_more'
                currentQuery: '',
                relevantArticles: [],
                currentArticleIndex: 0
            }};
            
            // Handle follow-up responses (yes/no)
            function handleFollowUp(response) {{
                const lowerResponse = response.toLowerCase().trim();
                
                if (conversationState.mode === 'offering_more' && 
                    (lowerResponse === 'yes' || lowerResponse === 'sure' || 
                     lowerResponse === 'ok' || lowerResponse.includes('yes'))) {{
                    
                    // Show next article from previously found relevant articles
                    if (conversationState.relevantArticles.length > conversationState.currentArticleIndex + 1) {{
                        conversationState.currentArticleIndex++;
                        const nextArticle = conversationState.relevantArticles[conversationState.currentArticleIndex];
                        
                        let response = '';
                        if (nextArticle.full_content) {{
                            const snippet = nextArticle.full_content.substring(0, 300) + '...';
                            response = `Here's another relevant article from ${{nextArticle.source}}: "${{snippet}}"`;
                        }} else {{
                            response = `Here's another relevant article: "${{nextArticle.title}}". ${{nextArticle.body.substring(0, 150)}}...`;
                        }}
                        
                        addMessageWithCitation(response, `${{nextArticle.source}}, ${{nextArticle.date}} - ${{nextArticle.url}}`);
                        
                        // If there are still more articles, offer again
                        const remaining = conversationState.relevantArticles.length - conversationState.currentArticleIndex - 1;
                        if (remaining > 0) {{
                            setTimeout(() => {{
                                addMessage(`I have ${{remaining}} more articles that might interest you. Would you like to see another one?`, 'bot');
                                // Stay in offering_more mode
                            }}, 1000);
                        }} else {{
                            setTimeout(() => {{
                                addMessage(`That's all the relevant articles I found. Is there something else you'd like to know about?`, 'bot');
                                conversationState.mode = 'initial'; // Reset mode
                            }}, 1000);
                        }}
                        return true; // Handled
                    }}
                }}
                
                // If response wasn't handled as a follow-up
                return false;
            }}
            
            // Event listeners for sending messages
            sendButton.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') sendMessage();
            }});
            
            // Make sure chat toggle is visible on page load
            chatToggle.style.display = 'none'; // Keep it hidden since we're auto-opening
            chatToggle.style.opacity = '1';
            
            // Add a timeout to make the chatbot button pulse after a short delay
            setTimeout(() => {{
                chatToggle.classList.add('attention');
            }}, 2000);
        }});
    </script>
</body>
</html>
"""

# Write the HTML file
with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML dashboard created successfully!")
