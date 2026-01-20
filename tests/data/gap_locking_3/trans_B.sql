-- Transaction B: Lock gap (20, 30) via UPDATE then try to insert into gap (10, 20)
BEGIN;
UPDATE gap_parent SET name = 'Updated by B' WHERE id > 20 AND id < 30;
SELECT SLEEP(1);
INSERT IGNORE INTO gap_parent (id, name) VALUES (15, 'B-Gap-3');
COMMIT;
