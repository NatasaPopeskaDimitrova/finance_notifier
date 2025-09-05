import requests
import logging
from src.app.utils import mask_secret
#from app.utils import mask_secret

logger = logging.getLogger("stock-alerts")


def notify_ntfy(
    server: str,
    topic: str,
    title: str,
    message: str,
    *,
    dry_run: bool = False,
    markdown: bool = False,
    click_url: str | None = None,
) -> None:
    """
    Send a push notification via ntfy.sh.

    Args:
        server (str): ntfy server URL (e.g. "https://ntfy.sh").
        topic (str): Secret topic string subscribed in the ntfy app.
        title (str): Notification title (header).
        message (str): Notification body text (supports Unicode + Emojis).
        dry_run (bool, optional): If True, do not actually send,
                                  only log message content. Default: False.
        markdown (bool, optional): If True, enable Markdown rendering
                                   in ntfy (web app only for now).
                                   Default: False.
        click_url (str | None, optional): Optional URL that opens when
                                          tapping the notification.

    Returns:
        None

    Side effects:
        - Performs an HTTP POST request to the ntfy server.
        - On success, the subscribed app receives a push message.

    Example:
        >>> notify_ntfy(
                "https://ntfy.sh",#server
                "my-secret-topic",#topic
                "Stock Alert",    #title
                "AAPL is up 5% 📈",#message
                markdown=True,
                click_url="https://finance.yahoo.com/quote/AAPL"
            )
    """
    # TODO:If dry_run is True, log the message and return without sending
    # Wenn dry_run: nur loggen und beenden
    if dry_run: #verhindert echten HTTP-Request; loggt nur die Werte (Topic wird mit mask_secret anonymisiert)
        logger.info( "Dry-run ntfy -> server=%s topic=%s title=%r message=%r",
            server, mask_secret(topic), title, message)
        return

    # TODO: Construct the topic URL and prepare request headers
    url = f"{server.rstrip('/')}/{topic}"
    print(f"URL={url}")
    headers = {
        "Title": title,
        "Priority": "high",
        #optional :
        # Markdown und 
        # Click
    }
    if not isinstance(message, str):
        message = str(message)
    print(f"message ={message }")
    print(f"message-encode ={message.encode("utf-8") }")
    print(f"url ={url}")
    try:
        r=requests.post(url,data=message.encode("utf-8"), headers=headers, timeout=20)
        print(f"R={r}")
    except Exception as e:
        print(f"Fehler:{e}")

   

    # TODO: If markdown is enabled, set the appropriate header
    if markdown:
        headers["Markdown"] = "yes"

    # TODO: If a click_url is provided, add it to headers
    if click_url:
        headers["Click"] = click_url

    # TODO: Perform the POST request inside a try/except block and handle errors
    try:
        r = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=20)
        r.raise_for_status()
        logger.debug(
            "ntfy success: %s topic=%s title=%r",
            server, mask_secret(topic), title
        )
    except requests.RequestException as e:
        logger.warning( "ntfy failed: server=%s topic=%s title=%r error=%s",
                        server, mask_secret(topic), title, e)
        





   ################       Beispielaufruf          ###################
#if __name__ == "__main__":
logging.basicConfig(level=logging.DEBUG)
notify_ntfy(
        "https://ntfy.sh", #server
        "mein-geheimes-topic-123", #topic
        "Stock Alert",           #title
        "AAPL ist um 5% gestiegen 📈",# message
        markdown=True,                  #markdown
        click_url="https://finance.yahoo.com/quote/AAPL" #click_url
    )


def send_ntfy(server: str, topic: str, title: str, message: str, tags: list[str] | None = None) -> None:
    url = f"{server.rstrip('/')}/{topic}"
    headers = {
        "Title": title,
        "Priority": "high",
    }
    if tags:
        headers["Tags"] = ",".join(tags)

    resp = requests.post(url, data=message.encode("utf-8"), headers=headers, timeout=15)
    resp.raise_for_status()
