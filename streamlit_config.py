# streamlit_config.py
# Start in Terminal: streamlit run streamlit_config.py
from __future__ import annotations
import json
from pathlib import Path
from typing import Any, Dict, List
from copy import deepcopy

import streamlit as st

# --- Imports aus deinem Projekt (freiwillig robust gemacht) ---
try:
    from src.app.utils import mask_secret  # relative zum Projekt-Root
except Exception:
    def mask_secret(s: str, visible: int = 2) -> str:
        if not s:
            return ""
        return (s[:visible] + "*" * max(0, len(s) - 2 * visible) + s[-visible:]) if len(s) > 2*visible else "*"*len(s)

try:
    from src.app.ntfy import notify_ntfy
    NTFY_AVAILABLE = True
except Exception:
    NTFY_AVAILABLE = False

# --------------------------------------------------------------
PROJECT_ROOT = Path.cwd()
print(f"PROJECT_ROOT={PROJECT_ROOT}") #C:\Users\natas\Documents\KI\Pyton Schulungen\Data Scientis\finance_notifier Projekt
DEFAULT_CONFIG_PATH = PROJECT_ROOT / "config.json"


DEFAULT_CFG: Dict[str, Any] = {
    "log": {
        "level": "INFO",
        "to_file": False,
        "file_path": "alerts.log",
        "file_max_bytes": 1_000_000,
        "file_backup_count": 3,
    },
    "tickers": ["AAPL"],
    "threshold_pct": 2.5,
    "ntfy": {
        "server": "https://ntfy.sh",
        "topic": "",
    },
    "state_file": "state.json",
    "market_hours": {
        "timezone": "America/New_York",
        "open": "09:30",
        "close": "16:00",
        "weekdays_only": True,
    },
    "test": {},
    "news": {},
}

# ----------##########################  helpers ###################################----------

def load_config(p: Path) -> Dict[str, Any]:
    if not p.exists():
        return DEFAULT_CFG.copy()
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        st.warning(f"Konfiguration konnte nicht gelesen werden ({e}). Es werden Defaults geladen.")
        return DEFAULT_CFG.copy()

def save_config(p: Path, cfg: Dict[str, Any]) -> None:
    p.write_text(json.dumps(cfg, ensure_ascii=False, indent=2), encoding="utf-8")

def to_list(text: str) -> List[str]:
    items = [x.strip() for x in text.replace(";", ",").split(",")]
    return [x for x in items if x]

def validate_cfg(cfg: Dict[str, Any]) -> list[str]:
    errors: list[str] = []
    # log
    levels = {"CRITICAL","ERROR","WARNING","INFO","DEBUG","NOTSET"}
    if cfg["log"]["level"] not in levels:
        errors.append(f"Ungültiges Log-Level: {cfg['log']['level']}")
    for k in ("file_max_bytes","file_backup_count"):
        try:
            cfg["log"][k] = int(cfg["log"][k])
        except Exception:
            errors.append(f"`log.{k}` muss eine Ganzzahl sein.")
    # threshold
    try:
        cfg["threshold_pct"] = float(cfg["threshold_pct"])
    except Exception:
        errors.append("`threshold_pct` muss eine Zahl sein.")
    # ntfy
    if not (isinstance(cfg["ntfy"]["server"], str) and cfg["ntfy"]["server"].startswith("http")):
        errors.append("`ntfy.server` muss mit http/https beginnen.")
    # market hours (rudimentär)
    for k in ("open","close"):
        if not isinstance(cfg["market_hours"].get(k, ""), str) or len(cfg["market_hours"][k].split(":")) != 2:
            errors.append(f"`market_hours.{k}` muss im Format HH:MM sein.")
    return errors


# ---------- ###################### UI ##################################----------
st.set_page_config(page_title="Stock Notifier – Konfiguration", layout="centered")
st.title("⚙️ Stock Notifier – Konfiguration")

with st.sidebar:
    st.header("Datei")
    config_path = st.text_input("Pfad zur config.json", value=str(DEFAULT_CONFIG_PATH))
    config_file = Path(config_path).expanduser().resolve()
    col_sb1, col_sb2 = st.columns(2)
    with col_sb1:
        load_btn = st.button("🔄 Neu laden")
    with col_sb2:
        reset_btn = st.button("↩️ Defaults")
    st.caption(f"Aktuelles Arbeitsverzeichnis: `{PROJECT_ROOT}`")

