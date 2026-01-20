-- Transaction 1: Update 1 then 2
BEGIN;
UPDATE deadlock_test SET val = val + 1 WHERE id = 1;
SELECT SLEEP(0.2);
UPDATE deadlock_test SET val = val + 1 WHERE id = 2;
COMMIT;
