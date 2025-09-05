# MySQL 8.0 Documentation

## Overview
MySQL 8.0 is a powerful open-source relational database management system (RDBMS) that uses Structured Query Language (SQL). This version introduces significant improvements including window functions, common table expressions (CTEs), improved JSON support, and better performance.

## Installation & Configuration

### Connection Parameters
```sql
-- Basic connection
mysql -h hostname -u username -p database_name

-- With port
mysql -h hostname -P 3306 -u username -p database_name
```

### Configuration File (my.cnf / my.ini)
```ini
[mysqld]
# Basic Settings
port = 3306
datadir = /var/lib/mysql
socket = /var/lib/mysql/mysql.sock
max_connections = 151
max_allowed_packet = 64M

# InnoDB Settings
innodb_buffer_pool_size = 1G
innodb_log_file_size = 256M
innodb_flush_log_at_trx_commit = 1
innodb_flush_method = O_DIRECT

# Query Cache (deprecated in 8.0)
# query_cache_size = 0

# Character Set
character-set-server = utf8mb4
collation-server = utf8mb4_unicode_ci

# Performance Schema
performance_schema = ON
```

## Data Types

### Numeric Types
| Type | Storage | Range |
|------|---------|-------|
| `TINYINT` | 1 byte | -128 to 127 (signed) |
| `SMALLINT` | 2 bytes | -32,768 to 32,767 |
| `MEDIUMINT` | 3 bytes | -8,388,608 to 8,388,607 |
| `INT` | 4 bytes | -2,147,483,648 to 2,147,483,647 |
| `BIGINT` | 8 bytes | -9,223,372,036,854,775,808 to 9,223,372,036,854,775,807 |
| `DECIMAL(M,D)` | Variable | Exact numeric with M digits, D decimals |
| `FLOAT` | 4 bytes | Approximate numeric |
| `DOUBLE` | 8 bytes | Approximate numeric |

### String Types
| Type | Maximum Length | Description |
|------|----------------|-------------|
| `CHAR(M)` | 255 | Fixed-length string |
| `VARCHAR(M)` | 65,535 | Variable-length string |
| `TEXT` | 65,535 | Variable-length text |
| `MEDIUMTEXT` | 16,777,215 | Medium text |
| `LONGTEXT` | 4,294,967,295 | Long text |
| `ENUM` | 65,535 values | Enumeration |
| `SET` | 64 members | Set of values |

### Date and Time Types
| Type | Format | Range |
|------|--------|-------|
| `DATE` | YYYY-MM-DD | 1000-01-01 to 9999-12-31 |
| `TIME` | HH:MM:SS | -838:59:59 to 838:59:59 |
| `DATETIME` | YYYY-MM-DD HH:MM:SS | 1000-01-01 00:00:00 to 9999-12-31 23:59:59 |
| `TIMESTAMP` | YYYY-MM-DD HH:MM:SS | 1970-01-01 00:00:01 UTC to 2038-01-19 03:14:07 UTC |
| `YEAR` | YYYY | 1901 to 2155 |

### JSON Type (Enhanced in 8.0)
```sql
CREATE TABLE products (
    id INT PRIMARY KEY,
    name VARCHAR(100),
    attributes JSON
);

INSERT INTO products VALUES 
    (1, 'Laptop', '{"brand": "Dell", "ram": 16, "storage": {"ssd": 512, "hdd": null}}');

-- Query JSON
SELECT name, attributes->>'$.brand' AS brand
FROM products
WHERE JSON_EXTRACT(attributes, '$.ram') > 8;
```

## DDL (Data Definition Language)

### Database Operations
```sql
-- Create database
CREATE DATABASE IF NOT EXISTS medical_db
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

-- Use database
USE medical_db;

-- Drop database
DROP DATABASE IF EXISTS medical_db;

-- Show databases
SHOW DATABASES;
SHOW CREATE DATABASE medical_db;
```

