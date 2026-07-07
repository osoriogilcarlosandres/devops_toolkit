
import subprocess, re, logging, requests
from src.reports import temp_save_api, temp_save_local
from pathlib import Path
from src.config_parser import get_command, get_config
logger = logging.getLogger(__name__)

config = get_config()

def run_command(action):
    shell, command = get_command(action)
    command_runed=subprocess.run([shell, command]
                    , text=True, capture_output=True)
    
    return command_runed


def get_cpu_ram():

    return run_command("CpuAndRam")

def parse_cpu_ram(arg):
    parternCpuAndRamRegex = r'\d+[\.,]\d+'
    
    filteredCpuAndRam = re.findall(parternCpuAndRamRegex,arg.stdout)
    #convierte a floats el cpu y ram y si no encuentra nada devuelve dos none y si encuentra solo devuelve el seguund como none
    return (float(filteredCpuAndRam[0]) if len(filteredCpuAndRam) > 0 else None, 
            float(filteredCpuAndRam[1]) if len(filteredCpuAndRam) > 1 else None)
   


def get_most_process():
  return run_command("Process")
    


def parse_processes(arg):
        #                                    Han    NPM(K)   PM(K)   WS(K)   CPU(s)      Id      SI   ProcessName
    parternCosumingProcessRegex = r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)?\s+(\d+)\s+(\d)\s+(.+)$"
    lista_procesos = [] # lista retornada 
    # lista creo xd.  retorna el subprocess  se eliminan los espacios de lo que 
    #atras y adelante y se hace split en cada salto de linea 
    lineasProcesses=arg.stdout.strip().split('\n')
    # se recorre la lista anterior con cada item 
    # siendo una linea de la tabla que da get- process
    for linea in lineasProcesses:
        #se hace re.search en cada item de la lista y se guarda en match
        match = re.search(parternCosumingProcessRegex, linea)
        # no recuerdo pero si no se encuentra nada re.search devuelve none
        if match:
            #se guardan los grupos de coincidencias en un diccionario
            datos = {
                    "handles": int(match.group(1)),
                    "npm":     int(match.group(2)),
                    "ram_kb":   int(match.group(3)),
                    "ws_kb":   int(match.group(4)),
                    # aveces el cpu puede venir vacio
                    "cpu":     float(match.group(5)) if match.group(5) else 0.0, 
                    "id":     int(match.group(6)),
                    "name":    match.group(8).strip()
                    }
            # se hace .append a la lista retornada con datos
            lista_procesos.append(datos)

    return lista_procesos # retorna una lista con un diccionario.
    '''
    for p in lista_procesos:
        print(f"Name: {p['name']}\t Ram: {p['pm']}\t Cpu: {p['cpu']}")
    '''

def get_storage_space():
    return run_command("Storage")
   
def parse_storage(arg):
    partenStorageSpaceRegex = r'\d+\.\d+'

    filteredStorageSpace = re.findall(partenStorageSpaceRegex, arg.stdout)

   
    final_list = []
    for floats in filteredStorageSpace:
        final_list.append(float(floats))
    return final_list


    
def evaluete_conditions(parse_audit_instance):
    parse_audit = parse_audit_instance
    cpu = parse_audit[0][0]
    ram = parse_audit[0][1]
    storage_space_used = parse_audit[2][0] 
    storage_space_remaining = parse_audit[2][1]
    total_storage = storage_space_used + storage_space_remaining
    storage_percentage_remainig = (storage_space_remaining / total_storage) * 100
    if cpu > config["ConditionsToEvaluete"]["CpuMax"]:
        logger.info("Cpu arriba de 90%")
    if ram> config["ConditionsToEvaluete"]["RamMax"]:
        logger.info("Ram arriba del 80%")
    if storage_percentage_remainig< config["ConditionsToEvaluete"]["FreeStorageMin"]:
        logger.info("Espacio de almacenamiento libre menos del 20%")


    


def run_raw_audit():
    cpuAndRam = get_cpu_ram()
    Process = get_most_process()
    storage_space = get_storage_space()
    return cpuAndRam, Process, storage_space

def parsed_audit():
    raw_audit=run_raw_audit()
    parsed_cpu_ram =parse_cpu_ram(raw_audit[0])
    parsed_processes=parse_processes(raw_audit[1])
    parsed_storage=parse_storage(raw_audit[2])
    return parsed_cpu_ram,  parsed_processes , parsed_storage




    
def get_formated_audit(parse_audit_instance_local):
    parse_audit_instance= parse_audit_instance_local
    evaluete_conditions(parse_audit_instance)
    cpuAndRam = parse_audit_instance[0]
    Process = parse_audit_instance[1]
    storage_space = parse_audit_instance[2]
    #sorted ordena los procesos en Process = get_most_process()
    #key=lambda p: p['ram_kb'] basicamente itera process y evalua 
    #p['ram_kb'] que es la ram y es un int . reverse=True pone numeros grandes primero
    #por ultimo se corta la lista creo de 0 a 9
    most_process_ram = sorted(Process, key=lambda p: p['ram_kb'], reverse=True)[:10]
    most_process_cpu = sorted(Process, key=lambda p: p['cpu'], reverse=True)[:10]

    # se crea un diccionario con cada valor importante individual
    complete_audit = {
        'cpu':cpuAndRam[0],
        'ram':cpuAndRam[1],
        'process_ram':most_process_ram,
        'process_cpu':most_process_cpu,
        'storage_used':storage_space[0],
        'storage_ramaining':storage_space[1]
    }
    # se crea un string formateado para mostrar. 
    string_cpu_ram = f"Cpu: {complete_audit['cpu']} Ram: {complete_audit['ram']}"

    line_ram = []

    for p in complete_audit['process_ram']: # se reccore la lista most_process_ram
         line_ram.append(
             f"  --Name: {p['name']}   | Cpu: {p['cpu']} KB | ram: {p['ram_kb']:<2} KB"
         )

    line_cpu = []


    for p in complete_audit['process_cpu']:  # se reccore la lista most_process_cpu
         line_cpu.append(
             f"  --Name: {p['name']}   | Cpu: {p['cpu']} KB | ram: {p['ram_kb']:<2} KB"
         )
    
    string_most_ram = f"Most consuming processes by ram: {complete_audit['process_ram']}"
    string_most_cpu = f"Most consuming processes by cpu: {complete_audit['process_cpu']}"
    string_most_cpu = "Most consuming processes by cpu:\n\n" + "\n".join(line_cpu)
    string_most_ram = "Most consuming processes by ram:\n\n" + "\n".join(line_ram)
    string_storage_space = f"Storage used: {complete_audit['storage_used']}GB | Storage remaining: {complete_audit['storage_ramaining']}GB"
    final_string = "\n\n".join([string_cpu_ram, string_most_cpu, string_most_ram, string_storage_space])
    return final_string
    #retorna todos los strings formateados con .join
    

def local_audit():
    parse_audit_instance = parsed_audit()
    print(get_formated_audit(parse_audit_instance))
    temp_save_local(parse_audit_instance)

    



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
