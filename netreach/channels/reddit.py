import httpx

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 netreach/1.0"

def parse_reddit_post_url(url: str) -> str:
    """Appends .json to the Reddit post URL properly, stripping query parameters."""
    url = url.split("?")[0]
    if not url.endswith(".json"):
        if url.endswith("/"):
            url = url[:-1]
        url += ".json"
    return url

def get_post(url: str) -> dict:
    """Fetches details of a single Reddit post and its top 5 comments."""
    try:
        json_url = parse_reddit_post_url(url)
        headers = {"User-Agent": USER_AGENT}
        
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(json_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                if not isinstance(data, list) or len(data) < 1:
                    return {
                        "error": True,
                        "message": "Invalid response format from Reddit JSON endpoint",
                        "channel": "reddit",
                        "fallback_tried": False
                    }
                
                post_data = data[0]["data"]["children"][0]["data"]
                title = post_data.get("title", "")
                selftext = post_data.get("selftext", "")
                score = post_data.get("score", 0)
                author = post_data.get("author", "")
                subreddit = post_data.get("subreddit", "")
                
                comments = []
                if len(data) > 1:
                    comments_children = data[1]["data"]["children"]
                    for child in comments_children:
                        cdata = child.get("data", {})
                        body = cdata.get("body")
                        if body:
                            comments.append({
                                "author": cdata.get("author", "[deleted]"),
                                "body": body,
                                "score": cdata.get("score", 0)
                            })
                            if len(comments) >= 5:
                                break
                                
                return {
                    "title": title,
                    "body": selftext,
                    "score": score,
                    "author": author,
                    "subreddit": subreddit,
                    "comments": comments,
                    "error": False
                }
            else:
                return {
                    "error": True,
                    "message": f"Reddit API returned HTTP status {response.status_code}",
                    "channel": "reddit",
                    "fallback_tried": False
                }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred fetching post: {str(e)}",
            "channel": "reddit",
            "fallback_tried": False
        }

def search_reddit(query: str, subreddit: str = None, limit: int = 10) -> dict:
    """Searches public Reddit posts matching a query, optionally filtering by subreddit."""
    try:
        headers = {"User-Agent": USER_AGENT}
        if subreddit:
            search_url = f"https://www.reddit.com/r/{subreddit}/search.json"
            params = {
                "q": query,
                "restrict_sr": "on",
                "sort": "relevance",
                "limit": limit
            }
        else:
            search_url = "https://www.reddit.com/search.json"
            params = {
                "q": query,
                "sort": "relevance",
                "limit": limit
            }
            
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(search_url, params=params, headers=headers)
            if response.status_code == 200:
                data = response.json()
                children = data.get("data", {}).get("children", [])
                results = []
                for child in children:
                    cdata = child.get("data", {})
                    results.append({
                        "title": cdata.get("title", ""),
                        "url": f"https://reddit.com{cdata.get('permalink', '')}" if cdata.get('permalink') else cdata.get('url', ''),
                        "score": cdata.get("score", 0),
                        "subreddit": cdata.get("subreddit", ""),
                        "author": cdata.get("author", ""),
                        "num_comments": cdata.get("num_comments", 0),
                        "selftext": cdata.get("selftext", "")[:300] + "..." if len(cdata.get("selftext", "")) > 300 else cdata.get("selftext", "")
                    })
                return {"results": results, "error": False}
            else:
                return {
                    "error": True,
                    "message": f"Reddit API returned HTTP status {response.status_code}",
                    "channel": "reddit",
                    "fallback_tried": False
                }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred searching posts: {str(e)}",
            "channel": "reddit",
            "fallback_tried": False
        }

def probe() -> dict:
    """Probes Reddit's JSON interface."""
    try:
        headers = {"User-Agent": USER_AGENT}
        with httpx.Client(timeout=5.0, follow_redirects=True) as client:
            response = client.get("https://www.reddit.com/r/python.json?limit=1", headers=headers)
            if response.status_code == 200:
                return {
                    "ok": True,
                    "backend": "Reddit Public JSON API",
                    "detail": "Successfully retrieved r/python.json"
                }
            else:
                return {
                    "ok": False,
                    "backend": "Reddit Public JSON API",
                    "detail": f"Reddit API returned HTTP status {response.status_code}"
                }
    except Exception as e:
        return {
            "ok": False,
            "backend": "Reddit Public JSON API",
            "detail": f"Probe error: {str(e)}"
        }
