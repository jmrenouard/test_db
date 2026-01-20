-- Transaction 2: Update 2 then 1
BEGIN;
UPDATE deadlock_test SET val = val + 1 WHERE id = 2;
SELECT SLEEP(0.2);
UPDATE deadlock_test SET val = val + 1 WHERE id = 1;
COMMIT;
