
DevOps Automation Toolkit

A small CLI toolkit to audit a local machine (CPU, RAM, processes, storage,
critical config files), audit a REST API endpoint, generate reports
(JSON / CSV / HTML), and send notifications to Slack or Discord.

The Problem It Solves

In distributed cloud environments or bare-metal setups, 
deploying heavy monitoring agents (like Datadog, Prometheus, 
or New Relic) on every transient instance 
or edge node can be cost-prohibitive or structurally restricted. 

**DevOps Automation Toolkit** solves this by providing an on-demand,
dependency-light health checker that can be injected via CI/CD, cron jobs,
or startup scripts to evaluate OS baselines, 
detect human errors in crucial configuration deployments (e.g., empty `.env` files), 
and report health directly back to modern communication hubs like Slack or Discord.

Architecture & Component Flow

The system operates via a decoupled multi-module flow managed by a single entry point (`main.py`):
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

Known limitations


macOS is not currently supported by the local audit commands.
