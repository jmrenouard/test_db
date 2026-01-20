-- trans_10: Maintenance Category Shift
BEGIN;
UPDATE products SET category = 'Tool-Shift' WHERE category = 'Tool';
SELECT SLEEP(0.1);
COMMIT;
