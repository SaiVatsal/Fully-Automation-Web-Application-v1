import re
import httpx
from html.parser import HTMLParser

try:
    import snscrape.modules.twitter as sntwitter
    SNSCRAPE_AVAILABLE = True
except ImportError:
    SNSCRAPE_AVAILABLE = False

USER_AGENT = "Mozilla/5.0 (compatible; netreach/1.0)"

NITTER_INSTANCES = [
    "nitter.privacydev.net",
    "nitter.poast.org",
    "nitter.moomoo.me",
    "nitter.net"
]

class NitterTweetParser(HTMLParser):
    """Parses a Nitter single-tweet page."""
    def __init__(self):
        super().__init__()
        self.in_main_tweet = False
        self.in_tweet_content = False
        self.in_username = False
        self.in_fullname = False
        self.in_date = False
        self.in_stat = False
        
        self.tweet_data = {
            "username": "",
            "fullname": "",
            "text": "",
            "date": "",
            "retweets": "0",
            "likes": "0",
        }
        self.current_stat_type = None
        self.div_depth = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        
        if tag == "div" and "main-tweet" in cls:
            self.in_main_tweet = True
            self.div_depth = 0
            
        if self.in_main_tweet:
            if tag == "div":
                self.div_depth += 1
                
            if tag == "a" and "username" in cls:
                self.in_username = True
            elif tag == "a" and "fullname" in cls:
                self.in_fullname = True
            elif tag == "div" and "tweet-content" in cls:
                self.in_tweet_content = True
            elif tag == "p" and "tweet-date" in cls:
                self.in_date = True
            elif tag == "a" and self.in_date:
                title = attrs_dict.get("title", "")
                if title:
                    self.tweet_data["date"] = title
            elif tag == "span" and "tweet-stat" in cls:
                self.in_stat = True
            elif tag == "span" and self.in_stat:
                if "icon-retweet" in cls:
                    self.current_stat_type = "retweets"
                elif "icon-heart" in cls:
                    self.current_stat_type = "likes"
                    
    def handle_endtag(self, tag):
        if self.in_main_tweet:
            if tag == "div":
                self.div_depth -= 1
                if self.div_depth < 0:
                    self.in_main_tweet = False
            
            if tag == "a":
                self.in_username = False
                self.in_fullname = False
            elif tag == "div":
                self.in_tweet_content = False
            elif tag == "p":
                self.in_date = False
            elif tag == "span":
                self.in_stat = False
                self.current_stat_type = None
                
    def handle_data(self, data):
        if self.in_main_tweet:
            if self.in_username:
                self.tweet_data["username"] += data.strip()
            elif self.in_fullname:
                self.tweet_data["fullname"] += data.strip()
            elif self.in_tweet_content:
                self.tweet_data["text"] += data
            elif self.in_date and not self.tweet_data["date"]:
                self.tweet_data["date"] += data.strip()
            elif self.in_stat and self.current_stat_type:
                cleaned = data.strip().replace(",", "")
                if cleaned.isdigit():
                    self.tweet_data[self.current_stat_type] = cleaned

class NitterSearchParser(HTMLParser):
    """Parses a Nitter search page."""
    def __init__(self):
        super().__init__()
        self.tweets = []
        self.current_tweet = None
        self.in_tweet_body = False
        self.in_username = False
        self.in_fullname = False
        self.in_tweet_content = False
        self.in_date = False
        self.in_stat = False
        self.current_stat_type = None
        self.div_depth = 0
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        cls = attrs_dict.get("class", "")
        
        if tag == "div" and "tweet-body" in cls:
            self.in_tweet_body = True
            self.div_depth = 0
            self.current_tweet = {
                "username": "",
                "fullname": "",
                "text": "",
                "date": "",
                "retweets": "0",
                "likes": "0",
            }
            
        if self.in_tweet_body:
            if tag == "div":
                self.div_depth += 1
            if tag == "a" and "username" in cls:
                self.in_username = True
            elif tag == "a" and "fullname" in cls:
                self.in_fullname = True
            elif tag == "div" and "tweet-content" in cls:
                self.in_tweet_content = True
            elif tag == "span" and "tweet-date" in cls:
                self.in_date = True
            elif tag == "a" and self.in_date:
                title = attrs_dict.get("title", "")
                if title:
                    self.current_tweet["date"] = title
            elif tag == "span" and "tweet-stat" in cls:
                self.in_stat = True
            elif tag == "span" and self.in_stat:
                if "icon-retweet" in cls:
                    self.current_stat_type = "retweets"
                elif "icon-heart" in cls:
                    self.current_stat_type = "likes"
                    
    def handle_endtag(self, tag):
        if self.in_tweet_body:
            if tag == "div":
                self.div_depth -= 1
                if self.div_depth < 0:
                    self.in_tweet_body = False
                    if self.current_tweet:
                        self.current_tweet["text"] = self.current_tweet["text"].strip()
                        self.tweets.append(self.current_tweet)
                        self.current_tweet = None
            if tag == "a":
                self.in_username = False
                self.in_fullname = False
            elif tag == "div":
                self.in_tweet_content = False
            elif tag == "span":
                self.in_date = False
                self.in_stat = False
                self.current_stat_type = None
                
    def handle_data(self, data):
        if self.in_tweet_body and self.current_tweet:
            if self.in_username:
                self.current_tweet["username"] += data.strip()
            elif self.in_fullname:
                self.current_tweet["fullname"] += data.strip()
            elif self.in_tweet_content:
                self.current_tweet["text"] += data
            elif self.in_date and not self.current_tweet["date"]:
                self.current_tweet["date"] += data.strip()
            elif self.in_stat and self.current_stat_type:
                cleaned = data.strip().replace(",", "")
                if cleaned.isdigit():
                    self.current_tweet[self.current_stat_type] = cleaned

