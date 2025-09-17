# Faculty Data Migration Guide

## Schema Evolution

### ❌ DEPRECATED: `faculty_database_schema.sql` 
- Conference-specific approach
- Modified existing table structure
- Limited cross-conference capabilities

### ✅ CURRENT: `improved_faculty_schema.sql`
- Master faculty table approach
- Cross-conference deduplication
- Career progression tracking

## Migration Steps

### 1. Use Improved Schema
```bash
mysql -u user -p database < improved_faculty_schema.sql
```

### 2. Process with Deduplication
```bash
python faculty_deduplication_processor.py \
    --user DB_USER \
    --password DB_PASS \
    --database DB_NAME
```

### 3. Verify Results
```sql
-- Check faculty distribution
SELECT * FROM faculty_conference_summary;

-- Verify poster counts
SELECT conference_name, conference_year, COUNT(*) as poster_count
FROM Conference_Posters 
GROUP BY conference_name, conference_year;
```

## Key Differences

| Feature | Old Schema | New Schema |
|---------|------------|------------|
| Cross-conference | ❌ No | ✅ Yes |
| Deduplication | ❌ Manual | ✅ Automatic |
| Career tracking | ❌ No | ✅ Yes |
| Scalability | ❌ Limited | ✅ Excellent |
| Data integrity | ⚠️ OK | ✅ High |

## Benefits of New Approach

- **Juan Carlos Orengo problem solved** - One person, multiple conferences
- **Organization changes tracked** - Career progression visible
- **Email deduplication** - Catches same person, different name formats
- **Future-proof** - Easy to add ECCMID, ESCMID data

## Files Status

- ✅ `improved_faculty_schema.sql` - **USE THIS**
- ✅ `faculty_deduplication_processor.py` - **USE THIS** 
- ✅ `faculty_html_parser.py` - Still valid
- ❌ `faculty_database_schema_DEPRECATED.sql` - Reference only
- ❌ `process_faculty_data.py` - Replace with deduplication processor