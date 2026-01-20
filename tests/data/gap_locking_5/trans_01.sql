-- trans_01: Deadlock Driver A
BEGIN;
UPDATE products SET category = 'A' WHERE sku > 'SKU100' AND sku < 'SKU200';
SELECT SLEEP(0.1);
UPDATE products SET category = 'A' WHERE sku > 'SKU200' AND sku < 'SKU300';
COMMIT;
