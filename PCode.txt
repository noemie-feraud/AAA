OBJECTIF
  Produire un “instantané” (snapshot) complet de l’état de la machine :
    - utilisation CPU (coeurs, fréquence, charge globale)
    - mémoire RAM (totale, utilisée, pourcentage)
    - informations système (nom machine, OS / version, démarrage, uptime, utilisateurs, IP)
    - liste des processus actifs avec leur consommation CPU & RAM
    - top 3 des processus les plus gourmands (CPU & RAM)

IMPORTS

import psutil
import socket
import platform
import datetime

VARIABLES / DONNÉES
  cpu_cores_physical         // entier : nombre de cœurs physiques
  cpu_cores_logical          // entier : nombre de cœurs logiques (threads)
  cpu_freq_current           // nombre : fréquence actuelle du CPU
  cpu_usage_percent          // nombre : pourcentage d’utilisation CPU global

  ram_total                  // nombre : capacité RAM totale
  ram_used                   // nombre : RAM utilisée actuellement
  ram_usage_percent          // nombre : pourcentage de RAM utilisée

  hostname                   // chaîne : nom de la machine
  os_name                    // chaîne : nom du système d’exploitation
  os_version                 // chaîne : version / release du système
  boot_time                  // date / timestamp : moment de démarrage du système
  uptime                     // durée : temps écoulé depuis le démarrage
  users_connected            // entier : nombre d’utilisateurs connectés
  users_list                 // liste de chaînes : identifiants / noms des utilisateurs connectés
  ip_address                 // chaîne : adresse IP principale (locale)

  processes_list             // tableau / liste d’objets processus
    chaque objet_processe contient :
      - pid                  // entier : identifiant du processus
      - name                 // chaîne : nom du processus
      - cpu_percent          // nombre : pourcentage CPU utilisé par le processus
      - ram_percent          // nombre : pourcentage RAM utilisé par le processus

  top_3_cpu_processes        // liste de 3 objets processus les plus gourmands en CPU
  top_3_ram_processes        // liste de 3 objets processus les plus gourmands en RAM

DÉBUT

  // --- Collecte CPU ---
  Obtenir cpu_cores_physical
  Obtenir cpu_cores_logical
  Obtenir cpu_freq_current
  Mesurer cpu_usage_percent

  // --- Collecte RAM ---
  Obtenir ram_total
  Obtenir ram_used
  Calculer ram_usage_percent

  // --- Collecte des informations système ---
  Obtenir hostname
  Obtenir os_name et os_version
  Obtenir boot_time
  Calculer uptime = (date_maintenant − boot_time)
  Obtenir users_list
  Définir users_connected = longueur(users_list)
  Déterminer ip_address (adresse IP “principale” / par défaut)

  // --- Collecte des processus ---
  Initialiser processes_list comme une liste vide
  POUR chaque processus actif FAIRE
    Lire pid, name
    Mesurer cpu_percent du processus
    Mesurer ram_percent du processus
    Ajouter à processes_list un objet { pid, name, cpu_percent, ram_percent }
  FIN POUR

  // --- Sélection des top processus ---
  Trier processes_list par cpu_percent descendant → prendre 3 premiers → top_3_cpu_processes
  Trier processes_list par ram_percent descendant → prendre 3 premiers → top_3_ram_processes

  // --- Construction du résultat final ---
  Créer un objet resultat contenant :
    CPU_info : { cpu_cores_physical, cpu_cores_logical, cpu_freq_current, cpu_usage_percent }
    RAM_info : { ram_total, ram_used, ram_usage_percent }
    System_info : { hostname, os_name, os_version, boot_time, uptime, users_connected, users_list, ip_address }
    Processes : processes_list
    Top_CPU : top_3_cpu_processes
    Top_RAM : top_3_ram_processes

  // --- Sortie / Export (selon usage) ---
  Afficher / Retourner / Exporter resultat

FIN