### Table Operations
```sql
-- Create table
CREATE TABLE articles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author_id INT,
    category_id INT,
    status ENUM('draft', 'published', 'archived') DEFAULT 'draft',
    tags JSON,
    view_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    published_at DATETIME,
    INDEX idx_author (author_id),
    INDEX idx_category (category_id),
    INDEX idx_status_published (status, published_at),
    FOREIGN KEY (author_id) REFERENCES users(id) ON DELETE SET NULL,
    FOREIGN KEY (category_id) REFERENCES categories(id),
    FULLTEXT idx_fulltext (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Alter table
ALTER TABLE articles 
    ADD COLUMN subtitle VARCHAR(255) AFTER title,
    MODIFY COLUMN content LONGTEXT,
    DROP COLUMN view_count,
    ADD INDEX idx_created (created_at DESC);

-- Rename table
RENAME TABLE articles TO medical_articles;

-- Truncate table (delete all data)
TRUNCATE TABLE articles;

-- Drop table
DROP TABLE IF EXISTS articles;

-- Show table information
SHOW TABLES;
SHOW CREATE TABLE articles;
DESCRIBE articles;
SHOW FULL COLUMNS FROM articles;
```

### Partitioning (Enhanced in 8.0)
```sql
-- Range partitioning
CREATE TABLE articles_partitioned (
    id INT,
    title VARCHAR(255),
    published_date DATE,
    content TEXT,
    PRIMARY KEY (id, published_date)
) PARTITION BY RANGE (YEAR(published_date)) (
    PARTITION p2020 VALUES LESS THAN (2021),
    PARTITION p2021 VALUES LESS THAN (2022),
    PARTITION p2022 VALUES LESS THAN (2023),
    PARTITION p2023 VALUES LESS THAN (2024),
    PARTITION p_future VALUES LESS THAN MAXVALUE
);

-- List partitioning
CREATE TABLE regional_data (
    id INT,
    region VARCHAR(20),
    data JSON,
    PRIMARY KEY (id, region)
) PARTITION BY LIST COLUMNS(region) (
    PARTITION p_north VALUES IN ('NY', 'MA', 'CT'),
    PARTITION p_south VALUES IN ('FL', 'GA', 'TX'),
    PARTITION p_west VALUES IN ('CA', 'OR', 'WA')
);

-- Hash partitioning
CREATE TABLE user_sessions (
    session_id VARCHAR(64),
    user_id INT,
    data JSON,
    PRIMARY KEY (session_id)
) PARTITION BY HASH(user_id) PARTITIONS 8;
```

## DML (Data Manipulation Language)

### INSERT Operations
```sql
-- Single row insert
INSERT INTO articles (title, content, author_id)
VALUES ('MySQL 8.0 Features', 'Content here...', 1);

-- Multiple rows
INSERT INTO articles (title, content, author_id) VALUES
    ('Title 1', 'Content 1', 1),
    ('Title 2', 'Content 2', 2),
    ('Title 3', 'Content 3', 1);

-- Insert with ON DUPLICATE KEY UPDATE
INSERT INTO articles (id, title, view_count)
VALUES (1, 'Updated Title', 1)
ON DUPLICATE KEY UPDATE 
    title = VALUES(title),
    view_count = view_count + VALUES(view_count);

-- Insert from SELECT
INSERT INTO archived_articles
SELECT * FROM articles WHERE status = 'archived';

-- INSERT IGNORE (skip errors)
INSERT IGNORE INTO categories (name) VALUES ('Duplicate Name');
```

### UPDATE Operations
```sql
-- Basic update
UPDATE articles 
SET status = 'published',
    published_at = NOW()
WHERE id = 1;

-- Update with JOIN
UPDATE articles a
INNER JOIN users u ON a.author_id = u.id
SET a.status = 'archived'
WHERE u.status = 'inactive';

-- Update with subquery
UPDATE articles
SET category_id = (
    SELECT id FROM categories WHERE name = 'Research'
)
WHERE category_id IS NULL;

-- Update with CASE
UPDATE articles
SET status = CASE
    WHEN view_count > 1000 THEN 'popular'
    WHEN view_count > 100 THEN 'active'
    ELSE 'normal'
END;
```

### DELETE Operations
```sql
-- Basic delete
DELETE FROM articles WHERE id = 1;

-- Delete with JOIN
DELETE a FROM articles a
INNER JOIN users u ON a.author_id = u.id
WHERE u.status = 'deleted';

-- Delete with LIMIT
DELETE FROM log_entries 
WHERE created_at < DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at
LIMIT 1000;

-- Delete all rows (slower than TRUNCATE)
DELETE FROM articles;
```

