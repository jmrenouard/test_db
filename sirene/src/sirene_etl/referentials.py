"""Referential data seeding and dynamic FK protection for the Sirene 3NF schema."""

from __future__ import annotations

import csv
from pathlib import Path
from typing import TYPE_CHECKING, Any

import httpx

from sirene_etl.config import Settings
from sirene_etl.downloader import download_with_verification
from sirene_etl.logging_utils import get_logger

if TYPE_CHECKING:
    import psycopg

logger = get_logger(__name__)

_UPSERT_CHUNK_SIZE = 5000

# Built-in INSEE workforce bracket codes (trancheEffectifs).
BUILTIN_TRANCHES_EFFECTIFS: tuple[tuple[str, int | None, int | None, str], ...] = (
    ("NN", None, None, "Unité non employeuse"),
    ("00", 0, 0, "0 salarié (ayant employé au moins un salarié dans l'année)"),
    ("01", 1, 2, "1 ou 2 salariés"),
    ("02", 3, 5, "3 à 5 salariés"),
    ("03", 6, 9, "6 à 9 salariés"),
    ("11", 10, 19, "10 à 19 salariés"),
    ("12", 20, 49, "20 à 49 salariés"),
    ("21", 50, 99, "50 à 99 salariés"),
    ("22", 100, 199, "100 à 199 salariés"),
    ("31", 200, 249, "200 à 249 salariés"),
    ("32", 250, 499, "250 à 499 salariés"),
    ("41", 500, 999, "500 à 999 salariés"),
    ("42", 1000, 1999, "1 000 à 1 999 salariés"),
    ("51", 2000, 4999, "2 000 à 4 999 salariés"),
    ("52", 5000, 9999, "5 000 à 9 999 salariés"),
    ("53", 10000, None, "10 000 salariés et plus"),
    ("UN", None, None, "Tranche d'effectif inconnue"),
)

# Built-in French regions (18 administrative regions + COM + UNK sentinel).
BUILTIN_REGIONS: tuple[tuple[str, str | None, str, str], ...] = (
    ("UNK", None, "INCONNUE", "Région inconnue"),
    ("01", "97105", "GUADELOUPE", "Guadeloupe"),
    ("02", "97209", "MARTINIQUE", "Martinique"),
    ("03", "97302", "GUYANE", "Guyane"),
    ("04", "97411", "LA REUNION", "La Réunion"),
    ("06", "97608", "MAYOTTE", "Mayotte"),
    ("11", "75056", "ILE-DE-FRANCE", "Île-de-France"),
    ("24", "45234", "CENTRE-VAL DE LOIRE", "Centre-Val de Loire"),
    ("27", "21231", "BOURGOGNE-FRANCHE-COMTE", "Bourgogne-Franche-Comté"),
    ("28", "76540", "NORMANDIE", "Normandie"),
    ("32", "59350", "HAUTS-DE-FRANCE", "Hauts-de-France"),
    ("44", "67482", "GRAND EST", "Grand Est"),
    ("52", "44109", "PAYS DE LA LOIRE", "Pays de la Loire"),
    ("53", "35238", "BRETAGNE", "Bretagne"),
    ("75", "33063", "NOUVELLE-AQUITAINE", "Nouvelle-Aquitaine"),
    ("76", "31555", "OCCITANIE", "Occitanie"),
    ("84", "69123", "AUVERGNE-RHONE-ALPES", "Auvergne-Rhône-Alpes"),
    ("93", "13055", "PROVENCE-ALPES-COTE D'AZUR", "Provence-Alpes-Côte d'Azur"),
    ("94", "2A004", "CORSE", "Corse"),
    ("975", None, "SAINT-PIERRE-ET-MIQUELON", "Saint-Pierre-et-Miquelon"),
    ("977", None, "SAINT-BARTHELEMY", "Saint-Barthélemy"),
    ("978", None, "SAINT-MARTIN", "Saint-Martin"),
    ("986", None, "WALLIS-ET-FUTUNA", "Wallis-et-Futuna"),
    ("987", None, "POLYNESIE FRANCAISE", "Polynésie française"),
    ("988", None, "NOUVELLE-CALEDONIE", "Nouvelle-Calédonie"),
)

