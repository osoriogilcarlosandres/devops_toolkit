import requests, logging, json
from src.config_parser import get_config
from src.reports import load_history
logger = logging.getLogger(__name__)
config = get_config()
env_config = config["secrets"]

def not_slack(history):
    Slack_weebhook_URL = env_config["SLACK_WEBHOOK_URL"]
    payload = {"text": str(history)}
    headers = {"Content-Type": "application/json"}
    respuesta =requests.post(Slack_weebhook_URL, data=json.dumps(payload), headers=headers)
    if respuesta.status_code == 200:
        logger.info("Succesful notificantion!")
    else:
        logger.critical(f"status code: {respuesta.status_code}")


def not_discord(history):
    Discord_weebhook_URL = env_config["DISCORD_WEBHOOK_URL"]
    payload = {"content": history}
    respuesta =requests.post(Discord_weebhook_URL, json=payload)
    if respuesta.status_code == 204:
        logger.info("Succesful notificantion!")
    else:
        logger.critical(f"status code: {respuesta.status_code}")
notifyFn = {
    "slack": not_slack,
    "discord": not_discord
    }   


def send_notification(channel = None, conditions = None):
    msg = ""
    max_proceses = 1
    if channel is None:
        if conditions["status"] == "OK":
            msg = "Everything is OK. Wuuuuu!"
            
        else:
            list_warnings = "\n".join(conditions["Alerts_found"])
            msg = f"In this audit instance\n{conditions['Metrics']} this warnings where found: \n {list_warnings}"
            
    
        not_discord(msg)
        not_slack(msg)
    
    if not channel is None:
        history = load_history()
        for elements in history:
           if isinstance(elements, dict) and "Processes" in elements:
            elements["Processes"] = elements["Processes"][:max_proceses]
        
        channel_func = notifyFn.get(channel)
        #history is modified bc is a referens
        channel_func(str(history))