# Zustand laden / neu laden
if "cfg" not in st.session_state or load_btn:
    st.session_state.cfg = load_config(config_file)

if reset_btn:
    st.session_state.cfg = deepcopy(DEFAULT_CFG)
    st.success("Defaults geladen (noch nicht gespeichert).")

cfg = st.session_state.cfg
print(f"cfg={cfg}")
#{'log':{
#   'level': 'INFO', 
#   'to_file': True, 
#   'file_path': 'alerts.log', 
#   'file_max_bytes': 1000000, 
#   'file_backup_count': 3}, 
#   'ntfy': {
#       'server': 'https://ntfy.sh', 
#       'topic': 'DeinGeheimerTopicName'}, 
#   'tickers': ['AAPL', 'O', 'WPY.F', 'QDVX.DE'], 
#   'threshold_pct': 3.0, 
#   'state_file': 'alert_state.json', 
#   'market_hours': {
#       'enabled': True, 
#       'tz': 'Europe/Berlin', 
#       'start_hour': 8, 
#       'end_hour': 22, 
#       'days_mon_to_fri_only': True}, 
#   'news': {
#       'enabled': True, 
#       'limit': 2, 
#       'lookback_hours': 12, 
#       'lang': 'de', 
#       'country': 'DE'}, 
#   'test': {
#       'enabled': False, 
#       'bypass_market_hours': True, 
#       'force_delta_pct': 4.3, 
#       'dry_run': False}
#}

# ################################--------- Basis ----------################################
st.subheader("Allgemein")
col1, col2 = st.columns(2)
with col1:
    threshold_pct = st.number_input("Schwellenwert in %", value=float(cfg.get("threshold_pct", 2.5)), step=0.1)
with col2:
    state_file = st.text_input("State-Datei", value=str(cfg.get("state_file","state.json")))

# Tickers
st.subheader("Ticker")
tickers_text = st.text_input(
    "Zu überwachende Ticker (durch Komma oder Semikolon getrennt)",
    value=",".join(cfg.get("tickers", []))
)

############################## NTFY #########################################
st.subheader("NTFY (Benachrichtigungen)")
ntfy_server = st.text_input("Server", value=cfg["ntfy"].get("server","https://ntfy.sh"))
ntfy_topic = st.text_input("Topic", value=cfg["ntfy"].get("topic",""), help="Wird beim Loggen maskiert")
st.caption(f"Topic (maskiert): `{mask_secret(ntfy_topic)}`")

########################################### Logging #########################################
st.subheader("Logging")
colA, colB = st.columns(2)
with colA:
    log_level = st.selectbox("Level", ["CRITICAL","ERROR","WARNING","INFO","DEBUG","NOTSET"], index=["CRITICAL","ERROR","WARNING","INFO","DEBUG","NOTSET"].index(cfg["log"].get("level","INFO")))
    log_to_file = st.checkbox("Auch in Datei schreiben", value=bool(cfg["log"].get("to_file", False)))
with colB:
    log_file = st.text_input("Log-Datei", value=cfg["log"].get("file_path","alerts.log"))
    file_max_bytes = st.number_input("Max. Dateigröße (Bytes)", value=int(cfg["log"].get("file_max_bytes", 1_000_000)), step=100_000, min_value=10_000)
    file_backup = st.number_input("Anzahl Backups", value=int(cfg["log"].get("file_backup_count", 3)), step=1, min_value=1)


######################################### Market hours ####################################
st.subheader("Marktzeiten")
mh = cfg.get("market_hours", {})
colM1, colM2, colM3 = st.columns(3)
with colM1:
    mh_tz = st.text_input("Zeitzone (IANA)", value=mh.get("timezone","America/New_York"))
with colM2:
    mh_open = st.text_input("Öffnung (HH:MM)", value=mh.get("open","09:30"))
with colM3:
    mh_close = st.text_input("Schließung (HH:MM)", value=mh.get("close","16:00"))
mh_weekdays = st.checkbox("Nur Wochentage", value=bool(mh.get("weekdays_only", True)))

