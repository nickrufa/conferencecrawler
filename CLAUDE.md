# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

Conference Crawler is a specialized data extraction toolkit for scraping and processing medical conference data from infectious disease conferences (ECCMID, IDWeek, ESCMID). The system combines Python-based web scraping with ColdFusion web interfaces for data visualization.

## Tech Stack

- **Python 3.9-3.12**: Main scripting language for data extraction
- **ColdFusion (.cfm)**: Web templates for data visualization  
- **BeautifulSoup4 + Requests**: Web scraping framework
- **PyPDF2**: PDF text extraction
- **Pandas**: Data processing and CSV/JSON output

## Development Setup

Each conference has its own isolated environment:

```bash
# IDWeek 2024
cd "IDWEEK 2024"
source myenv/bin/activate
pip install -r archive/requirements.txt

# ESCMID 2025  
cd "ESCMID 2025/2025"
source venv/bin/activate
# Install: beautifulsoup4, requests, pandas, PyPDF2

# ECCMID 2024
cd "ECCMID 2024"
# No virtual environment - uses system Python
```

## Common Commands

### Data Extraction Workflows

**IDWeek 2024:**
```bash
python main.py                          # Extract session data
python cleanPosterData7.py             # Clean poster data  
python crawl_IDWEEK_2024_Schedule.py   # Crawl schedule
python saveParsedSessionData.py        # Save to database
```

**ESCMID 2025:**
```bash
python conference-data-extractor.py    # Extract from PDFs
python poster-data-extractor.py        # Process poster data
python manual-extractor.py             # Manual data tools
```

**ECCMID 2024:**
```bash
python crawl_ECCMID_main.py           # Main conference crawler
python crawl_ECCMID_Posters_main.py   # Poster-specific crawler
```

## Architecture

### Data Processing Pipeline
1. **Web Scraping/PDF Parsing**: Extract raw content from conference sources
2. **Data Cleaning**: Normalize author names, affiliations, abstracts  
3. **Multi-format Output**: Generate CSV, JSON, SQL, and Excel files
4. **ColdFusion Interface**: Web-based data browsing with DataTables.js
5. **Database Integration**: SQL Server-style queries for data retrieval

### Directory Structure
- `IDWEEK 2024/`: IDWeek conference processing (Python 3.12 + myenv/)
- `ESCMID 2025/2025/`: ESCMID processing (Python 3.9 + venv/)  
- `ECCMID 2024/`: ECCMID processing (system Python)
- Root-level `.txt` files: Extracted output data

### Key Components

**Session Data Extraction**: 
- Parses HTML tables for session times, speakers, locations
- Handles multi-day conference schedules
- Extracts abstracts and author affiliations

**Poster Processing**:
- PDF text extraction for poster sessions
- Author/affiliation parsing and normalization
- Structured output with presentation numbers and topics

**ColdFusion Web Interface**:
- Interactive data tables with search/filter
- Date-based session filtering 
- Direct SQL database queries
- Bootstrap responsive design

## Data Output Formats

The system generates multiple output formats simultaneously:
- **CSV**: Structured tabular data for analysis
- **JSON**: Hierarchical data for APIs
- **SQL**: Database insert statements  
- **Excel**: Formatted reports for stakeholders
- **HTML**: Raw scraped content for debugging

## Development Notes

- Documentation stored in `/docs` folder
- Each conference uses conference-specific parsing logic
- Built-in rate limiting with `time.sleep()` between requests
- No centralized package management - dependencies managed per conference
- Local development URLs hardcoded to `http://local.dev.meetings.com`
- ColdFusion templates expect specific database table structures (e.g., `ECCMID_Posters_2024_03_27`, `IDWEEK_2024`)