import pytest, sys, json, csv
from pathlib import Path
from unittest.mock import patch

#esto basicamente toma como referencia el archivo actual y sale primero a test y despeues al current working directorury, despues se agrega a la lista sys.path para que el import funcione
audit_path = Path(__file__).resolve().parent.parent
sys.path.append(str(audit_path))
from src.reports import save_csv, save_json, generate_report, get_output_path

def test_save_json(tmp_path):

    test_data = [
        ("17", "8"),
        {'Pm': 134244, 'cpu': 421.42},
        ("100", "400")

    ]
    output_dir = tmp_path
    save_json(datos=test_data, output_path=output_dir)
    
    expected_file = output_dir / "report_JSON.json"



    assert expected_file.exists(), "El archivo JSON no fue creado."

    with open(expected_file, mode='r', encoding='utf-8') as jf:
        content = json.load(jf)
    assert content["Cpu: "] == "17"
    assert content["Ram: "] == "8"
    assert content["Procesess: "] == {'Pm': 134244, 'cpu': 421.42}
    assert content["StorageSpaceUsed: "] == "100"
    assert content["StorageSpaceRemaining: "] == "400"



def test_save_csv(tmp_path):
    test_data = [
        ("17", "8"),
        {'Pm': 134244, 'cpu': 421.42},
        ("100", "400")

    ]
    output_dir = tmp_path
    save_csv(datos=test_data, output_path=output_dir)
    expected_file = output_dir / "report_CSV.csv"
    assert expected_file.exists()

    with open(expected_file, mode='r') as cf:
        content = csv.DictReader(cf)
        rows = list(content)
    assert len(rows)== 1
    first_row = rows[0]
    assert first_row["Cpu"] == "17"
    assert first_row["RAM"] == "8"
    assert first_row["Procesess"] == "{'Pm': 134244, 'cpu': 421.42}"
    assert first_row["StorageSpaceUsed"] == "100"
    assert first_row["StorageSpaceRemaining"] == "400"

def test_get_output_path(tmp_path):

    test_folder = "./reports/"
    
    expected_path = tmp_path / test_folder
    
    path_geted = get_output_path(test_folder, base_path=tmp_path)


    assert path_geted == expected_path

    assert expected_path.exists()
    assert expected_path.is_dir()

'''def test_generate_report():
    test_format_1 = "json"
    test_format_2 = "csv"
    test_output = "./reports/"
    generate_report(format=test_format_1, output=test_format)
    generate_report(format=test_format_2, output=test_output)
    '''

