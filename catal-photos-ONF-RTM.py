import re
import csv
import cv2
import pytesseract
import time

from pathlib import Path

import configparser

t0 = time.time()

config = configparser.ConfigParser()
config.read('config.ini')
# Variables configurés
pytesseract.pytesseract.tesseract_cmd = config['Localisation OCR']['pytesseract.pytesseract.tesseract_cmd']
config_tesseract = config['Localisation OCR']['config_tesseract']
directory = config['Fichiers']['directory']
nom_fichier_csv = config['Fichiers']['nom_fichier_csv']
formatImg = config['Fichiers']['formatImg']

files = Path(directory).rglob(formatImg)

"""
# Données de test :
Data = [
    "GI E7Z\n\nMONTAGNE DE L'EAU FROIDE\n\nFontaine construite\n\nh\n|\n30 juin 1899 |\n|\n",
    "Périmètre du FTER 11-08-1947 chavanod saint gervais\n\nSérie de la Combe de St Ruph\n\nAncien chemin rural des Fingles à St Ruph\n\n(largeur Im60)\n",
    "PERIMETRE DU FIER — FORET DOMANTALE DE Transport de charbon de bois brut vers le centre de cont\n\nC1. M. BOUVEROT — 01/02/1937 \n\nSEYTHENEX, MERCURY-GENTLLY\njitionnement à ANNECY\n\nPERIMETRE DU FTER FORET DOMANTALE DE SEYTHENEX, MERCURY, GENILLY\n\nCentre de carbonisation au fond de la vallée, près de la route nationale\n\nCl. M.BOUVEROT -— 13 février 1941 -—\n——————— j\nDES OUR ER "
]
"""

# Liste des mois
mois = {
    "janvier": "01",
    "février": "02",
    "mars": "03",
    "avril": "04",
    "mai": "05",
    "juin": "06",
    "juillet": "07",
    "août": "08",
    "septembre": "09",
    "octobre": "10",
    "novembre": "11",
    "décembre": "12",
}

# Expressions régulières pour extraire la date
date_pattern = re.compile(r'(' + '|'.join(mois) + r')\s\d{4}'r'|\d\d\s(' + '|'.join(mois) + r')\s\d{4}',
                          re.IGNORECASE)
date_num_pattern = re.compile(r'\d{1,2}.\d{1,2}.\d{4}|[12]\d\d\d')

# Permet de lire les fichiers INI selon l'indentation
def lire_fichier_structure(file_path):
    structure = {}  # Dictionnaire pour stocker la structure
    current_levels = [None] * 5  # Liste pour stocker les niveaux de hiérarchie actuels

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            if not line.strip():
                continue  # Ignorer les lignes vides

            # Déterminer le niveau de hiérarchie en comptant les tabulations au début de la ligne
            indentation = len(re.match(r'^\t*', line).group(0))
            line = line.strip()  # Retirer les espaces et tabulations en début et fin de ligne

            # Mettre à jour les niveaux de hiérarchie actuels
            current_levels[indentation] = line.lower()

            # Utiliser match case pour gérer les niveaux de hiérarchie
            match indentation:
                case 0:  # Niveau 1
                    structure[current_levels[0]] = {}
                case 1:  # Niveau 2
                    structure[current_levels[0]][current_levels[1]] = {}
                case 2:  # Niveau 3
                    structure[current_levels[0]][current_levels[1]][current_levels[2]] = {}
                case 3:  # Niveau 4
                    structure[current_levels[0]][current_levels[1]][current_levels[2]][current_levels[3]] = []
                case 4:  # Niveau 5
                    structure[current_levels[0]][current_levels[1]][current_levels[2]][current_levels[3]].append(
                        line.lower())

    return structure
def chercher_correspondances(structure, texte):
    correspondances = []  # Liste pour stocker les correspondances trouvées

    def chercher_dans_structure(structure, texte, parent=None):
        for cle, valeur in structure.items():
            if cle.lower() in texte.lower():
                correspondances.append((cle, parent))

            if isinstance(valeur, dict):
                chercher_dans_structure(valeur, texte, cle)

    chercher_dans_structure(structure, texte)
    return correspondances

