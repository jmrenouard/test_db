-- trans_08: SELECT FOR UPDATE on Empty Range (Pure Gap Lock)
BEGIN;
SELECT * FROM products WHERE sku > 'SKU600' AND sku < 'SKU700' FOR UPDATE;
SELECT SLEEP(0.1);
COMMIT;
