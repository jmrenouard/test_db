-- Setup tables for gap locking demonstration
DROP TABLE IF EXISTS gap_child;
DROP TABLE IF EXISTS gap_parent;

CREATE TABLE gap_parent (
    id INT PRIMARY KEY,
    name VARCHAR(50)
) ENGINE=InnoDB;

CREATE TABLE gap_child (
    id INT PRIMARY KEY,
    parent_id INT,
    description VARCHAR(100),
    FOREIGN KEY (parent_id) REFERENCES gap_parent(id) ON DELETE CASCADE
) ENGINE=InnoDB;

-- Insert sparse data to create gaps
INSERT INTO gap_parent (id, name) VALUES (10, 'Node 10'), (20, 'Node 20'), (30, 'Node 30');
INSERT INTO gap_child (id, parent_id, description) VALUES (1, 10, 'Child 1'), (2, 20, 'Child 2');
