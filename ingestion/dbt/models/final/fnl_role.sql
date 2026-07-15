SELECT
    role_id,
    role AS role_name,
    CASE role
        WHEN '1er assistant opérateur' THEN '1er assistant·e opérateur·rice'
        WHEN '1er assistant réalisateur' THEN 'Assistant·e à la réalisation'
        WHEN '2ème assistant opérateur' THEN '2ème assistant·e opérateur·rice'
        WHEN '2ème assistant réalisateur' THEN '2ème assistant·e réalisateur·rice'
        WHEN '2ème caméra' THEN '2ème caméra'
        WHEN '3ème assistant réalisateur' THEN '3ème assistant·e réalisateur·rice'
        WHEN 'Accessoiriste' THEN 'Accessoiriste'
        WHEN 'Acteur' THEN 'Acteur·rice'
        WHEN 'Actrice' THEN 'Acteur·rice'
        WHEN 'Adaptateur' THEN 'Adaptateur·rice'
        WHEN 'Adaptatrice' THEN 'Adaptateur·rice'
        WHEN 'Administrateur de production' THEN 'Administrateur·rice de production'
        WHEN 'Assistant caméra' THEN 'Assistant·e caméra'
        WHEN 'Assistant décorateur' THEN 'Assistant·e décorateur·rice'
        WHEN 'Assistant monteur' THEN 'Assistant·e monteur·euse'
        WHEN 'Assistant opérateur' THEN 'Assistant·e opérateur·rice'
        WHEN 'Assistant réalisateur' THEN 'Assistant·e réalisateur·rice'
        WHEN 'Assistant son' THEN 'Assistant·e son'
        WHEN 'Assistante caméra' THEN 'Assistant·e caméra'
        WHEN 'Assistante décoratrice' THEN 'Assistant·e décorateur·rice'
        WHEN 'Assistant directeur artistique' THEN 'Assistant·e directeur·rice artistique'
        WHEN 'Assistante monteur' THEN 'Assistant·e monteur·euse'
        WHEN 'Assistante opératrice' THEN 'Assistant·e opérateur·rice'
        WHEN 'Assistante réalisateur' THEN 'Assistant·e réalisateur·rice'
        WHEN 'Assistante son' THEN 'Assistant·e son'
        WHEN 'Attaché de presse' THEN 'Attaché·e de presse'
        WHEN 'Attachée de presse' THEN 'Attaché·e de presse'
        WHEN 'Auteur' THEN 'Auteur·e'
        WHEN 'Auteure' THEN 'Auteur·e'
        WHEN 'Cadreur' THEN 'Cadreur·euse'
        WHEN 'Cadreuse' THEN 'Cadreur·euse'
        WHEN 'Chef décorateur' THEN 'Chef·fe décorateur·rice'
        WHEN 'Chef monteur' THEN 'Chef·fe monteur·euse'
        WHEN 'Chef opérateur' THEN 'Chef·fe opérateur·rice'
        WHEN 'Chef son' THEN 'Chef·fe son'
        WHEN 'Cheffe décoratrice' THEN 'Chef·fe décorateur·rice'
        WHEN 'Cheffe monteur' THEN 'Chef·fe monteur·euse'
        WHEN 'Cheffe opératrice' THEN 'Chef·fe opérateur·rice'
        WHEN 'Cheffe son' THEN 'Chef·fe son'
        WHEN 'Chorégraphe' THEN 'Chorégraphe'
        WHEN 'Compositeur' THEN 'Compositeur·rice'
        WHEN 'Compositrice' THEN 'Compositeur·rice'
        WHEN 'Costumier' THEN 'Costumier·ère'
        WHEN 'Costumière' THEN 'Costumier·ère'
        WHEN 'Directeur' THEN 'Directeur·rice'
        WHEN 'Directeur de la photographie' THEN 'Directeur·rice de la photographie'
        WHEN 'Directeur de production' THEN 'Directeur·rice de production'
        WHEN 'Directrice de la photographie' THEN 'Directeur·rice de la photographie'
        WHEN 'Directrice de production' THEN 'Directeur·rice de production'
        WHEN 'Distributeur' THEN 'Distributeur·rice'
        WHEN 'Distributrice' THEN 'Distributeur·rice'
        WHEN 'Ingénieur son' THEN 'Ingénieur·e son'
        WHEN 'Ingénieure son' THEN 'Ingénieur·e son'
        WHEN 'Maquilleur' THEN 'Maquilleur·euse'
        WHEN 'Maquilleuse' THEN 'Maquilleur·euse'
        WHEN 'Mixeur' THEN 'Mixeur·euse'
        WHEN 'Mixeuse' THEN 'Mixeur·euse'
        WHEN 'Monteur' THEN 'Monteur·euse'
        WHEN 'Monteuse' THEN 'Monteur·euse'
        WHEN 'Producteur' THEN 'Producteur·rice'
        WHEN 'Productrice' THEN 'Producteur·rice'
        WHEN 'Producteur délégué' THEN 'Producteur·rice délégué·e'
        WHEN 'Productrice déléguée' THEN 'Producteur·rice délégué·e'
        WHEN 'Producteur exécutif' THEN 'Producteur·rice exécutif·ve'
        WHEN 'Productrice exécutive' THEN 'Producteur·rice exécutif·ve'
        WHEN 'Réalisateur' THEN 'Réalisateur·rice'
        WHEN 'Réalisatrice' THEN 'Réalisateur·rice'
        WHEN 'Régisseur' THEN 'Régisseur·euse'
        WHEN 'Régisseuse' THEN 'Régisseur·euse'
        WHEN 'Scénariste' THEN 'Scénariste'
        WHEN 'Scripte' THEN 'Scripte'
        WHEN 'free_broadcaster' THEN 'Chaîne/plateforme de diffusion gratuite'
        WHEN 'paying_broadcaster' THEN 'Chaîne/plateforme de diffusion payante'
        ELSE role
    END AS role_inclusive_name,
    CASE
        WHEN role IN (
            '1er assistant réalisateur',
            'Chef costumier',
            'Chef décorateur',
            'Chef monteur',
            'Compositeur',
            'Directeur de la photographie',
            'Directeur de production',
            'Directeur du casting',
            'Ingénieur du son',
            'Producteur délégué',
            'Producteur des effets visuels',
            'Scénariste',
            'SoundEngineer',
            'Réalisateur'
        ) THEN TRUE
        ELSE FALSE
    END AS is_key_role
FROM {{ ref('int_credit_holders_role') }}
GROUP BY
    role_id,
    role_name,
    role_inclusive_name,
    is_key_role