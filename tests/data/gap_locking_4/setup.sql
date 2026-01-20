-- Setup for Gap Locking 4 (Comprehensive Scenario)
DROP TABLE IF EXISTS child_details;
DROP TABLE IF EXISTS parent_metadata;

-- Parent table with UNIQUE index (non-PK)
CREATE TABLE parent_metadata (
    id INT PRIMARY KEY,
    code VARCHAR(10) UNIQUE,
    info VARCHAR(50)
) ENGINE=InnoDB;

-- Child table with Foreign Key on the non-PK column
CREATE TABLE child_details (
    id INT AUTO_INCREMENT PRIMARY KEY,
    p_code VARCHAR(10),
    FOREIGN KEY (p_code) REFERENCES parent_metadata(code)
) ENGINE=InnoDB;

-- Insert sparse data
INSERT INTO parent_metadata (id, code, info) VALUES 
(10, 'C10', 'P10'), 
(20, 'C20', 'P20'), 
(30, 'C30', 'P30');
