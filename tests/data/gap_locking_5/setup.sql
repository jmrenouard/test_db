-- Setup for Gap Locking 5 (The Extreme Scenario)
DROP TABLE IF EXISTS audit_trail;
DROP TABLE IF EXISTS inventory;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS warehouses;

-- Table 1: Master Catalog
CREATE TABLE products (
    id INT PRIMARY KEY,
    sku VARCHAR(10) UNIQUE,
    category VARCHAR(20)
) ENGINE=InnoDB;

-- Table 2: Stocks referencing SKUs
CREATE TABLE inventory (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sku_code VARCHAR(10),
    qty INT DEFAULT 0,
    FOREIGN KEY (sku_code) REFERENCES products(sku) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Table 3: Static Reference
CREATE TABLE warehouses (
    id INT PRIMARY KEY,
    location VARCHAR(50),
    capacity INT
) ENGINE=InnoDB;

-- Table 4: Logging table for Shared Lock demonstration
CREATE TABLE audit_trail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    event_type VARCHAR(20),
    ref_sku VARCHAR(10),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- Initial Sparse Data
INSERT INTO warehouses (id, location, capacity) VALUES (1, 'North-1', 5000), (2, 'South-2', 8000);

INSERT INTO products (id, sku, category) VALUES 
(100, 'SKU100', 'Electronic'),
(200, 'SKU200', 'Electronic'),
(300, 'SKU300', 'Furniture'),
(400, 'SKU400', 'Furniture'),
(500, 'SKU500', 'Tool');

INSERT INTO inventory (sku_code, qty) VALUES 
('SKU100', 10), ('SKU200', 50), ('SKU300', 5), ('SKU400', 12);
