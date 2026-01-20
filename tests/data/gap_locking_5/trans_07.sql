-- trans_07: Rapid Audit Point Inserts
BEGIN;
INSERT INTO audit_trail (event_type, ref_sku) VALUES ('MANUAL', 'SKU999');
SELECT SLEEP(0.1);
COMMIT;
