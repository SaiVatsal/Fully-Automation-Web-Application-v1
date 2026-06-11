import time
from duckduckgo_search import DDGS

def search_ddg(query: str, limit: int = 10) -> dict:
    """Performs a web search using DuckDuckGo, enforcing a 1-second rate-limiting delay."""
    try:
        # Rate limit safety delay
        time.sleep(1.0)
        
        with DDGS() as ddgs:
            # In duckduckgo_search v6+, ddgs.text returns list/iterator of dicts
            results_generator = ddgs.text(query, max_results=limit)
            results = []
            for r in results_generator:
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", r.get("url", "")),
                    "snippet": r.get("body", r.get("snippet", ""))
                })
            return {"results": results, "error": False}
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred during search: {str(e)}",
            "channel": "search",
            "fallback_tried": False
        }

def probe() -> dict:
    """Probes the search channel using a 1-result query."""
    try:
        res = search_ddg("python", limit=1)
        if res.get("error"):
            return {
                "ok": False,
                "backend": "duckduckgo_search (DDGS)",
                "detail": res.get("message")
            }
        results = res.get("results", [])
        if results:
            return {
                "ok": True,
                "backend": "duckduckgo_search (DDGS)",
                "detail": f"Successfully performed 1-result search. Title: '{results[0].get('title')}'"
            }
        else:
            return {
                "ok": False,
                "backend": "duckduckgo_search (DDGS)",
                "detail": "Search executed successfully but returned empty result list"
            }
    except Exception as e:
        return {
            "ok": False,
            "backend": "duckduckgo_search (DDGS)",
            "detail": f"Probe error: {str(e)}"
        }
