-- trans_09: Complex Cascading Delete
BEGIN;
DELETE FROM products WHERE sku = 'SKU200';
SELECT SLEEP(0.1);
COMMIT;
