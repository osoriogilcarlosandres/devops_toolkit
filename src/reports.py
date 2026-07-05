import json, csv, logging
import src.logger_config as logger_config
from pathlib import Path
from src.auditor import run_raw_audit
from typing import Any, Callable
from functools import wraps

logger = logging.getLogger(__name__)
#ok basicamente aqui 
type Data = tuple
type output = Path
type ExportFn = Callable[[Data, output], None]


def unpack_data(data) :
    unpackdata = {
        "Cpu: ": data[0][0],
        "Ram: ": data[0][1],
        "Procesess: ": data[1],
        "StorageSpaceUsed: ": data[2][0],
        "StorageSpaceRemaining: ": data[2][1],

    }
    return unpackdata

    

def save_json(data, output_path):

    logger.info('Generating report')
    with open(Path(output_path) / "report_JSON.json", mode='w', encoding="utf-8") as write_json:
        json.dump(data, write_json, indent=1)


def save_csv(data, output_path):

    with open(Path(output_path) / f"report_CSV.csv", mode='w') as write_csv:
        fieldnames = ['Cpu', 'RAM', 'Procesess','StorageSpaceUsed','StorageSpaceRemaining']
        write_csv = csv.DictWriter(write_csv, delimiter=',',fieldnames = fieldnames)
        write_csv.writeheader()
        
        write_csv.writerow(data)

    
exporters: dict[str, ExportFn] = {
    "json": save_json,
    "csv": save_csv
}

def get_output_path(output, base_path = None):

    #if the output value is invalid for the output path
    #esto es se ejecuta normamente y
    #  solo se una el base path cuando se requieren test
    if base_path is None:
        base_path = Path(__file__).resolve().parent.parent
    outputpath =  Path(base_path) / output
    #crea el directorio donde se guardara si no existe
    Path(outputpath).mkdir(exist_ok=True, parents=True)
    
    return Path(outputpath)



def generate_report(format, output):
    output_path = get_output_path(output)
    export = exporters.get(format)
    export(unpack_data(run_raw_audit()), output_path)

if __file__ != "__main__":
    logger.debug("Estas importando reporerts")