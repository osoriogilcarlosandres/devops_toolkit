import json, csv, logging, os
from pathlib import Path
from src.config_parser import get_config
from jinja2 import Template

config = get_config()
logger = logging.getLogger(__name__)
temp_json =  Path(__file__).resolve().parent.parent / "session_json.json"


def load_history(): 
    if not temp_json.exists():
        return[]
    try:
        with open(temp_json, mode='r', encoding="utf-8") as file:
            return json.load(file)
    except (json.JSONDecodeError, IOError) as e:
        logging.error(f"Error reading history {e}")  # Bloque A: Excepciones
        return []


def save_history(data):
 with open(temp_json, mode='w', encoding="utf-8") as file:
     json.dump(data, file, indent=1)


def save_json(data, output_path):
    
    with open(Path(output_path) / "report_JSON.json", mode='w', encoding="utf-8") as write_json:
        json.dump(data, write_json, indent=1)


def save_csv(data, output_path):

    #forces it to be a list
    entries = data if isinstance(data, list) else [data]

    fieldnames = []
    for entry in entries:
        for key in entry.keys():
            if key not in fieldnames:
                fieldnames.append(key)


    with open(Path(output_path) / f"report_CSV.csv", mode='w', encoding='utf-8') as write_csv:
        
        writer = csv.DictWriter(write_csv, delimiter=',', fieldnames = fieldnames, restval='')
        writer.writeheader()
        
        for entry in entries:
            row = {
                key: (json.dumps(value) if isinstance(value, (list, dict)) else value)
                for key, value in entry.items()
            }
            writer.writerow(row)

def save_html(data, output_path):

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>DevOps Audit Report</title>
        <style>
            body { font-family: sans-serif; margin: 30px; background: #f4f6f9; }
            h1 { color: #333; }
            .card { background: white; padding: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }
            pre { background: #272822; color: #f8f8f2; padding: 15px; border-radius: 4px; overflow-x: auto; }
        </style>
    </head>
    <body>
        <h1>Audit History</h1>
        <div class="card">
            <h3>Collected Data:</h3>
            <pre>{{ formated_history }}</pre>
        </div>
    </body>
    </html>
    """
    template = Template(html_template)
    phistory = json.dumps(data, indent=2, ensure_ascii=False)
    html_final = template.render(formated_history=phistory)

    with open(Path(output_path) / "report_HTML.html", mode="w", encoding="utf-8") as f:
        f.write(html_final)


exporters= {
    "json": save_json,
    "csv": save_csv,
    "html": save_html
}


def get_output_path(output, base_path = None):


    if base_path is None:
        base_path = Path(__file__).resolve().parent.parent
    outputpath =  Path(base_path) / output

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
