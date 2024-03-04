# catal-photos-ONF-RTM74

Ce code entre dans le contexte de la numérisation des photos des archives ONF du service RTM 74. Le service inventorie environ 6000 photographies. L’objectif de ce programme est donc d’océriser automatiquement les légendes présentes sur les numérisations des photos et de trier le contenu dans un fichier CSV afin de simplifier l’importation des données IPTC dans la base Picasa.

## Table des Matières
1. [Objectifs](#objectifs)
2. [Structure](#structure)
3. [Utilisation](#utilisation)

## Objectifs <a name="objectifs"></a>

• OCR des photos par paquets.

• Reconnaissance automatique du contenu à cataloguer (lieu, date, mots clés).

• Envoi du contenu dans un fichier CSV.

## Structure du programme <a name="structure"></a>

• catal-photos-ONF-RTM74.py

• config.ini : fichier de configuration de l'OCR et des chemins d'accès.

• keywords.ini : liste des mots clés de la base Picasa.

• SubLocation.ini : liste des lieux reconnus dans la base Picasa (régions, régions naturelles, communes) spécifiques au service 74.

• divDomaniales.ini : liste des divisions domaniales spécifiques au service 74. Non employé.

• interfaceEditCaption : programme alternatif permettant d'éditer manuellement les légendes du fichier csv.
## Utilisation <a name="utilisation"></a>
Nécessite Python 3.11.

Installation des dépendances :
>pip install -r requirements.txt 

**Cas d'utilisation 1 - Traitement par OCR :**
1. [Installer tesseract](https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe).
2. Définir le chemin de tesseract.exe dans config.ini.
3. Définir le répertoire contenant les photos à traiter dans config.ini, par défaut "process".
4. Lancement du code (cas 1).
5. Récupération des données dans donnees_fichiers.csv

**Cas d'utilisation 2 - Indexation automatique d'un CSV :** 
1. Définir le nom du fichier "nom_fichier_csv" dans config.ini, par défaut "donnees_photos.csv".
2. Lancement du code (cas 2).
3. Entrer une clé pour le nommage final des fichiers (facultatif).
4. Récupération des données dans donnees_fichiers.csv.

**InterfaceEditCaption**
1. Installer les dépendances "requirements-interface.txt" :
>pip install -r requirements-interface.txt 

2. Intégrer un fichier donnees_photo.csv dans le même répertoire, contenant les colonnes 
   1. "chemin_jpg" : Chemin absolu menant aux images.
   2. "ImageCaption" : Légende à éditer.
3. Lancer le programme :
   1. La case supérieur contient la légende à éditer, la case inférieure permet de revenir en arrière en cas d'erreur.
   2. On circule à travers les images via la colonne de droite ou via la molette.
   2. Les légendes sont sauvegardées lorsque l'on change d'image via la molette.
   3. Flèche du bas sauvegarde la légende, passe à l'image suivante et copie la dernière légende.
   4. Cliquer sur l'image ouvre le JPG correspondant.
   5. Le fichier CSV **ne doit pas** être ouvert lors du légendage.
## Contact <a name="contact"></a>
Teïlo Ospiri : teilo.ospiri@onf.fr, teilo.ospiri@gmail.com

