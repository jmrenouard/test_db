-- trans_06: Relational Cross-Update
BEGIN;
UPDATE inventory SET qty = qty + 1 WHERE sku_code = 'SKU100';
UPDATE products SET category = 'Updated-6' WHERE sku = 'SKU200';
SELECT SLEEP(0.1);
COMMIT;
