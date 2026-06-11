import httpx

USER_AGENT = "Mozilla/5.0 (compatible; netreach/1.0)"

def fetch_web(url: str) -> dict:
    """Fetches any webpage as clean markdown using the Jina Reader API."""
    try:
        headers = {
            "User-Agent": USER_AGENT,
        }
        # Build Jina Reader URL
        jina_url = f"https://r.jina.ai/{url}"
        
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(jina_url, headers=headers)
            if response.status_code == 200:
                return {"content": response.text.strip(), "error": False}
            else:
                return {
                    "error": True,
                    "message": f"HTTP error {response.status_code} from Jina Reader API",
                    "channel": "web",
                    "fallback_tried": False
                }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred: {str(e)}",
            "channel": "web",
            "fallback_tried": False
        }

def probe() -> dict:
    """Probes the web channel backend."""
    try:
        res = fetch_web("https://example.com")
        if res.get("error"):
            return {
                "ok": False,
                "backend": "Jina Reader (https://r.jina.ai)",
                "detail": res.get("message")
            }
        return {
            "ok": True,
            "backend": "Jina Reader (https://r.jina.ai)",
            "detail": "Successfully resolved and fetched https://example.com"
        }
    except Exception as e:
        return {
            "ok": False,
            "backend": "Jina Reader (https://r.jina.ai)",
            "detail": f"Probe error: {str(e)}"
        }
