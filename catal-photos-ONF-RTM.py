import re
import csv
import cv2
import pytesseract
import time
import os
import sys
from PIL import Image

from pathlib import Path

import configparser

t0 = time.time()

config = configparser.ConfigParser()
config.read('config.ini')
# Variables configurés
pytesseract.pytesseract.tesseract_cmd = config['Localisation OCR']['pytesseract.pytesseract.tesseract_cmd']
config_tesseract = config['Localisation OCR']['config_tesseract']
# Chemin manuel des images
# directory = config['Fichiers']['directory']
nom_fichier_csv = config['Fichiers']['nom_fichier_csv']
formatImg = config['Fichiers']['formatImg']
directory = os.path.dirname(os.path.abspath(sys.argv[0]))
processDirectory = directory+"\\process"
files = Path(processDirectory).rglob(formatImg)

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
#JJ MM AAAA
date_num_pattern = re.compile(r'\d{1,2}[-/. \\]\d{1,2}[-/. \\]\d{4}|\d{1,2}[-/. \\]\d{4}|\d{4}')

# Definition des noms des champs du CSV
noms_champs = ["chemin_jpg", "Category", "Orientation", "Keywords", "LocationName", "State", "City",
                   "ContentLocName", "SubLocation", "ImageCredit", "ImageCaption", "Copyright", "RefService",
                   "releaseDate", "DigitizeDate", "nom_final"]


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

def equivalence(texte):
    return texte.replace('st','saint').replace('ô','o').replace('â','a').replace('ê','e').replace('è','e').replace('é','e').replace('ë','e')
def chercher_correspondances(structure, texte):
    correspondances = []  # Liste pour stocker les correspondances trouvées

    def chercher_dans_structure(structure, texte, parent=None):
        for cle, valeur in structure.items():
            if cle.lower().replace('-','_') in equivalence(texte.lower()):
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

def compress_images(input_dir, output_dir, target_size=2_000_000, min_size=1_200_000, min_quality=10):


    for filename in files:

        relative_path = os.path.relpath(filename,
                                        start="C:\\Users\\pc\\Desktop\\Editphoto\\catal-photos-ONF-RTM74\\process")

        count=0

        input_path = os.path.join(input_dir, relative_path)
        output_path = os.path.join(output_dir, relative_path)
        print(output_path)

        output_dirname = os.path.dirname(output_path)
        if not os.path.exists(output_dirname):
            os.makedirs(output_dirname)

        with Image.open(input_path) as img:
            if os.path.getsize(input_path) <= target_size:
                img.save(output_path)
                print(f"{filename} a été enregistré sans compression.")
            else:
                try:
                    img.save(output_path, quality=img.info['quality'] - 10)
                except KeyError:
                    img.save(output_path, quality=75)
                print(f"{filename} a été compressé et enregistré.")
                while os.path.getsize(output_path) > target_size:
                    if count > 20:
                        break
                    current_quality = img.info.get('quality', 75) - 10
                    if current_quality < min_quality:
                        break
                    img.save(output_path, quality=current_quality)
                    print(f"{filename} a été réduit dans la boucle de compression : {os.path.getsize(output_path)}")
                    if os.path.getsize(output_path) < min_size:
                        break
                    count+=1

def compress_images_undir(input_dir, output_dir, target_size=2_000_000, min_size=1_200_000, min_quality=10):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    for filename in os.listdir(input_dir):
        count = 0
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, filename)
            with Image.open(input_path) as img:
                if os.path.getsize(input_path) <= target_size:
                    img.save(output_path)
                    print(f"{filename} a été enregistré sans compression.")
                else:
                    try:
                        img.save(output_path, quality=img.info['quality'] - 5)
                    except KeyError:
                        img.save(output_path, quality=75)
                    print(f"{filename} a été compressé et enregistré.")
                    while os.path.getsize(output_path) > target_size:
                        if count > 20:
                            break
                        current_quality = img.info.get('quality', 75) - 5
                        if os.path.getsize(input_path) <= target_size:
                            break
                        img.save(output_path, quality=current_quality)
                        print(f"{filename} a été réduit dans la boucle de compression : {os.path.getsize(output_path)}")
                        if os.path.getsize(output_path) < min_size:
                            break
                        count += 1