# --------- Erweiterte Einstellungen ----------
with st.expander("🧪 Erweiterte Einstellungen", expanded=False):
    st.markdown("**Test-Modus**")
    colT1, colT2, colT3 = st.columns(3)
    with colT1:
        test_enabled = st.checkbox("Test aktiv", value=bool(cfg["test"].get("enabled", False)))
    with colT2:
        test_dry = st.checkbox("Dry-Run (ohne Senden)", value=bool(cfg["test"].get("dry_run", False)))
    with colT3:
        test_sim = st.checkbox("Kursänderung simulieren", value=bool(cfg["test"].get("simulate_change", False)))
    demo_msg = st.text_input("Demo-Message", value=cfg["test"].get("demo_message","Dies ist eine Demo-Benachrichtigung."))

    st.markdown("---")
    st.markdown("**News**")
    news_enabled = st.checkbox("News verwenden", value=bool(cfg["news"].get("enabled", False)))
    colN1, colN2 = st.columns(2)
    with colN1:
        news_provider = st.selectbox("Provider", ["yfinance","custom"], index=["yfinance","custom"].index(cfg["news"].get("provider","yfinance")))
        news_language = st.text_input("Sprache (ISO-Code)", value=cfg["news"].get("language","de"))
    with colN2:
        news_query = st.text_input("Query/Filter", value=cfg["news"].get("query",""))
        news_max = st.number_input("Max. Meldungen", value=int(cfg["news"].get("max_items", 5)), min_value=1, step=1)

st.markdown("---")
col_run1, col_run2, col_run3 = st.columns([1,1,1])
with col_run1:
    save = st.button("💾 Speichern")
with col_run2:
    test_ntfy = st.button("📣 Test-Notification", disabled=not NTFY_AVAILABLE)
with col_run3:
    preview = st.checkbox("JSON-Vorschau", value=False)

# ---------- Aktionen ----------
# aktuelle Eingaben in cfg zurückschreiben
cfg["threshold_pct"] = threshold_pct
cfg["state_file"] = state_file
cfg["tickers"] = to_list(tickers_text)
cfg["ntfy"] = {"server": ntfy_server.strip(), "topic": ntfy_topic.strip()}
cfg["log"] = {
    "level": log_level,
    "to_file": bool(log_to_file),
    "file_path": log_file.strip(),
    "file_max_bytes": file_max_bytes,
    "file_backup_count": file_backup,
}
cfg["market_hours"] = {
    "timezone": mh_tz.strip(),
    "open": mh_open.strip(),
    "close": mh_close.strip(),
    "weekdays_only": bool(mh_weekdays),
}

cfg["test"] = {
    "enabled": bool(test_enabled),
    "dry_run": bool(test_dry),
    "simulate_change": bool(test_sim),
    "demo_message": demo_msg,
}
cfg["news"] = {
    "enabled": bool(news_enabled),
    "provider": news_provider,
    "query": news_query,
    "language": news_language,
    "max_items": news_max,
}


if save:
    errors = validate_cfg(cfg)
    if errors:
        st.error("Bitte korrigiere die folgenden Punkte:")
        for e in errors:
            st.write("• " + e)
    else:
        save_config(config_file, cfg)
        st.success(f"Konfiguration gespeichert: `{config_file}`")

if test_ntfy:
    if not NTFY_AVAILABLE:
        st.warning("`notify_ntfy` konnte nicht importiert werden. Stelle sicher, dass dein Projekt importierbar ist (`src`-Struktur, -m Start).")
    elif not ntfy_topic:
        st.warning("Bitte ein Topic angeben.")
    else:
        try:
            notify_ntfy(server=ntfy_server, topic=ntfy_topic, title="Stock Notifier", message="Testnachricht aus der Streamlit-Konfiguration")
            st.success("Testnachricht gesendet ✅")
        except Exception as e:
            st.error(f"Fehler beim Senden: {e}")

# Vorschau / Rohdaten
# with st.expander("📄 Vorschau (JSON)"):
#     st.code(json.dumps(cfg, ensure_ascii=False, indent=2), language="json")
if preview:
    st.subheader("📄 Vorschau (JSON)")
    st.code(json.dumps(cfg, ensure_ascii=False, indent=2), language="json")