# Titre du Projet

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
## Utilisation <a name="utilisation"></a>

    1. Définir le chemin de tesseract dans config.ini.
    2. Définir le répertoire contenant les photos à traiter dans config.ini, par défaut "process".
    3. Lancement du code.
    4. Récupération des données dans donnees_fichiers.csv
## Contact <a name="contact"></a>

Teïlo Ospiri : teilo.ospiri@onf.fr, teilo.ospiri@gmail.com

