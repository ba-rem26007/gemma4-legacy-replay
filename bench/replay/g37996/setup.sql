-- Create a parent tab that is inactive (active=0) but has an active child.
-- This simulates the "More" tab which is a container.
INSERT INTO ps_tab (id_tab, class_name, active, id_parent) VALUES (999, 'AdminParentMore', 0, 0);
INSERT INTO ps_tab_lang (id_tab, id_lang, name) VALUES (999, 1, 'More');
-- Create an active child tab to ensure the parent is considered "viewable" by the old logic
INSERT INTO ps_tab (id_tab, class_name, active, id_parent) VALUES (1000, 'AdminOrders', 1, 999);
INSERT INTO ps_tab_lang (id_tab, id_lang, name) VALUES (1000, 1, 'Orders');
-- Grant access to the admin profile (id 1)
INSERT INTO ps_tab_access (id_tab, id_profile) VALUES (999, 1), (1000, 1);
