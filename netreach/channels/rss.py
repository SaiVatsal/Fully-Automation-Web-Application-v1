import re
import httpx
import feedparser

def parse_feed(feed_url: str, limit: int = 5) -> dict:
    """Parses any RSS/Atom feed using feedparser, fetching it via httpx to respect timeouts."""
    try:
        headers = {"User-Agent": "Mozilla/5.0 (compatible; netreach/1.0)"}
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(feed_url, headers=headers)
            if response.status_code == 200:
                feed_data = feedparser.parse(response.text)
                
                entries = []
                for entry in feed_data.entries[:limit]:
                    pub_date = entry.get("published", entry.get("pubDate", entry.get("updated", "Unknown Date")))
                    
                    summary = entry.get("summary", "")
                    if not summary and "content" in entry:
                        # Feedparser parses multiple contents if present
                        summary = entry.content[0].value if entry.content else ""
                    
                    # Strip HTML tags from summary for cleaner display
                    summary = re.sub(r"<[^>]+>", "", summary)
                    summary = summary.replace("\n", " ").strip()
                    if len(summary) > 250:
                        summary = summary[:247] + "..."
                        
                    entries.append({
                        "title": entry.get("title", "No Title").strip(),
                        "link": entry.get("link", "").strip(),
                        "summary": summary,
                        "published": pub_date
                    })
                    
                return {
                    "feed_title": feed_data.feed.get("title", "Unknown Feed").strip(),
                    "entries": entries,
                    "error": False
                }
            else:
                return {
                    "error": True,
                    "message": f"HTTP error {response.status_code} fetching feed",
                    "channel": "rss",
                    "fallback_tried": False
                }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred parsing feed: {str(e)}",
            "channel": "rss",
            "fallback_tried": False
        }

def probe() -> dict:
    """Probes the RSS channel."""
    try:
        # Probe using BBC RSS Feed
        res = parse_feed("https://feeds.bbci.co.uk/news/rss.xml", limit=1)
        if res.get("error"):
            # Fallback probe HackerNews RSS
            res2 = parse_feed("https://news.ycombinator.com/rss", limit=1)
            if res2.get("error"):
                return {
                    "ok": False,
                    "backend": "feedparser + httpx",
                    "detail": f"Failed BBC probe ({res.get('message')}) and HN probe ({res2.get('message')})"
                }
            return {
                "ok": True,
                "backend": "feedparser + httpx",
                "detail": "HN RSS feed parsed successfully"
            }
        return {
            "ok": True,
            "backend": "feedparser + httpx",
            "detail": f"BBC RSS feed parsed successfully: '{res.get('feed_title')}'"
        }
    except Exception as e:
        return {
            "ok": False,
            "backend": "feedparser + httpx",
            "detail": f"Probe error: {str(e)}"
        }
