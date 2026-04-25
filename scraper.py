import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import sqlite3
import schedule
import time

# RSS feeds od pouzdanih izvora koji pokrivaju konflikte
RSS_FEEDS = [
    # Opće vijesti
    "https://feeds.bbci.co.uk/news/world/rss.xml",
    "https://www.aljazeera.com/xml/rss/all.xml",
    "https://feeds.npr.org/1004/rss.xml",
    # Konflikti i sigurnost
    "https://feeds.feedburner.com/ReliefWeb",
    "https://rss.dw.com/rdf/rss-en-world",
    "https://www.france24.com/en/rss",
    "https://feeds.skynews.com/feeds/rss/world.xml",
    # Ukrajina specifično
    "https://www.kyivindependent.com/feed/",
    "https://feeds.bbci.co.uk/news/topics/c302m85q5ljt/rss.xml",
    # Bliski istok
    "https://www.middleeasteye.net/rss",
]

def init_db():
    conn = sqlite3.connect("conflict_intel.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS articles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            content TEXT,
            url TEXT UNIQUE,
            source TEXT,
            published_at TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()
    print("✅ Baza podataka inicijalizirana")

def scrape_feeds():
    conn = sqlite3.connect("conflict_intel.db")
    cursor = conn.cursor()
    total_new = 0

    for feed_url in RSS_FEEDS:
        print(f"📡 Skidamo: {feed_url}")
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries[:10]:  # prvih 10 po feedu
                title = entry.get("title", "")
                url = entry.get("link", "")
                published = entry.get("published", str(datetime.now()))
                source = feed.feed.get("title", feed_url)
                content = entry.get("summary", "")

                try:
                    cursor.execute("""
                        INSERT OR IGNORE INTO articles (title, content, url, source, published_at)
                        VALUES (?, ?, ?, ?, ?)
                    """, (title, content, url, source, published))
                    if cursor.rowcount > 0:
                        total_new += 1
                except Exception as e:
                    print(f"  ⚠️ Greška pri unosu: {e}")

        except Exception as e:
            print(f"  ❌ Greška pri skidanju feeda: {e}")

    conn.commit()
    conn.close()
    print(f"✅ Gotovo! {total_new} novih članaka dodano\n")

if __name__ == "__main__":
    init_db()
    scrape_feeds()
    print("⏰ Scraper pokrenut, provjerava svakih 6 sati...")
    schedule.every(6).hours.do(scrape_feeds)
    while True:
        schedule.run_pending()
        time.sleep(60)