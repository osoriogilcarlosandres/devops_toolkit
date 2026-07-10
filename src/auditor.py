
import subprocess, logging, requests, json, time
from src.reports import temp_save_api, temp_save_local
from src.config_parser import get_command, get_config
from src.notifer import send_notification
from pathlib import Path

logger = logging.getLogger(__name__)
config = get_config()

def run_command(action):
    shell, command = get_command(action)
    shell_flag = "-Command" if "powershell" in shell.lower() else "-c"
    try:
        command_runned=subprocess.run([shell, shell_flag, command]
                        , text=True, capture_output=True, check=True)
    except subprocess.CalledProcessError as e:
        logger.error(  f"Command for action '{action}' failed (exit {e.returncode}): {e.stderr.strip() if e.stderr else ''}")
        raise 
    return command_runned


def get_and_deserialize(action):
    getted = run_command(action)
    data =json.loads(getted.stdout)
    return data


def get_commands_output():
    Cpu = get_and_deserialize("Cpu")
    Ram = get_and_deserialize("Ram")
    Process = get_and_deserialize("Process")
    storage_space = get_and_deserialize("Storage")
    return Cpu, Ram, Process, storage_space


def organized_commands():
    commands = get_commands_output()
    dict_list_processes = [
        {
            "Name": d["Name"],
            "Id": d["Id"],
            "CPU_Percent": float(d["CPU_Percent"]),
            "Ram": float(d["RAM"])
        }
        for d in commands[2]
    ]
    storage_list = [
        {   
            "storage_NAME": d["DeviceID"],
            "storage_USED": float(d["Used"]),
            "storage_FREE": float(d["Free"]),
            "storage_SIZE": float(d["Size"])
        }
        for d in commands[3]
    ]

    organized_dict = {    
                        "CPU_Usage_Percent": float(commands[0]["CPU_Usage_Percent"]),
                        "RAM_Usage_Percent": float(commands[1]["RAM_Usage_Percent"]),
                        "Processes": dict_list_processes,
                        "storage_devices": storage_list
                    }
    return organized_dict
    

def evaluete_conditions(local_audit_instance, formated_local_audit_instance):
    org_dict = local_audit_instance
    cpu = org_dict["CPU_Usage_Percent"]
    ram = org_dict["RAM_Usage_Percent"]
    warnings_found = []
    last_storage_free = None

    for devices in org_dict["storage_devices"]:
        storage_space_remaining = devices["storage_FREE"]
        total_storage = devices["storage_SIZE"]
        last_storage_free = storage_space_remaining

        if total_storage<=0:
            logger.warning(f"Decive \"{devices['storage_NAME']}\"reports 0 total storage; skipping check.")
            continue

        storage_percentage_remainig = (storage_space_remaining / total_storage) * 100
        minStorage = config["ConditionsToEvaluete"]["FreeStorageMin"]
        if storage_percentage_remainig< minStorage:
            msg = f"WARNING! The device \"{devices["storage_NAME"]}\" is below the configured minimum {minStorage}"
            logger.warning(msg)
            warnings_found.append(msg)

    
    cpuMax = config["ConditionsToEvaluete"]["CpuMax"]
    if cpu > cpuMax:
        msg = f"WARNING! The CPU usage percentage {cpu:.3f} exceeded the configured threshold of {cpuMax}"
        logger.warning(msg)
        warnings_found.append(msg)

    ramMax = config["ConditionsToEvaluete"]["RamMax"]
    if ram > ramMax:
        msg = f"WARNING! The RAM usage parcentage {ram:.3f} exceeded tje configured threshold of {ramMax}"
        logger.warning(msg)
        warnings_found.append(msg)
    
    if not warnings_found:
        free_txt = f"{last_storage_free:.3f}" if last_storage_free is not None else "N/A"
        logger.info(f"Successful local audit. CPU at {cpu:.3f}. Ram at {ram:.3f}. Free storage {free_txt}")


    return {
        "Metrics": formated_local_audit_instance,
        "Alerts_found": warnings_found,
        "status": "DANGER" if warnings_found else "OK"

    }


