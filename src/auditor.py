
import subprocess, re, logging
import src.logger_config as logger_config

logger = logging.getLogger(__name__)


def get_cpu_ram():
    
#ts gets the cpu and ram
    cpuAndRam=subprocess.run(["powershell", "Get-Counter", r"'\Processor(_Total)\% Processor Time', '\Memory\% Committed Bytes In Use'"]
                    , text=True, capture_output=True)
    #support for english consols and spanish

    parternCpuAndRamRegex = r'\d+[\.,]\d+'
    
    filteredCpuAndRam = re.findall(parternCpuAndRamRegex,cpuAndRam.stdout)
    return filteredCpuAndRam # turple o lista condsjfakfidfeqr 2 elemntos creo xd
#espanol porque me esta costando hacer los test y probablemente me costaria mas si los pongo en ingles
#esto creo que podria ser mas facilmene testeable si el llamamiento de subprocess pasaria en una funcion diferente 
def get_most_process():


    #ts get the porcess
    mostConsumingProcess = subprocess.run(["powershell",r"`Get-Process"], 
                                        text=True, capture_output=True)
    #TODO se me olvido incluir el SI en todo el programa xd tal vez algun dia me animo a corregir esto 
    #                                    Han    NPM(K)   PM(K)   WS(K)   CPU(s)      Id      SI   ProcessName
    parternCosumingProcessRegex = r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)?\s+(\d+)\s+(\d)\s+(.+)$"
    lista_procesos = [] # lista retornada 
    # lista creo xd.  retorna el subprocess  se eliminan los espacios de lo que 
    #atras y adelante y se hace split en cada salto de linea 
    lineasProcesses=mostConsumingProcess.stdout.strip().split('\n')
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
                    "pm_kb":   int(match.group(3)),
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

    #this gives the storege space and saves it in storageSpace
    storageSpace = subprocess.run(["powershell", r"Get-PSDrive -PSProvider FileSystem"],
                                text=True, capture_output=True)
    
    #this block of code clean the text in storageSpace and gives a list with 
    #2 string items, the first item is the space used and the second is the free space
    # the list is 
    partenStorageSpaceRegex = r'\d+\.\d+'

    filteredStorageSpace = re.findall(partenStorageSpaceRegex, storageSpace.stdout)

   
    
    return filteredStorageSpace

#TODO tal vez me animo en crear una funcion que ordene los procesos

def run_formated_audit():
    #consigue una lista, lista, lista
    cpuAndRam = get_cpu_ram()
    Process = get_most_process()
    storage_space = get_storage_space()
    #sorted ordena los procesos en Process = get_most_process()
    #key=lambda p: p['pm_kb'] basicamente itera process y evalua 
    #p['pm_kb'] que es la ram y es un int . reverse=True pone numeros grandes primero
    #por ultimo se corta la lista creo de 0 a 9
    most_process_ram = sorted(Process, key=lambda p: p['pm_kb'], reverse=True)[:10]
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
    '''
      for p in complete_audit['process_ram']:
         name = f"{p['name']:<8}"
         cpu = f"{p['cpu']:<7}"
         ram = f"{p['pm_kb']:<7}"
         line_ram.append(f"  --Name: {name} | Cpu: {cpu}KB | ram: {ram}KB")'''
    for p in complete_audit['process_ram']: # se reccore la lista most_process_ram
         line_ram.append(
             f"  --Name: {p['name']}   | Cpu: {p['cpu']} KB | ram: {p['pm_kb']:<2} KB"
         )

    line_cpu = []

    '''   
    formato mas bonito pero cambiado para testear 
      for p in complete_audit['process_cpu']:
         name = f"{p['name']:<8}"
         cpu = f"{p['cpu']:<7}"
         ram = f"{p['pm_kb']:<7}"
         line_cpu.append(f"  --Name: {name} | Cpu: {cpu}KB | ram: {ram}KB")
    '''
    for p in complete_audit['process_cpu']:  # se reccore la lista most_process_cpu
         line_cpu.append(
             f"  --Name: {p['name']}   | Cpu: {p['cpu']} KB | ram: {p['pm_kb']:<2} KB"
         )
    
    string_most_ram = f"Most consuming processes by ram: {complete_audit['process_ram']}"
    string_most_cpu = f"Most consuming processes by cpu: {complete_audit['process_cpu']}"
    string_most_cpu = "Most consuming processes by cpu:\n\n" + "\n".join(line_cpu)
    string_most_ram = "Most consuming processes by ram:\n\n" + "\n".join(line_ram)
    string_storage_space = f"Storage used: {complete_audit['storage_used']}GB | Storage remaining: {complete_audit['storage_ramaining']}GB"

    #retorna todos los strings formateados con .join
    return "\n\n".join([string_cpu_ram, string_most_cpu, string_most_ram, string_storage_space])


def run_raw_audit():
    cpuAndRam = get_cpu_ram()
    Process = get_most_process()
    storage_space = get_storage_space()
    return cpuAndRam, Process, storage_space

if __file__ != "__main__":
    logger.debug("Estas importando auditor.py desde otro archivo")