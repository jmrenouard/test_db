-- trans_05: SELECT / INSERT (Shared Gap Lock)
BEGIN;
-- This SELECT part sets SHARED gap locks
INSERT INTO audit_trail (event_type, ref_sku)
SELECT 'LOG', sku FROM products WHERE sku > 'SKU200' AND sku < 'SKU300';
SELECT SLEEP(0.1);
COMMIT;
