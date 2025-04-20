import html
import datetime
import json

def generate_html_head_and_styles():
    """
    Generate the HTML header and CSS styles
    
    Returns:
        HTML string containing the head section and CSS styles
    """
    return """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta http-equiv="refresh" content="604800">
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

def generate_news_items_html(news_items):
    """
    Generate HTML for each news item
    
    Args:
        news_items: List of news items as dictionaries
        
    Returns:
        HTML string containing all news item cards
    """
    html_content = ""
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
    return html_content

def generate_chatbot_html(news_data_for_js):
    """
    Generate the HTML for the chatbot section
    
    Args:
        news_data_for_js: List of news items prepared for JavaScript
        
    Returns:
        HTML string containing the chatbot section and closing tags
    """
    # Use date-only format without time components
    current_date = datetime.datetime.now().strftime('%Y-%m-%d')
    
    return f"""
    </div>
    
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
        const newsData = {json.dumps(news_data_for_js)};
        const DEBUG = true;
    </script>
</body>
</html>
"""
