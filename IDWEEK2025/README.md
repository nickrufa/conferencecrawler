# IDWeek 2025 Conference Data Extraction

This directory contains the complete workflow for scraping and parsing data from the IDWeek 2025 event website.

## Process Overview

### Step 1: Save HTML from Meeting Site
Visit the IDWeek 2025 meeting website and manually save HTML content from Session and Poster pages to:
- `IDWEEK2025/source_html_from_meeting_URLs/`

### Step 2: Extract Poster IDs
Extract poster IDs from the saved HTML files and insert them into MySQL table, populating the `poster_id` column.
Use BBEdit or text tool to parse out IDs. SQL Insert the list of IDs.

### Step 3: Crawl Raw Poster Data
Use the CFML crawler to fetch and save raw poster data:
- Run: `IDWEEK2025/cfml_crawler/_getPosterSessionAgendaItem.cfm`
- This saves `rawPosterData` to the same MySQL table

### Step 4: Review Poster Data
Use the CFML viewer to cycle through posters:
- Access: `IDWEEK2025/cfml_viewer/posters.cfm`
- Navigate through poster IDs from 1 through total count of table records

### Step 5: Parse Poster Data
Run the Python parser to extract structured data:
- Execute: `python IDWEEK2025/parse_idweek2025_posters.py`
- Outputs: CSV and JSON files with extracted poster data

### Steps 6-10: Session Data Processing
Repeat the above process for Session data:
6. Save Session HTML files to source directory
7. Extract session IDs and populate MySQL table
8. Use CFML crawler for raw session data collection
9. Review session data with CFML viewer
10. Run Python parser for session data extraction

## Directory Structure
- `cfml_crawler/` - ColdFusion scripts for data crawling
- `cfml_viewer/` - ColdFusion templates for data review
- `source_html_from_meeting_URLs/` - Raw HTML files from meeting site
- `parse_idweek2025_posters.py` - Python parser for poster data

## Important Notes
Hard-coded paths and URLs will need to be updated when adapting this workflow for new meetings/years. New SQL tables and also locally running web server, to do the crawls and parsing scripts.
