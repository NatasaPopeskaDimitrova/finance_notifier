from __future__ import annotations
import datetime as dt
from typing import List, Dict, Iterable
from urllib.parse import quote_plus
import feedparser


def build_query(name: str, ticker: str) -> str:
    """
    Build a Google News search query for a company.
    Beispiel: "Microsoft MSFT stock OR shares OR earnings OR analyst"
    """
    # TODO: Return a query combining company name, ticker, and finance keywords
    base_terms = ["stock", "shares", "earnings", "analyst", "forecast", "upgrade", "downgrade"]
    # Name + Ticker + einige Finanz-Schlüsselwörter, mit OR verknüpft
    kw = " OR ".join(base_terms)
    # etwas „noise“ vermeiden: bevorzugt Finanzkontext
    return f'{name} {ticker} ({kw})'


def filter_titles(items: List[Dict[str, str]], required_keywords: Iterable[str] = ()) -> List[Dict[str, str]]:
    """
    Filter news items so that only those containing required keywords
    in their title are kept (case-insensitive). If no keywords given, return as-is.
    """
    # TODO: If no required keywords, return items unchanged
    # TODO: Otherwise, keep only items whose title contains any keyword (case-insensitive)
    req = [k.strip().lower() for k in required_keywords or [] if k.strip()]
    if not req:
        return items

    out: List[Dict[str, str]] = []
    for it in items:
        title = (it.get("title") or "").lower()
        if any(k in title for k in req):
            out.append(it)
    return out


def _google_news_rss_url(query: str, lang: str = "de", country: str = "DE") -> str:
    """
    Build a Google News RSS URL for a given query.
    - query wird URL-enkodiert
    - 'when:12h' (o. ä.) grenzt die Zeitspanne bei Google News ein (serverseitig)
    """
    # TODO: Encode the query with quote_plus, append "when:12h"
    # TODO: Construct and return the final RSS URL

    q = f"{query} when:12h"
    q_enc = quote_plus(q)
    # Beispiel-Endpunkt:
    # https://news.google.com/rss/search?q=<QUERY>&hl=de&gl=DE&ceid=DE:de
    return f"https://news.google.com/rss/search?q={q_enc}&hl={lang}&gl={country}&ceid={country}:{lang}"
    


