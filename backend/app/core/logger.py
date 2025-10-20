import logging
from logging.handlers import RotatingFileHandler
import sys

# -------------------------
# Configuración básica del logger
# -------------------------
LOG_FILE = "app.log"

logger = logging.getLogger("eshop_logger")
logger.setLevel(logging.DEBUG)

# Rotating File Handler para no crecer indefinidamente
file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
file_handler.setLevel(logging.DEBUG)

# Stream Handler para consola
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setLevel(logging.INFO)

# Formato de los logs
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Agregar handlers
logger.addHandler(file_handler)
logger.addHandler(console_handler)
