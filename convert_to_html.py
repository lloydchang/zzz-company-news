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
    <title>Company News Dashboard</title>
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
            bottom: 20px;
            right: 20px;
            width: 350px;
            height: 450px;
            background-color: white;
            border-radius: 10px;
            box-shadow: 0 5px 25px rgba(0,0,0,0.2);
            display: flex;
            flex-direction: column;
            z-index: 1000;
            transition: transform 0.3s ease, opacity 0.3s ease;
            transform: translateY(100%);
            opacity: 0;
        }
        
        .chatbot-container.active {
            transform: translateY(0);
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
            display: flex;
            justify-content: center;
            align-items: center;
            font-size: 24px;
            cursor: pointer;
            box-shadow: 0 4px 8px rgba(0,0,0,0.2);
            z-index: 1001;
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
    <div class="header">
        <h1>Company News Dashboard</h1>
    </div>
    
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
    
    html_content += f"""
    <div class="news-card">
        {company_tag}
        {image_html}
        <h3 class="news-title"><a href="{url}" target="_blank">{title}</a></h3>
        <div class="news-source">{source}</div>
        <p>{body}</p>
        <div class="news-date">{date}</div>
    </div>
    """

# Function to fetch content from URLs
def fetch_url_content(url):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # Raise an exception for 4XX/5XX responses
        
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Remove script, style, and nav elements
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside']):
            element.decompose()
            
        # Get text and clean it up
        text = soup.get_text(separator=' ', strip=True)
        # Clean up white spaces
        text = ' '.join(text.split())
        return text
    except Exception as e:
        print(f"Error fetching content from {url}: {e}")
        return ""

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

# Prepare news data for the chatbot with URL content
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
        "full_content": ""
    }
    
    # Check if we already have the content in cache
    cache_key = f"{url}_{title}"
    if cache_key in cached_news_data and cached_news_data[cache_key].get("full_content"):
        print(f"Using cached content for: {title}")
        article_data["full_content"] = cached_news_data[cache_key]["full_content"]
    # Only fetch content if we have a real URL and it's not in cache
    elif url and url != "#" and url.startswith("http"):
        try:
            print(f"Fetching content from {url}")
            article_data["full_content"] = fetch_url_content(url)
            # Update the cache with new content
            cached_news_data[cache_key] = article_data
            # Polite delay to avoid hammering websites
            time.sleep(random.uniform(1, 3))
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
    
    news_data_for_js.append(article_data)

# Save updated cache
try:
    with open(cache_file, 'w', encoding='utf-8') as f:
        json.dump(cached_news_data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(cached_news_data)} articles to cache")
except Exception as e:
    print(f"Error saving cache: {e}")

# Complete the HTML document
current_time = datetime.datetime.now(datetime.timezone.utc).isoformat()
html_content += f"""
    </div>
    <p class="timestamp">Last updated: {current_time}</p>
    
    <!-- Chatbot UI -->
    <button class="chat-toggle-button">💬</button>
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
        
        // Chatbot functionality
        document.addEventListener('DOMContentLoaded', () => {{
            const chatToggle = document.querySelector('.chat-toggle-button');
            const chatContainer = document.querySelector('.chatbot-container');
            const closeChat = document.querySelector('.close-chat');
            const chatInput = document.querySelector('.chatbot-input input');
            const sendButton = document.querySelector('.chatbot-input button');
            const messagesContainer = document.querySelector('.chatbot-messages');
            
            // Toggle chat open/close
            chatToggle.addEventListener('click', () => {{
                chatContainer.classList.add('active');
                chatToggle.style.display = 'none';
            }});
            
            closeChat.addEventListener('click', () => {{
                chatContainer.classList.remove('active');
                chatToggle.style.display = 'flex';
            }});
            
            // Send message function
            function sendMessage() {{
                const question = chatInput.value.trim();
                if (!question) return;
                
                // Add user message to chat
                addMessage(question, 'user');
                chatInput.value = '';
                
                // Process the query and generate response (RAG)
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
                
                // Simple keyword extraction (this could be more sophisticated)
                const keywords = lowerQuestion.split(' ')
                    .filter(word => word.length > 3)
                    .map(word => word.replace(/[^a-zA-Z0-9]/g, ''));
                
                // Search for relevant articles
                let relevantArticles = [];
                newsData.forEach(article => {{
                    let score = 0;
                    const title = article.title.toLowerCase();
                    const body = article.body.toLowerCase();
                    const fullContent = article.full_content ? article.full_content.toLowerCase() : '';
                    
                    // Check if keywords are in title, body or full content
                    keywords.forEach(keyword => {{
                        if (title.includes(keyword)) score += 5;  // Title matches are weighted highest
                        if (body.includes(keyword)) score += 3;   // Summary matches are important
                        if (fullContent && fullContent.includes(keyword)) score += 1;  // Full content matches
                    }});
                    
                    // For specific question types, check for entities in full content
                    if ((lowerQuestion.includes('who') || lowerQuestion.includes('person')) && fullContent) {{
                        // Simple entity detection (could be more sophisticated)
                        const nameRegex = /([A-Z][a-z]+ [A-Z][a-z]+)/g;
                        const names = fullContent.match(nameRegex);
                        if (names && names.length > 0) score += 2;
                    }}
                    
                    if (score > 0) {{
                        relevantArticles.push({{...article, score}});
                    }}
                }});
                
                // Sort by relevance
                relevantArticles.sort((a, b) => b.score - a.score);
                
                // Generate response based on findings
                if (relevantArticles.length > 0) {{
                    const mostRelevant = relevantArticles[0];
                    let response = "";  // Define response variable
                    
                    // Extract the most relevant snippet from full content if available
                    let informativeSnippet = '';
                    if (mostRelevant.full_content) {{
                        const fullContent = mostRelevant.full_content;
                        
                        // Find a paragraph containing at least one keyword
                        const paragraphs = fullContent.split(/\\s+/).join(' ').split('. ').filter(p => p.length > 50);
                        
                        for (const paragraph of paragraphs) {{
                            if (keywords.some(keyword => paragraph.toLowerCase().includes(keyword))) {{
                                informativeSnippet = paragraph.substring(0, 250) + '...';
                                break;
                            }}
                        }}
                        
                        // If no good paragraph found, just take the beginning
                        if (!informativeSnippet && fullContent.length > 0) {{
                            informativeSnippet = fullContent.substring(0, 250) + '...';
                        }}
                    }}
                    
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
                    
                    addMessageWithCitation(response, `${{mostRelevant.source}}, ${{mostRelevant.date}}`);
                    
                    // If there are more relevant articles, mention them
                    if (relevantArticles.length > 1) {{
                        setTimeout(() => {{
                            addMessage(`I also found ${{relevantArticles.length - 1}} more articles that might be relevant. Would you like to know more about any specific topic?`, 'bot');
                        }}, 1000);
                    }}
                }} else {{
                    addMessage(`I couldn't find any information about that in the current news articles. Could you try asking something else?`, 'bot');
                }}
            }}
            
            // Event listeners for sending messages
            sendButton.addEventListener('click', sendMessage);
            chatInput.addEventListener('keypress', (e) => {{
                if (e.key === 'Enter') sendMessage();
            }});
        }});
    </script>
</body>
</html>
"""

# Write the HTML file
with open("index.html", "w", encoding="utf-8") as file:
    file.write(html_content)

print("HTML dashboard created successfully!")
