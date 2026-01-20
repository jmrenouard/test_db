-- Transaction B: Range UPDATE and Intrusion INSERT
BEGIN;

-- Part 1: Range-based UPDATE (Locks gap (C20, C30) and record C30)
UPDATE parent_metadata SET info = 'Updated by B' WHERE code > 'C20' AND code < 'C40';

SELECT SLEEP(1);

-- Part 2: Intrusion into A's gap (C10, C20)
-- This will wait for Transaction A's shared gap lock
INSERT IGNORE INTO parent_metadata (id, code, info) VALUES (15, 'C15', 'Conflict A');

COMMIT;
