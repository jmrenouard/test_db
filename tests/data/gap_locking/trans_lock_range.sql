-- Transaction locking a range (gap)
BEGIN;
-- This will lock the gap between 10 and 20 (and the record 20)
SELECT * FROM gap_parent WHERE id > 10 AND id < 20 FOR UPDATE;
-- Simulate processing time to allow conflict
SELECT SLEEP(0.05);
COMMIT;
