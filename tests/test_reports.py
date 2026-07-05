import pytest, sys, json, csv
from pathlib import Path
from unittest.mock import patch

#esto basicamente toma como referencia el archivo actual y sale primero a test y despeues al current working directorury, despues se agrega a la lista sys.path para que el import funcione
audit_path = Path(__file__).resolve().parent.parent
sys.path.append(str(audit_path))
from src.reports import save_csv, save_json, generate_report, get_output_path, unpack_data

def test_save_json(tmp_path):

    test_data = [
        ("17", "8"),
        {'Pm': 134244, 'cpu': 421.42},
        ("100", "400")

    ]
    output_dir = tmp_path
    unpacked = unpack_data(test_data)
    save_json(data=unpacked, output_path=output_dir)
    
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
    unpacked = unpack_data(test_data)
    csv_data = {
        'Cpu': unpacked['Cpu: '],
        'RAM': unpacked['Ram: '],
        'Procesess': unpacked['Procesess: '],
        'StorageSpaceUsed': unpacked['StorageSpaceUsed: '],
        'StorageSpaceRemaining': unpacked['StorageSpaceRemaining: '],
    }
    save_csv(data=csv_data, output_path=output_dir)
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


@patch("src.reports.run_raw_audit")
def test_generate_report_json(mock_run_raw_audit, tmp_path):
    mock_run_raw_audit.return_value = [
        ("17", "8"),
        [{"name": "python", "cpu": 3.5}],
        ("100", "400"),
    ]

    output_path = tmp_path / "reports"
    generate_report(format="json", output=str(output_path))

    expected_file = output_path / "report_JSON.json"
    assert expected_file.exists()

    with open(expected_file, mode="r", encoding="utf-8") as jf:
        content = json.load(jf)

    assert content["Cpu: "] == "17"
    assert content["Ram: "] == "8"
    assert content["Procesess: "] == [{"name": "python", "cpu": 3.5}]
    assert content["StorageSpaceUsed: "] == "100"
    assert content["StorageSpaceRemaining: "] == "400"


@patch("src.reports.run_raw_audit")
def test_generate_report_csv(mock_run_raw_audit, tmp_path):
    mock_run_raw_audit.return_value = [
        ("17", "8"),
        [{"name": "python", "cpu": 3.5}],
        ("100", "400"),
    ]

    output_path = tmp_path / "reports"
    # El nuevo flujo separa el unpacking y la exportación CSV; construimos los datos esperados
    unpacked = unpack_data(mock_run_raw_audit.return_value)
    csv_data = {
        'Cpu': unpacked['Cpu: '],
        'RAM': unpacked['Ram: '],
        'Procesess': str(unpacked['Procesess: ']),
        'StorageSpaceUsed': unpacked['StorageSpaceUsed: '],
        'StorageSpaceRemaining': unpacked['StorageSpaceRemaining: '],
    }
    # ensure output directory exists (save_csv does not create dirs)
    output_path.mkdir(parents=True, exist_ok=True)
    save_csv(data=csv_data, output_path=output_path)

    expected_file = output_path / "report_CSV.csv"
    assert expected_file.exists()

    with open(expected_file, mode="r", encoding="utf-8") as cf:
        rows = list(csv.DictReader(cf))

    assert len(rows) == 1
    assert rows[0]["Cpu"] == "17"
    assert rows[0]["RAM"] == "8"
    assert rows[0]["Procesess"] == "[{'name': 'python', 'cpu': 3.5}]"
    assert rows[0]["StorageSpaceUsed"] == "100"
    assert rows[0]["StorageSpaceRemaining"] == "400"

