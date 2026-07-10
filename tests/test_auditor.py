import pytest, sys, json, logging
from pathlib import Path
from unittest.mock import patch, MagicMock

# Ajuste de path para importaciones
audit_path = Path(__file__).resolve().parent.parent
sys.path.append(str(audit_path))

from src import auditor
from src.auditor import (
    get_and_deserialize,
    organized_commands,
    get_commands_output,
    get_formated_audit,
    evaluete_conditions,
    evaluete_critical_files,
    audit_api,
    print_on_console,
    run_command,
    local_audit,
)
 
@patch('src.auditor.get_command')
@patch('src.auditor.subprocess.run')
def test_run_command_builds_expected_subprocess_call_bash(mock_subproc_run, mock_get_command):
    mock_get_command.return_value = ("bash", "echo hola")
    mock_result = MagicMock(stdout="hola\n")
    mock_subproc_run.return_value = mock_result
 
    result = run_command("Cpu")
 
    mock_get_command.assert_called_once_with("Cpu")
    mock_subproc_run.assert_called_once_with(
        ["bash", "-c", "echo hola"], text=True, capture_output=True, check=True
    )
    assert result is mock_result
 
 
@patch('src.auditor.get_command')
@patch('src.auditor.subprocess.run')
def test_run_command_builds_expected_subprocess_call_powershell(mock_subproc_run, mock_get_command):
    mock_get_command.return_value = ("powershell", "Get-Process")
    mock_result = MagicMock(stdout="[]")
    mock_subproc_run.return_value = mock_result
 
    run_command("Process")
 
    mock_subproc_run.assert_called_once_with(
        ["powershell", "-Command", "Get-Process"], text=True, capture_output=True, check=True
    )
 
 
@patch('src.auditor.run_command')
def test_get_and_deserialize(mock_run_command):
    mock_result = MagicMock()
    mock_result.stdout = '{"CPU_Usage_Percent": "12.5", "RAM_Usage_Percent": "45.8"}'
    mock_run_command.return_value = mock_result
 
    data = get_and_deserialize("Cpu")
 
    assert data == {"CPU_Usage_Percent": "12.5", "RAM_Usage_Percent": "45.8"}
    mock_run_command.assert_called_once_with("Cpu")
 
 
@patch('src.auditor.get_and_deserialize')
def test_get_commands_output_calls_each_metric_once(mock_get_and_deserialize):
    mock_get_and_deserialize.side_effect = [
        {"CPU_Usage_Percent": "10"},
        {"RAM_Usage_Percent": "20"},
        [{"Name": "python"}],
        [{"DeviceID": "/dev/sda1"}],
    ]
 
    result = get_commands_output()
 
    assert result == (
        {"CPU_Usage_Percent": "10"},
        {"RAM_Usage_Percent": "20"},
        [{"Name": "python"}],
        [{"DeviceID": "/dev/sda1"}],
    )
    assert mock_get_and_deserialize.call_args_list == [
        (("Cpu",),), (("Ram",),), (("Process",),), (("Storage",),)
    ]

@patch('src.auditor.get_commands_output')
def test_organized_commands(mock_get_commands):
    mock_get_commands.return_value = (
        {"CPU_Usage_Percent": "15.5"},
        {"RAM_Usage_Percent": "60.2"},
        [{"Name": "python", "Id": "101", "CPU_Percent": "5.0", "RAM": "2048"}],
        [{"DeviceID": "/dev/sda1", "Size": "500", "Used": "200", "Free": "300"}]
    )
 
    result = organized_commands()
 
    assert result["CPU_Usage_Percent"] == 15.5
    assert result["RAM_Usage_Percent"] == 60.2
    assert len(result["Processes"]) == 1
    assert result["Processes"][0]["Name"] == "python"
    assert result["Processes"][0]["Ram"] == 2048.0
 
    # storage_USED <- Used, storage_FREE <- Free, storage_SIZE <- Size
    assert result["storage_devices"][0]["storage_USED"] == 200.0
    assert result["storage_devices"][0]["storage_FREE"] == 300.0
    assert result["storage_devices"][0]["storage_SIZE"] == 500.0
 
 

def _base_audit_dict(cpu=10.0, ram=10.0, free_pct=90.0):
    total = 100.0
    free = total * (free_pct / 100.0)
    return {
        "CPU_Usage_Percent": cpu,
        "RAM_Usage_Percent": ram,
        "storage_devices": [
            {"storage_NAME": "/dev/sda1", "storage_USED": total - free,
             "storage_FREE": free, "storage_SIZE": total}
        ],
    }
 
 
def test_evaluete_conditions_ok_status(monkeypatch):
    monkeypatch.setattr(auditor, "config", {
        "ConditionsToEvaluete": {"CpuMax": 90, "RamMax": 80, "FreeStorageMin": 20}
    })
    data = _base_audit_dict(cpu=10.0, ram=10.0, free_pct=90.0)
 
    result = evaluete_conditions(data, "formatted-metrics")
 
    assert result["status"] == "OK"
    assert result["Alerts_found"] == []
    assert result["Metrics"] == "formatted-metrics"
 
 
def test_evaluete_conditions_storage_warning(monkeypatch):
    monkeypatch.setattr(auditor, "config", {
        "ConditionsToEvaluete": {"CpuMax": 90, "RamMax": 80, "FreeStorageMin": 50}
    })
    # Solo 10% libre, por debajo del mínimo configurado (50%)
    data = _base_audit_dict(cpu=10.0, ram=10.0, free_pct=10.0)
 
    result = evaluete_conditions(data, "formatted-metrics")
 
    assert result["status"] == "DANGER"
    assert len(result["Alerts_found"]) == 1
    assert "/dev/sda1" in result["Alerts_found"][0]
 
 