# All 101 French departments + COM + legacy/foreign/sentinel codes.
BUILTIN_DEPARTEMENTS: tuple[tuple[str, str, str | None, str, str], ...] = (
    ("UNK", "UNK", None, "INCONNU", "Département inconnu"),
    ("99", "UNK", None, "ETRANGER", "Pays étrangers et hors territoire"),
    ("20", "94", None, "CORSE (HISTORIQUE)", "Corse (historique avant 1976)"),
    ("01", "84", "01053", "AIN", "Ain"),
    ("02", "32", "02408", "AISNE", "Aisne"),
    ("03", "84", "03190", "ALLIER", "Allier"),
    ("04", "93", "04070", "ALPES-DE-HAUTE-PROVENCE", "Alpes-de-Haute-Provence"),
    ("05", "93", "05061", "HAUTES-ALPES", "Hautes-Alpes"),
    ("06", "93", "06088", "ALPES-MARITIMES", "Alpes-Maritimes"),
    ("07", "84", "07186", "ARDECHE", "Ardèche"),
    ("08", "44", "08105", "ARDENNES", "Ardennes"),
    ("09", "76", "09122", "ARIEGE", "Ariège"),
    ("10", "44", "10387", "AUBE", "Aube"),
    ("11", "76", "11069", "AUDE", "Aude"),
    ("12", "76", "12202", "AVEYRON", "Aveyron"),
    ("13", "93", "13055", "BOUCHES-DU-RHONE", "Bouches-du-Rhône"),
    ("14", "28", "14118", "CALVADOS", "Calvados"),
    ("15", "84", "15014", "CANTAL", "Cantal"),
    ("16", "75", "16015", "CHARENTE", "Charente"),
    ("17", "75", "17300", "CHARENTE-MARITIME", "Charente-Maritime"),
    ("18", "24", "18033", "CHER", "Cher"),
    ("19", "75", "19272", "CORREZE", "Corrèze"),
    ("2A", "94", "2A004", "CORSE-DU-SUD", "Corse-du-Sud"),
    ("2B", "94", "2B033", "HAUTE-CORSE", "Haute-Corse"),
    ("21", "27", "21231", "COTE-D'OR", "Côte-d'Or"),
    ("22", "53", "22278", "COTES-D'ARMOR", "Côtes-d'Armor"),
    ("23", "75", "23096", "CREUSE", "Creuse"),
    ("24", "75", "24322", "DORDOGNE", "Dordogne"),
    ("25", "27", "25056", "DOUBS", "Doubs"),
    ("26", "84", "26362", "DROME", "Drôme"),
    ("27", "28", "27229", "EURE", "Eure"),
    ("28", "24", "28085", "EURE-ET-LOIR", "Eure-et-Loir"),
    ("29", "53", "29232", "FINISTERE", "Finistère"),
    ("30", "76", "30189", "GARD", "Gard"),
    ("31", "76", "31555", "HAUTE-GARONNE", "Haute-Garonne"),
    ("32", "76", "32013", "GERS", "Gers"),
    ("33", "75", "33063", "GIRONDE", "Gironde"),
    ("34", "76", "34172", "HERAULT", "Hérault"),
    ("35", "53", "35238", "ILLE-ET-VILAINE", "Ille-et-Vilaine"),
    ("36", "24", "36044", "INDRE", "Indre"),
    ("37", "24", "37261", "INDRE-ET-LOIRE", "Indre-et-Loire"),
    ("38", "84", "38185", "ISERE", "Isère"),
    ("39", "27", "39300", "JURA", "Jura"),
    ("40", "75", "40192", "LANDES", "Landes"),
    ("41", "24", "41018", "LOIR-ET-CHER", "Loir-et-Cher"),
    ("42", "84", "42218", "LOIRE", "Loire"),
    ("43", "84", "43157", "HAUTE-LOIRE", "Haute-Loire"),
    ("44", "52", "44109", "LOIRE-ATLANTIQUE", "Loire-Atlantique"),
    ("45", "24", "45234", "LOIRET", "Loiret"),
    ("46", "76", "46042", "LOT", "Lot"),
    ("47", "75", "47001", "LOT-ET-GARONNE", "Lot-et-Garonne"),
    ("48", "76", "48095", "LOZERE", "Lozère"),
    ("49", "52", "49007", "MAINE-ET-LOIRE", "Maine-et-Loire"),
    ("50", "28", "50502", "MANCHE", "Manche"),
    ("51", "44", "51108", "MARNE", "Marne"),
    ("52", "44", "52121", "HAUTE-MARNE", "Haute-Marne"),
    ("53", "52", "53130", "MAYENNE", "Mayenne"),
    ("54", "44", "54395", "MEURTHE-ET-MOSELLE", "Meurthe-et-Moselle"),
    ("55", "44", "55029", "MEUSE", "Meuse"),
    ("56", "53", "56260", "MORBIHAN", "Morbihan"),
    ("57", "44", "57463", "MOSELLE", "Moselle"),
    ("58", "27", "58194", "NIEVRE", "Nièvre"),
    ("59", "32", "59350", "NORD", "Nord"),
    ("60", "32", "60057", "OISE", "Oise"),
    ("61", "28", "61001", "ORNE", "Orne"),
    ("62", "32", "62041", "PAS-DE-CALAIS", "Pas-de-Calais"),
    ("63", "84", "63113", "PUY-DE-DOME", "Puy-de-Dôme"),
    ("64", "75", "64445", "PYRENEES-ATLANTIQUES", "Pyrénées-Atlantiques"),
    ("65", "76", "65440", "HAUTES-PYRENEES", "Hautes-Pyrénées"),
    ("66", "76", "66136", "PYRENEES-ORIENTALES", "Pyrénées-Orientales"),
    ("67", "44", "67482", "BAS-RHIN", "Bas-Rhin"),
    ("68", "44", "68066", "HAUT-RHIN", "Haut-Rhin"),
    ("69", "84", "69123", "RHONE", "Rhône"),
    ("70", "27", "70550", "HAUTE-SAONE", "Haute-Saône"),
    ("71", "27", "71270", "SAONE-ET-LOIRE", "Saône-et-Loire"),
    ("72", "52", "72181", "SARTHE", "Sarthe"),
    ("73", "84", "73065", "SAVOIE", "Savoie"),
    ("74", "84", "74010", "HAUTE-SAVOIE", "Haute-Savoie"),
    ("75", "11", "75056", "PARIS", "Paris"),
    ("76", "28", "76540", "SEINE-MARITIME", "Seine-Maritime"),
    ("77", "11", "77288", "SEINE-ET-MARNE", "Seine-et-Marne"),
    ("78", "11", "78646", "YVELINES", "Yvelines"),
    ("79", "75", "79191", "DEUX-SEVRES", "Deux-Sèvres"),
    ("80", "32", "80021", "SOMME", "Somme"),
    ("81", "76", "81004", "TARN", "Tarn"),
    ("82", "76", "82121", "TARN-ET-GARONNE", "Tarn-et-Garonne"),
    ("83", "93", "83137", "VAR", "Var"),
    ("84", "93", "84007", "VAUCLUSE", "Vaucluse"),
    ("85", "52", "85191", "VENDEE", "Vendée"),
    ("86", "75", "86194", "VIENNE", "Vienne"),
    ("87", "75", "87085", "HAUTE-VIENNE", "Haute-Vienne"),
    ("88", "44", "88160", "VOSGES", "Vosges"),
    ("89", "27", "89024", "YONNE", "Yonne"),
    ("90", "27", "90010", "TERRITOIRE DE BELFORT", "Territoire de Belfort"),
    ("91", "11", "91228", "ESSONNE", "Essonne"),
    ("92", "11", "92050", "HAUTS-DE-SEINE", "Hauts-de-Seine"),
    ("93", "11", "93008", "SEINE-SAINT-DENIS", "Seine-Saint-Denis"),
    ("94", "11", "94028", "VAL-DE-MARNE", "Val-de-Marne"),
    ("95", "11", "95500", "VAL-D'OISE", "Val-d'Oise"),
    ("971", "01", "97105", "GUADELOUPE", "Guadeloupe"),
    ("972", "02", "97209", "MARTINIQUE", "Martinique"),
    ("973", "03", "97302", "GUYANE", "Guyane"),
    ("974", "04", "97411", "LA REUNION", "La Réunion"),
    ("975", "975", "97502", "SAINT-PIERRE-ET-MIQUELON", "Saint-Pierre-et-Miquelon"),
    ("976", "06", "97608", "MAYOTTE", "Mayotte"),
    ("977", "977", "97701", "SAINT-BARTHELEMY", "Saint-Barthélemy"),
    ("978", "978", "97801", "SAINT-MARTIN", "Saint-Martin"),
    ("984", "UNK", None, "TERRES AUSTRALES ET ANTARCTIQUES FRANCAISES", "Terres australes et antarctiques françaises"),
    ("986", "986", "98613", "WALLIS-ET-FUTUNA", "Wallis-et-Futuna"),
    ("987", "987", "98735", "POLYNESIE FRANCAISE", "Polynésie française"),
    ("988", "988", "98818", "NOUVELLE-CALEDONIE", "Nouvelle-Calédonie"),
    ("989", "UNK", None, "ILE DE CLIPPERTON", "Île de Clipperton"),
)

_CJ_LEVEL1_LABELS: dict[str, str] = {
    "0": "Catégorie juridique inconnue",
    "1": "Entrepreneur individuel",
    "2": "Groupement de droit privé non doté de la personnalité morale",
    "3": "Personne morale de droit étranger",
    "4": "Personne morale de droit public soumise au droit commercial",
    "5": "Société commerciale",
    "6": "Autre personne morale immatriculée au RCS",
    "7": "Personne morale et organisme soumis au droit administratif",
    "8": "Organisme privé spécialisé",
    "9": "Groupement de droit privé",
}

_CJ_LEVEL2_LABELS: dict[str, str] = {
    "00": "Inconnue",
    "10": "Entrepreneur individuel",
    "21": "Indivision",
    "22": "Société créée de fait",
    "23": "Société en participation",
    "24": "Fiducie",
    "27": "Paroisse hors zone concordataire",
    "28": "Assujetti unique à la TVA",
    "29": "Autre groupement de droit privé non doté de la personnalité morale",
    "31": "Personne morale de droit étranger, immatriculée au RCS",
    "32": "Personne morale de droit étranger, non immatriculée au RCS",
    "41": "Établissement public ou régie à caractère industriel ou commercial",
    "51": "Société coopérative commerciale particulière",
    "52": "Société en nom collectif",
    "53": "Société en commandite",
    "54": "Société à responsabilité limitée (SARL)",
    "55": "Société anonyme à conseil d'administration",
    "56": "Société anonyme à directoire",
    "57": "Société par actions simplifiée",
    "58": "Société européenne",
    "61": "Caisse d'épargne et de prévoyance",
    "62": "Groupement d'intérêt économique",
    "63": "Société coopérative agricole",
    "64": "Société d'assurance mutuelle",
    "65": "Société civile",
    "69": "Autre personne morale de droit privé inscrite au RCS",
    "71": "Administration de l'État",
    "72": "Collectivité territoriale",
    "73": "Établissement public administratif",
    "74": "Autre personne morale de droit public administratif",
    "81": "Organisme gérant un régime de protection sociale à adhésion obligatoire",
    "82": "Organisme mutualiste",
    "83": "Comité social et économique",
    "84": "Organisme professionnel",
    "85": "Organisme de retraite à adhésion non obligatoire",
    "91": "Syndicat de propriétaires",
    "92": "Association loi 1901 ou assimilé",
    "93": "Fondation",
    "99": "Autre personne morale de droit privé",
}