def renommer_fichiers(csv_path):
    with open(csv_path, 'r', encoding='ansi') as fichier_csv:
        lecteur_csv = csv.DictReader(fichier_csv, delimiter=';')

        for ligne in lecteur_csv:
            chemin_absolu = ligne['chemin_jpg']
            nouveau_nom = ligne['nom_final']

            # Obtenir le chemin du répertoire du fichier
            repertoire, ancien_nom = os.path.split(chemin_absolu)

            # Construire le nouveau chemin absolu avec le nouveau nom de fichier
            nouveau_chemin = os.path.join(directory+"\\compressed", f'{nouveau_nom}.jpg')
            try:
                os.rename(chemin_absolu, nouveau_chemin)
                print(f'Le fichier {chemin_absolu} a été renommé en {nouveau_chemin}')
            except Exception as e:
                print(f'Erreur lors du renommage du fichier {chemin_absolu}: {str(e)}')

# Lecture des fichiers .ini
parse_locations = lire_fichier_structure('SubLocation.ini')
parse_keywords = lire_fichier_structure('keywords.ini')

mode = input("Processus d'indexation automatique du RTM74, vous voulez :"
             "\n     Océriser et indexer les photos, entrez '1'. (Cas de base)"
             "\n     Indexer les légendes dans le ficher " + nom_fichier_csv + ", entrez '2'. (Utile suite à l'affinage des légendes, post étape 1.)"
             "\n     Compresser et renommer les fichiers, entrez '3'. (Suite à l'insertion des données IPTC.)")

if mode == "3" :
    renommer_fichiers(nom_fichier_csv)
    compress_images_undir(processDirectory, directory+"\\compressed")
    print("Les fichiers ont été enregistrés dans \compressed.")
    exit()

index_nommage = input("Quel index souhaitez-vous donner à ce lot (Si index = 'A', alors la légende finira par OCR n° A0001).")

if mode == "1":
    #OCRisation des photos
    outOCR = {}
    if not files:
        print("Aucun fichier détecté, avez-vous renseigné correctement config.ini ?")
    for jpgs in files:
        image = cv2.imread(str(jpgs), cv2.IMREAD_GRAYSCALE)
        print(jpgs)
        # OCR
        outOCR[jpgs] = pytesseract.image_to_string(image, config=config_tesseract)
elif mode == "2":
    outOCR = {}
    with open(nom_fichier_csv, mode='r', newline='', encoding='ansi') as fichier_csv:
        # Crée un objet lecteur CSV
        lecteur_csv = csv.DictReader(fichier_csv, delimiter=';')

        # Parcours chaque ligne du fichier CSV, alimente outOCR chemin:légende, enlève les precedents identifiants OCR
        for ligne in lecteur_csv:
            chemin_fichier = ligne['chemin_jpg']
            image_caption = re.sub(" ?- OCR n°.*", "", ligne['ImageCaption'])
            outOCR[str(chemin_fichier)] = image_caption

    fichier_csv.close()

