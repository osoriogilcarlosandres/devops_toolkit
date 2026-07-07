import yaml, os, logging, platform
from pathlib import Path 
from dotenv import load_dotenv, dotenv_values

logger = logging.getLogger(__name__)

base_path = Path(__file__).resolve().parent.parent
config_path = Path(base_path) / "config\\config.yaml"
env_path = Path(base_path) / ".env"

def load_yaml_config(path = config_path ):

    path = Path(path)

    if not path.exists():
        logger.error(f"The file was not found")
        raise FileNotFoundError(f"{path} was not found")
    with open(path, mode="r", encoding="utf-8") as yaml_file:
        data = yaml.safe_load(yaml_file)
    if data is None:
        
        logger.warning(f"The file was found but is empty")
        data={}
    return data

def load_env_config(path=env_path):

    load_dotenv(dotenv_path=path)

    env_config = {
        "SLACK_WEBHOOK_URL": os.getenv("SLACK_WEBHOOK_URL"),
        "DISCORD_WEBHOOK_URL": os.getenv("DISCORD_WEBHOOK_URL"),
    }
    return env_config

def get_config():
    yaml_config = load_yaml_config()
    env_config = load_env_config()

    config = {
        **yaml_config,
        "secrets": env_config,
    }
    return config


def get_current_os():
    system = platform.system().lower()
    return system



def get_command(action, config=None):
    if config is None:
        config = get_config()
    
    current_os = get_current_os()
    


    os_commands = config["Commands"][current_os]
    return os_commands["shell"], os_commands[action]

    
if __name__ == "__main__":
    import json
    print(json.dumps(get_config(), indent=2, default=str))