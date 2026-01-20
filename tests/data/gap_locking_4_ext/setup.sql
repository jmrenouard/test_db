-- Setup for Gap Locking 4 Extended (Cascading & Multi-Child)
DROP TABLE IF EXISTS child_logs;
DROP TABLE IF EXISTS child_orders;
DROP TABLE IF EXISTS main_catalog;

-- Main table with UNIQUE non-PK SKU
CREATE TABLE main_catalog (
    id INT PRIMARY KEY,
    sku VARCHAR(10) UNIQUE,
    description VARCHAR(50)
) ENGINE=InnoDB;

-- First child table with CASCADE
CREATE TABLE child_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(10),
    FOREIGN KEY (sku_code) REFERENCES main_catalog(sku) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Second child table with CASCADE
CREATE TABLE child_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(10),
    FOREIGN KEY (sku_code) REFERENCES main_catalog(sku) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Insert sparse data
INSERT INTO main_catalog (id, sku, description) VALUES 
(10, 'S10', 'Item 10'), 
(20, 'S20', 'Item 20'), 
(30, 'S30', 'Item 30');
