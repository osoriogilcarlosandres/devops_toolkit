import pytest, sys, json, csv
from pathlib import Path
from unittest.mock import patch, MagicMock

audit_path = Path(__file__).resolve().parent.parent
sys.path.append(str(audit_path))

from src.reports import (save_csv, save_json, generate_report, get_output_path,
                         load_history)

def test_load_history():
    result = load_history()
    assert result == 
def test_save_json(tmp_path):
    test_data = [{"Cpu_Usage": 12.5, "RAM_Usage": 45.8}]
    output_dir = tmp_path
    
    save_json(data=test_data, output_path=output_dir)
    expected_file = output_dir / "report_JSON.json"

    assert expected_file.exists(), "El archivo JSON no fue creado."

    with open(expected_file, mode='r', encoding='utf-8') as jf:
        content = json.load(jf)
        
    assert content == test_data

def test_save_csv(tmp_path):
    
    test_data = {
        'Cpu': 12.5,
        'RAM': 45.8,
        'Procesess': "[{'Name': 'python'}]",
        'storage_devices': "[{'Device': 'C:'}]"
    }
    output_dir = tmp_path
    
    save_csv(data=test_data, output_path=output_dir)
    expected_file = output_dir / "report_CSV.csv"
    
    assert expected_file.exists(), "El archivo CSV no fue creado."

    with open(expected_file, mode='r') as cf:
        content = csv.DictReader(cf)
        rows = list(content)
        
    assert len(rows) == 1
    first_row = rows[0]
    assert first_row["Cpu"] == "12.5"
    assert first_row["RAM"] == "45.8"
    assert first_row["Procesess"] == "[{'Name': 'python'}]"

def test_get_output_path(tmp_path):
    test_folder = "reports_test"
    expected_path = tmp_path / test_folder
    
    path_geted = get_output_path(test_folder, base_path=tmp_path)

    assert path_geted == expected_path
    assert expected_path.exists()
    assert expected_path.is_dir()

@patch("src.reports.load_history")
@patch("src.reports.os.remove")
def test_generate_report_json(mock_os_remove, mock_load_history, tmp_path):
    
    mock_load_history.return_value = [
        {"Cpu": 17, "RAM": 8, "Procesess": [], "storage_devices": []}
    ]

    output_path = tmp_path / "reports"
    generate_report(format="json", output=str(output_path))

    expected_file = output_path / "report_JSON.json"
    assert expected_file.exists()

    with open(expected_file, mode="r", encoding="utf-8") as jf:
        content = json.load(jf)

    assert len(content) == 1
    assert content[0]["Cpu"] == 17
    
    mock_os_remove.assert_called_once()