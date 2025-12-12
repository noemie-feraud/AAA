# Challenge Triple A - Dashboard de Monitoring

## Description

Ce projet génère un **dashboard HTML statique** (`index.html`) qui affiche en quasi temps réel :
- l’état du CPU, de la RAM et du système,
- les **top processus** (CPU / RAM),
- des **statistiques de fichiers** sur un dossier donné.

Les données sont collectées par `monitor.py` puis injectées dans `template.html` grâce à des placeholders `{{...}}`.

## Prérequis

- Python 3.10+  
- `pip` installé  
- Un navigateur web  
- Bibliothèque Python : `psutil`

## Installation

1. Cloner ou copier le projet.
2. (Optionnel) Créer un environnement virtuel.
3. Vérifier / adapter dans `monitor.py` le chemin du dossier analysé :

   ```python
   directory_to_analyze = "C:/school/AAA"

# Commandes pour installer les dépendances

bash
Copier le code
(dans le dossier du projet, venv activé si utilisé)

```pip install psutil

## Utilisation

# Comment lancer le script

bash
Copier le code

# Windows
```python monitor.py

# Linux / macOS
```python3 monitor.py
- Le script régénère index.html toutes les 30 secondes.

# Ouvrir index.html dans le navigateur

1. Lancer monitor.py.

2. Ouvrir index.html dans le navigateur (double-clic ou “Ouvrir un fichier”).

3. Laisser l’onglet ouvert : une balise <meta http-equiv="refresh" content="10"> force le rafraîchissement automatique.

## Fonctionnalitées 

CPU : cœurs physiques/logiques, fréquence, % d’utilisation, barre de progression.
RAM : total, utilisé, disponible estimé (en GB), % d’utilisation.
Système : hostname, OS + version, boot time formaté, uptime HHh MMm SSs, utilisateurs + IP.
Processus : top 3 CPU, top 3 RAM (pourcentages arrondis), nombre total de processus.

Fichiers : analyse “de base” et “avancée” par extension, espace disque utilisé, 
           pourcentage de fichiers par extension, top 10 fichiers les plus volumineux.

## Captures d’écran
 
Des exemples de rendu sont disponibles dans le dossier :

screenshots/

(Non nécessaires à l’exécution, uniquement pour illustrer le projet.)

## Difficultés rencontrées 
 
- Mesure fiable du CPU par processus : besoin de deux passes psutil + petit sleep pour obtenir des pourcentages stables.

- Gestion des chemins et des tailles : unification des chemins (Windows / Linux) et conversion propre des octets en GB.

- Synchronisation génération / rafraîchissement : coordonner la boucle Python (mise à jour toutes les 10 s) avec la balise meta du          navigateur.

## Améliorations possible 

- Modularité du code : découper monitor.py en plusieurs fichiers (par ex. system_stats.py, file_stats.py, template_renderer.py, main.py) pour améliorer la lisibilité et la réutilisation.

- Configuration externe (fichier config.json) pour choisir le dossier à analyser, l’intervalle de rafraîchissement, etc.

## Auteur

Nom : Terry Fall, Natalia Giraldo, Noémie Feraud 
Contexte : Projet étudiant – Challenge Triple A
Github : https://github.com/noemie-feraud