BUILTIN_CATEGORIES_JURIDIQUES: tuple[tuple[str, str], ...] = (
    ("0000", "Catégorie juridique inconnue"),
    ("1000", "Entrepreneur individuel"),
    ("2110", "Indivision entre personnes physiques"),
    ("2120", "Indivision avec personne morale"),
    ("2210", "Société créée de fait entre personnes physiques"),
    ("2220", "Société créée de fait avec personne morale"),
    ("2310", "Société en participation entre personnes physiques"),
    ("2900", "Autre groupement de droit privé non doté de la personnalité morale"),
    ("3110", "Représentation ou agence commerciale d'État ou organisme public étranger"),
    ("3120", "Société commerciale étrangère immatriculée au RCS"),
    ("3210", "État, collectivité ou établissement public étranger"),
    ("3220", "Société étrangère non immatriculée au RCS"),
    ("4110", "Établissement public national à caractère industriel ou commercial doté d'un comptable public"),
    ("4120", "Établissement public national à caractère industriel ou commercial non doté d'un comptable public"),
    ("4140", "Établissement public local à caractère industriel ou commercial"),
    ("5191", "Société de caution mutuelle"),
    ("5202", "Société en nom collectif"),
    ("5306", "Société en commandite simple"),
    ("5308", "Société en commandite par actions"),
    ("5410", "SARL nationale"),
    ("5415", "SARL d'économie mixte"),
    ("5422", "SARL immobilière pour le commerce et l'industrie (SICOMI)"),
    ("5426", "SARL immobilière de gestion"),
    ("5430", "SARL d'aménagement foncier et d'équipement rural (SAFER)"),
    ("5431", "SARL mixte d'intérêt agricole (SMIA)"),
    ("5432", "SARL d'intérêt collectif agricole (SICA)"),
    ("5442", "SARL d'attribution"),
    ("5443", "SARL coopérative de construction"),
    ("5451", "SARL coopérative de consommation"),
    ("5453", "SARL coopérative artisanale"),
    ("5454", "SARL coopérative d'intérêt maritime"),
    ("5455", "SARL coopérative de transport"),
    ("5458", "SARL coopérative de production (SCOP)"),
    ("5459", "SARL union de sociétés coopératives"),
    ("5460", "Autre SARL coopérative"),
    ("5470", "Société de Participations Financières de Profession Libérale à responsabilité limitée (SPFPL SARL)"),
    ("5485", "Société d'exercice libéral à responsabilité limitée (SELARL)"),
    ("5498", "SARL unipersonnelle (EURL)"),
    ("5499", "Société à responsabilité limitée (sans autre indication)"),
    ("5505", "SA à participation ouvrière à conseil d'administration"),
    ("5510", "SA nationale à conseil d'administration"),
    ("5515", "SA d'économie mixte à conseil d'administration"),
    ("5560", "Autre SA coopérative à conseil d'administration"),
    ("5585", "Société d'exercice libéral à forme anonyme à conseil d'administration"),
    ("5599", "SA à conseil d'administration (s.a.i.)"),
    ("5610", "SA nationale à directoire"),
    ("5699", "SA à directoire (s.a.i.)"),
    ("5710", "SAS, société par actions simplifiée"),
    ("5720", "Société par actions simplifiée à associé unique ou société par actions simplifiée unipersonnelle"),
    ("5770", "Société de Participations Financières de Profession Libérale par actions simplifiée"),
    ("5785", "Société d'exercice libéral par actions simplifiée"),
    ("5800", "Société européenne"),
    ("6100", "Caisse d'épargne et de prévoyance"),
    ("6210", "Groupement européen d'intérêt économique (GEIE)"),
    ("6220", "Groupement d'intérêt économique (GIE)"),
    ("6316", "Coopérative d'utilisation de matériel agricole en commun (CUMA)"),
    ("6317", "Société coopérative agricole"),
    ("6411", "Société d'assurance à forme mutuelle"),
    ("6521", "Société civile de placement collectif immobilier (SCPI)"),
    ("6533", "Groupement agricole d'exploitation en commun (GAEC)"),
    ("6534", "Groupement foncier agricole"),
    ("6540", "Société civile immobilière"),
    ("6541", "Société civile immobilière de construction-vente"),
    ("6585", "Autre société civile professionnelle"),
    ("6589", "Société civile de moyens"),
    ("6595", "Caisse locale de crédit mutuel"),
    ("6597", "Société civile d'exploitation agricole"),
    ("6598", "Exploitation agricole à responsabilité limitée"),
    ("6599", "Autre société civile"),
    ("6901", "Autre personne de droit privé inscrite au registre du commerce et des sociétés"),
    ("7111", "Autorité constitutionnelle"),
    ("7112", "Autorité administrative ou publique indépendante"),
    ("7113", "Ministère"),
    ("7120", "Service central d'un ministère"),
    ("7150", "Service du ministère de la Défense"),
    ("7160", "Service déconcentré à compétence nationale d'un ministère (hors Défense)"),
    ("7171", "Service déconcentré de l'État à compétence (inter) régionale"),
    ("7172", "Service déconcentré de l'État à compétence (inter) départementale"),
    ("7190", "Autre service déconcentré de l'État à compétence territoriale"),
    ("7210", "Commune et commune nouvelle"),
    ("7220", "Département"),
    ("7229", "Autre collectivité territoriale"),
    ("7230", "Région"),
    ("7312", "Commune associée et commune déléguée"),
    ("7321", "Association syndicale autorisée"),
    ("7331", "Établissement public local d'enseignement"),
    ("7344", "Métropole"),
    ("7346", "Communauté de communes"),
    ("7348", "Communauté d'agglomération"),
    ("7361", "Centre communal d'action sociale"),
    ("7364", "Établissement d'hospitalisation"),
    ("7372", "Service départemental d'incendie et de secours (SDIS)"),
    ("7381", "Organisme consulaire"),
    ("7383", "Établissement public national à caractère scientifique culturel et professionnel"),
    ("7389", "Établissement public national à caractère administratif"),
    ("7470", "Groupement d'intérêt public (GIP)"),
    ("8110", "Régime général de la Sécurité Sociale"),
    ("8210", "Mutuelle"),
    ("8310", "Comité social d'entreprise"),
    ("8410", "Syndicat de salariés"),
    ("8450", "Ordre professionnel ou assimilé"),
    ("9110", "Syndicat de copropriété"),
    ("9210", "Association non déclarée"),
    ("9220", "Association déclarée"),
    ("9221", "Association déclarée d'insertion par l'économique"),
    ("9222", "Association intermédiaire"),
    ("9223", "Groupement d'employeurs"),
    ("9224", "Association d'avocats à responsabilité professionnelle individuelle"),
    ("9230", "Association déclarée, reconnue d'utilité publique"),
    ("9240", "Congrégation"),
    ("9260", "Association de droit local (Bas-Rhin, Haut-Rhin et Moselle)"),
    ("9300", "Fondation"),
    ("9900", "Autre personne morale de droit privé"),
)

