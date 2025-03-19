import csv
import html
import datetime
import os

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

# Complete the HTML document
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