## SELECT Queries

### Basic SELECT
```sql
-- Select all columns
SELECT * FROM articles;

-- Select specific columns
SELECT id, title, created_at FROM articles;

-- With WHERE clause
SELECT * FROM articles 
WHERE status = 'published' 
  AND created_at >= '2024-01-01';

-- With ORDER BY and LIMIT
SELECT * FROM articles
ORDER BY created_at DESC, title ASC
LIMIT 10 OFFSET 20;

-- DISTINCT values
SELECT DISTINCT category_id FROM articles;

-- Aggregation
SELECT 
    status,
    COUNT(*) as count,
    AVG(view_count) as avg_views,
    MAX(created_at) as latest
FROM articles
GROUP BY status
HAVING count > 5;
```

### JOINs
```sql
-- INNER JOIN
SELECT a.title, u.name as author_name, c.name as category
FROM articles a
INNER JOIN users u ON a.author_id = u.id
INNER JOIN categories c ON a.category_id = c.id;

-- LEFT JOIN
SELECT u.name, COUNT(a.id) as article_count
FROM users u
LEFT JOIN articles a ON u.id = a.author_id
GROUP BY u.id;

-- RIGHT JOIN
SELECT c.name, a.title
FROM articles a
RIGHT JOIN categories c ON a.category_id = c.id;

-- CROSS JOIN
SELECT u.name, c.name as category
FROM users u
CROSS JOIN categories c;

-- Self JOIN
SELECT a1.title, a2.title as related_title
FROM articles a1
JOIN articles a2 ON a1.category_id = a2.category_id
WHERE a1.id != a2.id AND a1.id = 1;
```

### Subqueries
```sql
-- Scalar subquery
SELECT title,
    (SELECT name FROM users WHERE id = articles.author_id) as author_name
FROM articles;

-- IN subquery
SELECT * FROM articles
WHERE author_id IN (
    SELECT id FROM users WHERE status = 'active'
);

-- EXISTS subquery
SELECT * FROM users u
WHERE EXISTS (
    SELECT 1 FROM articles a 
    WHERE a.author_id = u.id 
    AND a.status = 'published'
);

-- Correlated subquery
SELECT title, view_count
FROM articles a1
WHERE view_count > (
    SELECT AVG(view_count) 
    FROM articles a2 
    WHERE a2.category_id = a1.category_id
);
```

## Advanced Features (MySQL 8.0)

### Window Functions
```sql
-- ROW_NUMBER()
SELECT 
    title,
    category_id,
    view_count,
    ROW_NUMBER() OVER (PARTITION BY category_id ORDER BY view_count DESC) as rank_in_category
FROM articles;

-- RANK() and DENSE_RANK()
SELECT 
    title,
    view_count,
    RANK() OVER (ORDER BY view_count DESC) as rank,
    DENSE_RANK() OVER (ORDER BY view_count DESC) as dense_rank
FROM articles;

-- LAG() and LEAD()
SELECT 
    title,
    created_at,
    LAG(created_at, 1) OVER (ORDER BY created_at) as previous_article_date,
    LEAD(created_at, 1) OVER (ORDER BY created_at) as next_article_date
FROM articles;

-- Running totals
SELECT 
    DATE(created_at) as date,
    COUNT(*) as daily_count,
    SUM(COUNT(*)) OVER (ORDER BY DATE(created_at)) as running_total
FROM articles
GROUP BY DATE(created_at);
```

### Common Table Expressions (CTEs)
```sql
-- Simple CTE
WITH active_authors AS (
    SELECT DISTINCT author_id 
    FROM articles 
    WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
)
SELECT u.* 
FROM users u
JOIN active_authors aa ON u.id = aa.author_id;

-- Recursive CTE
WITH RECURSIVE category_tree AS (
    -- Anchor member
    SELECT id, name, parent_id, 0 as level
    FROM categories
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive member
    SELECT c.id, c.name, c.parent_id, ct.level + 1
    FROM categories c
    JOIN category_tree ct ON c.parent_id = ct.id
)
SELECT * FROM category_tree ORDER BY level, name;

-- Multiple CTEs
WITH 
author_stats AS (
    SELECT author_id, COUNT(*) as article_count
    FROM articles
    GROUP BY author_id
),
category_stats AS (
    SELECT category_id, COUNT(*) as article_count
    FROM articles
    GROUP BY category_id
)
SELECT u.name, aus.article_count, c.name as top_category
FROM users u
JOIN author_stats aus ON u.id = aus.author_id
JOIN articles a ON u.id = a.author_id
JOIN category_stats cs ON a.category_id = cs.category_id
GROUP BY u.id;
```

