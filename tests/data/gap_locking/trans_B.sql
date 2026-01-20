-- Transaction B: Lock gap (20, 30) then try to insert into gap (10, 20)
BEGIN;
SELECT * FROM gap_parent WHERE id > 20 AND id < 30 FOR UPDATE;
SELECT SLEEP(1);
INSERT IGNORE INTO gap_parent (id, name) VALUES (15, 'B-Gap');
COMMIT;