# Built-in NAF fallback entries including 00.00Z sentinel and common sectors.
BUILTIN_NAF: tuple[tuple[str, str, str | None, str | None, str | None, str | None, str], ...] = (
    ("00.00Z", "UNKNOWN", None, None, None, None, "Activité inconnue ou non précisée"),
    ("41.20A", "NAFRev2", "F", "Construction", "41", "Construction de bâtiments", "Construction de maisons individuelles"),
    ("41.20B", "NAFRev2", "F", "Construction", "41", "Construction de bâtiments", "Construction d'autres bâtiments"),
    ("43.21A", "NAFRev2", "F", "Construction", "43", "Travaux de construction spécialisés", "Travaux d'installation électrique dans tous locaux"),
    ("45.11Z", "NAFRev2", "G", "Commerce", "45", "Commerce et réparation d'automobiles", "Commerce de voitures et de véhicules automobiles légers"),
    ("46.90Z", "NAFRev2", "G", "Commerce", "46", "Commerce de gros", "Commerce de gros non spécialisé"),
    ("47.11D", "NAFRev2", "G", "Commerce", "47", "Commerce de détail", "Supermarchés"),
    ("47.11F", "NAFRev2", "G", "Commerce", "47", "Commerce de détail", "Hypermarchés"),
    ("47.91A", "NAFRev2", "G", "Commerce", "47", "Commerce de détail", "Vente à distance sur catalogue général"),
    ("47.91B", "NAFRev2", "G", "Commerce", "47", "Commerce de détail", "Vente à distance sur catalogue spécialisé"),
    ("49.41A", "NAFRev2", "H", "Transports et entreposage", "49", "Transports terrestres", "Transports routiers de fret interurbains"),
    ("55.10Z", "NAFRev2", "I", "Hébergement et restauration", "55", "Hébergement", "Hôtels et hébergement similaire"),
    ("56.10A", "NAFRev2", "I", "Hébergement et restauration", "56", "Restauration", "Restauration traditionnelle"),
    ("56.10C", "NAFRev2", "I", "Hébergement et restauration", "56", "Restauration", "Restauration de type rapide"),
    ("62.01Z", "NAFRev2", "J", "Information et communication", "62", "Programmation, conseil et autres activités informatiques", "Programmation informatique"),
    ("62.02A", "NAFRev2", "J", "Information et communication", "62", "Programmation, conseil et autres activités informatiques", "Conseil en systèmes et logiciels informatiques"),
    ("62.02B", "NAFRev2", "J", "Information et communication", "62", "Programmation, conseil et autres activités informatiques", "Tierce maintenance de systèmes et d'applications informatiques"),
    ("62.03Z", "NAFRev2", "J", "Information et communication", "62", "Programmation, conseil et autres activités informatiques", "Gestion d'installations informatiques"),
    ("62.09Z", "NAFRev2", "J", "Information et communication", "62", "Programmation, conseil et autres activités informatiques", "Autres activités informatiques"),
    ("63.11Z", "NAFRev2", "J", "Information et communication", "63", "Services d'information", "Traitement de données, hébergement et activités connexes"),
    ("63.12Z", "NAFRev2", "J", "Information et communication", "63", "Services d'information", "Portails Internet"),
    ("64.20Z", "NAFRev2", "K", "Activités financières et d'assurance", "64", "Activités des services financiers", "Activités des sociétés holding"),
    ("68.20A", "NAFRev2", "L", "Activités immobilières", "68", "Activités immobilières", "Location de logements"),
    ("68.20B", "NAFRev2", "L", "Activités immobilières", "68", "Activités immobilières", "Location de terrains et d'autres biens immobiliers"),
    ("69.20Z", "NAFRev2", "M", "Activités spécialisées, scientifiques et techniques", "69", "Activités juridiques et comptables", "Activités comptables"),
    ("70.10Z", "NAFRev2", "M", "Activités spécialisées, scientifiques et techniques", "70", "Activités des sièges sociaux ; conseil de gestion", "Activités des sièges sociaux"),
    ("70.22Z", "NAFRev2", "M", "Activités spécialisées, scientifiques et techniques", "70", "Activités des sièges sociaux ; conseil de gestion", "Conseil pour les affaires et autres conseils de gestion"),
    ("71.12B", "NAFRev2", "M", "Activités spécialisées, scientifiques et techniques", "71", "Activités d'architecture et d'ingénierie", "Ingénierie, études techniques"),
    ("74.90B", "NAFRev2", "M", "Activités spécialisées, scientifiques et techniques", "74", "Autres activités spécialisées, scientifiques et techniques", "Activités spécialisées, scientifiques et techniques diverses"),
    ("84.11Z", "NAFRev2", "O", "Administration publique", "84", "Administration publique et défense", "Administration publique générale"),
    ("85.59A", "NAFRev2", "P", "Enseignement", "85", "Enseignement", "Formation continue d'adultes"),
    ("86.21Z", "NAFRev2", "Q", "Santé humaine et action sociale", "86", "Activités pour la santé humaine", "Activité des médecins généralistes"),
    ("94.99Z", "NAFRev2", "S", "Autres activités de services", "94", "Activités des organisations associatives", "Autres organisations fonctionnant par adhésion volontaire"),
    ("96.02A", "NAFRev2", "S", "Autres activités de services", "96", "Autres services personnels", "Coiffure"),
)

BUILTIN_PAYS: tuple[tuple[str, str | None, str | None, str], ...] = (
    ("UNK", None, None, "Pays inconnu"),
    ("99100", "FR", "FRA", "France"),
)


def _iter_chunks(items: list[Any], chunk_size: int = _UPSERT_CHUNK_SIZE) -> list[list[Any]]:
    return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]


def _clean_text(val: Any, max_len: int) -> str | None:
    if val is None:
        return None
    text = str(val).strip()
    if not text:
        return None
    return text[:max_len]


def _derive_departement_code(code_commune: str, raw_dep: str | None = None) -> str:
    dep = (raw_dep or "").strip()[:4]
    if dep:
        return dep
    if code_commune.startswith(("97", "98")) and len(code_commune) >= 3:
        return code_commune[:3]
    if len(code_commune) >= 2:
        return code_commune[:2]
    return "UNK"


def _read_csv_rows(file_path: Path) -> list[dict[str, str]]:
    with file_path.open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(4096)
        handle.seek(0)
        first_line = sample.splitlines()[0] if sample else ""
        delimiter = ";" if (";" in first_line and "," not in first_line) else ","
        reader = csv.DictReader(handle, delimiter=delimiter)
        rows: list[dict[str, str]] = []
        for raw_row in reader:
            cleaned = {
                key.strip().upper(): (val.strip() if val is not None else "")
                for key, val in raw_row.items()
                if key is not None
            }
            rows.append(cleaned)
        return rows


def _upsert_regions(
    conn: psycopg.Connection,
    rows: list[tuple[str, str | None, str, str]],
) -> int:
    if not rows:
        return 0
    dedup = {r[0]: r for r in rows if r[0]}
    items = list(dedup.values())
    query = """
        INSERT INTO ref_regions (code_region, cheflieu, nom_majuscule, libelle)
        SELECT code_region, cheflieu, nom_majuscule, libelle
        FROM UNNEST(
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[]
        ) AS t(code_region, cheflieu, nom_majuscule, libelle)
        ON CONFLICT (code_region) DO UPDATE SET
            cheflieu = COALESCE(EXCLUDED.cheflieu, ref_regions.cheflieu),
            nom_majuscule = EXCLUDED.nom_majuscule,
            libelle = EXCLUDED.libelle
    """
    with conn.cursor() as cur:
        for chunk in _iter_chunks(items):
            cur.execute(
                query,
                (
                    [r[0] for r in chunk],
                    [r[1] for r in chunk],
                    [r[2] for r in chunk],
                    [r[3] for r in chunk],
                ),
            )
    return len(items)