def nettoyer_legende(input_string):
    parts = input_string.split("-")
    cleaned_parts = []

    for part in parts:
        # Vérifie que le morceau contient bien des lettres ou 4 chiffres
        if not re.search(r'[a-z]|\d{4}', part.lower()):
            continue
        cleaned_parts.append(part)

    result = "-".join(cleaned_parts)
    return result

# Lecture des fichiers .ini
parse_locations = lire_fichier_structure('SubLocation.ini')
parse_keywords = lire_fichier_structure('keywords.ini')

mode = input("Processus d'indexation automatique du RTM74, vous voulez :\nOcériser et indexer les photos, entrez '1'.\nIndexer le ficher " + nom_fichier_csv + ", entrez '2'.")
if mode == "1":
    #OCRisation des photos
    outOCR = {}
    for jpgs in files:
        image = cv2.imread(str(jpgs), cv2.IMREAD_GRAYSCALE)
        print(jpgs)
        # OCR
        outOCR[jpgs] = pytesseract.image_to_string(image, config=config_tesseract)
elif mode == "2":
    outOCR = {}
    with open(nom_fichier_csv, mode='r', newline='', encoding='ansi') as fichier_csv:
        # Créez un objet lecteur CSV
        lecteur_csv = csv.DictReader(fichier_csv, delimiter=';')

        # Parcourez chaque ligne du fichier CSV
        for ligne in lecteur_csv:
            outOCR[ligne['chemin_jpg']] = ligne['ImageCaption']
    fichier_csv.close()

indx = 0
donnees_fichiers = []
# Parcourir les données OCR
for photo in outOCR:
    donnees_fichiers.append({
            "chemin_jpg": "",
            "Category": "",
            "Orientation": "",
            "Keywords": "",
            "LocationName": "",
            "State": "",
            "City": "",
            "ContentLocName": "",
            "SubLocation": "",
            "ImageCredit": "",
            "ImageCaption": "",
            "Copyright": "",
            "RefService": "",
            "releaseDate": "",
            "DigitizeDate": "",
            "nom_final": ""
        })

