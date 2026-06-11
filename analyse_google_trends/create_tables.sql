-- =============================================================================
-- Creation des 3 tables du TP Google Trends
-- =============================================================================
-- A executer UNE SEULE FOIS dans Snowflake (web UI ou client SQL)
-- Pre-requis : etre connecte en tant que CHRISTOPHEGUEROULT01 (ACCOUNTADMIN)
-- Contexte cible : FORMATION_DB.PUBLIC avec le warehouse COMPUTE_WH
-- =============================================================================

-- 1. Selectionner le bon contexte
USE WAREHOUSE COMPUTE_WH;
USE DATABASE FORMATION_DB;
USE SCHEMA PUBLIC;


-- =============================================================================
-- TABLE 1 : MESURES_TRENDS
-- =============================================================================
-- Stocke les mesures Google Trends interrogees pour les 30 sous-categories
-- de produits Cdiscount, a raison de 2 mesures par semaine (lundi + jeudi).
--
-- Volumetrie attendue apres seeding : ~1440 lignes (6 mois d'historique)
-- =============================================================================

CREATE TABLE IF NOT EXISTS MESURES_TRENDS (
    ID INTEGER AUTOINCREMENT PRIMARY KEY,
    DATE_MESURE DATE NOT NULL,
    CATEGORIE VARCHAR(100) NOT NULL,
    SOUS_CATEGORIE VARCHAR(100) NOT NULL,
    MOT_CLE VARCHAR(200) NOT NULL,
    VALEUR_INTERET INTEGER NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

ALTER TABLE MESURES_TRENDS CLUSTER BY (DATE_MESURE);

GRANT SELECT, INSERT ON TABLE MESURES_TRENDS TO ROLE FORMATION_STAGIAIRE;


-- =============================================================================
-- TABLE 2 : VENTES
-- =============================================================================
-- Contient l'historique des ventes Cdiscount sur 6 mois pour les 30
-- sous-categories suivies par Google Trends. Chaque sous-categorie a
-- 4 produits avec des ventes journalieres.
--
-- Volumetrie attendue apres seeding : ~21 600 lignes
-- (30 sous-categories x 4 produits x 180 jours)
-- =============================================================================

CREATE TABLE IF NOT EXISTS VENTES (
    ID INTEGER AUTOINCREMENT PRIMARY KEY,
    DATE_VENTE DATE NOT NULL,
    CATEGORIE VARCHAR(100) NOT NULL,
    SOUS_CATEGORIE VARCHAR(100) NOT NULL,
    PRODUIT VARCHAR(200) NOT NULL,
    QUANTITE INTEGER NOT NULL,
    PRIX_UNITAIRE DECIMAL(10, 2) NOT NULL,
    CHIFFRE_AFFAIRES DECIMAL(12, 2) NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

ALTER TABLE VENTES CLUSTER BY (DATE_VENTE);

GRANT SELECT ON TABLE VENTES TO ROLE FORMATION_STAGIAIRE;


-- =============================================================================
-- TABLE 3 : METEO_HISTORIQUE
-- =============================================================================
-- Contient l'historique meteo journalier pour la France (moyenne nationale)
-- sur les 6 derniers mois. Sert aux analyses de correlation entre meteo
-- et ventes par categorie de produits.
--
-- Volumetrie attendue apres seeding : ~180 lignes (1 ligne par jour)
-- =============================================================================

CREATE TABLE IF NOT EXISTS METEO_HISTORIQUE (
    ID INTEGER AUTOINCREMENT PRIMARY KEY,
    DATE_METEO DATE NOT NULL UNIQUE,
    TEMPERATURE_MOYENNE DECIMAL(5, 2) NOT NULL,
    PRECIPITATIONS_MM DECIMAL(6, 2) NOT NULL,
    ENSOLEILLEMENT_HEURES DECIMAL(4, 2) NOT NULL,
    CREATED_AT TIMESTAMP_NTZ DEFAULT CURRENT_TIMESTAMP()
);

ALTER TABLE METEO_HISTORIQUE CLUSTER BY (DATE_METEO);

GRANT SELECT ON TABLE METEO_HISTORIQUE TO ROLE FORMATION_STAGIAIRE;


-- =============================================================================
-- VERIFICATION FINALE
-- =============================================================================

SELECT
    TABLE_NAME,
    ROW_COUNT,
    BYTES,
    CREATED
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'PUBLIC'
  AND TABLE_NAME IN ('MESURES_TRENDS', 'VENTES', 'METEO_HISTORIQUE')
ORDER BY TABLE_NAME;


-- =============================================================================
-- POUR RESET LES TABLES PLUS TARD SI BESOIN :
-- TRUNCATE TABLE MESURES_TRENDS;
-- TRUNCATE TABLE VENTES;
-- TRUNCATE TABLE METEO_HISTORIQUE;
--
-- POUR LES SUPPRIMER COMPLETEMENT :
-- DROP TABLE MESURES_TRENDS;
-- DROP TABLE VENTES;
-- DROP TABLE METEO_HISTORIQUE;
-- =============================================================================