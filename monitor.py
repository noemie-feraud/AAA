import psutil
import socket
import platform
import datetime
import os

# CPU, RAM, System, Process, and File Analysis Variables
cpu_cores_physical = 0    
cpu_cores_logical = 0     
cpu_freq_current = 0.0      
cpu_usage_percent = 0.0 

ram_total = 0               
ram_used = 0               
ram_usage_percent = 0.0 

hostname = ""              
os_name = ""               
os_version = ""             
boot_time_ts = 0           
uptime_seconds = 0         
users_list = []             
users_count = 0            
ip_address = ""    

processes_list = []         
top_cpu_processes = []      
top_ram_processes = []      

# We need to define the path according to the PC on which the project is presented
directory_to_analyze = "/home/user/Documents" 
base_extensions = [".txt", ".py", ".pdf", ".jpg"]
extended_extensions = [".txt", ".py", ".pdf", ".jpg", ".csv", ".log", ".md", ".json", ".xml", ".html", ".png"]

files_by_extension = {}
space_by_extension = {}
percentage_by_extension = {}
largest_files = []

# --- PROJECT FUNCTIONS ---

def analyze_directory(directory, extensions):
    """
    Analyzes a directory to count files, calculate space usage, 
    and identify the largest files based on specific extensions.
    """
    # Create dictionaries to count files and space
    local_files_by_ext = {}
    local_space_by_ext = {}
    local_largest_files = []
    total_files = 0

    # Walk through all files in the directory and subdirectories
    for root, dirs, files in os.walk(directory):
        for file in files:
            path = os.path.join(root, file)
            ext = os.path.splitext(file)[1].lower()
            try:
                size = os.path.getsize(path)
            except OSError:
                size = 0
            
            total_files += 1

            if ext in extensions:
                if ext in local_files_by_ext:
                    local_files_by_ext[ext] += 1
                    local_space_by_ext[ext] += size
                else:
                    local_files_by_ext[ext] = 1
                    local_space_by_ext[ext] = size
                
                local_largest_files.append({"path": path, "size": size})

    # Calculate percentage for each file type
    local_pct_by_ext = {}
    for ext in local_files_by_ext:
        if total_files > 0:
            local_pct_by_ext[ext] = (local_files_by_ext[ext] / total_files) * 100
        else:
            local_pct_by_ext[ext] = 0

    # Sort to find the largest files
    local_largest_files.sort(key=lambda x: x["size"], reverse=True)
    local_largest_files = local_largest_files[:10]

    return {
        "files_by_extension": local_files_by_ext,
        "space_by_extension": local_space_by_ext,
        "percentage_by_extension": local_pct_by_ext,
        "largest_files": local_largest_files
    }