def fetch_headlines(
    query: str,
    limit: int = 2,
    lookback_hours: int = 12,
    lang: str = "de",
    country: str = "DE",
) -> List[Dict[str, str]]:
    """
    Fetch latest headlines from Google News RSS for a given query.
    - serverseitige Einschränkung per 'when:12h' in der URL
    - zusätzlich clientseitiger Filter via lookback_hours
    """
    # TODO: Build the RSS URL via _google_news_rss_url and parse it with feedparser
    # TODO: Filter entries by publication time (lookback_hours) and collect title/source/link
    # TODO: Stop after collecting 'limit' items
    url = _google_news_rss_url(query, lang=lang, country=country)
    #print(f"url={url}")
    #=> https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de
    feed = feedparser.parse(url)
    #{'bozo': False, 
    # 'entries': [{'title': 'Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt - Traders Union', 
    # 'title_detail': {
    #       'type': 'text/plain', 
    #       'language': None, 
    #       'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 
    #       'value': 'Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt - Traders Union'}, 
    #       'links': [{'rel': 'alternate', 'type': 'text/html', 'href': 'https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5'}], 
    #       'link': 'https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5', 
    #       'id': 'CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg', 
    #       'guidislink': False, 
    #       'published': 'Wed, 03 Sep 2025 08:45:46 GMT', 
    #       'published_parsed': time.struct_time(tm_year=2025, tm_mon=9, tm_mday=3, tm_hour=8, tm_min=45, tm_sec=46, tm_wday=2, tm_yday=246, tm_isdst=0), 
    #       'summary': '<a href="https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5" target="_blank">Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt</a>&nbsp;&nbsp;<font color="#6f6f6f">Traders Union</font>', 'summary_detail': {'type': 'text/html', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': '<a href="https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5" target="_blank">Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt</a>&nbsp;&nbsp;<font color="#6f6f6f">Traders Union</font>'}, 'source': {'href': 'https://tradersunion.com', 'title': 'Traders Union'}}], 'feed': {'generator_detail': {'name': 'NFE/5.0'}, 'generator': 'NFE/5.0', 'title': '"Microsoft MSFT (stock OR shares OR earnings OR analyst OR forecast OR upgrade OR downgrade) when:12h" - Google News', 'title_detail': {'type': 'text/plain', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': '"Microsoft MSFT (stock OR shares OR earnings OR analyst OR forecast OR upgrade OR downgrade) when:12h" - Google News'}, 'links': [{'rel': 'alternate', 'type': 'text/html', 'href': 'https://news.google.com/search?q=Microsoft+MSFT+(stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade)+when:12h&hl=de&gl=DE&ceid=DE:de'}], 'link': 'https://news.google.com/search?q=Microsoft+MSFT+(stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade)+when:12h&hl=de&gl=DE&ceid=DE:de', 'language': 'de', 'publisher': 'news-webmaster@google.com', 'publisher_detail': {'email': 'news-webmaster@google.com'}, 'rights': 'Copyright © 2025 Google. All rights reserved. This XML feed is made available solely for the purpose of rendering Google News results within a personal feed reader for personal, non-commercial use. Any other use of the feed is expressly prohibited. By accessing this feed or using these results in any manner whatsoever, you agree to be bound by the foregoing restrictions.', 'rights_detail': {'type': 'text/plain', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': 'Copyright © 2025 Google. All rights reserved. This XML feed is made available solely for the purpose of rendering Google News results within a personal feed reader for personal, non-commercial use. Any other use of the feed is expressly prohibited. By accessing this feed or using these results in any manner whatsoever, you agree to be bound by the foregoing restrictions.'}, 'updated': 'Wed, 03 Sep 2025 16:15:44 GMT', 'updated_parsed': time.struct_time(tm_year=2025, tm_mon=9, tm_mday=3, tm_hour=16, tm_min=15, tm_sec=44, tm_wday=2, tm_yday=246, tm_isdst=0), 'image': {'title': 'Google News', 'title_detail': {'type': 'text/plain', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': 'Google News'}, 'href': 'https://lh3.googleusercontent.com/-DR60l-K8vnyi99NZovm9HlXyZwQ85GMDxiwJWzoasZYCUrPuUM_P_4Rb7ei03j-0nRs0c4F=w256', 'links': [{'rel': 'alternate', 'type': 'text/html', 'href': 'https://news.google.com/'}], 'link': 'https://news.google.com/', 'height': 256, 'width': 256}, 'subtitle': 'Google News', 'subtitle_detail': {'type': 'text/html', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': 'Google News'}}, 'headers': {'content-type': 'application/xml; charset=utf-8', 'vary': 'Sec-Fetch-Dest, Sec-Fetch-Mode, Sec-Fetch-Site', 'cache-control': 'no-cache, no-store, max-age=0, must-revalidate', 'pragma': 'no-cache', 'expires': 'Mon, 01 Jan 1990 00:00:00 GMT', 'date': 'Wed, 03 Sep 2025 16:15:44 GMT', 'strict-transport-security': 'max-age=31536000', 'permissions-policy': 'ch-ua-arch=*, ch-ua-bitness=*, ch-ua-full-version=*, ch-ua-full-version-list=*, ch-ua-model=*, ch-ua-wow64=*, ch-ua-form-factors=*, ch-ua-platform=*, ch-ua-platform-version=*', 'content-security-policy': "script-src 'report-sample' 'nonce-XiYyTLDBitGM1jII1XFIug' 'unsafe-inline';object-src 'none';base-uri 'self';report-uri /_/DotsSplashUi/cspreport;worker-src 'self'", 'cross-origin-opener-policy': 'same-origin-allow-popups', 'cross-origin-resource-policy': 'same-site', 'accept-ch': 'Sec-CH-UA-Arch, Sec-CH-UA-Bitness, Sec-CH-UA-Full-Version, Sec-CH-UA-Full-Version-List, Sec-CH-UA-Model, Sec-CH-UA-WoW64, Sec-CH-UA-Form-Factors, Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version', 'reporting-endpoints': 'default="/_/DotsSplashUi/web-reports?context=eJzjitDikmLw1JBi-LxjBmvrzXOsk4HYUOESqz0QX06_xFokcYW1AYg_Vd1gFai-wZrEfpO1AIjXbLzFuhmII6fcZU0A4t9r7rIyrb3LuiXZh-0QEAtxc2y4_PAom8CDp3t9lJST8gvjU_JLiosLchKLM4pTi8pSi-KNDIxMDSwNDPUMLeILDABSMDce"', 'content-encoding': 'gzip', 'server': 'ESF', 'x-xss-protection': '0', 'x-frame-options': 'SAMEORIGIN', 'x-content-type-options': 'nosniff', 'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000', 'connection': 'close', 'transfer-encoding': 'chunked'}, 'href': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'status': 200, 'encoding': 'utf-8', 'version': 'rss20', 'namespaces': {'media': 'http://search.yahoo.com/mrss/'}}
    #print(f"feed={feed}")
    #feed={
    # 'bozo': False, 
    # 'entries': [
    #   {'title': 'Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt - Traders Union', 
    #    'title_detail': {'type': 'text/plain', 
    #                     'language': None, 
    #                     'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 
    #                     'value': 'Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt - Traders Union'}, 
    #                     'links': [{
    #                           'rel': 'alternate', 
    #                           'type': 'text/html', 
    #                           'href': 'https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5'}],
    #                    'link': 'https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5', 
    #                    'id': 'CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg', 
    #                    'guidislink': False, 
    #                    'published': 'Wed, 03 Sep 2025 08:45:46 GMT', 
    #                    'published_parsed': time.struct_time(tm_year=2025, tm_mon=9, tm_mday=3, tm_hour=8, tm_min=45, tm_sec=46, tm_wday=2, tm_yday=246, tm_isdst=0), 
    #                    'summary': '<a href="https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5" target="_blank">Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt</a>&nbsp;&nbsp;<font color="#6f6f6f">Traders Union</font>', 
    #                    'summary_detail': {'type': 'text/html', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': '<a href="https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5" target="_blank">Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt</a>&nbsp;&nbsp;<font color="#6f6f6f">Traders Union</font>'}, 'source': {'href': 'https://tradersunion.com', 'title': 'Traders Union'}}], 'feed': {'generator_detail': {'name': 'NFE/5.0'}, 'generator': 'NFE/5.0', 'title': '"Microsoft MSFT (stock OR shares OR earnings OR analyst OR forecast OR upgrade OR downgrade) when:12h" - Google News', 'title_detail': {'type': 'text/plain', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': '"Microsoft MSFT (stock OR shares OR earnings OR analyst OR forecast OR upgrade OR downgrade) when:12h" - Google News'}, 'links': [{'rel': 'alternate', 'type': 'text/html', 'href': 'https://news.google.com/search?q=Microsoft+MSFT+(stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade)+when:12h&hl=de&gl=DE&ceid=DE:de'}], 'link': 'https://news.google.com/search?q=Microsoft+MSFT+(stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade)+when:12h&hl=de&gl=DE&ceid=DE:de', 'language': 'de', 'publisher': 'news-webmaster@google.com', 'publisher_detail': {'email': 'news-webmaster@google.com'}, 'rights': 'Copyright © 2025 Google. All rights reserved. This XML feed is made available solely for the purpose of rendering Google News results within a personal feed reader for personal, non-commercial use. Any other use of the feed is expressly prohibited. By accessing this feed or using these results in any manner whatsoever, you agree to be bound by the foregoing restrictions.', 'rights_detail': {'type': 'text/plain', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': 'Copyright © 2025 Google. All rights reserved. This XML feed is made available solely for the purpose of rendering Google News results within a personal feed reader for personal, non-commercial use. Any other use of the feed is expressly prohibited. By accessing this feed or using these results in any manner whatsoever, you agree to be bound by the foregoing restrictions.'}, 'updated': 'Wed, 03 Sep 2025 16:32:50 GMT', 'updated_parsed': time.struct_time(tm_year=2025, tm_mon=9, tm_mday=3, tm_hour=16, tm_min=32, tm_sec=50, tm_wday=2, tm_yday=246, tm_isdst=0), 'image': {'title': 'Google News', 'title_detail': {'type': 'text/plain', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': 'Google News'}, 'href': 'https://lh3.googleusercontent.com/-DR60l-K8vnyi99NZovm9HlXyZwQ85GMDxiwJWzoasZYCUrPuUM_P_4Rb7ei03j-0nRs0c4F=w256', 'links': [{'rel': 'alternate', 'type': 'text/html', 'href': 'https://news.google.com/'}], 'link': 'https://news.google.com/', 'height': 256, 'width': 256}, 'subtitle': 'Google News', 'subtitle_detail': {'type': 'text/html', 'language': None, 'base': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'value': 'Google News'}}, 'headers': {'content-type': 'application/xml; charset=utf-8', 'vary': 'Sec-Fetch-Dest, Sec-Fetch-Mode, Sec-Fetch-Site', 'cache-control': 'no-cache, no-store, max-age=0, must-revalidate', 'pragma': 'no-cache', 'expires': 'Mon, 01 Jan 1990 00:00:00 GMT', 'date': 'Wed, 03 Sep 2025 16:32:50 GMT', 'strict-transport-security': 'max-age=31536000', 'content-security-policy': "script-src 'report-sample' 'nonce-bDMAdW76q64itlTKOkpVrg' 'unsafe-inline';object-src 'none';base-uri 'self';report-uri /_/DotsSplashUi/cspreport;worker-src 'self'", 'permissions-policy': 'ch-ua-arch=*, ch-ua-bitness=*, ch-ua-full-version=*, ch-ua-full-version-list=*, ch-ua-model=*, ch-ua-wow64=*, ch-ua-form-factors=*, ch-ua-platform=*, ch-ua-platform-version=*', 'accept-ch': 'Sec-CH-UA-Arch, Sec-CH-UA-Bitness, Sec-CH-UA-Full-Version, Sec-CH-UA-Full-Version-List, Sec-CH-UA-Model, Sec-CH-UA-WoW64, Sec-CH-UA-Form-Factors, Sec-CH-UA-Platform, Sec-CH-UA-Platform-Version', 'cross-origin-resource-policy': 'same-site', 'cross-origin-opener-policy': 'same-origin-allow-popups', 'reporting-endpoints': 'default="/_/DotsSplashUi/web-reports?context=eJzjStDikmJw1ZBi-LRjBmvrzXOsk4HYUOESqz0QX06_xFokcYW1AYg_Vd1gFai-wZrEfpO1AIh3bbzFehCIzQ7eYnUB4sgpd1kTgJhz7V1WASDekuzDdgiIhbg5Nt1-eJRNYMeOPUJKykn5hfEp-SXFxQU5icUZxalFZalF8UYGRqYGlgaGeoYW8QUGAAO0OY4"', 'content-encoding': 'gzip', 'server': 'ESF', 'x-xss-protection': '0', 'x-frame-options': 'SAMEORIGIN', 'x-content-type-options': 'nosniff', 'alt-svc': 'h3=":443"; ma=2592000,h3-29=":443"; ma=2592000', 'connection': 'close', 'transfer-encoding': 'chunked'}, 'href': 'https://news.google.com/rss/search?q=Microsoft+MSFT+%28stock+OR+shares+OR+earnings+OR+analyst+OR+forecast+OR+upgrade+OR+downgrade%29+when%3A12h&hl=de&gl=DE&ceid=DE:de', 'status': 200, 'encoding': 'utf-8', 'version': 'rss20', 'namespaces': {'media': 'http://search.yahoo.com/mrss/'}}
   

    results: List[Dict[str, str]] = []
    now = dt.datetime.utcnow()

    for entry in feed.entries:
        # Publikationszeit parsen, falls vorhanden
        # feedparser liefert meist 'published_parsed' als time.struct_time
        published_dt = None
        if hasattr(entry, "published_parsed") and entry.published_parsed:
            published_dt = dt.datetime(*entry.published_parsed[:6])
        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
            published_dt = dt.datetime(*entry.updated_parsed[:6])

        # Wenn keine Zeit vorhanden ist, nehmen wir sie trotzdem (oder du überspringst sie)
        if published_dt is not None:
            age = now - published_dt
            if age > dt.timedelta(hours=lookback_hours):
                continue

        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        source = ""
        if "source" in entry and isinstance(entry.source, dict):
            source = entry.source.get("title", "") or ""

        results.append(
            {
                "title": title,
                "link": link,
                "source": source,
                "published": entry.get("published", "") or entry.get("updated", ""),
            }
        )

        if len(results) >= limit:
            break

    return results


