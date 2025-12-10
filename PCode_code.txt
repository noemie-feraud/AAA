IMPORTS
    import psutil
    import socket
    import platform
    import datetime

VARIABLES
    cpu_cores_physical      ← entier
    cpu_cores_logical       ← entier
    cpu_freq_current        ← réel  // ou nombre
    cpu_usage_percent       ← réel

    ram_total               ← réel   // mémoire totale
    ram_used                ← réel   // mémoire utilisée
    ram_usage_percent       ← réel

    hostname                ← texte
    os_name                 ← texte
    os_version              ← texte
    boot_time_ts            ← nombre // timestamp du démarrage
    uptime_seconds          ← nombre // temps depuis démarrage
    users_list              ← liste de texte
    users_count             ← entier
    ip_address              ← texte   // adresse IP principale

    processes_list          ← liste de ProcessInfo
    top_cpu_processes       ← liste de ProcessInfo
    top_ram_processes       ← liste de ProcessInfo

TYPE ProcessInfo :
    pid                     ← entier
    name                    ← texte
    cpu_percent             ← réel
    ram_percent             ← réel

FONCTION GetSystemSnapshot() : RésultatSnapshot
    // Ce qu’on retourne : un objet/dictionnaire qui contient toutes les infos

    // --- CPU ---
    cpu_cores_physical   ← OBTENIR_NOMBRE_COEURS_PHYSIQUES()
    cpu_cores_logical    ← OBTENIR_NOMBRE_COEURS_LOGIQUES()
    cpu_freq_current     ← OBTENIR_FREQUENCE_CPU_COURANTE()
    cpu_usage_percent    ← MESURER_USAGE_CPU_GLOBAL()

    // --- RAM ---
    ram_total            ← OBTENIR_RAM_TOTALE()
    ram_used             ← OBTENIR_RAM_UTILISEE()
    ram_usage_percent    ← CALCULER_POURCENTAGE_RAM_UTILISEE(ram_total, ram_used)

    // --- Système général ---
    hostname             ← OBTENIR_NOM_MACHINE()
    os_name              ← OBTENIR_NOM_OS()
    os_version           ← OBTENIR_VERSION_OS()
    boot_time_ts         ← OBTENIR_BOOT_TIME()
    uptime_seconds       ← OBTENIR_TEMPS_PASSEPUIS_BOOT(boot_time_ts)
    users_list           ← OBTENIR_UTILISATEURS_CONNECTES()
    users_count          ← TAILLE(users_list)
    ip_address           ← DETERMINER_IP_PRINCIPALE()

    // --- Processus ---
    processes_list       ← VIDE
    POUR CHAQUE proc DANS LISTE_DES_PROCESSUS_ACTIFS() FAIRE
        info ← NOUVEL ProcessInfo
        info.pid          ← OBTENIR_PID(proc)
        info.name         ← OBTENIR_NOM_PROC(proc)
        info.cpu_percent  ← MESURER_CPU_PROC(proc)
        info.ram_percent  ← MESURER_RAM_PROC(proc)
        AJOUTER info À processes_list
    FIN POUR

    // --- Top processus ---
    top_cpu_processes  ← PRENDRE_TOP_N(processes_list, 3, critere = cpu_percent)
    top_ram_processes  ← PRENDRE_TOP_N(processes_list, 3, critere = ram_percent)

    // --- Construction du résultat ---
    snapshot ← DICTIONNAIRE
    snapshot["cpu"]       ← {cores_physical: cpu_cores_physical,
                             cores_logical: cpu_cores_logical,
                             freq_current: cpu_freq_current,
                             usage_percent: cpu_usage_percent}
    snapshot["memory"]    ← {total: ram_total,
                             used: ram_used,
                             usage_percent: ram_usage_percent}
    snapshot["system"]    ← {hostname: hostname,
                             os: os_name,
                             os_version: os_version,
                             boot_time: boot_time_ts,
                             uptime: uptime_seconds,
                             users_count: users_count,
                             users: users_list,
                             ip: ip_address}
    snapshot["processes"] ← processes_list
    snapshot["top_cpu"]   ← top_cpu_processes
    snapshot["top_ram"]   ← top_ram_processes

    RETOURNE snapshot
FIN FONCTION

// Point d’entrée du programme
DEBUT
    resultat ← GetSystemSnapshot()
    AFFICHER resultat  // ou LOGUER / EXPORTER selon besoin
FIN

