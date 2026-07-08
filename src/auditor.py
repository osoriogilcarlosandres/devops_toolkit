
import subprocess, logging, requests, json
from src.reports import temp_save_api, temp_save_local
from src.config_parser import get_command, get_config
logger = logging.getLogger(__name__)

config = get_config()

def run_command(action):
    shell, command = get_command(action)
    command_runned=subprocess.run([shell, command]
                    , text=True, capture_output=True, check=True)
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
            "storage_USED": float(d["Size"]),
            "storage_FREE": float(d["Used"]),
            "storage_SIZE": float(d["Free"])
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
    

def local_audit():
    local_audit_instance = organized_commands()
    print(get_formated_audit(local_audit_instance))
    #temp_save_local(local_audit_instance)


def evaluete_conditions(local_audit_instance):
    org_dict = local_audit_instance
    cpu = org_dict["CPU_Usage_Percent"]
    ram = org_dict["RAM_Usage_Percent"]

    for devices in org_dict["storage_devices"]:
        storage_space_remaining = devices["storage_FREE"]
        total_storage = devices["storage_SIZE"]
        storage_percentage_remainig = (storage_space_remaining / total_storage) * 100
        if storage_percentage_remainig< config["ConditionsToEvaluete"]["FreeStorageMin"]:
            logger.info(f"Espacio libre de {devices["storage_NAME"]} al menos del 20% de capacidad")
        
    
    if cpu > config["ConditionsToEvaluete"]["CpuMax"]:
        logger.info("Cpu arriba de 90%")
    if ram> config["ConditionsToEvaluete"]["RamMax"]:
        logger.info("Ram arriba del 80%")

    


def get_formated_audit(evaluete_conditions):
    org_audit= evaluete_conditions

    #sorted ordena los procesos en Process = get_most_process()
    #key=lambda p: p['ram_kb'] basicamente itera process y evalua 
    #p['ram_kb'] que es la ram y es un int . reverse=True pone numeros grandes primero
    #por ultimo se corta la lista creo de 0 a 9
    most_process_ram = sorted(org_audit["Processes"], key=lambda p: p["Ram"], reverse=True)[:10]
    most_process_cpu = sorted(org_audit["Processes"], key=lambda p: p["CPU_Percent"], reverse=True)[:10]

    # se crea un diccionario con cada valor importante individual

    # se crea un string formateado para mostrar. 
    
    line_ram = []
    for p in most_process_ram: # se reccore la lista most_process_ram
         line_ram.append(
             f"  --Name: {p['Name']}   | Id : {p["Id"]} | Cpu: {p['CPU_Percent']} KB | ram: {p['Ram']:<2} KB"
         )

    line_cpu = []
    for p in most_process_cpu:  # se reccore la lista most_process_cpu
         line_cpu.append(
             f"  --Name: {p['Name']}   | Id : {p["Id"]} | Cpu: {p['CPU_Percent']} KB | ram: {p['Ram']:<2} KB"
         )
    
    line_storage = []
    for device_ins in org_audit["storage_devices"]:
        line_storage.append(
            f"Device: {device_ins["storage_NAME"]} | Storage used: {device_ins["storage_USED"]}GB | Storage remaining: {device_ins["storage_FREE"]}GB | Total storage: {device_ins["storage_SIZE"]}"
        )
    string_cpu_ram = f"Cpu %: {org_audit["CPU_Usage_Percent"]}% Ram: {org_audit["RAM_Usage_Percent"]}%"
    string_most_cpu = "Most consuming processes by cpu:\n\n" + "\n".join(line_cpu)
    string_most_ram = "Most consuming processes by ram:\n\n" + "\n".join(line_ram)
    string_storage_space = "Devices: ""\n".join(line_storage)
    final_string = "\n\n".join([string_cpu_ram, string_most_cpu, string_most_ram, string_storage_space])
    return final_string
    #retorna todos los strings formateados con .join
    



    



def get_api_latency(response):

    return response.elapsed.total_seconds()

def get_api_status_code(response):

    return response.status_code

def save_api_results(response, api_url):

    pass

def print_on_console(status_code, latency, api_url):
    
    return f"Audited API: {api_url}. Status code: {status_code}. Lantency: {latency}."


def audit_api(api_url):
    response = requests.get(api_url)
    status_code = get_api_status_code(response)
    latency = get_api_latency(response)
    print = print_on_console(status_code, latency, api_url)
    #save_api_results(status_code,latency, api_url)
    return print
    
if __file__ == "__main__":
    logger.debug("Estas importando auditor.py desde otro archivo")
