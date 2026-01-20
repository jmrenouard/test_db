-- trans_02: Deadlock Driver B
BEGIN;
UPDATE products SET category = 'B' WHERE sku > 'SKU200' AND sku < 'SKU300';
SELECT SLEEP(0.1);
UPDATE products SET category = 'B' WHERE sku > 'SKU100' AND sku < 'SKU200';
COMMIT;
