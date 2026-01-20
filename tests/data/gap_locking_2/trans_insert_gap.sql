-- Transaction attempting to insert into a locked gap
BEGIN;
-- Use IGNORE to prevent crash on duplicate, but it will still WAIT if there is a gap lock
INSERT IGNORE INTO gap_parent (id, name) VALUES (15, 'Intruder');
COMMIT;
