# Conference Crawler - Project Overview

## Purpose
Conference Crawler is a specialized data extraction toolkit for scraping and processing medical conference data from infectious disease conferences (ECCMID, IDWeek, ESCMID). The system serves pharmaceutical medical science liaison teams by gathering cutting-edge science information when they attend meetings on-site. It compiles conference data into Excel files and provides GUI frontends for easy access.

## Architecture Overview
The system follows a multi-stage data processing pipeline:
1. **Web Scraping/PDF Parsing**: Extract raw content from conference sources
2. **Data Cleaning**: Normalize author names, affiliations, abstracts  
3. **Multi-format Output**: Generate CSV, JSON, SQL, and Excel files
4. **ColdFusion Interface**: Web-based data browsing with DataTables.js
5. **Database Integration**: SQL Server-style queries for data retrieval

## Key Components

### Session Data Extraction
- Parses HTML tables for session times, speakers, locations
- Handles multi-day conference schedules
- Extracts abstracts and author affiliations
- Example: IDWeek 2024 main.py processes session data with timezone handling

### Poster Processing
- PDF text extraction for poster sessions
- Author/affiliation parsing and normalization
- Structured output with presentation numbers and topics
- Example: ESCMID 2025 uses PyPDF2 for PDF text extraction

### ColdFusion Web Interface
- Interactive data tables with search/filter capabilities
- Date-based session filtering 
- Direct SQL database queries
- Bootstrap responsive design
- Expects specific database table structures (e.g., `ECCMID_Posters_2024_03_27`, `IDWEEK_2024`)

## Directory Structure
- `IDWEEK 2024/`: IDWeek conference processing (Python 3.12 + myenv/)
- `ESCMID 2025/2025/`: ESCMID processing (Python 3.9 + venv/)  
- `ECCMID 2024/`: ECCMID processing (system Python)
- Root-level `.txt` files: Extracted output data
- `@docs/`: Library documentation

## Data Output Formats
The system generates multiple output formats simultaneously:
- **CSV**: Structured tabular data for analysis
- **JSON**: Hierarchical data for APIs
- **SQL**: Database insert statements  
- **Excel**: Formatted reports for stakeholders
- **HTML**: Raw scraped content for debugging