### JSON Functions (Enhanced)
```sql
-- JSON_TABLE (new in 8.0)
SELECT jt.*
FROM products,
JSON_TABLE(attributes, '$' COLUMNS (
    brand VARCHAR(50) PATH '$.brand',
    ram INT PATH '$.ram',
    ssd_size INT PATH '$.storage.ssd'
)) AS jt;

-- JSON aggregation
SELECT 
    category_id,
    JSON_ARRAYAGG(title) as titles,
    JSON_OBJECTAGG(id, title) as id_title_map
FROM articles
GROUP BY category_id;

-- JSON_CONTAINS
SELECT * FROM products
WHERE JSON_CONTAINS(tags, '"electronics"', '$');

-- JSON_SEARCH
SELECT JSON_SEARCH(attributes, 'one', 'Dell') as path
FROM products;

-- JSON Schema Validation (8.0.17+)
ALTER TABLE products
ADD CONSTRAINT check_attributes CHECK (
    JSON_SCHEMA_VALID('{
        "type": "object",
        "properties": {
            "brand": {"type": "string"},
            "ram": {"type": "number"}
        }
    }', attributes)
);
```

## Indexes

### Index Types
```sql
-- B-Tree Index (default)
CREATE INDEX idx_title ON articles(title);

-- Composite Index
CREATE INDEX idx_status_date ON articles(status, published_at DESC);

-- Unique Index
CREATE UNIQUE INDEX idx_email ON users(email);

-- Fulltext Index (for MyISAM and InnoDB)
CREATE FULLTEXT INDEX idx_content ON articles(title, content);

-- Spatial Index (for geometry types)
CREATE SPATIAL INDEX idx_location ON stores(location);

-- Invisible Index (8.0+)
CREATE INDEX idx_test ON articles(created_at) INVISIBLE;
ALTER TABLE articles ALTER INDEX idx_test VISIBLE;

-- Functional Index (8.0.13+)
CREATE INDEX idx_year ON articles((YEAR(created_at)));
CREATE INDEX idx_json ON products((JSON_VALUE(attributes, '$.brand')));

-- Descending Index (8.0+)
CREATE INDEX idx_date_desc ON articles(created_at DESC);
```

### Index Management
```sql
-- Show indexes
SHOW INDEX FROM articles;

-- Analyze index usage
EXPLAIN SELECT * FROM articles WHERE title LIKE 'MySQL%';

-- Drop index
DROP INDEX idx_title ON articles;
ALTER TABLE articles DROP INDEX idx_title;

-- Force/Ignore index
SELECT * FROM articles FORCE INDEX (idx_status_date) WHERE status = 'published';
SELECT * FROM articles IGNORE INDEX (idx_title) WHERE title = 'Test';
```

## Stored Procedures and Functions

### Stored Procedures
```sql
DELIMITER $$

-- Simple procedure
CREATE PROCEDURE GetArticleCount(IN p_status VARCHAR(20), OUT p_count INT)
BEGIN
    SELECT COUNT(*) INTO p_count
    FROM articles
    WHERE status = p_status;
END$$

-- Procedure with logic
CREATE PROCEDURE ArchiveOldArticles(IN days_old INT)
BEGIN
    DECLARE affected_rows INT DEFAULT 0;
    
    START TRANSACTION;
    
    -- Archive articles
    INSERT INTO archived_articles
    SELECT * FROM articles
    WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY);
    
    SET affected_rows = ROW_COUNT();
    
    -- Delete from main table
    DELETE FROM articles
    WHERE created_at < DATE_SUB(NOW(), INTERVAL days_old DAY);
    
    COMMIT;
    
    SELECT CONCAT(affected_rows, ' articles archived') as result;
END$$

-- Procedure with cursor
CREATE PROCEDURE ProcessArticles()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE v_id INT;
    DECLARE v_title VARCHAR(255);
    DECLARE cur CURSOR FOR SELECT id, title FROM articles WHERE status = 'draft';
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
    
    OPEN cur;
    
    read_loop: LOOP
        FETCH cur INTO v_id, v_title;
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        -- Process each article
        UPDATE articles SET status = 'reviewed' WHERE id = v_id;
    END LOOP;
    
    CLOSE cur;
END$$

DELIMITER ;

-- Call procedures
CALL GetArticleCount('published', @count);
SELECT @count;

CALL ArchiveOldArticles(365);
```

