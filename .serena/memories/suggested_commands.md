# Conference Crawler - Suggested Commands

## Development Setup Commands

### IDWeek 2024 Environment
```bash
cd "IDWEEK 2024"
source myenv/bin/activate
pip install -r archive/requirements.txt
```

### ESCMID 2025 Environment
```bash
cd "ESCMID 2025/2025"
source venv/bin/activate
# Manual installation required:
pip install beautifulsoup4 requests pandas PyPDF2
```

### ECCMID 2024 Environment
```bash
cd "ECCMID 2024"
# Uses system Python - no virtual environment
```

## Data Extraction Workflows

### IDWeek 2024 Commands
```bash
python main.py                          # Extract session data
python cleanPosterData7.py             # Clean poster data  
python crawl_IDWEEK_2024_Schedule.py   # Crawl schedule
python saveParsedSessionData.py        # Save to database
```

### ESCMID 2025 Commands
```bash
python conference-data-extractor.py    # Extract from PDFs
python poster-data-extractor.py        # Process poster data
python manual-extractor.py             # Manual data tools
```

### ECCMID 2024 Commands
```bash
python crawl_ECCMID_main.py           # Main conference crawler
python crawl_ECCMID_Posters_main.py   # Poster-specific crawler
```

## System Utilities (macOS/Darwin)

### File Operations
```bash
ls -la                    # List files with details
find . -name "*.py"       # Find Python files
grep -r "pattern" .       # Search for text patterns
```

### Git Operations
```bash
git status                # Check repository status
git add .                 # Stage all changes
git commit -m "message"   # Commit changes
git log --oneline         # View commit history
```

### Directory Navigation
```bash
cd "IDWEEK 2024"         # Change to conference directory
pwd                       # Show current directory
tree                      # Display directory structure (if installed)
```

## Development Workflow
1. Navigate to specific conference directory
2. Activate virtual environment (if applicable)
3. Run extraction scripts in sequence
4. Check output files (.csv, .json, .txt)
5. Test ColdFusion interfaces locally