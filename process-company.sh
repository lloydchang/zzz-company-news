#!/bin/bash

# Create header for aggregated CSV with company as first column
echo "company,date,title,body,url,image,source" > aggregated-news.csv

# Process companies and append to CSV
for company in 'Unaliwear' 'BrainCheck' 'Dermala' 'Oralucent' 'Flowly' 'Rosy Wellness' 'De Oro Devices' 'Partum Health' 'Fort Health' 'RubyWell' 'Atlantic Sea Farms' 'VidaFuel'; do
  echo "Processing $company..."
  # Check if company name contains multiple words
  if [[ "$company" == *" "* ]]; then
    search_term="\"$company\" company"
  else
    search_term="$company company"
  fi
  
  # Normal processing with retry
  ddgs news -k "$search_term" -m 2 -o "news-$company.csv" || 
  # Retry once if it fails
  (echo "Retrying $company..." && sleep 5 && ddgs news -k "$search_term" -m 2 -o "news-$company.csv")
  
  # Check if CSV was created and has content (more than just header)
  if [ -f "news-$company.csv" ] && [ $(wc -l < "news-$company.csv") -gt 1 ]; then
    # Skip header row and add company as first column for each row
    awk -F, -v company="$company" 'NR>1 {printf("\"%s\",%s\n", company, $0)}' "news-$company.csv" >> aggregated-news.csv
    echo "Added $company news to aggregated CSV"
  else
    echo "Warning: No results for $company or CSV creation failed"
    # Create an empty CSV with just the header to prevent errors
    echo "date,title,body,url,image,source" > "news-$company.csv"
    # Add a placeholder entry in aggregated CSV with date only (no time components)
    echo "\"$company\",\"$(date +%Y-%m-%d)\",\"No news\",,,," >> aggregated-news.csv
  fi
done

# Show summary
echo "Aggregated news CSV created with $(( $(wc -l < aggregated-news.csv) - 1 )) entries"