### Functions
```sql
DELIMITER $$

-- Scalar function
CREATE FUNCTION GetAuthorName(author_id INT) 
RETURNS VARCHAR(100)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE author_name VARCHAR(100);
    
    SELECT name INTO author_name
    FROM users
    WHERE id = author_id;
    
    RETURN IFNULL(author_name, 'Unknown');
END$$

-- Function with complex logic
CREATE FUNCTION CalculateReadingTime(content TEXT)
RETURNS INT
DETERMINISTIC
NO SQL
BEGIN
    DECLARE word_count INT;
    DECLARE reading_time INT;
    
    -- Estimate word count
    SET word_count = CHAR_LENGTH(content) - CHAR_LENGTH(REPLACE(content, ' ', '')) + 1;
    
    -- Average reading speed: 200 words per minute
    SET reading_time = CEIL(word_count / 200);
    
    RETURN reading_time;
END$$

DELIMITER ;

-- Use functions
SELECT title, GetAuthorName(author_id) as author
FROM articles;

SELECT title, CalculateReadingTime(content) as reading_minutes
FROM articles;
```

## Triggers

```sql
DELIMITER $$

-- BEFORE INSERT trigger
CREATE TRIGGER before_article_insert
BEFORE INSERT ON articles
FOR EACH ROW
BEGIN
    IF NEW.title IS NULL OR NEW.title = '' THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Article title cannot be empty';
    END IF;
    
    SET NEW.created_at = IFNULL(NEW.created_at, NOW());
END$$

-- AFTER INSERT trigger
CREATE TRIGGER after_article_insert
AFTER INSERT ON articles
FOR EACH ROW
BEGIN
    INSERT INTO audit_log (table_name, action, record_id, user_id, timestamp)
    VALUES ('articles', 'INSERT', NEW.id, USER(), NOW());
    
    UPDATE users 
    SET article_count = article_count + 1
    WHERE id = NEW.author_id;
END$$

-- BEFORE UPDATE trigger
CREATE TRIGGER before_article_update
BEFORE UPDATE ON articles
FOR EACH ROW
BEGIN
    SET NEW.updated_at = NOW();
    
    IF OLD.status != 'published' AND NEW.status = 'published' THEN
        SET NEW.published_at = NOW();
    END IF;
END$$

-- AFTER DELETE trigger
CREATE TRIGGER after_article_delete
AFTER DELETE ON articles
FOR EACH ROW
BEGIN
    INSERT INTO deleted_articles_log
    SELECT *, NOW() as deleted_at FROM articles WHERE id = OLD.id;
    
    UPDATE users 
    SET article_count = article_count - 1
    WHERE id = OLD.author_id;
END$$

DELIMITER ;

-- Show triggers
SHOW TRIGGERS;
SHOW CREATE TRIGGER before_article_insert;

-- Drop trigger
DROP TRIGGER IF EXISTS before_article_insert;
```

## Views

```sql
-- Simple view
CREATE VIEW published_articles AS
SELECT id, title, content, author_id, created_at
FROM articles
WHERE status = 'published';

-- View with JOIN
CREATE VIEW article_details AS
SELECT 
    a.id,
    a.title,
    a.created_at,
    u.name as author_name,
    c.name as category_name
FROM articles a
LEFT JOIN users u ON a.author_id = u.id
LEFT JOIN categories c ON a.category_id = c.id;

-- Updatable view
CREATE VIEW active_users AS
SELECT id, name, email
FROM users
WHERE status = 'active'
WITH CHECK OPTION;

-- Materialized view workaround (MySQL doesn't have native materialized views)
CREATE TABLE materialized_article_stats AS
SELECT 
    category_id,
    COUNT(*) as article_count,
    AVG(view_count) as avg_views
FROM articles
GROUP BY category_id;

-- Refresh "materialized view"
TRUNCATE TABLE materialized_article_stats;
INSERT INTO materialized_article_stats
SELECT 
    category_id,
    COUNT(*) as article_count,
    AVG(view_count) as avg_views
FROM articles
GROUP BY category_id;

-- Show views
SHOW FULL TABLES WHERE Table_type = 'VIEW';
SHOW CREATE VIEW article_details;

-- Drop view
DROP VIEW IF EXISTS article_details;
```

