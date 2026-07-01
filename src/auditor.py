import subprocess, re





def get_cpu_ram():
    
#ts gets the cpu and ram
    cpuAndRam=subprocess.run(["powershell", "Get-Counter", r"'\Processor(_Total)\% Processor Time', '\Memory\% Committed Bytes In Use'"]
                    , text=True, capture_output=True)
    
    parternCpuAndRamRegex = r'\d+\.\d+'
    
    filteredCpuAndRam = re.findall(parternCpuAndRamRegex,cpuAndRam.stdout)
    return filteredCpuAndRam

def get_most_process():


    #ts get the porcess
    mostConsumingProcess = subprocess.run(["powershell",r"`Get-Process"], 
                                        text=True, capture_output=True)
    
    #                                    Han    NPM(K)   PM(K)   WS(K)   CPU(s)      Id      SI   ProcessName
    parternCosumingProcessRegex = r"^\s*(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s+([\d.]+)?\s+(\d+)\s+(\d)\s+(.+)$"
    lista_procesos = []
    lineasProcesses=mostConsumingProcess.stdout.strip().split('\n')
    for linea in lineasProcesses:
        match = re.search(parternCosumingProcessRegex, linea)
        
        if match:

            if match.group(5)==None:
                    
                    datos = {
                        
                        "pm": int(match.group(3)),
                       
                        "cpu": 0,
                       
                        "name": match.group(8).strip()
                    }
                    
            else:
                datos = {
                    
                    
                    "pm": int(match.group(3)),
                    
                    "cpu": float(match.group(5)),
                    
                    
                    "name": match.group(8).strip()
                    }
            lista_procesos.append(datos)

    return lista_procesos
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
    partenStorageSpaceRegex = r'[\d.]+'

    filteredStorageSpace = re.findall(partenStorageSpaceRegex, storageSpace.stdout)

   
    
    return filteredStorageSpace


def run_audit():
    cpuAndRam = get_cpu_ram()
    Process = get_most_process()
    storage_space = get_storage_space()

    most_process_ram = sorted(Process, key=lambda p: p['pm'], reverse=True)[:10]
    most_process_cpu = sorted(Process, key=lambda p: p['cpu'], reverse=True)[:10]

    ''' tempram = []
        tempcpu = []
        most_process_ram = []
        most_process_cpu = []

        for p in Process:
            tempram.append(p['pm'])
            tempcpu.append(p['cpu'])

        tempram.sort()
        tempcpu.sort()
        tempram = tempram[:10]
        tempcpu = tempcpu[:10]
        for t in Process:
            for y in tempram:
                if t['pm']==y:
                    most_process_ram.append(t)

            for u in tempcpu:
                if t['cpu']==u:
                    most_process_cpu.append(t)
        
    '''



    complete_audit = {
        'cpu':cpuAndRam[0],
        'ram':cpuAndRam[1],
        'process_ram':most_process_ram,
        'process_cpu':most_process_cpu,
        'storage_used':storage_space[0],
        'storage_ramaining':storage_space[1]
    }
    
    string_cpu_ram = f"Cpu: {complete_audit['cpu']} Ram: {complete_audit['ram']}"

    line_ram = []
    for p in complete_audit['process_ram']:
         name = f"{p['name']:<8}"
         cpu = f"{p['cpu']:<7}"
         ram = f"{p['pm']:<7}"
         line_ram.append(f"  --Name: {name} | Cpu: {cpu}KB | ram: {ram}KB")

    line_cpu = []
    for p in complete_audit['process_cpu']:
         name = f"{p['name']:<8}"
         cpu = f"{p['cpu']:<7}"
         ram = f"{p['pm']:<7}"
         line_cpu.append(f"  --Name: {name} | Cpu: {cpu}KB | ram: {ram}KB")
    
    string_most_ram = f"Most consuming processes by ram: {complete_audit['process_ram']}"
    string_most_cpu = f"Most consuming processes by cpu: {complete_audit['process_cpu']}"
    string_most_cpu = "Most consuming processes by cpu:\n\n" + "\n".join(line_cpu)
    string_most_ram = "Most consuming processes by ram:\n\n" + "\n".join(line_ram)
    string_storage_space = f"Storage used: {complete_audit['storage_used']}GB | Storage remaining: {complete_audit['storage_ramaining']}GB\n"

    return "\n\n".join([string_cpu_ram, string_most_cpu, string_most_ram, string_storage_space])


