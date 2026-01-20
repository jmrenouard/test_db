-- Transaction A: Lock gap (10, 20) then try to insert into gap (20, 30)
BEGIN;
SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE;
SELECT SLEEP(1);
INSERT IGNORE INTO gap_parent (id, name) VALUES (25, 'A-Gap');
COMMIT;
