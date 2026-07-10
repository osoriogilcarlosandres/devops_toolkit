
DevOps Automation Toolkit

A small CLI toolkit to audit a local machine (CPU, RAM, processes, storage,
critical config files), audit a REST API endpoint, generate reports
(JSON / CSV / HTML), and send notifications to Slack or Discord.

Features


Local system audit: CPU, RAM, top processes, and storage usage via
ps, df, free (Linux) or WMI/CIM cmdlets (Windows).
Config file audit: verifies that critical files (e.g. .env,
config.yaml) exist, are not empty, and don't have overly permissive
file permissions.
API audit: checks a REST endpoint's status code and latency.
Reports: exports the audit history as JSON, CSV, or a rendered HTML
page (via Jinja2).
Notifications: sends a summary to a Slack or Discord webhook.
Logging: timestamped logs at INFO/WARNING/ERROR/CRITICAL levels,
rotated daily, written to logs/app.log.


Installation

bashgit clone <your-repo-url>
cd devops-toolkit
python -m venv venv
source venv/bin/activate   # venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env       # then fill in your own webhook URLs

Usage

bash# Audit the local machine
python main.py audit --target local

# Audit a REST API
python main.py audit --target api --url https://api.github.com

# Generate a report
python main.py report --format json --output ./reports/
python main.py report --format csv  --output ./reports/
python main.py report --format html --output ./reports/

# Send a notification
python main.py notify --channel slack
python main.py notify --channel discord

Configuration

Edit config/config.yaml to adjust the OS-specific audit commands and the
alert thresholds:

yamlConditionsToEvaluete:
  CpuMax: 90
  RamMax: 80
  FreeStorageMin: 20

critical_files:
  - ".env"
  - "config.yaml"
  - "settings.json"

Running tests

bashpytest tests/ -v

Project structure

devops-toolkit/
├── src/\n
│   ├── auditor.py         # Core auditing logic
│   ├── reports.py         # JSON / CSV / HTML report generation
│   ├── notifer.py         # Slack / Discord webhook notifications
│   ├── config_parser.py   # YAML + .env configuration loading
│   └── logger_config.py   # Logging setup (rotating file handler)
├── tests/
│   ├── test_auditor.py
│   └── test_reports.py
├── config/
│   └── config.yaml
├── .env.example
├── requirements.txt
└── main.py

Known limitations


macOS is not currently supported by the local audit commands.
