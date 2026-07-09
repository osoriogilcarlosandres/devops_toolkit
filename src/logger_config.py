import logging
from logging.handlers import RotatingFileHandler # noqa: F401
from pathlib import Path

#logger.warning("Look at my logger!") "OHHH, loook, i hame my own logger, this is so much fun! "

#formatter for the handlers
my_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
                                 datefmt="%Y-%m-%d %H:%M:%S")

# logger creation
logger = logging.getLogger("")
logger.setLevel(logging.DEBUG)# set minimal log level

# Reduce ruido de librerías externas
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("urllib3.connectionpool").setLevel(logging.WARNING)
logging.getLogger("requests").setLevel(logging.WARNING)

#handlers
console_handler = logging.StreamHandler()
logs_dir = Path(__file__).resolve().parent.parent / "logs"
logs_dir.mkdir(parents=True, exist_ok=True)
file_rotating_handler = RotatingFileHandler(
    filename=logs_dir / "app.log",
    maxBytes=3024,
    backupCount=10)


#asignate formatter to the handlers 
console_handler.setFormatter(my_formatter)
file_rotating_handler.setFormatter(my_formatter)

#append handlers to the logger
logger.addHandler(file_rotating_handler)
logger.addHandler(console_handler)