## Transactions

```sql
-- Basic transaction
START TRANSACTION;

INSERT INTO orders (user_id, total) VALUES (1, 100.00);
SET @order_id = LAST_INSERT_ID();

INSERT INTO order_items (order_id, product_id, quantity)
VALUES (@order_id, 1, 2), (@order_id, 2, 1);

UPDATE inventory SET quantity = quantity - 2 WHERE product_id = 1;
UPDATE inventory SET quantity = quantity - 1 WHERE product_id = 2;

COMMIT;
-- or ROLLBACK;

-- Transaction with savepoints
START TRANSACTION;

INSERT INTO orders (user_id, total) VALUES (1, 100.00);
SAVEPOINT order_created;

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 1, 2);
SAVEPOINT item1_added;

INSERT INTO order_items (order_id, product_id, quantity) VALUES (1, 2, 1);

-- Rollback to savepoint if needed
ROLLBACK TO SAVEPOINT item1_added;

COMMIT;

-- Transaction isolation levels
SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ; -- Default
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;

-- Check current isolation level
SELECT @@transaction_isolation;
```

## Performance Optimization

### EXPLAIN Analysis
```sql
-- Basic EXPLAIN
EXPLAIN SELECT * FROM articles WHERE status = 'published';

-- EXPLAIN with FORMAT
EXPLAIN FORMAT=JSON 
SELECT a.*, u.name 
FROM articles a 
JOIN users u ON a.author_id = u.id;

-- EXPLAIN ANALYZE (8.0.18+)
EXPLAIN ANALYZE 
SELECT * FROM articles 
WHERE created_at > '2024-01-01';

-- Visual EXPLAIN (MySQL Workbench)
EXPLAIN FORMAT=TREE
SELECT * FROM articles WHERE category_id = 1;
```

### Query Optimization Tips
```sql
-- Use covering indexes
CREATE INDEX idx_covering ON articles(status, title, created_at);
SELECT title, created_at FROM articles WHERE status = 'published';

-- Avoid SELECT *
-- Bad
SELECT * FROM articles;
-- Good
SELECT id, title, status FROM articles;

-- Use LIMIT for large results
SELECT * FROM articles ORDER BY created_at DESC LIMIT 100;

-- Optimize JOIN order (smaller result set first)
SELECT * FROM 
    (SELECT * FROM articles WHERE status = 'published' LIMIT 100) a
    JOIN users u ON a.author_id = u.id;

-- Use EXISTS instead of IN for subqueries
-- Less efficient
SELECT * FROM users WHERE id IN (SELECT author_id FROM articles);
-- More efficient
SELECT * FROM users u WHERE EXISTS (SELECT 1 FROM articles a WHERE a.author_id = u.id);

-- Batch operations
INSERT INTO articles (title, content) VALUES
    ('Title 1', 'Content 1'),
    ('Title 2', 'Content 2'),
    ('Title 3', 'Content 3');
```