def test_evaluete_conditions_cpu_warning_generates_alert(monkeypatch):
    monkeypatch.setattr(auditor, "config", {
        "ConditionsToEvaluete": {"CpuMax": 50, "RamMax": 80, "FreeStorageMin": 10}
    })
    data = _base_audit_dict(cpu=95.0, ram=10.0, free_pct=90.0)
 
    result = evaluete_conditions(data, "formatted-metrics")
 
    assert result["status"] == "DANGER"
    assert len(result["Alerts_found"]) == 1
    assert "95.000" in result["Alerts_found"][0]
 
 
def test_evaluete_conditions_no_storage_devices_does_not_crash(monkeypatch):
    monkeypatch.setattr(auditor, "config", {
        "ConditionsToEvaluete": {"CpuMax": 90, "RamMax": 80, "FreeStorageMin": 20}
    })
    data = {"CPU_Usage_Percent": 10.0, "RAM_Usage_Percent": 10.0, "storage_devices": []}
 
    result = evaluete_conditions(data, "formatted-metrics")
 
    assert result["status"] == "OK"
    assert result["Alerts_found"] == []

def test_get_formated_audit_includes_cpu_and_ram_summary():
    data = {
        "CPU_Usage_Percent": 12.3456,
        "RAM_Usage_Percent": 45.6789,
        "Processes": [{"Name": "python", "Id": "1", "CPU_Percent": 5.0, "Ram": 1024.0}],
        "storage_devices": [
            {"storage_NAME": "/dev/sda1", "storage_USED": 1.0, "storage_FREE": 2.0, "storage_SIZE": 3.0}
        ],
    }
 
    result = get_formated_audit(data)
 
    assert "Cpu: 12.346% Ram: 45.679%" in result
    assert "python" in result
    assert "/dev/sda1" in result
 
 
def test_get_formated_audit_multiple_storage_devices_header_is_correct():
    data = {
        "CPU_Usage_Percent": 1.0,
        "RAM_Usage_Percent": 1.0,
        "Processes": [],
        "storage_devices": [
            {"storage_NAME": "/dev/sda1", "storage_USED": 1.0, "storage_FREE": 2.0, "storage_SIZE": 10.0},
            {"storage_NAME": "/dev/sda2", "storage_USED": 3.0, "storage_FREE": 4.0, "storage_SIZE": 20.0},
        ],
    }
 
    result = get_formated_audit(data)
 
    # "Devices: " ahora es el encabezado del bloque, y ambos dispositivos
    # aparecen despues, cada uno en su propia linea.
    assert "Devices: \nDevice: /dev/sda1" in result
    assert "Device: /dev/sda2" in result
    assert "Devices: \nDevice: /dev/sda2" not in result

def test_evaluete_critical_files_logs_found_and_missing(monkeypatch, caplog):
    # "auditor.py" existe de verdad dentro del arbol del proyecto (src/auditor.py),
    # asi que rglob lo encontrara; "no_existe.txt" no existe.
    monkeypatch.setattr(auditor, "config", {"critical_files": ["auditor.py", "no_existe.txt"]})
 
    with caplog.at_level(logging.INFO):
        evaluete_critical_files()
 
    messages = " | ".join(caplog.messages)
    assert "auditor.py" in messages
    assert "no_existe.txt" in messages
 

@patch("src.auditor.requests.get")
@patch("src.auditor.temp_save_api")
def test_audit_api_success(mock_temp_save, mock_requests_get):
    fake_response = MagicMock()
    fake_response.status_code = 200
    mock_requests_get.return_value = fake_response
 
    audit_api("https://api.github.com")
 
    mock_requests_get.assert_called_once()
    mock_temp_save.assert_called_once()
    args, _ = mock_temp_save.call_args
    assert args[0]["Status_code"] == 200
    assert args[0]["Api_url"] == "https://api.github.com"
 
 
@patch("src.auditor.requests.get")
@patch("src.auditor.temp_save_api")
def test_audit_api_server_error_is_logged(mock_temp_save, mock_requests_get, caplog):
    fake_response = MagicMock()
    fake_response.status_code = 503
    mock_requests_get.return_value = fake_response
 
    with caplog.at_level(logging.ERROR):
        audit_api("https://api.example.com")
 
    assert any("FAIL" in message for message in caplog.messages)
    mock_temp_save.assert_called_once()
    args, _ = mock_temp_save.call_args
    assert args[0]["Status_code"] == 503
 
 
def test_print_on_console():
    result = print_on_console(200, 0.123, "https://api.github.com")
    assert result == "Audited API: https://api.github.com. Status code: 200. Lantency: 0.123."

@patch("src.auditor.send_notification")
@patch("src.auditor.temp_save_local")
@patch("src.auditor.evaluete_critical_files")
@patch("src.auditor.evaluete_conditions")
@patch("src.auditor.get_formated_audit")
@patch("src.auditor.organized_commands")
def test_local_audit_calls_every_step_in_order(
    mock_organized, mock_formatted, mock_evaluete, mock_critical, mock_save, mock_notify
):
    mock_organized.return_value = {"CPU_Usage_Percent": 1.0}
    mock_formatted.return_value = "formatted"
    mock_evaluete.return_value = {"status": "OK", "Alerts_found": [], "Metrics": "formatted"}
 
    local_audit()
 
    mock_organized.assert_called_once()
    mock_formatted.assert_called_once_with({"CPU_Usage_Percent": 1.0})
    mock_evaluete.assert_called_once_with({"CPU_Usage_Percent": 1.0}, "formatted")
    mock_critical.assert_called_once()
    mock_save.assert_called_once_with({"CPU_Usage_Percent": 1.0})
    mock_notify.assert_called_once_with(conditions={"status": "OK", "Alerts_found": [], "Metrics": "formatted"})
 