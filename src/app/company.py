from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, Any, Tuple, List
import json
import time
import yfinance as yf
from dataclasses import asdict

# TODO Create with 'Path' class the 'CACHE_FILE' object which stores location to 'company_cache.json'
# CACHE_FILE =
CACHE_FILE: Path = Path(__file__).resolve().parent / "company_cache.json"

# TODO # Common legal suffixes often found in company names (ADD MORE),
# which we remove to get a cleaner keyword (e.g., "Apple Inc." -> "Apple"). 
# Häufige Rechtsformen/Suffixe (kannst du bei Bedarf erweitern)
LEGAL_SUFFIXES = {
    "inc", "inc.", "corp", "corp.", "corporation",
    "ltd", "ltd.", "plc", "ag", "se", "nv", "sa", "s.a.",
    "spa", "s.p.a.", "oyj", "ab", "asa",
    "co", "co.", "company", "limited", "holdings", "holding",
    "llc", "llp", "kg", "kgaa",
}

# TODO Add class attributes like in the class description

@dataclass
class CompanyMeta:
    """
    Represents metadata about a company/ticker.
    
    Attributes:
        ticker (str): The full ticker symbol, e.g., "SAP.DE".
        name (Optional[str]): Cleaned company name without legal suffixes, e.g., "Apple".
        raw_name (Optional[str]): Original company name as returned by Yahoo Finance, e.g., "Apple Inc.".
        source (str): Source of the name (e.g., "info.longName", "info.shortName", "fallback").
        base_ticker (str): Simplified ticker without suffixes, e.g., "SAP" for "SAP.DE".
    """
    ticker: str
    name: Optional[str]
    raw_name: Optional[str]
    source: str
    base_ticker: str

# TODO Finish this function:

def _load_cache() -> Dict[str, Any]:
    """Load cached company metadata from JSON file."""
    if CACHE_FILE.exists():
        try:
            # Return content of file
             return json.loads(CACHE_FILE.read_text(encoding="utf-8"))
        except Exception:
            # Return empty dictionary
            return {}
    else:
        # Return empty dictionary
        return {}

def _save_cache(cache: Dict[str, Any]) -> None:
    """Save company metadata to local cache file."""
    # TODO What parameters are missing?
    CACHE_FILE.write_text(json.dumps(cache, ensure_ascii=False, indent=2), encoding="utf-8")


# TODO Finish the function logic    
def _strip_legal_suffixes(name: str) -> str:
    """
    Remove common legal suffixes from a company name.

    Example:
        "Apple Inc." -> "Apple"
        "SAP SE" -> "SAP"
    """
    if not name:
        return ""
    parts = [p.strip(",. ") for p in name.split()]
    # entferne bekannte Suffixe am Ende
    while parts and parts[-1].lower() in LEGAL_SUFFIXES:
        parts.pop()
    return " ".join(parts) if parts else name.strip()

# TODO Finish the function logic
def _base_ticker(symbol: str) -> str:
    """
    Extract the base ticker symbol.

    Examples:
        "SAP.DE" -> "SAP"
        "BRK.B"  -> "BRK"
        "^GDAXI" -> "^GDAXI" (indices remain unchanged)
    """
    if symbol.startswith("^"):  # Indizes unverändert
        return symbol
    # Klasse/Suffixe wie BRK.B oder RDS-A -> erster Teil
    if "." in symbol:
        return symbol.split(".", 1)[0]
    if "-" in symbol:
        # für Klassentrenner wie BRK-B
        return symbol.split("-", 1)[0]
    return symbol

