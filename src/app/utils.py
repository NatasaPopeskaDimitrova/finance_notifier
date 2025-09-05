def mask_secret(s: str, keep: int = 1) -> str:
    """Maskiert sensible Strings für Logging-Ausgaben.
    Args:
        s (str): Der geheime String (z. B. API-Key, Token).
        keep (int): Anzahl der sichtbaren Zeichen am Anfang und Ende.

    Returns:
        str: Maskierte Version, z. B. "a...z"
    """
    if not s:
        # Gib "(unset)" zurück, falls der String leer oder None ist
        return "(unset)"
    # TODO: Falls die Länge > keep * 2 ist, behalte jeweils die ersten/letzten
    #       'keep' Zeichen und ersetze die Mitte durch eine Ellipse
    # Andernfalls gib den ersten und letzten Buchstaben mit Ellipse dazwischen aus
    if len(s) > keep * 2:
        # Genug Länge: vorne + hinten behalten, Mitte ersetzen
        return s[:keep]+"..."+ s[-keep:0]
    elif len(s) > 2:
        # Kürzer: ersten und letzten Buchstaben zeigen
        return s[0] + "..." + s[-1]
    else:
        # Mini-Strings (1 oder 2 Zeichen) → ganz maskieren
        return "***"
   


#########       Beispiele     ###################

print(mask_secret("supergeheimespasswort", keep=2))
# su...rt

print(mask_secret("abc", keep=2))
# a...c

print(mask_secret("x", keep=1))
# ***

print(mask_secret("", keep=1))
# (unset)