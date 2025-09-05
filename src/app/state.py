import json
import logging
from pathlib import Path
from typing import Dict

logger = logging.getLogger("stock-alerts")


def load_state(path: Path) -> Dict[str, str]:
    """
    Load the last alert "state" from a JSON file.

    The state keeps track of which direction (up/down/none) a stock
    has already triggered an alert for. This prevents sending duplicate
    notifications every run.
    """
    # TODO: Prüfen, ob die Datei existiert und deren Inhalt als JSON laden
    # TODO: Bei Erfolg den geladenen Zustand zurückgeben und einen Debug-Log schreiben
    # TODO: Bei Fehlern eine Warnung loggen und ein leeres Dict zurückgeben
    # pass

    if not path.exists():
        logger.debug(f"State file {path} does not exist. Returning empty dict.")
        return {}

    try:
        with path.open("r", encoding="utf-8") as f:
            state = json.load(f)
        if not isinstance(state, dict): # Sicherstellen, dass der Inhalt ein dict ist (falls jemand die Datei manuell kaputt gemacht hat
            logger.warning(f"State file {path} does not contain a dict. Resetting.")
            return {}
        logger.debug(f"Loaded state from {path}: {state}")
        return state
    except Exception as e:
        logger.warning(f"Failed to load state from {path}: {e}")
        return {}




def save_state(path: Path, state: Dict[str, str]) -> None:
    """
    Save the current alert state to disk.
    """
    # TODO: Den Zustand als JSON (UTF-8) in die Datei schreiben
    # TODO: Einen Debug-Log mit dem gespeicherten Zustand ausgeben
    #pass
    try:
        with path.open("w", encoding="utf-8") as f:
            json.dump(state, f, ensure_ascii=False, indent=2)
        logger.debug(f"Saved state to {path}: {state}")
    except Exception as e:
        logger.error(f"Failed to save state to {path}: {e}")


####### Beispielverwendung #######


state_path = Path("config.json")

# Laden
state = load_state(state_path)
print("Aktueller State:", state)

# Ändern
#state["AAPL"] = "down"
#state["TSLA"] = "down"

# Speichern
#save_state(state_path, state)