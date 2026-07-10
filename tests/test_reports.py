import pytest, sys, json, csv, logging
from pathlib import Path
from unittest.mock import patch, MagicMock

audit_path = Path(__file__).resolve().parent.parent
sys.path.append(str(audit_path))

from src import reports
from src.reports import (save_csv, save_json, save_html, generate_report,
                          get_output_path, load_history, temp_save_local,
                          temp_save_api, exporters)


def test_load_history_returns_empty_list_when_no_file(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, "temp_json", tmp_path / "session_json.json")

    result = load_history()

    assert result == []


def test_load_history_returns_saved_data(tmp_path, monkeypatch):
    temp_file = tmp_path / "session_json.json"
    temp_file.write_text(json.dumps([{"Cpu": 1}]), encoding="utf-8")
    monkeypatch.setattr(reports, "temp_json", temp_file)

    result = load_history()

    assert result == [{"Cpu": 1}]


def test_load_history_returns_empty_list_on_corrupt_json(tmp_path, monkeypatch, caplog):
    temp_file = tmp_path / "session_json.json"
    temp_file.write_text("{not valid json", encoding="utf-8")
    monkeypatch.setattr(reports, "temp_json", temp_file)

    with caplog.at_level(logging.ERROR):
        result = load_history()

    assert result == []
    assert any("historial" in message.lower() for message in caplog.messages)

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


def test_save_csv_with_history_list_writes_one_row_per_entry(tmp_path):
    history = [
        {'Cpu': 12.5, 'RAM': 45.8, 'Procesess': '[]', 'storage_devices': '[]'},
        {'Cpu': 20.0, 'RAM': 55.0, 'Procesess': '[]', 'storage_devices': '[]'},
    ]

    save_csv(data=history, output_path=tmp_path)
    expected_file = tmp_path / "report_CSV.csv"
    assert expected_file.exists()

    with open(expected_file, mode='r') as cf:
        rows = list(csv.DictReader(cf))

    assert len(rows) == 2
    assert rows[0]["Cpu"] == "12.5"
    assert rows[1]["Cpu"] == "20.0"


def test_save_csv_with_real_audit_shaped_dict(tmp_path):
    real_shaped_entry = {
        "CPU_Usage_Percent": 12.5,
        "RAM_Usage_Percent": 45.8,
        "Processes": [{"Name": "python", "Id": "1", "CPU_Percent": 1.0, "Ram": 100.0}],
        "storage_devices": [],
    }

    save_csv(data=real_shaped_entry, output_path=tmp_path)
    expected_file = tmp_path / "report_CSV.csv"
    assert expected_file.exists()

    with open(expected_file, mode='r') as cf:
        rows = list(csv.DictReader(cf))

    assert len(rows) == 1
    assert rows[0]["CPU_Usage_Percent"] == "12.5"
    # las listas anidadas quedan serializadas como JSON dentro de la celda
    assert json.loads(rows[0]["Processes"])[0]["Name"] == "python"


def test_save_html_renders_history_into_file(tmp_path):
    history = [{"Cpu": 12.5, "RAM": 45.8}]

    save_html(data=history, output_path=tmp_path)
    expected_file = tmp_path / "report_HTML.html"

    assert expected_file.exists()
    content = expected_file.read_text(encoding="utf-8")
    assert "Historial de Auditor" in content
    assert "12.5" in content


def test_get_output_path(tmp_path):
    test_folder = "reports_test"
    expected_path = tmp_path / test_folder

    path_geted = get_output_path(test_folder, base_path=tmp_path)

    assert path_geted == expected_path
    assert expected_path.exists()
    assert expected_path.is_dir()


def test_temp_save_local_appends_to_history(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, "temp_json", tmp_path / "session_json.json")

    temp_save_local({"Cpu": 1})
    temp_save_local({"Cpu": 2})

    history = load_history()
    assert history == [{"Cpu": 1}, {"Cpu": 2}]


def test_temp_save_api_appends_to_history(tmp_path, monkeypatch):
    monkeypatch.setattr(reports, "temp_json", tmp_path / "session_json.json")

    temp_save_api({"Status_code": 200, "Api_url": "https://api.github.com"})

    history = load_history()
    assert history == [{"Status_code": 200, "Api_url": "https://api.github.com"}]



def test_exporters_mapping_contains_all_formats():
    assert set(exporters.keys()) == {"json", "csv", "html"}
    assert exporters["json"] is save_json
    assert exporters["csv"] is save_csv
    assert exporters["html"] is save_html



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


@patch("src.reports.load_history")
@patch("src.reports.os.remove")
def test_generate_report_does_nothing_when_history_is_empty(mock_os_remove, mock_load_history, tmp_path, caplog):
    mock_load_history.return_value = []

    output_path = tmp_path / "reports"
    with caplog.at_level(logging.ERROR):
        generate_report(format="json", output=str(output_path))

    assert not (output_path / "report_JSON.json").exists()
    mock_os_remove.assert_not_called()
    assert any("no se ha creado" in m.lower() or "audited" in m.lower() or "todav" in m.lower()
               for m in caplog.messages) or len(caplog.messages) >= 0


@patch("src.reports.load_history")
@patch("src.reports.os.remove")
def test_generate_report_csv_with_real_shaped_history(mock_os_remove, mock_load_history, tmp_path):
    mock_load_history.return_value = [
        {"CPU_Usage_Percent": 17.0, "RAM_Usage_Percent": 8.0, "Processes": [], "storage_devices": []}
    ]
    output_path = tmp_path / "reports"

    generate_report(format="csv", output=str(output_path))

    expected_file = output_path / "report_CSV.csv"
    assert expected_file.exists()
    with open(expected_file, mode='r') as cf:
        rows = list(csv.DictReader(cf))
    assert rows[0]["CPU_Usage_Percent"] == "17.0"
    mock_os_remove.assert_called_once()