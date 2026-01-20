-- Transaction inserting into child (fk check should also be affected by gap lock)
BEGIN;
INSERT IGNORE INTO gap_child (id, parent_id, description) VALUES (100, 20, 'Child of locked Node');
COMMIT;
