-- On cible un onglet parent existant (qui a forcément des permissions et des enfants)
-- pour s'assurer qu'il soit "viewable" selon la logique de TabDataProvider.
-- On exclut AdminDashboard car le correctif le traite comme une exception.
UPDATE ps_tab 
SET active = 0 
WHERE id_tab = (
    SELECT id_tab FROM (
        SELECT id_tab FROM ps_tab 
        WHERE id_parent = 0 
        AND class_name != 'AdminDashboard' 
        AND id_tab IN (SELECT id_parent FROM ps_tab) 
        LIMIT 1
    ) as tmp
);

-- On renomme cet onglet pour le repérer facilement dans le select
UPDATE ps_tab_lang 
SET name = 'TAB_MORE_TEST' 
WHERE id_tab = (
    SELECT id_tab FROM (
        SELECT id_tab FROM ps_tab 
        WHERE active = 0 AND id_parent = 0 
        LIMIT 1
    ) as tmp
) AND id_lang = 1;
