-- Transaction A: SELECT (via INSERT) and DELETE
BEGIN;

-- Part 1: Shared Gap Lock via range-based INSERT ... SELECT
-- This SELECT (without FOR UPDATE) still sets shared locks because it is part of an INSERT
INSERT INTO child_details (p_code)
SELECT code FROM parent_metadata WHERE code > 'C10' AND code < 'C20';

SELECT SLEEP(1);

-- Part 2: Exclusive lock on another record
DELETE FROM parent_metadata WHERE code = 'C30';

SELECT SLEEP(1);
COMMIT;
