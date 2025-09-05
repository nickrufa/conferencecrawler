# Conference Crawler - Coding Conventions and Style

## Python Code Style

### Function Naming
- Snake_case for function names: `extract_country()`, `parse_session()`, `write_to_csv()`
- Descriptive names that clearly indicate purpose
- Functions often prefixed with action verb: `extract_`, `parse_`, `crawl_`, `clean_`

### Variable Naming
- Snake_case for variables: `session_header_div`, `date_time_split`, `program_session_card_references`
- Descriptive names with context: `session_type_pattern`, `chairs_match`, `presentation_pattern`
- HTML-related variables often include element type: `_div`, `_span`, `_el`

### Documentation Style
- Docstrings for complex functions: `"""Parse a single session block into structured data."""`
- Inline comments for regex patterns and complex logic
- No extensive type hints used in legacy code

### Error Handling
- Basic existence checks: `if not os.path.exists(pdf_path):`
- Print statements for user feedback: `print(f"Error: File {pdf_path} not found.")`
- Graceful degradation when data parsing fails

### Data Structures
- Dictionaries for structured data:
  ```python
  session_data = {
      'session_id': None,
      'time': None,
      'hall': None,
      'session_type': None,
      'title': None,
      'chairs': [],
      'presentations': []
  }
  ```
- Lists for collections: `faculty_sections`, `presentations`

### Regular Expressions
- Compiled patterns stored in variables for reuse
- Named groups not commonly used, positional groups preferred
- Complex multi-line patterns with `re.DOTALL` flag

## ColdFusion Code Style

### Parameter Definition
- All parameters defined at top with defaults:
  ```cfm
  <cfparam name="thisPageAction" default="display">
  <cfparam name="url.thisID" default="">
  ```

### Query Naming
- Descriptive prefixes: `getAllECCMIDSessionData`, `getFilteredECCMIDSessionData`
- CamelCase for query names
- Conditional WHERE clauses with cfqueryparam for security

### Database Integration
- Table names follow conference pattern: `ECCMID_2024`, `IDWEEK_2024`
- Date-based filtering common: `sessionLocalStart like "#url.thisStartDate#%"`

## File Organization

### Conference-Specific Structure
- Each conference in separate directory
- Main scripts named descriptively: `crawl_ECCMID_main.py`, `cleanPosterData7.py`
- Version numbers in filenames when iterating: `v2.py`, `v3.py`

### Output Files
- Timestamped HTML files: `eccmid-posters-20240328105852.html`
- Multiple format outputs: `.csv`, `.json`, `.txt`, `.xlsx`
- Debug files often prefixed: `_debug.txt`, `unparsed.txt`

### Dependencies
- No centralized package management
- Conference-specific requirements files
- Manual dependency installation documented per environment

## Development Patterns

### Rate Limiting
- Built-in delays: `time.sleep()` between requests
- Respectful scraping practices

### Data Processing Pipeline
1. Extract raw data (HTML/PDF)
2. Parse and structure
3. Clean and normalize
4. Output multiple formats
5. Optional database storage

### Local Development
- Hardcoded local URLs: `http://local.dev.meetings.com`
- Development/production environment distinction