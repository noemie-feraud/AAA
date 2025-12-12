import psutil
import socket
import platform
import datetime
import os
import time

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

# We need to define the path according to the computer on which the project is running.
# For Ubuntu / VM: we use the default user's home directory.

directory_to_analyze = "C:/school/aaa" 

base_extensions = [".txt", ".py", ".pdf", ".jpg"]
extended_extensions = [
    ".txt",
    ".py",
    ".pdf",
    ".jpg",
    ".csv",
    ".log",
    ".md",
    ".json",
    ".xml",
    ".html",
    ".png",
]

files_by_extension = {}
space_by_extension = {}
percentage_by_extension = {}
largest_files = []

# --- PROJECT FUNCTIONS ---

def analyze_directory(directory, extensions):

    """
    Walk through a directory and:
      - count how many files we have for each extension
      - calculate the total space used per extension
      - keep the list of the biggest files

    This function is reused for both the "basic" and "advanced" analysis.
    """

    # Local dictionaries to count files and space
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

    # Calculate percentage for each tracked file type
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
        "largest_files": local_largest_files,
    }


def get_system_snapshot():

    """
    Collect all the data needed for the dashboard:
    CPU, RAM, system info, processes and file statistics.
    Everything is packed in a single "snapshot" dictionary.
    """
        
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
        # Trick to find the local IP address used to access the internet
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip_address = s.getsockname()[0]
        s.close()
    except Exception:
        ip_address = "0.0.0.0"

 # PROCESSES
    global processes_list, top_cpu_processes, top_ram_processes

    # First pass: prime CPU counters for all processes
    for p in psutil.process_iter():
        try:
            p.cpu_percent(None)
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    # Small interval so psutil can compute CPU usage correctly
    time.sleep(0.2)

    # Second pass: actually collect data
    processes_list = []
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

    # Sort processes for CPU and RAM usage (we only keep the top 3)
    top_cpu_processes = sorted(processes_list, key=lambda x: x["cpu_percent"], reverse=True)[:3]
    top_ram_processes = sorted(processes_list, key=lambda x: x["ram_percent"], reverse=True)[:3]

    # FILE ANALYSIS
    basic_file_result = analyze_directory(directory_to_analyze, base_extensions)
    advanced_file_result = analyze_directory(directory_to_analyze, extended_extensions)

    # CONSTRUCT SNAPSHOT (all the data is grouped in one dict)
    snapshot = {
        "cpu": {
            "cores_physical": cpu_cores_physical,
            "cores_logical": cpu_cores_logical,
            "freq_current": cpu_freq_current,
            "usage_percent": cpu_usage_percent,
        },
        "memory": {
            "total": ram_total,
            "used": ram_used,
            "usage_percent": ram_usage_percent,
        },
        "system": {
            "hostname": hostname,
            "os": os_name,
            "os_version": os_version,
            "boot_time": boot_time_ts,
            "uptime": uptime_seconds,
            "users_count": users_count,
            "users": users_list,
            "ip": ip_address,
        },
        "processes": {
            # I only return the count here to avoid sending the full list
            "all_count": len(processes_list),
            "top_cpu": top_cpu_processes,
            "top_ram": top_ram_processes,
        },
        "files_basic": basic_file_result,
        "files_advanced": advanced_file_result,
    }

    return snapshot

def format_timestamp(ts: float) -> str:
    #Convert a timestamp (seconds since epoch) to a readable date/time.
    dt = datetime.datetime.fromtimestamp(ts)
    return dt.strftime("%Y-%m-%d %H:%M:%S")

def format_seconds_to_hms(seconds: int) -> str:
    #Convert seconds to HHh MMm SSs format.
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}h {minutes:02d}m {secs:02d}s"