# GESTION DATE :
    # Chercher la date dans le texte
    date_match = re.search(date_pattern, outOCR[photo])
    date_num_match = re.search(date_num_pattern, outOCR[photo])

    #Si date écrite
    if date_match:
        date_string = date_match.group()
        #Cas si pas le jour
        if not date_string[0].isdecimal():
            date_string = "01 " + date_string

        date_split = date_string.split()
        # Conversion du mois en chiffre en utilisant le dictionnaire
        mois_chiffre = mois.get(date_split[1].lower())
        date_string = f"{date_split[0]}/{mois_chiffre}/{date_split[2]}"
        #print("Date = " + date_string)

        donnees_fichiers[indx]["releaseDate"] = date_string
        donnees_fichiers[indx]["DigitizeDate"] = date_string



    #Si date numérique
    elif date_num_match:
        date_string = date_num_match.group()
        # Si AAAA
        if len(date_string) == 4:
            date_string = "01/01/" + date_string
        date_string = date_string[0:2] + "/" + date_string[3:5] + "/" + date_string[6:10]
        donnees_fichiers[indx]["releaseDate"] = date_string
        donnees_fichiers[indx]["DigitizeDate"] = date_string


    # Pour CSV
    outOCR[photo] = outOCR[photo].replace(';', ',')
    outOCR[photo] = outOCR[photo].replace('\n', ' - ')
    outOCR[photo] = outOCR[photo].replace('\r', '')

    #Recherche du lieu dans les resultats
    results_locations = chercher_correspondances(parse_locations, outOCR[photo].replace(' ', '_'))

    #Recherche des mots-clées dans les resultats
    results_keywords = chercher_correspondances(parse_keywords, outOCR[photo].replace(' ', '_'))

    #Attribution des données
    donnees_fichiers[indx]["chemin_jpg"] = photo
    if results_locations:
        donnees_fichiers[indx]["SubLocation"] = results_locations[0][1]
        donnees_fichiers[indx]["City"] = results_locations[0][0]
    donnees_fichiers[indx]["LocationName"] = "FRANCE"
    donnees_fichiers[indx]["State"] = "HAUTE-SAVOIE"
    donnees_fichiers[indx]["Copyright"] = "© Office National des Forêts"
    donnees_fichiers[indx]["RefService"] = "889104"
    donnees_fichiers[indx]["Keywords"] = "R.T.M,ARCHIVES PHOTOGRAPHIQUES,"
    donnees_fichiers[indx]["Category"] = ""
    for correspondance, parent in results_keywords:
        if parent:
            if correspondance.upper() not in donnees_fichiers[indx]["Keywords"]:
                donnees_fichiers[indx]["Keywords"] = donnees_fichiers[indx]["Keywords"] + parent.upper() + ","
                if correspondance.upper() == "GLISSEMENT": #Exception pour ce mot-clé courant
                    correspondance = "GLISSEMENT DE TERRAIN"
                donnees_fichiers[indx]["Keywords"] = donnees_fichiers[indx]["Keywords"] + correspondance.upper() + ","
    # Gestion des divisions domaniales, mais peu de chance d'indexer cette donnée automatiquement
    with open("divsDomaniales.ini", 'r', encoding='utf-8') as file:
        for line in file:
            if line in outOCR[photo]:
                donnees_fichiers[indx]["ContentLocName"] = line
    # Le reste du texte est considéré comme la légende
    donnees_fichiers[indx]["ImageCaption"] = nettoyer_legende(outOCR[photo]) + " - OCR n° " + str(indx)
    donnees_fichiers[indx]["ImageCredit"] = "Autre RTM"

    if not donnees_fichiers[indx]["releaseDate"] :
        donnees_fichiers[indx]["ImageCaption"] = donnees_fichiers[indx]["ImageCaption"] + " SD"
    if not donnees_fichiers[indx]["City"] :
        donnees_fichiers[indx]["ImageCaption"] = donnees_fichiers[indx]["ImageCaption"] + " SL"

    #Nommage du fichier, à déplacer dans un programme externe afin de le faire après redaction manuelle des légendes manquantes
    if date_string:
        donnees_fichiers[indx]["nom_final"] = date_string[6:10]+date_string[3:5]+date_string[0:2]
    else:
        donnees_fichiers[indx]["nom_final"] = "00000000"
    if results_locations:
        donnees_fichiers[indx]["nom_final"] = donnees_fichiers[indx]["nom_final"] + "-" + results_locations[0][0][0:8]
    else:
        donnees_fichiers[indx]["nom_final"] = donnees_fichiers[indx]["nom_final"] + "-" + "inconnue"
    donnees_fichiers[indx]["nom_final"] = donnees_fichiers[indx]["nom_final"] + "-" + str(indx).rjust(4, '0')
    indx += 1

# Fermeture divDomaniales.ini
file.close()
print("Nombre de traitements : " + str(indx))

# Definition des noms des champs du CSV
noms_champs = ["chemin_jpg", "Category", "Orientation", "Keywords", "LocationName", "State", "City",
                   "ContentLocName", "SubLocation", "ImageCredit", "ImageCaption", "Copyright", "RefService",
                   "releaseDate", "DigitizeDate", "nom_final"]

# Ecriture des données dans le fichier CSV
with open(nom_fichier_csv, mode='w', newline='', encoding='ansi') as fichier_csv:
    writer = csv.DictWriter(fichier_csv, fieldnames=noms_champs, delimiter=';')
    writer.writeheader()
    for donnee in donnees_fichiers:
        writer.writerow(donnee)
    print("Données extraites dans " + nom_fichier_csv)

t1 = time.time()
print("temps : = " + str(t1-t0))