-- Setup for deadlock simulation
DROP TABLE IF EXISTS deadlock_test;
CREATE TABLE deadlock_test (
    id INT PRIMARY KEY,
    val INT
) ENGINE=InnoDB;

INSERT INTO deadlock_test (id, val) VALUES (1, 10), (2, 20);
