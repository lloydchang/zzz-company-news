import csv
import html
import datetime

# Read the CSV file
news_items = []
with open("aggregated-news.csv", "r", encoding="utf-8") as file:
    reader = csv.DictReader(file)
    for row in reader:
        news_items.append(row)

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
    title = html.escape(item.get("title", "No title"))
    url = html.escape(item.get("url", "#"))
    source = html.escape(item.get("source", "Unknown source"))
    snippet = html.escape(item.get("snippet", "No description available"))
    date = html.escape(item.get("date", ""))
    
    # Determine company by looking at the filename pattern in the CSV
    company = "Unknown"
    for field in item:
        if field.lower() == "query" and item[field]:
            company = item[field].strip('"')
            break
    
    html_content += f"""
    <div class="news-card">
        <span class="company-tag">{company}</span>
        <h3 class="news-title"><a href="{url}" target="_blank">{title}</a></h3>
        <div class="news-source">{source}</div>
        <p>{snippet}</p>
        <div class="news-date">{date}</div>
    </div>
    """

# Complete the HTML document
current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
