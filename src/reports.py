import json, csv, logging, os
import src.logger_config as logger_config
from pathlib import Path
from src.config_parser import get_config

config = get_config()

logger = logging.getLogger(__name__)
#ok basicamente aqui 

temp_json = Path("session_json.json")

def load_history(): 
    if not temp_json.exists():
        return[]
    try:
        with open(temp_json, mode='r', encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error al leer el historial: {e}")  # Bloque A: Excepciones
        return []

def save_history(data):
 with open(temp_json, mode='w', encoding="utf-8") as file:
     json.dump(data, file, indent=4)



def save_json(data, output_path):
    
    with open(Path(output_path) / "report_JSON.json", mode='w', encoding="utf-8") as write_json:
        json.dump(data, write_json, indent=4)


def save_csv(data, output_path):

    with open(Path(output_path) / f"report_CSV.csv", mode='w') as write_csv:
        fieldnames = ['Cpu', 'RAM', 'Procesess','storage_devices']
        write_csv = csv.DictWriter(write_csv, delimiter=',',fieldnames = fieldnames)
        write_csv.writeheader()
        
        write_csv.writerow(data)

    
exporters= {
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

def temp_save_local(local_intance):
    local_data = local_intance
    history = load_history()
    history.append(local_data)
    save_history(history)
    

def temp_save_api(dic_api):
    API_url = dic_api
    history = load_history()
    history.append(API_url)
    save_history(history)



def generate_report(format, output):
    output_path = get_output_path(output)
    export = exporters.get(format)
    history = load_history()
    if history:
        export(history, output_path)
        os.remove(temp_json) # esto remuve el archivo temporal cada vez que se crea un reporte
        logger.info("Report successfully created.")
    else:
        logger.error(f"The report has not been created because nothing has been audited yet.")