def evaluete_critical_files():
    critical_files = config["critical_files"]
    dir = Path(__file__).resolve().parent.parent
    for name in critical_files:
        coincidenses = list(dir.rglob(name))
        if not coincidenses:    
            logger.info(f"The file {name} was not found.")
            continue
        for coindidense in coincidenses:
            try:
                size = coindidense.stat().st_size
            except OSError as e:
                logger.error(f"Could no stat {coindidense}: {}")
                continue

            if size ==0:
                logger.warning(f"THe file {coindidense} was found but is EMPTY.")
                continue

            mode = coindidense.stat().st_mode #extracs a num that 
            #represents the file type and the access permissions
            
            #significa leible para el mundo
            world_readable = bool(mode & 0o004)# cheks if the file has world readable permissions
                                #if name == ".env"
            if world_readable and name in (".env",):
                logger.warning(f"The file {coindidense} has permissive (world-readable) permissions.")
            
            else:
                logger.info(f"The file {coindidense} was found and it is ok")

        
def get_formated_audit(local_audit_instance):
    org_audit= local_audit_instance

    most_process_ram = sorted(org_audit["Processes"], key=lambda p: p["Ram"], reverse=True)[:10]
    most_process_cpu = sorted(org_audit["Processes"], key=lambda p: p["CPU_Percent"], reverse=True)[:10]

    line_ram = []
    for p in most_process_ram:
         line_ram.append(
             f"  --Name: {p['Name']:<9}   | Id : {p["Id"]:<5} | Cpu: {p['CPU_Percent']:<9} KB | ram: {p['Ram']} KB"
         )

    line_cpu = []
    for p in most_process_cpu:
         line_cpu.append(
             f"  --Name: {p['Name']:<9}   | Id : {p["Id"]:<5} | Cpu: {p['CPU_Percent']:<9} KB | ram: {p['Ram']} KB"
         )
    
    line_storage = []
    for device_ins in org_audit["storage_devices"]:
        line_storage.append(
            f"Device: {device_ins["storage_NAME"]} | Storage used: {device_ins["storage_USED"]}GB | Storage remaining: {device_ins["storage_FREE"]}GB | Total storage: {device_ins["storage_SIZE"]}"
        )

    string_cpu_ram = f"Cpu: {org_audit["CPU_Usage_Percent"]:.3f}% Ram: {org_audit["RAM_Usage_Percent"]:.3f}%"
    string_most_cpu = "Most consuming processes by cpu:\n\n" + "\n".join(line_cpu)
    string_most_ram = "Most consuming processes by ram:\n\n" + "\n".join(line_ram)
    string_storage_space = "Devices: \n"+"\n".join(line_storage)
    final_string = "\n\n".join([string_cpu_ram, string_most_cpu, string_most_ram, string_storage_space])
    
    return final_string
    

def local_audit():
    try:
        local_audit_instance = organized_commands()
    except Exception as e:
        logger.error(f"Local audit aborted, could not collect system metrics: {e}")
        return
    

    fortamted_org_dict = get_formated_audit(local_audit_instance)
    print(fortamted_org_dict)
    conditions = evaluete_conditions(local_audit_instance, fortamted_org_dict)
    evaluete_critical_files()
    temp_save_local(local_audit_instance)
    send_notification(conditions = conditions)


def print_on_console(status_code, latency, api_url):
     
    return f"Audited API: {api_url}. Status code: {status_code}. Lantency: {latency}."


def audit_api(api_url):
    start_time = time.time()
    try:
        response = requests.get(api_url, timeout=10)
    except requests.exceptions.RequestException as e:
        logger.error(f"{api_url} FAIL. CLULD not reach the endpoint: {e}")
        temp_save_api({"Status_code": None, "Latency": None, "Api_url": api_url, "Error": str(e)})
        return
    
    
    status_code = response.status_code
    latency = time.time() - start_time
    if status_code == 200:
        pconsol = print_on_console(status_code, latency, api_url)
        print(pconsol)
        logger.info(f"{api_url} OK in {latency}")
    elif status_code >= 500:
        logger.error(f"{api_url} FAIL. Status Code: {status_code}")
    else:
        logger.warning(f"{api_url} responded with a non-200 status code: {status_code}")
    org_dic_api = {
        "Status_code": status_code,
        "Latency": latency,
        "Api_url":api_url
    }
    temp_save_api(org_dic_api)