# IDWeek 2025 Faculty Data Processing

This toolkit processes faculty HTML data from the `IDWEEK_Faculty_2025` table and creates a normalized database structure for better data analysis and querying.

## Files Created

1. **`faculty_database_schema.sql`** - Database schema with normalized tables
2. **`faculty_html_parser.py`** - HTML parsing logic
3. **`process_faculty_data.py`** - Main processing script
4. **`requirements.txt`** - Python dependencies

## Database Structure

### Enhanced Faculty Table
The existing `IDWEEK_Faculty_2025` table gets new columns:
- `full_name`, `credentials`, `job_title`, `organization`
- `photo_url`, `email`, `disclosure_info`, `biography`
- `parsing_status`, `parse_error_msg`

### New Tables
- **`IDWEEK_Posters_2025`** - Normalized poster information
- **`IDWEEK_Faculty_Posters_2025`** - Faculty-poster relationships

### Useful Views
- `faculty_with_posters` - Complete faculty and poster information
- `faculty_without_posters` - Faculty missing poster data
- `parsing_stats` - Processing statistics

## Setup Instructions

### 1. Install Dependencies
```bash
cd "IDWEEK 2025"
source myenv/bin/activate  # Use your existing virtual environment
pip install -r requirements.txt
```

### 2. Create Database Schema
```bash
mysql -u your_user -p your_database < faculty_database_schema.sql
```

### 3. Process Faculty Data

#### Check Current Status
```bash
python process_faculty_data.py \
    --user your_db_user \
    --password your_db_password \
    --database your_db_name \
    --summary
```

#### Process All Records
```bash
python process_faculty_data.py \
    --user your_db_user \
    --password your_db_password \
    --database your_db_name
```

#### Process Limited Records (for testing)
```bash
python process_faculty_data.py \
    --user your_db_user \
    --password your_db_password \
    --database your_db_name \
    --limit 10
```

## Data Extraction Features

### Faculty Information Extracted
- **Name & Credentials** - Parsed from full name (e.g., "David Singer, PharmD, MS")
- **Job Title & Organization** - Extracted from organization field
- **Contact Info** - Email addresses from mailto links
- **Professional Info** - Disclosure statements and biographies
- **Photos** - Profile photo URLs

### Poster Information Extracted
- **Poster Details** - ID, number (P-1469), title
- **Schedule** - Date, time, timezone
- **References** - URL links to poster details

### Date/Time Parsing
Handles multiple formats:
- "Tuesday, October 21, 2025"
- "12:15 PM - 1:30 PM US ET"
- Converts to standardized database formats

## Usage Examples

### Query Faculty with Posters
```sql
SELECT * FROM faculty_with_posters 
WHERE organization LIKE '%GSK%';
```

### Find Faculty by Expertise Area
```sql
SELECT f.full_name, f.organization, p.title as poster_title
FROM IDWEEK_Faculty_2025 f
JOIN IDWEEK_Faculty_Posters_2025 fp ON f.id = fp.faculty_id
JOIN IDWEEK_Posters_2025 p ON fp.poster_id = p.poster_id
WHERE f.biography LIKE '%RSV%' OR p.title LIKE '%RSV%';
```

### Check Processing Statistics
```sql
SELECT * FROM parsing_stats;
```

## Error Handling

The system tracks processing status:
- **`pending`** - Not yet processed
- **`parsed`** - Successfully processed
- **`error`** - Processing failed (see `parse_error_msg`)

Failed records are logged with detailed error messages for debugging.

## Logging

Processing creates `faculty_processing.log` with detailed information:
- Records processed
- Parsing success/failure
- Database operations
- Error details

## Data Quality Notes

- **Name Parsing** - Handles various credential formats (MD, PhD, PharmD, etc.)
- **Organization Parsing** - Separates job titles from organization names
- **Date Standardization** - Converts various date formats to YYYY-MM-DD
- **Duplicate Handling** - Posters are deduplicated by poster_id
- **Relationship Tracking** - Maintains faculty-poster associations

## Maintenance

### Re-processing Records
To reprocess records (e.g., after parser improvements):
```sql
UPDATE IDWEEK_Faculty_2025 SET parsing_status = NULL WHERE parsing_status = 'error';
```

### Data Validation Queries
```sql
-- Find faculty without organizations
SELECT * FROM IDWEEK_Faculty_2025 WHERE parsing_status = 'parsed' AND organization IS NULL;

-- Find posters without dates
SELECT * FROM IDWEEK_Posters_2025 WHERE presentation_date IS NULL;

-- Check for parsing errors
SELECT parse_error_msg, COUNT(*) FROM IDWEEK_Faculty_2025 
WHERE parsing_status = 'error' GROUP BY parse_error_msg;
```