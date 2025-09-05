import time
import yfinance as yf
import logging
from typing import Tuple

logger = logging.getLogger("stock-alerts")


def get_open_and_last(ticker: str) -> Tuple[float, float]:
    """
    Retrieve today's opening price and the latest available price for a ticker.

    Strategy:
      1. Try intraday data with finer intervals ("1m", "5m", "15m").
         - Use the very first "Open" of the day. Öffnung = erstes "Open" des heutigen DataFrames
         - Use the most recent "Close" (last candle).  Letzter Preis = letztes "Close"
         - Retry once per interval in case Yahoo delivers empty DataFrames. Pro Intervall bis zu zwei Versuche (kleines Sleep zwischen den Versuchen)
      2. If no intraday data is available (e.g., market closed),
         fall back to daily interval ("1d"). Fallback: Tagesdaten ("1d"). Wenn auch leer -> RuntimeError.
    """
    ticker = ticker.upper()
    intervals = ("1m", "5m", "15m")

    # TODO: Loop over intraday intervals ("1m", "5m", "15m")
    for interval in ("1m", "5m", "15m"):# oder # in  intervals

        # TODO: For each interval, attempt up to two retries
        #Retries: pro Intervall zwei Versuche mit time.sleep(0.4) – das hilft, wenn Yahoo kurz „leer“ liefert
        #Logging: debug-Logs zeigen Intervall, Werte und Anzahl Zeilen. Fehler werden auf debug protokolliert (du kannst auf warning/error ändern, falls gewünscht).
        for attempt in range(2):
            df = yf.Ticker(ticker).history(
                period="1d", 
                interval=interval, 
                auto_adjust=False
            )
            if not df.empty:
                open_today = float(df.iloc[0]["Open"])
                last_price = float(df.iloc[-1]["Close"])
                logger.debug(
                    "Intraday %s: interval=%s open=%.4f last=%.4f",
                    ticker, interval, open_today, last_price, len(df)
                )
                return open_today, last_price
            logger.debug(
                "Empty intraday data (%s, %s), retry %d",
                ticker, interval, attempt + 1,
            )
            time.sleep(0.4) 

    # TODO: Fallback to daily data ("1d" interval) and raise RuntimeError if empty
    #Fallback: Wenn Intraday leer bleibt, werden Tagesdaten (1d) geholt; sind die auch leer → RuntimeError.
    df = yf.Ticker(ticker).history(period="1d", 
                                   interval="1d", 
                                   auto_adjust=False)
    if df.empty:
        raise RuntimeError(f"No data available for {ticker}")

    # TODO: Extract open and close from the last row, log them, and return
    row = df.iloc[-1]
    open_today, last_price = float(row["Open"]), float(row["Close"])
    logger.debug(
        "Fallback daily data %s: open=%.4f last=%.4f",
        ticker, open_today, last_price,
    )
    return open_today, last_price

#Mini-Beispiel
#if __name__ == "__main__":
logging.basicConfig(level=logging.DEBUG)
o, last = get_open_and_last("AAPL")
print("Open:", o, "Last:", last)

  
