-- Clean up to ensure idempotency
DELETE FROM ps_tab_access WHERE id_tab IN (9999, 10000);
DELETE FROM ps_tab_lang WHERE id_tab IN (9999, 10000);
DELETE FROM ps_tab WHERE id_tab IN (9999, 10000);

-- Ensure the admin employee (id 1) is linked to profile 1
UPDATE ps_employee SET id_profile = 1 WHERE id_employee = 1;

-- Create a parent tab that is inactive (active=0) but has an active child.
-- This simulates the "More" tab which is a container.
INSERT INTO ps_tab (id_tab, class_name, active, id_parent) VALUES (9999, 'AdminParentMore', 0, 0);
INSERT INTO ps_tab_lang (id_tab, id_lang, name) VALUES (9999, 1, 'More');

-- Create an active child tab to ensure the parent is considered "viewable" by the old logic
INSERT INTO ps_tab (id_tab, class_name, active, id_parent) VALUES (10000, 'AdminOrders', 1, 9999);
INSERT INTO ps_tab_lang (id_tab, id_lang, name) VALUES (10000, 1, 'Orders');

-- Grant access to the admin profile (id 1)
INSERT INTO ps_tab_access (id_tab, id_profile) VALUES (9999, 1), (10000, 1);