indx = 0
donnees_fichiers = []

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
    date_match = ''
    date_num_match = ''
    # Chercher la date dans le texte
    date_match = re.search(date_pattern, outOCR[photo].lower())
    date_num_match = re.search(date_num_pattern, outOCR[photo])

    date_string = ''
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
        print(date_string)
        # Si AAAA et non pas M AA
        if len(date_string) == 4 and re.match(r'\d*', date_string):
            date_string = "01/01/" + date_string
        # Si MM? AAAA
        if len(date_string) >= 7 and (re.match(r'\d\d?.\d\d\d\d', date_string)):
            date_string = "01/" + date_string
        # Si J MM AAAA
        if not re.match(r'\d', date_string[1]):
            date_string = '0' + date_string
        # Si JJ M AAAA
        if not re.match(r'\d', date_string[4]):
            date_string = date_string[0:4] + '0' + date_string[4:]
        # Si JJ MM AA
        if len(date_string) == 8:
            annee = date_string[6:]
            date_string = date_string[:6] + "19" + annee
        # On s'assure que la date est réaliste
        print(date_string)
        if int(date_string[6:10]) < 2030 and int(date_string[3:5]) <= 12 and len(date_string) == 10:
            date_string = date_string[0:2] + "/" + date_string[3:5] + "/" + date_string[6:10]
            donnees_fichiers[indx]["releaseDate"] = date_string
            donnees_fichiers[indx]["DigitizeDate"] = date_string

    # Pour CSV
    outOCR[photo] = outOCR[photo].replace(';', ',')
    outOCR[photo] = outOCR[photo].replace('\n', ' - ')
    outOCR[photo] = outOCR[photo].replace('\r', '')

    #Recherche du lieu dans les resultats
    results_locations = chercher_correspondances(parse_locations, outOCR[photo].replace(' ', '_').replace('-','_'))

    #Recherche des mots-clées dans les resultats
    results_keywords = chercher_correspondances(parse_keywords, outOCR[photo].replace(' ', '_'))

    #Attribution des données
    donnees_fichiers[indx]["chemin_jpg"] = photo
    city = ""
    if results_locations:
        donnees_fichiers[indx]["SubLocation"] = results_locations[0][1]
        city = results_locations[0][0]
        if "COMMUNE" in donnees_fichiers[indx]["ImageCaption"].upper():
            donnees_fichiers[indx]["City"] = city
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
    # Gestion des divisions domaniales, compliqué pour pas grand chose
    with open("divsDomaniales.csv", 'r', encoding='ansi') as csvfile:
        reader = csv.reader(csvfile, delimiter=';')
        DivDom = ""
        last_elements = 0
        for line in reader:
            CsvDivDom = line[0]
            CsvDivDomCourt = line[1].replace("-", "_").upper().split(',')
            certitude_column = line[2].strip()

            elements_found = sum(1 for value in CsvDivDomCourt if value in equivalence(outOCR[photo].replace("-", "_").upper()))
            required_certitude = int(certitude_column)

            if elements_found >= 1 and elements_found >= last_elements:
                DivDom = CsvDivDom
                last_elements = elements_found


    if elements_found >= required_certitude or "S.D " in outOCR[photo] or "DOMANIALE" in  outOCR[photo].upper():
        donnees_fichiers[indx]["ContentLocName"] = DivDom
    if not city == "":
        donnees_fichiers[indx]["City"] = city
    # Le reste du texte est considéré comme la légende
    donnees_fichiers[indx]["ImageCaption"] = nettoyer_legende(outOCR[photo]) + " - OCR n°" + index_nommage + str(indx)
    donnees_fichiers[indx]["ImageCredit"] = "Autre RTM"

    if not donnees_fichiers[indx]["releaseDate"]:
        donnees_fichiers[indx]["ImageCaption"] = donnees_fichiers[indx]["ImageCaption"] + " SD"
    if donnees_fichiers[indx]["City"] == "" and donnees_fichiers[indx]["ContentLocName"] == "":
        donnees_fichiers[indx]["ImageCaption"] = donnees_fichiers[indx]["ImageCaption"] + " SL"

    #Nommage du fichier,
    if date_string:
        donnees_fichiers[indx]["nom_final"] = date_string[6:10]+date_string[3:5]+date_string[0:2]
    else:
        donnees_fichiers[indx]["nom_final"] = "00000000"
    if results_locations:
        donnees_fichiers[indx]["nom_final"] = donnees_fichiers[indx]["nom_final"] + "-" + results_locations[0][0][0:8]
    elif not donnees_fichiers[indx]["ContentLocName"] == "" :
        donnees_fichiers[indx]["nom_final"] = donnees_fichiers[indx]["nom_final"] + "-" + donnees_fichiers[indx]["ContentLocName"][0:8]
    else:
        donnees_fichiers[indx]["nom_final"] = donnees_fichiers[indx]["nom_final"] + "-" + "inconnue"
    donnees_fichiers[indx]["nom_final"] = donnees_fichiers[indx]["nom_final"] + "-" + index_nommage + str(indx).rjust(4, '0')

    indx += 1

# Fermeture divDomaniales.ini
print("Nombre de traitements : " + str(indx))

# Ecriture des données dans le fichier CSV
with open(nom_fichier_csv, mode='w', newline='', encoding='ansi') as fichier_csv:
    writer = csv.DictWriter(fichier_csv, fieldnames=noms_champs, delimiter=';')
    writer.writeheader()
    for donnee in donnees_fichiers:
        writer.writerow(donnee)
    print("Données extraites dans " + nom_fichier_csv)

t1 = time.time()
print("temps : = " + str(t1-t0))



