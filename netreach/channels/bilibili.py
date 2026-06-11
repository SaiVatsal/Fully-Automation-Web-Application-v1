import httpx
from netreach.config import load_config

def get_bilibili_headers() -> dict:
    """Prepares standard headers and cookies for Bilibili requests."""
    config = load_config()
    sessdata = config.get("bilibili_sessdata", "")
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.bilibili.com"
    }
    if sessdata:
        headers["Cookie"] = f"SESSDATA={sessdata}"
    return headers

def get_video(bvid: str) -> dict:
    """Fetches video details (title, uploader, description, view count, tags) by BV ID."""
    try:
        headers = get_bilibili_headers()
        view_url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"
        tags_url = f"https://api.bilibili.com/x/tag/archive/tags?bvid={bvid}"
        
        with httpx.Client(timeout=15.0) as client:
            res_view = client.get(view_url, headers=headers)
            if res_view.status_code != 200:
                return {
                    "error": True,
                    "message": f"Bilibili API returned HTTP status {res_view.status_code}",
                    "channel": "bilibili",
                    "fallback_tried": False
                }
            
            view_data = res_view.json()
            if view_data.get("code") != 0:
                return {
                    "error": True,
                    "message": f"Bilibili API returned error: {view_data.get('message')}",
                    "channel": "bilibili",
                    "fallback_tried": False
                }
                
            data = view_data.get("data", {})
            title = data.get("title", "")
            description = data.get("desc", "")
            uploader = data.get("owner", {}).get("name", "")
            view_count = data.get("stat", {}).get("view", 0)
            
            # Fetch tags
            tags_list = []
            try:
                res_tags = client.get(tags_url, headers=headers)
                if res_tags.status_code == 200:
                    tags_data = res_tags.json()
                    if tags_data.get("code") == 0:
                        tags_list = [t.get("tag_name") for t in tags_data.get("data", []) if t.get("tag_name")]
            except Exception:
                pass  # Fallback to empty tags list
                
            return {
                "bvid": bvid,
                "title": title,
                "uploader": uploader,
                "description": description,
                "view_count": view_count,
                "tags": ", ".join(tags_list) if tags_list else "None",
                "error": False
            }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred fetching Bilibili video: {str(e)}",
            "channel": "bilibili",
            "fallback_tried": False
        }

def search_bilibili(query: str, limit: int = 5) -> dict:
    """Searches Bilibili for videos by keyword query."""
    try:
        headers = get_bilibili_headers()
        # Clean search type video URL
        url = f"https://api.bilibili.com/x/web-interface/search/all/v2?keyword={query}"
        
        with httpx.Client(timeout=15.0) as client:
            res = client.get(url, headers=headers)
            if res.status_code != 200:
                return {
                    "error": True,
                    "message": f"Bilibili API returned HTTP status {res.status_code}",
                    "channel": "bilibili",
                    "fallback_tried": False
                }
                
            data = res.json()
            if data.get("code") != 0:
                # Try fallback search type video
                fallback_url = f"https://api.bilibili.com/x/web-interface/search/type?search_type=video&keyword={query}"
                res_fb = client.get(fallback_url, headers=headers)
                if res_fb.status_code == 200:
                    data = res_fb.json()
                    
            res_data = data.get("data", {})
            result_field = res_data.get("result", {})
            
            video_entries = []
            if isinstance(result_field, dict):
                video_entries = result_field.get("video", [])
            elif isinstance(result_field, list):
                for item in result_field:
                    if isinstance(item, dict) and item.get("result_type") == "video":
                        video_entries = item.get("data", [])
                        break
            
            results = []
            # Strip HTML tags like <em class="keyword"> from search title/desc
            clean_html = re.compile(r"<[^>]+>")
            
            for entry in video_entries[:limit]:
                raw_title = entry.get("title", "")
                title = clean_html.sub("", raw_title)
                
                raw_desc = entry.get("description", "")
                description = clean_html.sub("", raw_desc)
                
                results.append({
                    "bvid": entry.get("bvid"),
                    "title": title,
                    "uploader": entry.get("author"),
                    "description": description,
                    "view_count": entry.get("play"),
                    "tags": entry.get("tag", "")
                })
                
            return {"results": results, "error": False}
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception occurred searching Bilibili: {str(e)}",
            "channel": "bilibili",
            "fallback_tried": False
        }

def probe() -> dict:
    """Probes the Bilibili channel."""
    try:
        headers = get_bilibili_headers()
        with httpx.Client(timeout=5.0) as client:
            res = client.get("https://api.bilibili.com/x/web-interface/nav", headers=headers)
            if res.status_code == 200:
                data = res.json()
                if "code" in data:
                    return {
                        "ok": True,
                        "backend": "Bilibili Public API",
                        "detail": f"Successfully connected. Bilibili code: {data.get('code')}"
                    }
            return {
                "ok": False,
                "backend": "Bilibili Public API",
                "detail": f"API returned status {res.status_code}"
            }
    except Exception as e:
        return {
            "ok": False,
            "backend": "Bilibili Public API",
            "detail": f"Probe error: {str(e)}"
        }