### Performance Schema
```sql
-- Enable Performance Schema
UPDATE performance_schema.setup_instruments 
SET ENABLED = 'YES', TIMED = 'YES';

-- Top slow queries
SELECT 
    DIGEST_TEXT,
    COUNT_STAR,
    AVG_TIMER_WAIT/1000000000 AS avg_time_ms,
    SUM_TIMER_WAIT/1000000000 AS total_time_ms
FROM performance_schema.events_statements_summary_by_digest
ORDER BY SUM_TIMER_WAIT DESC
LIMIT 10;

-- Table I/O statistics
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    COUNT_READ,
    COUNT_WRITE,
    COUNT_FETCH,
    SUM_TIMER_WAIT/1000000000 AS total_time_ms
FROM performance_schema.table_io_waits_summary_by_table
WHERE OBJECT_SCHEMA NOT IN ('mysql', 'performance_schema', 'information_schema')
ORDER BY SUM_TIMER_WAIT DESC;

-- Index usage
SELECT 
    OBJECT_SCHEMA,
    OBJECT_NAME,
    INDEX_NAME,
    COUNT_STAR AS usage_count
FROM performance_schema.table_io_waits_summary_by_index_usage
WHERE OBJECT_SCHEMA = 'your_database'
ORDER BY COUNT_STAR DESC;
```

## User Management and Security

### User Management
```sql
-- Create user
CREATE USER 'username'@'localhost' IDENTIFIED BY 'password';
CREATE USER 'username'@'%' IDENTIFIED BY 'password';

-- With authentication plugin
CREATE USER 'username'@'localhost' 
IDENTIFIED WITH mysql_native_password BY 'password';

-- Grant privileges
GRANT ALL PRIVILEGES ON database_name.* TO 'username'@'localhost';
GRANT SELECT, INSERT, UPDATE ON database_name.articles TO 'username'@'%';
GRANT EXECUTE ON PROCEDURE database_name.GetArticleCount TO 'username'@'localhost';

-- Specific privileges
GRANT CREATE, ALTER, DROP, INDEX, CREATE VIEW, SHOW VIEW 
ON database_name.* TO 'developer'@'localhost';

-- Revoke privileges
REVOKE INSERT, UPDATE ON database_name.articles FROM 'username'@'%';
REVOKE ALL PRIVILEGES ON database_name.* FROM 'username'@'localhost';

-- Show grants
SHOW GRANTS FOR 'username'@'localhost';
SHOW GRANTS FOR CURRENT_USER;

-- Change password
ALTER USER 'username'@'localhost' IDENTIFIED BY 'new_password';
SET PASSWORD FOR 'username'@'localhost' = 'new_password';

-- Drop user
DROP USER IF EXISTS 'username'@'localhost';

-- List users
SELECT User, Host FROM mysql.user;
```

### Roles (MySQL 8.0+)
```sql
-- Create role
CREATE ROLE 'app_developer', 'app_read', 'app_write';

-- Grant privileges to role
GRANT SELECT ON database_name.* TO 'app_read';
GRANT INSERT, UPDATE, DELETE ON database_name.* TO 'app_write';
GRANT ALL ON database_name.* TO 'app_developer';

-- Grant role to user
GRANT 'app_read' TO 'john'@'localhost';
GRANT 'app_developer' TO 'jane'@'localhost';

-- Set default role
SET DEFAULT ROLE 'app_read' TO 'john'@'localhost';

-- Activate roles
SET ROLE 'app_developer';
SET ROLE ALL;

-- Show roles
SELECT CURRENT_ROLE();
SHOW GRANTS FOR 'app_developer';
```

## Backup and Recovery

### mysqldump
```bash
# Basic backup
mysqldump -u username -p database_name > backup.sql

# Backup with routines and triggers
mysqldump -u username -p --routines --triggers database_name > backup.sql

# Backup specific tables
mysqldump -u username -p database_name table1 table2 > backup.sql

# Backup structure only
mysqldump -u username -p --no-data database_name > structure.sql

# Backup data only
mysqldump -u username -p --no-create-info database_name > data.sql

# Backup all databases
mysqldump -u username -p --all-databases > all_databases.sql

# Backup with compression
mysqldump -u username -p database_name | gzip > backup.sql.gz

# Restore
mysql -u username -p database_name < backup.sql
gunzip < backup.sql.gz | mysql -u username -p database_name
```

### Binary Log Backup
```sql
-- Show binary logs
SHOW BINARY LOGS;
SHOW MASTER STATUS;

-- Backup binary logs
-- Command line:
mysqlbinlog --read-from-remote-server --host=localhost --user=root --password \
    --to-last-log --result-file=binlog_backup.sql mysql-bin.000001

-- Point-in-time recovery
mysqlbinlog --start-datetime="2024-01-01 00:00:00" \
            --stop-datetime="2024-01-01 12:00:00" \
            mysql-bin.000001 | mysql -u root -p
```

