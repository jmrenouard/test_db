-- trans_03: Range UPDATE (Exclusive Gap Locks)
BEGIN;
UPDATE products SET category = 'Promo' WHERE sku > 'SKU100' AND sku < 'SKU200';
SELECT SLEEP(0.1);
COMMIT;