def _ensure_region_stubs(conn: psycopg.Connection, region_codes: set[str]) -> None:
    clean = sorted({c.strip()[:3] for c in region_codes if c and c.strip()})
    if not clean:
        return
    query = """
        INSERT INTO ref_regions (code_region, cheflieu, nom_majuscule, libelle)
        SELECT c, NULL, c, 'Région ' || c
        FROM UNNEST(%s::varchar[]) AS t(c)
        ON CONFLICT (code_region) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(query, (clean,))


def _upsert_departements(
    conn: psycopg.Connection,
    rows: list[tuple[str, str, str | None, str, str]],
) -> int:
    if not rows:
        return 0
    dedup = {r[0]: r for r in rows if r[0]}
    items = list(dedup.values())
    _ensure_region_stubs(conn, {r[1] for r in items})
    query = """
        INSERT INTO ref_departements (
            code_departement, code_region, cheflieu, nom_majuscule, libelle
        )
        SELECT code_departement, code_region, cheflieu, nom_majuscule, libelle
        FROM UNNEST(
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[]
        ) AS t(code_departement, code_region, cheflieu, nom_majuscule, libelle)
        ON CONFLICT (code_departement) DO UPDATE SET
            code_region = EXCLUDED.code_region,
            cheflieu = COALESCE(EXCLUDED.cheflieu, ref_departements.cheflieu),
            nom_majuscule = EXCLUDED.nom_majuscule,
            libelle = EXCLUDED.libelle
    """
    with conn.cursor() as cur:
        for chunk in _iter_chunks(items):
            cur.execute(
                query,
                (
                    [r[0] for r in chunk],
                    [r[1] for r in chunk],
                    [r[2] for r in chunk],
                    [r[3] for r in chunk],
                    [r[4] for r in chunk],
                ),
            )
    return len(items)


def _ensure_departement_stubs(conn: psycopg.Connection, dept_codes: set[str]) -> None:
    clean = sorted({c.strip()[:4] for c in dept_codes if c and c.strip()})
    if not clean:
        return
    _ensure_region_stubs(conn, {"UNK"})
    query = """
        INSERT INTO ref_departements (
            code_departement, code_region, cheflieu, nom_majuscule, libelle
        )
        SELECT c, 'UNK', NULL, c, 'Département ' || c
        FROM UNNEST(%s::varchar[]) AS t(c)
        ON CONFLICT (code_departement) DO NOTHING
    """
    with conn.cursor() as cur:
        cur.execute(query, (clean,))


def _upsert_communes(
    conn: psycopg.Connection,
    rows: list[tuple[str, str, str, str, str, bool]],
    *,
    preserve_active_on_conflict: bool = False,
) -> int:
    if not rows:
        return 0
    dedup = {r[0]: r for r in rows if r[0]}
    items = list(dedup.values())
    _ensure_departement_stubs(conn, {r[1] for r in items})

    if preserve_active_on_conflict:
        conflict_clause = """
            ON CONFLICT (code_commune) DO UPDATE SET
                code_departement = CASE
                    WHEN ref_communes.est_active THEN ref_communes.code_departement
                    ELSE EXCLUDED.code_departement
                END,
                type_commune = CASE
                    WHEN ref_communes.est_active THEN ref_communes.type_commune
                    ELSE EXCLUDED.type_commune
                END,
                nom_majuscule = CASE
                    WHEN ref_communes.est_active THEN ref_communes.nom_majuscule
                    ELSE EXCLUDED.nom_majuscule
                END,
                libelle = CASE
                    WHEN ref_communes.est_active THEN ref_communes.libelle
                    ELSE EXCLUDED.libelle
                END,
                est_active = ref_communes.est_active OR EXCLUDED.est_active
        """
    else:
        conflict_clause = """
            ON CONFLICT (code_commune) DO UPDATE SET
                code_departement = EXCLUDED.code_departement,
                type_commune = EXCLUDED.type_commune,
                nom_majuscule = EXCLUDED.nom_majuscule,
                libelle = EXCLUDED.libelle,
                est_active = EXCLUDED.est_active
        """

    query = f"""
        INSERT INTO ref_communes (
            code_commune, code_departement, type_commune, nom_majuscule, libelle, est_active
        )
        SELECT code_commune, code_departement, type_commune, nom_majuscule, libelle, est_active
        FROM UNNEST(
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::boolean[]
        ) AS t(code_commune, code_departement, type_commune, nom_majuscule, libelle, est_active)
        {conflict_clause}
    """
    with conn.cursor() as cur:
        for chunk in _iter_chunks(items):
            cur.execute(
                query,
                (
                    [r[0] for r in chunk],
                    [r[1] for r in chunk],
                    [r[2] for r in chunk],
                    [r[3] for r in chunk],
                    [r[4] for r in chunk],
                    [r[5] for r in chunk],
                ),
            )
    return len(items)


def _upsert_pays(
    conn: psycopg.Connection,
    rows: list[tuple[str, str | None, str | None, str]],
) -> int:
    if not rows:
        return 0
    dedup = {r[0]: r for r in rows if r[0]}
    items = list(dedup.values())
    query = """
        INSERT INTO ref_pays (code_pays, code_iso2, code_iso3, libelle)
        SELECT code_pays, code_iso2, code_iso3, libelle
        FROM UNNEST(
            %s::varchar[],
            %s::char(2)[],
            %s::char(3)[],
            %s::varchar[]
        ) AS t(code_pays, code_iso2, code_iso3, libelle)
        ON CONFLICT (code_pays) DO UPDATE SET
            code_iso2 = COALESCE(EXCLUDED.code_iso2, ref_pays.code_iso2),
            code_iso3 = COALESCE(EXCLUDED.code_iso3, ref_pays.code_iso3),
            libelle = EXCLUDED.libelle
    """
    with conn.cursor() as cur:
        for chunk in _iter_chunks(items):
            cur.execute(
                query,
                (
                    [r[0] for r in chunk],
                    [r[1] for r in chunk],
                    [r[2] for r in chunk],
                    [r[3] for r in chunk],
                ),
            )
    return len(items)


def _upsert_naf(
    conn: psycopg.Connection,
    rows: list[
        tuple[
            str,
            str,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str,
        ]
    ],
) -> int:
    if not rows:
        return 0
    dedup = {r[0]: r for r in rows if r[0]}
    items = list(dedup.values())
    query = """
        INSERT INTO ref_naf (
            code_naf,
            nomenclature,
            code_section,
            libelle_section,
            code_division,
            libelle_division,
            code_groupe,
            libelle_groupe,
            code_classe,
            libelle_classe,
            libelle_sous_classe
        )
        SELECT
            code_naf,
            nomenclature,
            code_section,
            libelle_section,
            code_division,
            libelle_division,
            code_groupe,
            libelle_groupe,
            code_classe,
            libelle_classe,
            libelle_sous_classe
        FROM UNNEST(
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[]
        ) AS t(
            code_naf,
            nomenclature,
            code_section,
            libelle_section,
            code_division,
            libelle_division,
            code_groupe,
            libelle_groupe,
            code_classe,
            libelle_classe,
            libelle_sous_classe
        )
        ON CONFLICT (code_naf) DO UPDATE SET
            nomenclature = EXCLUDED.nomenclature,
            code_section = COALESCE(EXCLUDED.code_section, ref_naf.code_section),
            libelle_section = COALESCE(EXCLUDED.libelle_section, ref_naf.libelle_section),
            code_division = COALESCE(EXCLUDED.code_division, ref_naf.code_division),
            libelle_division = COALESCE(EXCLUDED.libelle_division, ref_naf.libelle_division),
            code_groupe = COALESCE(EXCLUDED.code_groupe, ref_naf.code_groupe),
            libelle_groupe = COALESCE(EXCLUDED.libelle_groupe, ref_naf.libelle_groupe),
            code_classe = COALESCE(EXCLUDED.code_classe, ref_naf.code_classe),
            libelle_classe = COALESCE(EXCLUDED.libelle_classe, ref_naf.libelle_classe),
            libelle_sous_classe = EXCLUDED.libelle_sous_classe
    """
    with conn.cursor() as cur:
        for chunk in _iter_chunks(items):
            cur.execute(
                query,
                tuple([r[idx] for r in chunk] for idx in range(11)),
            )
    return len(items)


def _upsert_categories_juridiques(
    conn: psycopg.Connection,
    rows: list[tuple[str, str | None, str | None, str | None, str | None, str]],
) -> int:
    if not rows:
        return 0
    dedup = {r[0]: r for r in rows if r[0]}
    items = list(dedup.values())
    query = """
        INSERT INTO ref_categories_juridiques (
            code_cj,
            code_niveau1,
            libelle_niveau1,
            code_niveau2,
            libelle_niveau2,
            libelle
        )
        SELECT code_cj, code_niveau1, libelle_niveau1, code_niveau2, libelle_niveau2, libelle
        FROM UNNEST(
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[],
            %s::varchar[]
        ) AS t(code_cj, code_niveau1, libelle_niveau1, code_niveau2, libelle_niveau2, libelle)
        ON CONFLICT (code_cj) DO UPDATE SET
            code_niveau1 = COALESCE(EXCLUDED.code_niveau1, ref_categories_juridiques.code_niveau1),
            libelle_niveau1 = COALESCE(EXCLUDED.libelle_niveau1, ref_categories_juridiques.libelle_niveau1),
            code_niveau2 = COALESCE(EXCLUDED.code_niveau2, ref_categories_juridiques.code_niveau2),
            libelle_niveau2 = COALESCE(EXCLUDED.libelle_niveau2, ref_categories_juridiques.libelle_niveau2),
            libelle = EXCLUDED.libelle
    """
    with conn.cursor() as cur:
        for chunk in _iter_chunks(items):
            cur.execute(
                query,
                (
                    [r[0] for r in chunk],
                    [r[1] for r in chunk],
                    [r[2] for r in chunk],
                    [r[3] for r in chunk],
                    [r[4] for r in chunk],
                    [r[5] for r in chunk],
                ),
            )
    return len(items)


def _upsert_tranches_effectifs(
    conn: psycopg.Connection,
    rows: list[tuple[str, int | None, int | None, str]],
) -> int:
    if not rows:
        return 0
    dedup = {r[0]: r for r in rows if r[0]}
    items = list(dedup.values())
    query = """
        INSERT INTO ref_tranches_effectifs (
            code_tranche, effectif_min, effectif_max, libelle
        )
        SELECT code_tranche, effectif_min, effectif_max, libelle
        FROM UNNEST(
            %s::varchar[],
            %s::integer[],
            %s::integer[],
            %s::varchar[]
        ) AS t(code_tranche, effectif_min, effectif_max, libelle)
        ON CONFLICT (code_tranche) DO UPDATE SET
            effectif_min = EXCLUDED.effectif_min,
            effectif_max = EXCLUDED.effectif_max,
            libelle = EXCLUDED.libelle
    """
    with conn.cursor() as cur:
        cur.execute(
            query,
            (
                [r[0] for r in items],
                [r[1] for r in items],
                [r[2] for r in items],
                [r[3] for r in items],
            ),
        )
    return len(items)


def _seed_builtin_referentials(conn: psycopg.Connection) -> dict[str, int]:
    counts: dict[str, int] = {}
    counts["ref_regions"] = _upsert_regions(conn, list(BUILTIN_REGIONS))
    counts["ref_departements"] = _upsert_departements(conn, list(BUILTIN_DEPARTEMENTS))
    counts["ref_communes"] = _upsert_communes(
        conn,
        [("UNK00", "UNK", "HIST", "COMMUNE INCONNUE", "Commune inconnue", False)],
        preserve_active_on_conflict=True,
    )
    counts["ref_pays"] = _upsert_pays(conn, list(BUILTIN_PAYS))

    naf_rows = [
        (
            code,
            nomenclature,
            code_sec,
            lib_sec,
            code_div,
            lib_div,
            code[:4] if code != "00.00Z" else None,
            None,
            code[:5] if code != "00.00Z" else None,
            None,
            lib_sc,
        )
        for code, nomenclature, code_sec, lib_sec, code_div, lib_div, lib_sc in BUILTIN_NAF
    ]
    counts["ref_naf"] = _upsert_naf(conn, naf_rows)

    cj_rows: list[tuple[str, str | None, str | None, str | None, str | None, str]] = []
    for code_cj, label in BUILTIN_CATEGORIES_JURIDIQUES:
        n1 = code_cj[0]
        n2 = code_cj[:2]
        cj_rows.append(
            (
                code_cj,
                n1,
                _CJ_LEVEL1_LABELS.get(n1),
                n2,
                _CJ_LEVEL2_LABELS.get(n2),
                label[:255],
            )
        )
    counts["ref_categories_juridiques"] = _upsert_categories_juridiques(conn, cj_rows)
    counts["ref_tranches_effectifs"] = _upsert_tranches_effectifs(
        conn, list(BUILTIN_TRANCHES_EFFECTIFS)
    )
    return counts


def _resolve_ref_file(
    filename: str,
    url: str,
    cache_dir: Path,
    ref_dir: Path | None,
    offline_only: bool,
) -> Path | None:
    if ref_dir is not None:
        local_candidate = Path(ref_dir) / filename
        if local_candidate.is_file():
            return local_candidate

    cached_candidate = cache_dir / filename
    if cached_candidate.is_file():
        return cached_candidate

    if offline_only:
        return None

    try:
        downloaded_path, _ = download_with_verification(url, cached_candidate)
        return downloaded_path
    except (httpx.HTTPError, OSError) as exc:
        logger.warning(
            "Failed to download external referential; using built-in/fallback values",
            extra={"file_name": filename, "url": url, "error": str(exc)},
        )
        return None


def _ingest_regions_csv(conn: psycopg.Connection, path: Path) -> int:
    rows: list[tuple[str, str | None, str, str]] = []
    for rec in _read_csv_rows(path):
        code = _clean_text(rec.get("REG"), 3)
        if not code:
            continue
        cheflieu = _clean_text(rec.get("CHEFLIEU"), 5)
        libelle = _clean_text(
            rec.get("LIBELLE") or rec.get("NCCENR") or rec.get("NCC") or code,
            120,
        ) or code
        nom_maj = (
            _clean_text(rec.get("NCC") or rec.get("NCCENR") or libelle, 100) or code
        ).upper()[:100]
        rows.append((code, cheflieu, nom_maj, libelle))
    return _upsert_regions(conn, rows)


def _ingest_departements_csv(conn: psycopg.Connection, path: Path) -> int:
    rows: list[tuple[str, str, str | None, str, str]] = []
    for rec in _read_csv_rows(path):
        code = _clean_text(rec.get("DEP"), 4)
        if not code:
            continue
        region = _clean_text(rec.get("REG"), 3) or "UNK"
        cheflieu = _clean_text(rec.get("CHEFLIEU"), 5)
        libelle = _clean_text(
            rec.get("LIBELLE") or rec.get("NCCENR") or rec.get("NCC") or code,
            120,
        ) or code
        nom_maj = (
            _clean_text(rec.get("NCC") or rec.get("NCCENR") or libelle, 100) or code
        ).upper()[:100]
        rows.append((code, region, cheflieu, nom_maj, libelle))
    return _upsert_departements(conn, rows)


def _ingest_communes_csv(
    conn: psycopg.Connection,
    path: Path,
    active_communes: set[str],
) -> int:
    by_code: dict[str, tuple[int, tuple[str, str, str, str, str, bool]]] = {}
    for rec in _read_csv_rows(path):
        code = _clean_text(rec.get("COM"), 5)
        if not code:
            continue
        type_com = _clean_text(rec.get("TYPECOM"), 6) or "COM"
        dep = _derive_departement_code(code, rec.get("DEP"))
        libelle = _clean_text(
            rec.get("LIBELLE") or rec.get("NCCENR") or rec.get("NCC") or code,
            150,
        ) or code
        nom_maj = (
            _clean_text(rec.get("NCC") or rec.get("NCCENR") or libelle, 150) or code
        ).upper()[:150]
        priority = 2 if type_com == "COM" else 1
        existing = by_code.get(code)
        if existing is None or priority >= existing[0]:
            by_code[code] = (
                priority,
                (code, dep, type_com, nom_maj, libelle, True),
            )
        active_communes.add(code)

    return _upsert_communes(conn, [item[1] for item in by_code.values()])


def _ingest_comer_csv(
    conn: psycopg.Connection,
    path: Path,
    active_communes: set[str],
) -> int:
    by_code: dict[str, tuple[str, str, str, str, str, bool]] = {}
    for rec in _read_csv_rows(path):
        code = _clean_text(rec.get("COM_COMER") or rec.get("COM"), 5)
        if not code:
            continue
        raw_dep = rec.get("DEP") or rec.get("COMER")
        dep = _derive_departement_code(code, raw_dep)
        type_com = _clean_text(
            rec.get("TYPECOM") or rec.get("NATURE_ZONAGE") or "COMER",
            6,
        ) or "COMER"
        libelle = _clean_text(
            rec.get("LIBELLE") or rec.get("NCCENR") or rec.get("NCC") or code,
            150,
        ) or code
        nom_maj = (
            _clean_text(rec.get("NCC") or rec.get("NCCENR") or libelle, 150) or code
        ).upper()[:150]
        by_code[code] = (code, dep, type_com, nom_maj, libelle, True)
        active_communes.add(code)

    return _upsert_communes(conn, list(by_code.values()))


def _ingest_communes_hist_csv(
    conn: psycopg.Connection,
    path: Path,
    active_communes: set[str],
) -> int:
    has_active_catalog = len(active_communes) > 0
    by_code: dict[str, tuple[tuple[int, str, str], tuple[str, str, str, str, str, bool]]] = {}

    for rec in _read_csv_rows(path):
        code = _clean_text(rec.get("COM"), 5)
        if not code:
            continue
        date_debut = (rec.get("DATE_DEBUT") or "").strip()
        date_fin = (rec.get("DATE_FIN") or "").strip()
        dep = _derive_departement_code(code, rec.get("DEP"))
        type_com = _clean_text(rec.get("TYPECOM") or "HIST", 6) or "HIST"
        libelle = _clean_text(
            rec.get("LIBELLE") or rec.get("NCCENR") or rec.get("NCC") or code,
            150,
        ) or code
        nom_maj = (
            _clean_text(rec.get("NCC") or rec.get("NCCENR") or libelle, 150) or code
        ).upper()[:150]

        est_active = (
            code in active_communes if has_active_catalog else (date_fin == "")
        )
        rank = (1 if date_fin == "" else 0, date_fin, date_debut)
        existing = by_code.get(code)
        if existing is None or rank >= existing[0]:
            by_code[code] = (
                rank,
                (code, dep, type_com, nom_maj, libelle, est_active),
            )

    return _upsert_communes(
        conn,
        [item[1] for item in by_code.values()],
        preserve_active_on_conflict=True,
    )


def _ingest_pays_csv(conn: psycopg.Connection, path: Path) -> int:
    by_code: dict[str, tuple[int, tuple[str, str | None, str | None, str]]] = {}
    for rec in _read_csv_rows(path):
        code = _clean_text(rec.get("COG") or rec.get("CODE_PAYS"), 5)
        if not code:
            continue
        raw_iso2 = _clean_text(rec.get("CODEISO2") or rec.get("ISO2"), 2)
        iso2 = raw_iso2 if raw_iso2 and len(raw_iso2) == 2 else None
        raw_iso3 = _clean_text(rec.get("CODEISO3") or rec.get("ISO3"), 3)
        iso3 = raw_iso3 if raw_iso3 and len(raw_iso3) == 3 else None
        libelle = _clean_text(
            rec.get("LIBCOG") or rec.get("LIBENR") or rec.get("LIBELLE") or code,
            150,
        ) or code
        actual_rank = 1 if (rec.get("ACTUAL") or "1") == "1" else 0
        existing = by_code.get(code)
        if existing is None or actual_rank >= existing[0]:
            by_code[code] = (actual_rank, (code, iso2, iso3, libelle))

    return _upsert_pays(conn, [item[1] for item in by_code.values()])


def _ingest_naf_parquet(conn: psycopg.Connection, path: Path) -> int:
    import pyarrow.parquet as pq

    table = pq.read_table(path)
    raw_rows = table.to_pylist()
    parsed: list[
        tuple[
            str,
            str,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str | None,
            str,
        ]
    ] = []

    for raw in raw_rows:
        rec = {str(k).strip().lower(): v for k, v in raw.items() if k is not None}
        code_naf = _clean_text(
            rec.get("code_sous_classe")
            or rec.get("code_naf")
            or rec.get("naf")
            or rec.get("code")
            or rec.get("niv5")
            or rec.get("id_5"),
            6,
        )
        if not code_naf:
            continue

        lib_sc = _clean_text(
            rec.get("libelle_sous_classe")
            or rec.get("libelle_niv5")
            or rec.get("intitule_sous_classe")
            or rec.get("libelle")
            or rec.get("label_5")
            or code_naf,
            255,
        ) or code_naf

        code_sec = _clean_text(
            rec.get("code_section")
            or rec.get("section")
            or rec.get("niv1")
            or rec.get("id_1"),
            2,
        )
        lib_sec = _clean_text(
            rec.get("libelle_section")
            or rec.get("libelle_niv1")
            or rec.get("intitule_section")
            or rec.get("label_1"),
            255,
        )
        code_div = _clean_text(
            rec.get("code_division")
            or rec.get("division")
            or rec.get("niv2")
            or rec.get("id_2")
            or code_naf[:2],
            2,
        )
        lib_div = _clean_text(
            rec.get("libelle_division")
            or rec.get("libelle_niv2")
            or rec.get("intitule_division")
            or rec.get("label_2"),
            255,
        )
        code_grp = _clean_text(
            rec.get("code_groupe")
            or rec.get("groupe")
            or rec.get("niv3")
            or rec.get("id_3")
            or (code_naf[:4] if len(code_naf) >= 4 else None),
            4,
        )
        lib_grp = _clean_text(
            rec.get("libelle_groupe")
            or rec.get("libelle_niv3")
            or rec.get("intitule_groupe")
            or rec.get("label_3"),
            255,
        )
        code_cls = _clean_text(
            rec.get("code_classe")
            or rec.get("classe")
            or rec.get("niv4")
            or rec.get("id_4")
            or (code_naf[:5] if len(code_naf) >= 5 else None),
            5,
        )
        lib_cls = _clean_text(
            rec.get("libelle_classe")
            or rec.get("libelle_niv4")
            or rec.get("intitule_classe")
            or rec.get("label_4"),
            255,
        )

        parsed.append(
            (
                code_naf,
                "NAFRev2",
                code_sec,
                lib_sec,
                code_div,
                lib_div,
                code_grp,
                lib_grp,
                code_cls,
                lib_cls,
                lib_sc,
            )
        )

    return _upsert_naf(conn, parsed)


def seed_all_referentials(
    conn: psycopg.Connection,
    settings: Settings,
    ref_dir: Path | None = None,
    offline_only: bool = False,
) -> dict[str, int]:
    """Idempotently seed built-in and optional INSEE COG / NAF referentials."""
    counts = _seed_builtin_referentials(conn)

    cache_dir = Path(settings.staging_dir) / "referentials"
    if not offline_only:
        cache_dir.mkdir(parents=True, exist_ok=True)

    regions_path = _resolve_ref_file(
        "v_region_2026.csv",
        settings.cog_regions_url,
        cache_dir,
        ref_dir,
        offline_only,
    )
    if regions_path is not None:
        counts["ref_regions"] = max(
            counts["ref_regions"], _ingest_regions_csv(conn, regions_path)
        )

    departements_path = _resolve_ref_file(
        "v_departement_2026.csv",
        settings.cog_departements_url,
        cache_dir,
        ref_dir,
        offline_only,
    )
    if departements_path is not None:
        counts["ref_departements"] = max(
            counts["ref_departements"],
            _ingest_departements_csv(conn, departements_path),
        )

    active_communes: set[str] = set()
    communes_total = 0

    communes_path = _resolve_ref_file(
        "v_commune_2026.csv",
        settings.cog_communes_url,
        cache_dir,
        ref_dir,
        offline_only,
    )
    if communes_path is not None:
        communes_total += _ingest_communes_csv(conn, communes_path, active_communes)

    comer_path = _resolve_ref_file(
        "v_commune_comer_2026.csv",
        settings.cog_comer_url,
        cache_dir,
        ref_dir,
        offline_only,
    )
    if comer_path is not None:
        communes_total += _ingest_comer_csv(conn, comer_path, active_communes)

    communes_hist_path = _resolve_ref_file(
        "v_commune_depuis_1943.csv",
        settings.cog_communes_hist_url,
        cache_dir,
        ref_dir,
        offline_only,
    )
    if communes_hist_path is not None:
        communes_total += _ingest_communes_hist_csv(
            conn, communes_hist_path, active_communes
        )

    if communes_total > 0:
        counts["ref_communes"] = communes_total

    pays_path = _resolve_ref_file(
        "v_pays_territoire_2026.csv",
        settings.cog_pays_url,
        cache_dir,
        ref_dir,
        offline_only,
    )
    if pays_path is not None:
        counts["ref_pays"] = max(counts["ref_pays"], _ingest_pays_csv(conn, pays_path))

    naf_path = _resolve_ref_file(
        "nafr2.parquet",
        settings.naf_parquet_url,
        cache_dir,
        ref_dir,
        offline_only,
    )
    if naf_path is not None:
        counts["ref_naf"] += _ingest_naf_parquet(conn, naf_path)

    logger.info(
        "Referential seeding completed",
        extra={"counts": counts, "offline_only": offline_only},
    )
    return counts


def ensure_missing_referential_codes(
    conn: psycopg.Connection,
    *,
    naf_codes: set[str],
    cj_codes: set[str],
    commune_codes: set[str],
    pays_codes: set[str],
) -> None:
    """Bulk-insert any unseen NAF, CJ, commune, or country codes to satisfy 3NF FKs."""
    clean_naf = sorted({c.strip()[:6] for c in naf_codes if c and c.strip()})
    clean_cj = sorted({c.strip()[:4] for c in cj_codes if c and c.strip()})
    clean_communes = sorted({c.strip()[:5] for c in commune_codes if c and c.strip()})
    clean_pays = sorted({c.strip()[:5] for c in pays_codes if c and c.strip()})

    with conn.cursor() as cur:
        if clean_naf:
            cur.execute(
                "SELECT code_naf FROM ref_naf WHERE code_naf = ANY(%s)",
                (clean_naf,),
            )
            existing_naf = {row[0] for row in cur.fetchall()}
            missing_naf = [c for c in clean_naf if c not in existing_naf]
            if missing_naf:
                cur.execute(
                    """
                    INSERT INTO ref_naf (
                        code_naf, nomenclature, libelle_sous_classe
                    )
                    SELECT c, 'HIST', 'Historical or unlisted activity (' || c || ')'
                    FROM UNNEST(%s::varchar[]) AS t(c)
                    ON CONFLICT (code_naf) DO NOTHING
                    """,
                    (missing_naf,),
                )

        if clean_cj:
            cur.execute(
                "SELECT code_cj FROM ref_categories_juridiques WHERE code_cj = ANY(%s)",
                (clean_cj,),
            )
            existing_cj = {row[0] for row in cur.fetchall()}
            missing_cj = [c for c in clean_cj if c not in existing_cj]
            if missing_cj:
                cur.execute(
                    """
                    INSERT INTO ref_categories_juridiques (
                        code_cj, code_niveau1, code_niveau2, libelle
                    )
                    SELECT
                        c,
                        SUBSTRING(c, 1, 1),
                        CASE WHEN LENGTH(c) >= 2 THEN SUBSTRING(c, 1, 2) ELSE NULL END,
                        'Historical or unlisted legal category (' || c || ')'
                    FROM UNNEST(%s::varchar[]) AS t(c)
                    ON CONFLICT (code_cj) DO NOTHING
                    """,
                    (missing_cj,),
                )

        if clean_communes:
            cur.execute(
                "SELECT code_commune FROM ref_communes WHERE code_commune = ANY(%s)",
                (clean_communes,),
            )
            existing_communes = {row[0] for row in cur.fetchall()}
            missing_communes = [c for c in clean_communes if c not in existing_communes]
            if missing_communes:
                cur.execute("SELECT code_departement FROM ref_departements")
                valid_depts = {row[0] for row in cur.fetchall()}
                if "UNK" not in valid_depts:
                    _ensure_departement_stubs(conn, {"UNK"})
                    valid_depts.add("UNK")

                depts: list[str] = []
                for code in missing_communes:
                    candidate = (
                        code[:3]
                        if code.startswith(("97", "98")) and len(code) >= 3
                        else (code[:2] if len(code) >= 2 else "UNK")
                    )
                    if candidate in valid_depts:
                        depts.append(candidate)
                    elif code.startswith(("97", "98")) and code[:2] in valid_depts:
                        depts.append(code[:2])
                    else:
                        depts.append("UNK")

                cur.execute(
                    """
                    INSERT INTO ref_communes (
                        code_commune,
                        code_departement,
                        type_commune,
                        nom_majuscule,
                        libelle,
                        est_active
                    )
                    SELECT
                        c,
                        d,
                        'HIST',
                        UPPER(c),
                        'Historical or unlisted commune (' || c || ')',
                        FALSE
                    FROM UNNEST(%s::varchar[], %s::varchar[]) AS t(c, d)
                    ON CONFLICT (code_commune) DO NOTHING
                    """,
                    (missing_communes, depts),
                )

        if clean_pays:
            cur.execute(
                "SELECT code_pays FROM ref_pays WHERE code_pays = ANY(%s)",
                (clean_pays,),
            )
            existing_pays = {row[0] for row in cur.fetchall()}
            missing_pays = [c for c in clean_pays if c not in existing_pays]
            if missing_pays:
                cur.execute(
                    """
                    INSERT INTO ref_pays (code_pays, libelle)
                    SELECT c, 'Historical or unlisted country (' || c || ')'
                    FROM UNNEST(%s::varchar[]) AS t(c)
                    ON CONFLICT (code_pays) DO NOTHING
                    """,
                    (missing_pays,),
                )
