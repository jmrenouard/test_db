-- Transaction A: Shared Gap Lock + Delete Cascade
BEGIN;

-- Part 1: Shared Gap Lock via range-based INSERT ... SELECT
-- SELECT (without FOR UPDATE) triggers shared locks on unique index gaps
INSERT INTO child_orders (sku_code)
SELECT sku FROM main_catalog WHERE sku > 'S10' AND sku < 'S20';

SELECT SLEEP(1);

-- Part 2: Delete which triggers cascading checks and locks on children
DELETE FROM main_catalog WHERE sku = 'S30';

SELECT SLEEP(1);
COMMIT;