def get_system_snapshot():
    # CPU
    global cpu_cores_physical, cpu_cores_logical, cpu_freq_current, cpu_usage_percent
    cpu_cores_physical = psutil.cpu_count(logical=False)
    cpu_cores_logical = psutil.cpu_count(logical=True)
    freq = psutil.cpu_freq()
    cpu_freq_current = freq.current if freq else 0
    cpu_usage_percent = psutil.cpu_percent(interval=0.3)

    # RAM 
    global ram_total, ram_used, ram_usage_percent
    ram = psutil.virtual_memory()
    ram_total = ram.total
    ram_used = ram.used
    ram_usage_percent = ram.percent

    # SYSTEM
    global hostname, os_name, os_version, boot_time_ts, uptime_seconds, users_list, users_count, ip_address
    hostname = socket.gethostname()
    os_name = platform.system()
    os_version = platform.version()
    boot_time_ts = psutil.boot_time()
    uptime_seconds = int(datetime.datetime.now().timestamp() - boot_time_ts)
    users_list = [u.name for u in psutil.users()]
    users_count = len(users_list)
    try:
        # Trick to find the local IP address connected to the internet
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        ip_address = "0.0.0.0"

    # PROCESSES
    global processes_list, top_cpu_processes, top_ram_processes
    processes_list = []
    # Iterating over processes
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        try:
            processes_list.append({
                "pid": proc.info['pid'],
                "name": proc.info['name'],
                "cpu_percent": proc.info['cpu_percent'],
                "ram_percent": proc.info['memory_percent']
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Sort processes
    top_cpu_processes = sorted(processes_list, key=lambda x: x['cpu_percent'], reverse=True)[:3]
    top_ram_processes = sorted(processes_list, key=lambda x: x['ram_percent'], reverse=True)[:3]

    # FILE ANALYSIS 
    basic_file_result = analyze_directory(directory_to_analyze, base_extensions)
    advanced_file_result = analyze_directory(directory_to_analyze, extended_extensions)

    # CONSTRUCT SNAPSHOT
    snapshot = {
        "cpu": {
            "cores_physical": cpu_cores_physical,
            "cores_logical": cpu_cores_logical,
            "freq_current": cpu_freq_current,
            "usage_percent": cpu_usage_percent
        },
        "memory": {
            "total": ram_total,
            "used": ram_used,
            "usage_percent": ram_usage_percent
        },
        "system": {
            "hostname": hostname,
            "os": os_name,
            "os_version": os_version,
            "boot_time": boot_time_ts,
            "uptime": uptime_seconds,
            "users_count": users_count,
            "users": users_list,
            "ip": ip_address
        },
        "processes": {
            "all_count": len(processes_list), # Just returning count to avoid huge print output
            "top_cpu": top_cpu_processes,
            "top_ram": top_ram_processes
        },
        "files_basic": basic_file_result,
        "files_advanced": advanced_file_result
    }

    return snapshot

def creer_page_web(data):
    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()

    #ici on remplace les balises une à une pour toutes les sections

    #Section système

    html = html.replace("{{machine_name}}", data["system"]["hostname"]) 
    html = html.replace("{{os_name}}", data["system"]["os"]) 
    html = html.replace("{{a_remplacer}}", data["system"]["os_version"])  
    html = html.replace("{{a_remplacer}}", str(data["system"]["boot_time"])) 
    html = html.replace("{{uptime}}", str(data["system"]["uptime"]) + "s") 
    html = html.replace("{{user_count}}", str(data["system"]["users_count"])) 
    html = html.replace("{{a_remplacer}}", str(data["system"]["users"]))     
    html = html.replace("{{primary_ip}}", data["system"]["ip"]) 
    html = html.replace("{{timestamp}}", datetime.datetime.now().strftime("%H:%M:%S")) 

    #Section cpu 

    html = html.replace("{{cpu_percent}}", str(data["cpu"]["usage_percent"])) 
    html = html.replace("{{cpu_cores}}", str(data["cpu"]["cores_logical"])) 
    html = html.replace("{{a_remplacer}}", str(data["cpu"]["cores_physical"])) 
    html = html.replace("{{cpu_frequency}}", str(data["cpu"]["freq_current"])) 


    #Section ram

    html = html.replace("{{memoty_total}}", str(data["memory"]["total"]))  
    html = html.replace("{{memory_used}}", str(data["memory"]["used"]))      
    html = html.replace("{{memory_percent}}", str (data["cpu"]["usage_percent"])) 

    #Section fichiers 

    html = html.replace("{{a_remplacer}}", str(data["files_basic"]["files_by_extension"].get(".txt", 0)))
    html = html.replace("{{a_remplacer}}", str(data["files_basic"]["files_by_extension"].get(".py", 0)))
    html = html.replace("{{a_remplacer}}", str(data["files_basic"]["files_by_extension"].get(".pdf", 0)))
    html = html.replace("{{a_remplacer}}", str(data["files_basic"]["files_by_extension"].get(".jpg", 0)))
    html = html.replace("{{a_remplacer}}", str(sum(data["files_basic"]["files_by_extension"].values()))) 

    #Section fichiers avancés

    adv = data["files_advanced"]
    html = html.replace("{{total_files}}", str(sum(adv["files_by_extension"].values())))
    html = html.replace("{{a_remplacer}}", str(adv["files_by_extension"]))      
    html = html.replace("{{a_remplacer}}", str(adv["space_by_extension"]))      
    html = html.replace("{{a_remplacer}}", str(adv["percentage_by_extension"])) 

    # Top 10 fichiers les plus lourds
    largest = adv["largest_files"]
    for i in range(10):
        if i < len(largest):
            html = html.replace("{{a_remplacer}}", largest[i]["path"])
            html = html.replace("{{a_remplacer}}", str(largest[i]["size"]))
        else:
            html = html.replace("{{a_remplacer}}", "—")
            html = html.replace("{{a_remplacer}}", "0")

    # Section processus cpu
    top_cpu = data["processes"]["top_cpu"]
    if len(top_cpu) > 0:
        html = html.replace("{{process1_name}}", top_cpu[0]["name"])
        html = html.replace("{{process1_cpu}}", str(top_cpu[0]["cpu_percent"]))
    else:
        html = html.replace("{{process1_name}}", "—")
        html = html.replace("{{process1_cpu}}", "0")

    if len(top_cpu) > 1:
        html = html.replace("{{process2_name}}", top_cpu[1]["name"])
        html = html.replace("{{process2_cpu}}", str(top_cpu[1]["cpu_percent"]))
    else:
        html = html.replace("{{process2_name}}", "—")
        html = html.replace("{{process2_cpu}}", "0")

    if len(top_cpu) > 2:
        html = html.replace("{{process3_name}}", top_cpu[2]["name"])
        html = html.replace("{{process3_cpu}}", str(top_cpu[2]["cpu_percent"]))
    else:
        html = html.replace("{{process3_name}}", "—")
        html = html.replace("{{process3_cpu}}", "0")

    #Section processus ram

    top_ram = data["processes"]["top_ram"]
    if len(top_ram) > 0:
        html = html.replace("{{ram_process1_name}}", top_ram[0]["name"])
        html = html.replace("{{ram_process1_usage}}", str(top_ram[0]["ram_percent"]))
    else:
        html = html.replace("{{ram_process1_name}}", "—")
        html = html.replace("{{ram_process1_usage}}", "0")

    if len(top_ram) > 1:
        html = html.replace("{{ram_process2_name}}", top_ram[1]["name"])
        html = html.replace("{{ram_process2_usage}}", str(top_ram[1]["ram_percent"]))
    else:
        html = html.replace("{{ram_process2_name}}", "—")
        html = html.replace("{{ram_process2_usage}}", "0")

    if len(top_ram) > 2:
        html = html.replace("{{ram_process3_name}}", top_ram[2]["name"])
        html = html.replace("{{ram_process3_usage}}", str(top_ram[2]["ram_percent"]))
    else:
        html = html.replace("{{ram_process3_name}}", "—")
        html = html.replace("{{ram_process3_usage}}", "0")

    # all_count non utilisé → balise générique
    html = html.replace("{{a_remplacer}}", str(data["processes"]["all_count"]))

    #ici on enregistre le résultat dans un nouveau fichier

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

# --- MAIN PROGRAM ---
if __name__ == "__main__":
    result = get_system_snapshot()
    creer_page_web(result)
    print("La page index.html a été générée !")