############ So nutzt du das Modul ############
#if __name__ == "__main__":
name = "Microsoft"
ticker = "MSFT"

q = build_query(name, ticker) #query
#print(f" q = build_query(name, ticker) = {q}")
#=>
# Microsoft MSFT (
#   stock OR 
#   shares OR 
#   earnings OR 
#   analyst OR 
#   forecast OR 
#   upgrade OR 
#   downgrade)
headlines = fetch_headlines(q, limit=3, lookback_hours=12, lang="de", country="DE")
#print(f"headlines = {headlines}")#=> WEB Side
#[{'title': 'Microsoft-Aktie hält sich in der Nähe von $505, da die Einführung von KI die Geduld der Anleger auf die Probe stellt - Traders Union', 
#  'link': 'https://news.google.com/rss/articles/CBMisAFBVV95cUxOOHZVeEowTHRaVW8yeGV6YkJqbjNZNWlRTEhNOUV4NDBhVTU0YjUyUU1rUXcyUUNITUIwOTBrbGhDWXJWX2FlSXpSeENDZHNLX2pWZzE1VWFUQmg1bENhU3VxZGJCRklBbmZodWIweXB1cEhJWW96WG9OdzBIRTE1MHNZMGRVY1ZxS3ZVRklSakJNTHNwd2huRG1NMGNUVlE4eGlVeEZJS2lzQmk2WkNkSg?oc=5', 
#  'source': 'Traders Union', 
#  'published': 'Wed, 03 Sep 2025 08:45:46 GMT'}]

# Optional Titel-Filter, z. B. nur Earnings/Analyst
headlines = filter_titles(headlines, required_keywords=["earnings", "analyst", "downgrade", "upgrade", "stock", "shares", "forecast"])
#print(f"headlines = {headlines}") #headlines = []

for h in headlines:
    print(f"- {h['title']} ({h['source']})\n  {h['link']}\n  {h['published']}\n")