import json
import csv
import sys
sys.path.append('.')
from parse_idweek2025_sessions import IDWeek2025SessionCrawler

# Load existing JSON data
with open('original_data/idweek2025_sessions.json', 'r') as f:
    data = json.load(f)

# Create crawler instance and set data
crawler = IDWeek2025SessionCrawler()
crawler.crawled_data = data

# Save fixed CSV
crawler.save_to_csv('original_data/idweek2025_sessions_fixed.csv')
print(f'Generated fixed CSV with {len(data)} sessions')