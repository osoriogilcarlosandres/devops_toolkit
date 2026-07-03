from pathlib import Path
import json, csv, time
from src.auditor import run_raw_audit


def save_json(datos, output_path):
    data = {
        "Cpu: ": datos[0][0],
        "Ram: ": datos[0][1],
        "Procesess: ": datos[1],
        "StorageSpaceUsed: ": datos[2][0],
        "StorageSpaceRemaining: ": datos[2][1],

    }
    count = 0
    count+=1   
    with open(Path(output_path) / f"report_JSON{str(count)}.json", mode='w', encoding="utf-8") as write_json:
        json.dump(data, write_json, indent=1)

def save_csv(datos, output_path):
    count= 0
    count +=1
    with open(Path(output_path) / f"report_CSV{str(count)}.csv", mode='w') as write_csv:
        fieldnames = ['Cpu', 'RAM', 'Procesess','StorageSpaceUsed','StorageSpaceRemaining']
        write_csv = csv.DictWriter(write_csv, delimiter=',',fieldnames = fieldnames)
        write_csv.writeheader()
        
        write_csv.writerow({'Cpu': datos[0][0],'RAM': datos[0][1], 'Procesess':datos[1], 'StorageSpaceUsed':datos[2][0], 'StorageSpaceRemaining':datos[2][1]})

    


def get_output_path(output):
    outputpath = Path.cwd() / output
    #if not Path(outputpath).exists():
    Path(outputpath).mkdir(exist_ok=True, parents=True)
    return Path(outputpath)


def generate_report(format, output):
    output_path = get_output_path(output)
    datos = run_raw_audit()
    if format == "json":
        save_json(datos=datos, output_path=output_path)
    elif format == "csv":
        save_csv(datos=datos, output_path=output_path)

