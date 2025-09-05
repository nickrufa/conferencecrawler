# Conference Crawler - Tech Stack

## Core Technologies

### Programming Languages
- **Python 3.9-3.12**: Main scripting language for data extraction
- **ColdFusion (.cfm)**: Web templates for data visualization and database queries

### Python Libraries & Frameworks
- **BeautifulSoup4**: HTML parsing and web scraping framework
- **Requests**: HTTP client for web requests and API calls
- **Pandas**: Data processing, analysis, and CSV/JSON output generation
- **PyPDF2**: PDF text extraction (legacy, some projects use PyPDF)
- **pdfplumber**: Advanced PDF text extraction and table detection

### Web Technologies
- **HTML/CSS**: Static content and styling
- **JavaScript**: Client-side functionality
- **DataTables.js**: Interactive data table functionality
- **Bootstrap**: Responsive web design framework

### Database & Data Storage
- **SQL Server**: Primary database for conference data
- **CSV files**: Tabular data export format
- **JSON files**: Hierarchical data for APIs
- **Excel files**: Formatted reports for stakeholders

## Environment Setup

### IDWeek 2024
- Python 3.12
- Virtual environment: `myenv/`
- Dependencies: `requirements.txt` with beautifulsoup4, requests, etc.

### ESCMID 2025
- Python 3.9
- Virtual environment: `venv/`
- Manual installation: beautifulsoup4, requests, pandas, PyPDF2

### ECCMID 2024
- System Python (no virtual environment)
- Dependencies managed manually

## Development Tools
- **Git**: Version control
- **Virtual environments**: Isolated Python environments per conference
- **macOS (Darwin)**: Primary development platform