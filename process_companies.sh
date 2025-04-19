#!/bin/bash

# Create header for aggregated CSV with company as first column
echo "company,date,title,body,url,image,source" > aggregated-news.csv

# Process companies and append to CSV
for company in 'Unaliwear' 'BrainCheck' 'Dermala' 'Oralucent' 'Flowly' 'Rosy' 'De Oro Devices' 'Partum Health' 'Fort Health' 'RubyWell' 'Atlantic Sea Farms' 'VidaFuel'; do
  echo "Processing $company..."
  # Normal processing with retry - Add single quotes around company for phrase search
  ddgs news -k "'$company' company" -m 2 -o "news-$company.csv" || 
  # Retry once if it fails - Add single quotes around company for phrase search
  (echo "Retrying $company..." && sleep 5 && ddgs news -k "'$company' company" -m 2 -o "news-$company.csv")
    # Check if CSV was created and has content (more than just header)
    if [ -f "news-$company.csv" ] && [ $(wc -l < "news-$company.csv") -gt 1 ]; then
      # Skip header row and add company as first column for each row using awk with a variable
      awk -F, -v company="$company" 'NR>1 {printf("\"%s\",%s\n", company, $0)}' "news-$company.csv" >> aggregated-news.csv
      echo "Added $company news to aggregated CSV"
  else
    echo "Warning: No results for $company or CSV creation failed"
    # Create an empty CSV with just the header to prevent errors
    echo "date,title,body,url,image,source" > "news-$company.csv"
    # Add a placeholder entry in aggregated CSV
    echo "\"$company\",\"$(date +%Y-%m-%d)\",\"No recent news found for $company\",\"No content available\",\"#\",\"\",\"System\"" >> aggregated-news.csv
  fi
  # Add a small delay to avoid rate limiting
  sleep 2
done

# Show summary
echo "Aggregated news CSV created with $(( $(wc -l < aggregated-news.csv) - 1 )) entries"