# TODO Finish the try and except block
def _fetch_yf_info(symbol: str, retries: int = 2, delay: float = 0.4) -> Dict[str, Any]:
    """
    Fetch company information from Yahoo Finance.

    Args:
        symbol (str): Ticker symbol.
        retries (int): Number of retries if request fails.
        delay (float): Delay between retries in seconds.

    Returns:
        dict: Yahoo Finance info dictionary (may be empty if lookup fails).
    """
    last_exc: Optional[Exception] = None
    for _ in range(retries + 1):
        try:
            t = yf.Ticker(symbol)
            info = getattr(t, "info", {}) or {}
            # Manche yfinance-Versionen liefern ein leeres dict bei Fehlern
            if info:
                return info
        except Exception as e:
            last_exc = e
            time.sleep(delay)
    # Optional: Logging hier einbauen, falls du einen Logger hast
    return {}


def get_company_meta(symbol: str) -> CompanyMeta:
    """
    Retrieve company metadata (name, base ticker, etc.) with caching and fallbacks.
    """
    # TODO: Load the cache with _load_cache() and return early if the symbol exists
    cache = _load_cache()
    if symbol in cache:
        c = cache[symbol]
        return CompanyMeta(
            ticker=c["ticker"],
            name=c.get("name"),
            raw_name=c.get("raw_name"),
            source=c.get("source", "cache"),
            base_ticker=c.get("base_ticker", _base_ticker(symbol)),
        )

    # TODO: Fetch raw company information via _fetch_yf_info
    info = _fetch_yf_info(symbol)

    # TODO: Extract a potential company name from info ("longName", "shortName", "displayName")
    raw_name: Optional[str] = None
    source = "fallback"
    for key in ("longName", "shortName", "displayName"):
        if key in info and isinstance(info[key], str) and info[key].strip():
            raw_name = info[key].strip()
            source = f"info.{key}"
            break

    # TODO: Clean the extracted name with _strip_legal_suffixes and handle fallback to _base_ticker
    cleaned = _strip_legal_suffixes(raw_name) if raw_name else ""
    if not cleaned:
        cleaned = _base_ticker(symbol)

    # TODO: Create a CompanyMeta instance and cache the result using _save_cache
    meta = CompanyMeta(
        ticker=symbol,
        name=cleaned,
        raw_name=raw_name,
        source=source,
        base_ticker=_base_ticker(symbol),
    )

    # TODO: Save the constructed metadata back into the cache
    # In Cache speichern
    cache[symbol] = asdict(meta)
    _save_cache(cache)

    return meta

    


def auto_keywords(symbol: str) -> Tuple[str, list[str]]:
    """
    Generate a company search keyword set based on symbol.
    Returns:
        display_name (str), required_keywords (list[str])
    """
    # TODO: Fetch the CompanyMeta for the symbol
    meta = get_company_meta(symbol)
    # Anzeigename priorisieren: bereinigter Name > base_ticker > symbol
    display = (meta.name or meta.base_ticker or meta.ticker).strip()

    # TODO: Determine the display name and construct the keyword list
    # Keywords: Displayname, einzelne Worte daraus, Base-Ticker, Symbol (einzigartig, ohne Leers)
    words = [w for w in display.split() if w]
    req_raw = [display] + words + [meta.base_ticker, meta.ticker]
    # Entdoppeln bei Erhalt der Reihenfolge
    seen = set()
    req: List[str] = []
    for x in req_raw:
        if x and x not in seen:
            req.append(x)
            seen.add(x)

    # TODO: Return the cleaned name and the list of required keywords
    return display, req

    ###########  Mini-Test (im REPL oder in einem kleinen Script)#######


#from src.app.company import get_company_meta, auto_keywords

print(f"AAPL={get_company_meta("AAPL")}")
print(f"SAP.DE={auto_keywords("SAP.DE")}")




meta = CompanyMeta(
    ticker="AAPL",
    name="Apple",
    raw_name="Apple Inc.",
    source="info.longName",
    base_ticker="AAPL",
)


print(f"meta={meta}")
# CompanyMeta(ticker='AAPL', name='Apple', raw_name='Apple Inc.', source='info.longName', base_ticker='AAPL')


print(f"asdict-meta={asdict(meta)}")
# {'ticker': 'AAPL', 'name': 'Apple', 'raw_name': 'Apple Inc.', 'source': 'info.longName', 'base_