## ColdFusion Integration

### Using cfquery with MySQL
```cfml
<!--- Basic query --->
<cfquery name="getArticles" datasource="aiformedical">
    SELECT id, title, content, created_at
    FROM articles
    WHERE status = <cfqueryparam value="published" cfsqltype="cf_sql_varchar">
    ORDER BY created_at DESC
    LIMIT 10
</cfquery>

<!--- Insert with generated key --->
<cfquery name="insertArticle" datasource="aiformedical" result="insertResult">
    INSERT INTO articles (title, content, author_id, created_at)
    VALUES (
        <cfqueryparam value="#form.title#" cfsqltype="cf_sql_varchar">,
        <cfqueryparam value="#form.content#" cfsqltype="cf_sql_longvarchar">,
        <cfqueryparam value="#session.userId#" cfsqltype="cf_sql_integer">,
        <cfqueryparam value="#now()#" cfsqltype="cf_sql_timestamp">
    )
</cfquery>
<cfset newArticleId = insertResult.generatedKey>

<!--- Using stored procedure --->
<cfstoredproc procedure="GetArticleCount" datasource="aiformedical">
    <cfprocparam type="in" cfsqltype="cf_sql_varchar" value="published">
    <cfprocparam type="out" cfsqltype="cf_sql_integer" variable="articleCount">
</cfstoredproc>

<!--- Transaction handling --->
<cftransaction>
    <cftry>
        <cfquery datasource="aiformedical">
            INSERT INTO orders (user_id, total) 
            VALUES (#userId#, #orderTotal#)
        </cfquery>
        
        <cfquery name="getOrderId" datasource="aiformedical">
            SELECT LAST_INSERT_ID() as orderId
        </cfquery>
        
        <cfloop array="#orderItems#" index="item">
            <cfquery datasource="aiformedical">
                INSERT INTO order_items (order_id, product_id, quantity)
                VALUES (#getOrderId.orderId#, #item.productId#, #item.quantity#)
            </cfquery>
        </cfloop>
        
        <cftransaction action="commit" />
        
        <cfcatch>
            <cftransaction action="rollback" />
            <cfthrow message="Order processing failed: #cfcatch.message#">
        </cfcatch>
    </cftry>
</cftransaction>
```

## MySQL 8.0 New Features Summary

1. **Window Functions** - ROW_NUMBER(), RANK(), LAG(), LEAD()
2. **Common Table Expressions (CTEs)** - WITH clause for better query organization
3. **Improved JSON Support** - JSON_TABLE, JSON validation
4. **Descending Indexes** - True DESC index support
5. **Invisible Indexes** - Test index removal impact
6. **Functional Indexes** - Index on expressions
7. **Instant ADD COLUMN** - Fast ALTER TABLE for adding columns
8. **Roles** - Better privilege management
9. **EXPLAIN ANALYZE** - Actual execution statistics
10. **Document Store** - NoSQL capabilities with X DevAPI
11. **Data Dictionary** - Transactional data dictionary
12. **Atomic DDL** - DDL statements are atomic
13. **Resource Groups** - CPU resource management
14. **Improved Performance** - Up to 2x faster than MySQL 5.7
15. **Default to utf8mb4** - Better Unicode support

## Best Practices

1. **Always use parameterized queries** to prevent SQL injection
2. **Create appropriate indexes** for frequently queried columns
3. **Use InnoDB storage engine** for transactional consistency
4. **Implement proper backup strategies** including regular dumps and binary logs
5. **Monitor slow query log** and optimize problematic queries
6. **Use connection pooling** in applications
7. **Set appropriate buffer pool size** (70-80% of available RAM)
8. **Use EXPLAIN** to analyze query execution plans
9. **Normalize database design** but denormalize when necessary for performance
10. **Keep MySQL version updated** for security and performance improvements

## Resources

- [MySQL 8.0 Reference Manual](https://dev.mysql.com/doc/refman/8.0/en/)
- [MySQL Performance Blog](https://www.percona.com/blog/)
- [MySQL Workbench](https://www.mysql.com/products/workbench/)
- [Planet MySQL](https://planet.mysql.com/)
- [MySQL Forums](https://forums.mysql.com/)