def create_web_page(data):

    """
    Load the HTML template, replace all {{placeholders}} with
    the values from the snapshot, then write the final index.html.
    """

    with open("template.html", "r", encoding="utf-8") as f:
        html = f.read()

    # --- System section ---
    html = html.replace("{{machine_name}}", data["system"]["hostname"])
    html = html.replace("{{os_name}}", data["system"]["os"])
    html = html.replace("{{os_version}}", data["system"]["os_version"])

    boot_time_str = format_timestamp(data["system"]["boot_time"])
    html = html.replace("{{boot_time}}", boot_time_str)

    uptime_formatted = format_seconds_to_hms(data["system"]["uptime"])
    html = html.replace("{{uptime}}", uptime_formatted)
    html = html.replace("{{user_count}}", str(data["system"]["users_count"]))
    html = html.replace("{{users_list}}", str(data["system"]["users"]))
    html = html.replace("{{primary_ip}}", data["system"]["ip"])
    html = html.replace("{{timestamp}}", datetime.datetime.now().strftime("%H:%M:%S"))

    # --- CPU section ---
    html = html.replace("{{cpu_percent}}", str(data["cpu"]["usage_percent"]))
    html = html.replace("{{cpu_cores}}", str(data["cpu"]["cores_logical"]))
    html = html.replace("{{cores_physical}}", str(data["cpu"]["cores_physical"]))
    html = html.replace("{{cpu_frequency}}", str(data["cpu"]["freq_current"]))

    # --- RAM section (displayed in GB) ---
    gb = 1024**3  # 1 GB in bytes
    memory_total_gb = round(data["memory"]["total"] / gb, 2)
    memory_used_gb = round(data["memory"]["used"] / gb, 2)
    estimated_available_gb = round((data["memory"]["total"] - data["memory"]["used"]) / gb, 2)

    html = html.replace("{{memory_total}}", f"{memory_total_gb} GB")
    html = html.replace("{{memory_used}}", f"{memory_used_gb} GB")
    html = html.replace("{{memory_percent}}", str(data["memory"]["usage_percent"]))
    html = html.replace("{{memory_available}}", f"{estimated_available_gb} GB")

    # --- Basic files section ---
    basic = data["files_basic"]
    html = html.replace("{{txt_count}}", str(basic["files_by_extension"].get(".txt", 0)))
    html = html.replace("{{py_count}}", str(basic["files_by_extension"].get(".py", 0)))
    html = html.replace("{{pdf_count}}", str(basic["files_by_extension"].get(".pdf", 0)))
    html = html.replace("{{jpg_count}}", str(basic["files_by_extension"].get(".jpg", 0)))
    html = html.replace("{{total_basic_files}}", str(sum(basic["files_by_extension"].values())))
    html = html.replace("{{directory_to_analyze}}", directory_to_analyze)

    # --- Advanced files section ---
    adv = data["files_advanced"]
    html = html.replace("{{total_extended_files}}", str(sum(adv["files_by_extension"].values())))
    # We just dump the dictionaries as strings (simple but enough for the assignment)
    html = html.replace("{{advanced_files_by_extension}}", str(adv["files_by_extension"]))
    html = html.replace("{{advanced_space_by_extension}}", str(adv["space_by_extension"]))

    pretty_percentages = {
        ext: f"{pct:.2f}%"
        for ext, pct in adv["percentage_by_extension"].items()
    }
    html = html.replace("{{advanced_percentage_by_extension}}", str(pretty_percentages))


    # --- Top 10 largest files ---
    largest = adv["largest_files"]
    for i in range(10):
        # Using numbered placeholders (largest_file_1_path, largest_file_1_size, etc.)
        path_tag = f"{{{{largest_file_{i+1}_path}}}}"
        size_tag = f"{{{{largest_file_{i+1}_size}}}}"

        if i < len(largest):
            html = html.replace(path_tag, largest[i]["path"])
            html = html.replace(size_tag, str(largest[i]["size"]))
        else:
            html = html.replace(path_tag, "—")
            html = html.replace(size_tag, "0")

    # --- CPU processes section ---
    top_cpu = data["processes"]["top_cpu"]
    if len(top_cpu) > 0:
        html = html.replace("{{process1_name}}", top_cpu[0]["name"])
        html = html.replace("{{process1_cpu}}", str(f"{top_cpu[0]["cpu_percent"]:.2f}"))
    else:
        html = html.replace("{{process1_name}}", "—")
        html = html.replace("{{process1_cpu}}", "0")

    if len(top_cpu) > 1:
        html = html.replace("{{process2_name}}", top_cpu[1]["name"])
        html = html.replace("{{process2_cpu}}", str(f"{top_cpu[1]["cpu_percent"]:.2f}"))
    else:
        html = html.replace("{{process2_name}}", "—")
        html = html.replace("{{process2_cpu}}", "0")

    if len(top_cpu) > 2:
        html = html.replace("{{process3_name}}", top_cpu[2]["name"])
        html = html.replace("{{process3_cpu}}", str(f"{top_cpu[2]["cpu_percent"]:.2f}"))
    else:
        html = html.replace("{{process3_name}}", "—")
        html = html.replace("{{process3_cpu}}", "0")

    # --- RAM processes section ---
    top_ram = data["processes"]["top_ram"]
    if len(top_ram) > 0:
        html = html.replace("{{ram_process1_name}}", top_ram[0]["name"])
        html = html.replace("{{ram_process1_usage}}", str(f"{top_ram[0]["ram_percent"]:.2f}"))
    else:
        html = html.replace("{{ram_process1_name}}", "—")
        html = html.replace("{{ram_process1_usage}}", "0")

    if len(top_ram) > 1:
        html = html.replace("{{ram_process2_name}}", top_ram[1]["name"])
        html = html.replace("{{ram_process2_usage}}", str(f"{top_ram[1]["ram_percent"]:.2f}"))
    else:
        html = html.replace("{{ram_process2_name}}", "—")
        html = html.replace("{{ram_process2_usage}}", "0")

    if len(top_ram) > 2:
        html = html.replace("{{ram_process3_name}}", top_ram[2]["name"])
        html = html.replace("{{ram_process3_usage}}", str(f"{top_ram[2]["ram_percent"]:.2f}"))
    else:
        html = html.replace("{{ram_process3_name}}", "—")
        html = html.replace("{{ram_process3_usage}}", "0")

    # Total number of processes (used for the "Total Processes" box)
    html = html.replace("{{all_count}}", str(data["processes"]["all_count"]))
    html = html.replace("{{total_processes}}", str(data["processes"]["all_count"]))

    # --- Footer: generation time ---
    generation_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    html = html.replace("{{generation_time}}", generation_time)

    # Save the final result in index.html
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)


# --- MAIN PROGRAM ---
if __name__ == "__main__":
    # Main loop: update the snapshot and regenerate the page every 30 seconds
    while True:
        result = get_system_snapshot()
        create_web_page(result)
        print("The page index.html has been generated!")
        time.sleep(30)