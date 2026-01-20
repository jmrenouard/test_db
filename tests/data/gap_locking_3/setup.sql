-- Setup tables for gap locking 3 (UPDATE based)
DROP TABLE IF EXISTS gap_parent;

CREATE TABLE gap_parent (
    id INT PRIMARY KEY,
    name VARCHAR(50)
) ENGINE=InnoDB;

-- Insert sparse data to create gaps
INSERT INTO gap_parent (id, name) VALUES (10, 'Node 10'), (20, 'Node 20'), (30, 'Node 30');
