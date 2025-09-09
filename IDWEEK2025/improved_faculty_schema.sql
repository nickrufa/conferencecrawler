-- Improved Faculty Database Schema
-- Separates faculty from conference-specific data for better normalization

-- Master Faculty Table (conference-independent)
CREATE TABLE IF NOT EXISTS Faculty_Master (
    faculty_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255), -- For matching across conferences
    credentials VARCHAR(100),
    email VARCHAR(255),
    photo_url TEXT,
    primary_organization VARCHAR(500),
    biography TEXT,
    disclosure_info TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_normalized_name (normalized_name),
    INDEX idx_full_name (full_name),
    INDEX idx_email (email)
);

-- Conference-specific faculty participation
CREATE TABLE IF NOT EXISTS Faculty_Conference_Participation (
    participation_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    conference_year INT NOT NULL,
    conference_name VARCHAR(100) NOT NULL, -- 'IDWEEK', 'ECCMID', 'ESCMID'
    presenter_id VARCHAR(50), -- Original conference presenter ID
    job_title VARCHAR(500), -- Can change between conferences
    organization VARCHAR(500), -- Can change between conferences
    raw_data TEXT, -- Original HTML data
    parsing_status ENUM('pending', 'parsed', 'error') DEFAULT 'pending',
    parse_error_msg TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculty_id) REFERENCES Faculty_Master(faculty_id) ON DELETE CASCADE,
    UNIQUE KEY unique_faculty_conference (faculty_id, conference_year, conference_name),
    INDEX idx_conference (conference_year, conference_name),
    INDEX idx_presenter_id (presenter_id)
);

-- Updated poster table (conference-specific)
CREATE TABLE IF NOT EXISTS Conference_Posters (
    poster_db_id INT AUTO_INCREMENT PRIMARY KEY,
    poster_id VARCHAR(50) NOT NULL,
    conference_year INT NOT NULL,
    conference_name VARCHAR(100) NOT NULL,
    poster_number VARCHAR(50),
    title TEXT,
    presentation_date DATE,
    presentation_time VARCHAR(100),
    time_zone VARCHAR(10),
    url_reference TEXT,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    UNIQUE KEY unique_poster_conference (poster_id, conference_year, conference_name),
    INDEX idx_conference (conference_year, conference_name),
    INDEX idx_presentation_date (presentation_date)
);

-- Faculty-poster relationships (many-to-many)
CREATE TABLE IF NOT EXISTS Faculty_Poster_Relationships (
    relationship_id INT AUTO_INCREMENT PRIMARY KEY,
    faculty_id INT NOT NULL,
    poster_db_id INT NOT NULL,
    role VARCHAR(50) DEFAULT 'presenter', -- presenter, co-author, etc.
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (faculty_id) REFERENCES Faculty_Master(faculty_id) ON DELETE CASCADE,
    FOREIGN KEY (poster_db_id) REFERENCES Conference_Posters(poster_db_id) ON DELETE CASCADE,
    UNIQUE KEY unique_faculty_poster (faculty_id, poster_db_id),
    INDEX idx_faculty_id (faculty_id),
    INDEX idx_poster_id (poster_db_id)
);

-- Migration table to track old IDs
CREATE TABLE IF NOT EXISTS Faculty_ID_Migration (
    migration_id INT AUTO_INCREMENT PRIMARY KEY,
    new_faculty_id INT NOT NULL,
    old_table_name VARCHAR(100) NOT NULL,
    old_record_id INT NOT NULL,
    conference_year INT NOT NULL,
    conference_name VARCHAR(100) NOT NULL,
    created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (new_faculty_id) REFERENCES Faculty_Master(faculty_id) ON DELETE CASCADE,
    UNIQUE KEY unique_old_reference (old_table_name, old_record_id),
    INDEX idx_new_faculty (new_faculty_id)
);

-- Useful views
CREATE OR REPLACE VIEW faculty_conference_summary AS
SELECT 
    fm.faculty_id,
    fm.full_name,
    fm.credentials,
    fm.primary_organization,
    GROUP_CONCAT(
        CONCAT(fcp.conference_name, ' ', fcp.conference_year) 
        ORDER BY fcp.conference_year DESC 
        SEPARATOR ', '
    ) as conferences_participated,
    COUNT(DISTINCT CONCAT(fcp.conference_name, fcp.conference_year)) as total_conferences,
    MAX(fcp.conference_year) as latest_conference_year
FROM Faculty_Master fm
JOIN Faculty_Conference_Participation fcp ON fm.faculty_id = fcp.faculty_id
WHERE fcp.parsing_status = 'parsed'
GROUP BY fm.faculty_id;

CREATE OR REPLACE VIEW faculty_with_posters_cross_conference AS
SELECT 
    fm.faculty_id,
    fm.full_name,
    fm.credentials,
    fcp.conference_year,
    fcp.conference_name,
    fcp.organization as current_organization,
    cp.poster_number,
    cp.title as poster_title,
    cp.presentation_date,
    fpr.role
FROM Faculty_Master fm
JOIN Faculty_Conference_Participation fcp ON fm.faculty_id = fcp.faculty_id
JOIN Faculty_Poster_Relationships fpr ON fm.faculty_id = fpr.faculty_id
JOIN Conference_Posters cp ON fpr.poster_db_id = cp.poster_db_id
WHERE fcp.parsing_status = 'parsed'
ORDER BY fm.full_name, fcp.conference_year DESC;

-- Function to normalize names for matching
DELIMITER //
CREATE OR REPLACE FUNCTION normalize_faculty_name(input_name VARCHAR(255))
RETURNS VARCHAR(255)
DETERMINISTIC
READS SQL DATA
BEGIN
    DECLARE normalized VARCHAR(255);
    
    -- Remove credentials and common suffixes
    SET normalized = TRIM(input_name);
    SET normalized = REGEXP_REPLACE(normalized, ',\\s*(MD|PhD|PharmD|MPH|MS|MSc|DrPH|DO|DVM|RN|PA|NP|APRN|CPhT|RPh)([,\\s]*(MD|PhD|PharmD|MPH|MS|MSc|DrPH|DO|DVM|RN|PA|NP|APRN|CPhT|RPh))*\\s*$', '', 1, 0, 'i');
    
    -- Convert to lowercase for consistent matching
    SET normalized = LOWER(TRIM(normalized));
    
    -- Remove extra spaces
    SET normalized = REGEXP_REPLACE(normalized, '\\s+', ' ');
    
    RETURN normalized;
END //
DELIMITER ;