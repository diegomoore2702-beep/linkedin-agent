import feedparser
import requests

RSS_FEEDS = {
    "tecnología": [
        "https://feeds.feedburner.com/TechCrunch",
        "https://www.wired.com/feed/rss",
    ],
    "finanzas": [
        "https://feeds.bloomberg.com/markets/news.rss",
        "https://www.economist.com/finance-and-economics/rss.xml",
    ],
    "negocios": [
        "https://hbr.org/feed",
        "https://feeds.feedburner.com/entrepreneur/latest",
    ],
    "ia": [
        "https://feeds.feedburner.com/venturebeat/SZYF",
    ]
}

def get_trends(industria: str, n: int = 5) -> list[str]:
    industria = industria.lower()
    feeds = RSS_FEEDS.get(industria, RSS_FEEDS["negocios"])
    titulos = []
    for url in feeds:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:n]:
                titulos.append(entry.title)
        except Exception:
            continue
    return titulos[:n] if titulos else ["tendencias generales en " + industria]
