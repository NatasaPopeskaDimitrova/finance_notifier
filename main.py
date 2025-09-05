from pathlib import Path

from src.app.config import load_config, deep_merge
from src.app.logging_setup import setup_logging
from src.app.core import run_once
from src.app.utils import mask_secret

#import für testing:
from src.app.ntfy import notify_ntfy


def main():
    """
    Entry point of the Stock Notifier application.
    """
    # Load configuration from "config.json"
    cfg = load_config("config.json")

    print(f"cfg[log]={cfg["log"]}")
    #=> "log": {
            #"level": "INFO",              
            #"to_file": true,              
            #"file_path": "alerts.log",    
            #"file_max_bytes": 1000000,   
            #"file_backup_count": 3
            #}

    # TODO: Initialize the logging system with setup_logging
    logger = setup_logging(cfg["log"])
    logger.info("Logger initialized")
    print(f"logger={logger}")
    print(logger) # => {'log': {'level': 'DEBUG', 'to_file': False}, 'tickers': ['AAPL']}

    # TODO: Log the loaded configuration, masking secrets with mask_secret
    # Log masked config
    logger.info(
        "Configuration loaded: ntfy.server=%s | ntfy.topic(masked)=%s | log.level=%s",
        cfg["ntfy"]["server"],
        mask_secret(cfg["ntfy"]["topic"]),
        cfg["log"]["level"],
    )

    # TODO: Run one monitoring cycle via run_once using settings from cfg
    # One monitoring cycle
    run_once(
        tickers=cfg["tickers"],
        threshold_pct=float(cfg["threshold_pct"]),
        ntfy_server=cfg["ntfy"]["server"],
        ntfy_topic=cfg["ntfy"]["topic"],
        state_file=Path(cfg["state_file"]),
        market_hours_cfg=cfg["market_hours"],
        test_cfg=cfg["test"],
        news_cfg=cfg["news"],
    )

    
    from src.app.config import deep_merge
    test1 = {
        "log": 
            {"level": "INFO",
             "to_file": False
            },
            "tickers": ["AAPL"]
    }

    test2 = {"log": {"level": "DEBUG"}}
    merged=deep_merge(test1,test2)
    print(f"merged={merged}")
    logger.debug("Deep merged config: %s", merged)
    #test end

    # Remove once implemented
    notify_ntfy(server="https://ntfy.sh", topic="Z63e7WNX4JbEeRcK", title="TEST", message="TEST_1")
    print(f"cfg[ntfy][server]={cfg["ntfy"]["server"]}")
     # Send test notification
    notify_ntfy(server=cfg["ntfy"]["server"], topic="Z63e7WNX4JbEeRcK", title="TEST", message="TEST_2")
    notify_ntfy(server=cfg["ntfy"]["server"], topic=cfg["ntfy"]["topic"], title="TEST", message="Stock Notifier Testnachricht")



if __name__ == "__main__":
    main()
