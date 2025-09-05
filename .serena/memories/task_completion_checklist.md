# Conference Crawler - Task Completion Checklist

## When a Development Task is Completed

### Code Quality Checks
- **No formal linting/formatting tools configured** - Manual code review required
- Check for consistent naming conventions (snake_case for Python, camelCase for ColdFusion)
- Verify proper error handling and user feedback messages
- Ensure rate limiting is in place for web scraping operations

### Testing Procedures
- **No automated test framework** - Manual testing required
- Test with sample conference data
- Verify output file generation in multiple formats (CSV, JSON, Excel)
- Check ColdFusion web interfaces locally at `http://local.dev.meetings.com`
- Validate database integration if applicable

### Output Validation
- Confirm all expected output formats are generated:
  - CSV files for tabular data
  - JSON files for API compatibility  
  - Excel files for stakeholder reports
  - SQL files for database imports (if applicable)
- Check file naming conventions (timestamps, version numbers)
- Verify data integrity and completeness

### Environment-Specific Checks

#### IDWeek 2024
```bash
cd "IDWEEK 2024"
source myenv/bin/activate
python main.py                          # Test session extraction
python cleanPosterData7.py             # Test poster cleaning
python crawl_IDWEEK_2024_Schedule.py   # Test schedule crawling
```

#### ESCMID 2025
```bash
cd "ESCMID 2025/2025"  
source venv/bin/activate
python conference-data-extractor.py    # Test PDF extraction
python poster-data-extractor.py        # Test poster processing
```

#### ECCMID 2024
```bash
cd "ECCMID 2024"
python crawl_ECCMID_main.py           # Test main crawler
python crawl_ECCMID_Posters_main.py   # Test poster crawler  
```

### Documentation Updates
- Update CLAUDE.md if new commands or workflows are added
- Document any new dependencies or environment changes
- Update conference-specific README files if they exist

### Final Deployment Checklist
- Backup existing data files before running new extractions
- Test database connections and table structures
- Verify ColdFusion templates work with new data formats
- Confirm local development URLs are properly configured
- Check that all output files are properly generated and accessible

### Common Issues to Watch For
- **Memory usage**: Large conference datasets can cause memory issues
- **Rate limiting**: Ensure proper delays between web requests
- **File permissions**: Check write permissions for output directories
- **Database compatibility**: Verify SQL statements work with target database
- **Character encoding**: Handle international characters in author names/affiliations