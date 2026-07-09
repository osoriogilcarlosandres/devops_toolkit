import requests, logging
from config_parser import get_config
logger = logging.getLogger(__name__)
config = get_config()
env_config = config["secrets"]
def not_slack():
    Slack_weebhook_URL = env_config["SLACK_WEBHOOK_URL"]
    requests.post()
    pass
def not_discord():
    Discord_weebhook_URL = env_config["DISCORD_WEBHOOK_URL"]
    data = {"usuario": "juan", "clave": "12345"}
    payload = {"content": data}
    respuesta =requests.post(Discord_weebhook_URL, payload)
    if respuesta.status_code == 204:
        print("les go")
    print(respuesta.status_code)

notifyFn = {
    "slack": not_slack,
    "discord": not_discord
    }   

def set_conditions(conditions):
    
    if conditions["status"] == "OK":
        msg = "Everything is OK. Wuuuuu!"
        return msg
    else:
        list_warnings = "\n".join(conditions["Alerts_found"])
        msg = f"In this audit instance {conditions["Metrics"]} this warnings where found: \n {list_warnings}"
        return msg
def send_notification(channel=None):
    if channel is None:

    #noti = notifyFn.get(channel)
    #noti()