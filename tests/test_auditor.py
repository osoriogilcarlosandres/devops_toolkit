import pytest, sys
from pathlib import Path
from unittest.mock import patch

audit_path = Path(__file__).resolve().parent.parent
sys.path.append(str(audit_path))
from src.auditor import get_cpu_ram, get_most_process, get_storage_space, run_formated_audit, run_raw_audit


@patch(target='src.auditor.subprocess.run')
def test_get_cpu_ram(mock_subprocess_run):
    # esta clase le da el stdout a subprocces.run en lugar del verdadero
    class FalseConsol:
        stdout = "Texto de relleno... CPU: 12.5% y RAM: 45,8 bytes..."
    
    mock_subprocess_run.return_value = FalseConsol

    result = get_cpu_ram()
    assert result == ['12.5', '45,8']
    mock_subprocess_run.assert_called_once()


@patch(target='src.auditor.subprocess.run')
def test_get_most_process(mock_subprocess_run):
    
    class FalseConsol:
        stdout =  ("  1001   2045   1200     24    3.5    1   0    /usr/bin/python3\n" 
                   "     0      1      0      0           0   0    launchd")

    mock_subprocess_run.return_value = FalseConsol
    #get_most_process() devuelve una lista de diccionarios
    result = get_most_process()
    
    assert result == [{
        "handles": 1001,
        "npm": 2045,
        "pm_kb": 1200,
        "ws_kb": 24,
        "cpu": 3.5,
        "id": 1,
        "name": "/usr/bin/python3"
    },

    {
        "handles": 0,
        "npm": 1,
        "pm_kb": 0,
        "ws_kb": 0,
        "cpu": 0.0,
        "id": 0,
        "name": "launchd"        
    }]
    assert len(result) == 2
    mock_subprocess_run.assert_called_once()


@patch(target='src.auditor.subprocess.run')
def test_get_storage_space(mock_subprocess_run):
    class FalseConsol:
        stdout = "Storage space usage: 1843.2 GB has been successfully allocated. " \
        "Remainder storage space: 204.8 GB is currently free and available for system operations."
    
    mock_subprocess_run.return_value = FalseConsol

    result = get_storage_space()
    
    assert result==['1843.2', '204.8']


@patch(target='src.auditor.subprocess.run')
def test_run_formated_audit(mock_subprocess_run):
    
    class False_get_cpu_ram():
        stdout = "Texto de relleno... CPU: 12.5% y RAM: 45,8 bytes..."
    


    class False_get_most_process():
        stdout =  ("  1001   2045   1200     24    3.5    1   0    /usr/bin/python3\n" 
                   "     0      1      0      0           0   0    launchd")



    class False_get_storage_space:
        stdout = (
            "Storage space usage: 1843.2 GB has been successfully allocated. "
            "Remainder storage space: 204.8 GB is currently free and available for system operations."
        )

    mock_subprocess_run.side_effect = [
        False_get_cpu_ram(),
        False_get_most_process(),
        False_get_storage_space(),
    ]

    result = run_formated_audit()
    
    assert result == """Cpu: 12.5 Ram: 45,8

Most consuming processes by cpu:

  --Name: /usr/bin/python3   | Cpu: 3.5 KB | ram: 1200 KB
  --Name: launchd   | Cpu: 0.0 KB | ram: 0  KB

Most consuming processes by ram:

  --Name: /usr/bin/python3   | Cpu: 3.5 KB | ram: 1200 KB
  --Name: launchd   | Cpu: 0.0 KB | ram: 0  KB

Storage used: 1843.2GB | Storage remaining: 204.8GB"""




@patch(target='src.auditor.subprocess.run')
def test_run_raw_audit_get_cpu_ram(mock_subprocess_run):
    class False_get_cpu_ram():
        stdout = "Texto de relleno... CPU: 12.5% y RAM: 45,8 bytes..."
    


    class False_get_most_process():
        stdout =  ("  1001   2045   1200     24    3.5    1   0    /usr/bin/python3\n" 
                   "     0      1      0      0           0   0    launchd")



    class False_get_storage_space:
        stdout = (
            "Storage space usage: 1843.2 GB has been successfully allocated. "
            "Remainder storage space: 204.8 GB is currently free and available for system operations."
        )

    mock_subprocess_run.side_effect = [
        False_get_cpu_ram(),
        False_get_most_process(),
        False_get_storage_space(),
    ]

    result = run_raw_audit()

    assert result[0] == ['12.5', '45,8']
    assert result[1] == [{
        "handles": 1001,
        "npm": 2045,
        "pm_kb": 1200,
        "ws_kb": 24,
        "cpu": 3.5,
        "id": 1,
        "name": "/usr/bin/python3"
    }, {
        "handles": 0,
        "npm": 1,
        "pm_kb": 0,
        "ws_kb": 0,
        "cpu": 0.0,
        "id": 0,
        "name": "launchd"
    }]
    assert result[2] == ['1843.2', '204.8']
    assert mock_subprocess_run.call_count == 3

    
