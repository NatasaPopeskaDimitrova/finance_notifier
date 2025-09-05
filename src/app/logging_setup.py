import logging
from logging.handlers import RotatingFileHandler
from typing import Dict, Any


def setup_logging(cfg_log: Dict[str, Any]) -> logging.Logger:
    """
    Configure and return the central logger for the app.

    Features:
      - Log level configurable via config (DEBUG, INFO, WARNING, …)
      - Always logs to console (stdout)
      - Optional rotating file handler for persistent logs:
          * File size limit (maxBytes)
          * Number of backups (backupCount)
          * UTF-8 encoding for international characters

    Args:
        cfg_log: Logging configuration dictionary. Expected keys:
            - "level": str - log level (e.g. "INFO", "DEBUG")
            - "to_file": bool - whether to also log to a file
            - "file_path": str - log filename (default "alerts.log")
            - "file_max_bytes": int - max file size before rotation
            - "file_backup_count": int - number of rotated backups to keep

    Returns:
        logging.Logger: Configured logger instance named "stock-alerts".
    """
    # TODO: Resolve log level from cfg_log (fallback to INFO)
    level_name = str(cfg_log.get("level", "INFO")).upper()
    print(f"level_name ={level_name}")
    level = getattr(logging, level_name, logging.INFO)
    print(f"level ={level}")

    # TODO: Obtain the named logger "stock-alerts" and set its level
    logger = logging.getLogger("stock-alerts")
    logger.setLevel(level)
    logger.propagate = False  # keine Doppel-Logs über Root-Logger

    # TODO: Clear any existing handlers to avoid duplicates # Vorhandene Handler entfernen
    logger.handlers.clear()
    print(f"logger ={logger}")

    # TODO: Create a Formatter with timestamp, level and message
    fmt = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        "%Y-%m-%d %H:%M:%S",
    )

    # TODO: Configure a StreamHandler for Console output, apply formatter and add it
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(fmt)
    logger.addHandler(ch)
    print(f"ch ={ch}")

    # TODO: If cfg_log["to_file"] is true, create a RotatingFileHandler with provided settings
    if cfg_log.get("to_file", False):
        file_path = cfg_log.get("file_path", "alerts.log")
        print(f"file_path ={file_path}")
        max_bytes = int(cfg_log.get("file_max_bytes", 1_000_000))
        print(f"max_bytes ={max_bytes}")
        backup_count = int(cfg_log.get("file_backup_count", 3))
        print(f"backup_count ={backup_count}")
        fh = RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        fh.setLevel(level)
        fh.setFormatter(fmt)
        print(f"fh ={fh}")
        logger.addHandler(fh)
     # TODO: Log a debug message summarizing the final logging setup
    logger.debug(
        "Logging initialized: level=%s, to_file=%s, file=%s",
        level_name, cfg_log.get("to_file", False), cfg_log.get("file_path")
    )

    # TODO: Return the configured logger
    return logger


################## Aufruf-Beispiel (z. B. in core.py): ######################

#from .logging_setup import setup_logging
#from .utils import mask_secret

logger = setup_logging({
    "level": "DEBUG",
    "to_file": True,
    "file_path": "alerts.log",
    "file_max_bytes": 2_000_000,
    "file_backup_count": 5,
})
print(f"logger={logger}")