def fetch_tweet_nitter(username: str, tweet_id: str) -> dict:
    """Scrapes a tweet from public Nitter instances."""
    headers = {"User-Agent": USER_AGENT}
    errors = []
    for instance in NITTER_INSTANCES:
        url = f"https://{instance}/{username}/status/{tweet_id}"
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                res = client.get(url, headers=headers)
                if res.status_code == 200:
                    parser = NitterTweetParser()
                    parser.feed(res.text)
                    if parser.tweet_data["text"] or parser.tweet_data["username"]:
                        u = parser.tweet_data["username"]
                        if u and not u.startswith("@"):
                            parser.tweet_data["username"] = f"@{u}"
                        return parser.tweet_data
                errors.append(f"{instance} status {res.status_code}")
        except Exception as e:
            errors.append(f"{instance} error {str(e)}")
    raise Exception(f"All Nitter instances failed: {', '.join(errors)}")

def search_tweets_nitter(query: str, limit: int = 10) -> list:
    """Searches tweets using Nitter instances."""
    headers = {"User-Agent": USER_AGENT}
    errors = []
    for instance in NITTER_INSTANCES:
        url = f"https://{instance}/search?q={query}"
        try:
            with httpx.Client(timeout=10.0, follow_redirects=True) as client:
                res = client.get(url, headers=headers)
                if res.status_code == 200:
                    parser = NitterSearchParser()
                    parser.feed(res.text)
                    results = parser.tweets[:limit]
                    for tweet in results:
                        u = tweet["username"]
                        if u and not u.startswith("@"):
                            tweet["username"] = f"@{u}"
                    if results:
                        return results
                errors.append(f"{instance} status {res.status_code}")
        except Exception as e:
            errors.append(f"{instance} error {str(e)}")
    raise Exception(f"All Nitter instances failed: {', '.join(errors)}")

def get_tweet(url: str) -> dict:
    """Fetches a single tweet from URL, fallback to Nitter if snscrape fails."""
    match = re.match(r"https?://(?:twitter|x)\.com/([^/]+)/status/(\d+)", url)
    if not match:
        return {
            "error": True,
            "message": "Invalid Twitter/X URL format",
            "channel": "twitter",
            "fallback_tried": False
        }
    
    username, tweet_id = match.group(1), match.group(2)
    
    # Try snscrape first if available
    if SNSCRAPE_AVAILABLE:
        try:
            scraper = sntwitter.TwitterTweetScraper(tweet_id)
            for item in scraper.get_items():
                return {
                    "username": f"@{item.user.username}",
                    "fullname": item.user.displayname,
                    "text": item.rawContent,
                    "date": item.date.strftime("%b %d, %Y · %I:%M %p UTC") if item.date else "",
                    "retweets": str(item.retweetCount),
                    "likes": str(item.likeCount),
                    "error": False
                }
        except Exception:
            pass  # Fallback
            
    # Try Nitter fallback
    try:
        data = fetch_tweet_nitter(username, tweet_id)
        data["error"] = False
        return data
    except Exception as e:
        return {
            "error": True,
            "message": f"Failed to fetch tweet: {str(e)}",
            "channel": "twitter",
            "fallback_tried": True
        }

def search_tweets(query: str, limit: int = 10) -> dict:
    """Searches tweets, fallback to Nitter if snscrape fails."""
    # Try snscrape first if available
    if SNSCRAPE_AVAILABLE:
        try:
            scraper = sntwitter.TwitterSearchScraper(query)
            results = []
            for item in scraper.get_items():
                results.append({
                    "username": f"@{item.user.username}",
                    "fullname": item.user.displayname,
                    "text": item.rawContent,
                    "date": item.date.strftime("%b %d, %Y · %I:%M %p UTC") if item.date else "",
                    "retweets": str(item.retweetCount),
                    "likes": str(item.likeCount),
                })
                if len(results) >= limit:
                    break
            if results:
                return {"results": results, "error": False}
        except Exception:
            pass  # Fallback
            
    # Try Nitter fallback
    try:
        results = search_tweets_nitter(query, limit)
        return {"results": results, "error": False}
    except Exception as e:
        return {
            "error": True,
            "message": f"Failed to search tweets: {str(e)}",
            "channel": "twitter",
            "fallback_tried": True
        }

def probe() -> dict:
    """Probes the Twitter channel."""
    # Check if we can reach at least one Nitter instance
    nitter_reachable = False
    for instance in NITTER_INSTANCES[:2]:
        try:
            with httpx.Client(timeout=5.0) as client:
                res = client.get(f"https://{instance}/", follow_redirects=True)
                if res.status_code == 200:
                    nitter_reachable = True
                    break
        except Exception:
            pass
            
    backend = "snscrape" if SNSCRAPE_AVAILABLE else "Nitter Scraper"
    if nitter_reachable:
        return {
            "ok": True,
            "backend": f"{backend} + Nitter fallback",
            "detail": f"Twitter channel available. Nitter instance responded OK."
        }
    elif SNSCRAPE_AVAILABLE:
        return {
            "ok": True,
            "backend": "snscrape",
            "detail": "snscrape is available, but Nitter fallback is currently unreachable."
        }
    else:
        return {
            "ok": False,
            "backend": "None",
            "detail": "snscrape import failed and Nitter instances are unreachable."
        }
