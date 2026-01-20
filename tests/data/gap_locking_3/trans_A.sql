-- Transaction A: Lock gap (10, 20) via UPDATE then try to insert into gap (20, 30)
BEGIN;
UPDATE gap_parent SET name = 'Updated by A' WHERE id > 10 AND id < 20;
SELECT SLEEP(1);
INSERT IGNORE INTO gap_parent (id, name) VALUES (25, 'A-Gap-3');
COMMIT;
