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
        for element in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'form']):
            element.decompose()
            
        # First try to find the main article content
        main_content = None
        for selector in ['article', '.article', '.post-content', '.story', 'main', '#content', '.content']:
            content = soup.select_one(selector)
            if content and len(content.get_text(strip=True)) > 200:
                main_content = content
                break
        
        # If no specific article container is found, use the whole body
        if not main_content:
            main_content = soup.body
        
        # Get text and clean it up
        if (main_content):
            text = main_content.get_text(separator='\n', strip=True)
            # Clean up white spaces but preserve paragraph structure
            text = '\n'.join([' '.join(line.split()) for line in text.split('\n') if line.strip()])
        else:
            text = soup.get_text(separator='\n', strip=True)
            text = '\n'.join([' '.join(line.split()) for line in text.split('\n') if line.strip()])
        
        # Return only the first 10000 characters to avoid massive texts
        return text[:10000]
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
                
                if (DEBUG) {{
                    console.log('Processing query:', question);
                    console.log('Available articles:', newsData.length);
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
                    
                    // Check for direct question matches in content
                    if (fullContent && fullContent.includes(lowerQuestion)) {{
                        score += 10; // Large boost for exact question match
                    }}
                    
                    // Check if keywords are in title, body or full content
                    keywords.forEach(keyword => {{
                        // Check for exact matches first
                        if (title.includes(keyword)) score += 5;  // Title matches are weighted highest
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
                            console.log(`Article: ${article.title}, Score: ${score}`);
                        }}
                        relevantArticles.push({{...article, score}});
                    }}
                }});
                
                // Sort by relevance
                relevantArticles.sort((a, b) => b.score - a.score);
                
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
            
            // Make sure chat toggle is visible on page load
            chatToggle.style.display = 'flex';
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
