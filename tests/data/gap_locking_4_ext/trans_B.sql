-- Transaction B: Range UPDATE + Gap Intrusion
BEGIN;

-- Part 1: Range-based UPDATE triggers exclusive range locks (including gaps)
UPDATE main_catalog SET description = 'Updated by B' WHERE sku > 'S20' AND sku < 'S40';

SELECT SLEEP(1);

-- Part 2: Try to insert into the gap currently locked by Transaction A (Shared)
-- This creates a deadlock potential if B waits for A, and A later needs something B has
INSERT IGNORE INTO main_catalog (id, sku, description) VALUES (15, 'S15', 'New Item');

COMMIT;
