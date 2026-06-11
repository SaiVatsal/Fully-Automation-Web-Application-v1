import json
import shutil
import subprocess
import httpx
from netreach.config import load_config

def is_gh_cli_available() -> bool:
    """Checks if gh CLI is installed and authenticated."""
    if shutil.which("gh") is None:
        return False
    try:
        res = subprocess.run(["gh", "auth", "status"], capture_output=True, text=True, check=False)
        return res.returncode == 0
    except Exception:
        return False

def run_gh_cmd(args: list) -> str:
    """Runs a gh CLI command and returns its stdout."""
    res = subprocess.run(["gh"] + args, capture_output=True, text=True, check=True)
    return res.stdout

def get_headers() -> dict:
    """Prepares headers for GitHub API, including token from config if present."""
    config = load_config()
    token = config.get("github_token", "")
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; netreach/1.0)",
        "Accept": "application/vnd.github.v3+json"
    }
    if token:
        headers["Authorization"] = f"token {token}"
    return headers

def get_repo(owner_repo: str) -> dict:
    """Fetches repository details and README content."""
    # Attempt gh CLI first
    if is_gh_cli_available():
        try:
            repo_data_raw = run_gh_cmd(["api", f"repos/{owner_repo}"])
            repo_json = json.loads(repo_data_raw)
            readme_text = run_gh_cmd(["api", f"repos/{owner_repo}/readme", "--accept", "application/vnd.github.raw+json"])
            return {
                "name": repo_json.get("full_name"),
                "description": repo_json.get("description"),
                "stars": repo_json.get("stargazers_count"),
                "readme": readme_text.strip(),
                "error": False,
                "backend": "gh CLI"
            }
        except Exception:
            pass  # Fallback to API
            
    # API Fallback
    try:
        headers = get_headers()
        with httpx.Client(timeout=15.0) as client:
            res_repo = client.get(f"https://api.github.com/repos/{owner_repo}", headers=headers)
            if res_repo.status_code != 200:
                return {
                    "error": True,
                    "message": f"GitHub API returned status {res_repo.status_code}",
                    "channel": "github",
                    "fallback_tried": True
                }
            repo_json = res_repo.json()
            
            headers_readme = headers.copy()
            headers_readme["Accept"] = "application/vnd.github.raw+json"
            res_readme = client.get(f"https://api.github.com/repos/{owner_repo}/readme", headers=headers_readme)
            readme_text = res_readme.text if res_readme.status_code == 200 else "README not found or could not be loaded."
            
            return {
                "name": repo_json.get("full_name"),
                "description": repo_json.get("description"),
                "stars": repo_json.get("stargazers_count"),
                "readme": readme_text.strip(),
                "error": False,
                "backend": "GitHub REST API"
            }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception fetching repo: {str(e)}",
            "channel": "github",
            "fallback_tried": True
        }

def list_issues(owner_repo: str, limit: int = 10) -> dict:
    """Lists issues for the repository."""
    if is_gh_cli_available():
        try:
            res = run_gh_cmd([
                "issue", "list", "-R", owner_repo, "-L", str(limit),
                "--state", "all", "--json", "number,title,state,author,createdAt"
            ])
            issues = json.loads(res)
            formatted_issues = []
            for issue in issues:
                author_data = issue.get("author", {})
                author = author_data.get("login", "") if isinstance(author_data, dict) else str(author_data)
                formatted_issues.append({
                    "number": issue.get("number"),
                    "title": issue.get("title"),
                    "state": issue.get("state"),
                    "author": author,
                    "created_at": issue.get("createdAt")
                })
            return {"issues": formatted_issues, "error": False, "backend": "gh CLI"}
        except Exception:
            pass  # Fallback to API
            
    # API Fallback
    try:
        headers = get_headers()
        url = f"https://api.github.com/repos/{owner_repo}/issues?per_page={limit}&state=all"
        with httpx.Client(timeout=15.0) as client:
            res = client.get(url, headers=headers)
            if res.status_code == 200:
                issues = res.json()
                formatted_issues = []
                for issue in issues:
                    # Filter out PRs if desired, but standard issue endpoints return PRs as well
                    author = issue.get("user", {}).get("login", "")
                    formatted_issues.append({
                        "number": issue.get("number"),
                        "title": issue.get("title"),
                        "state": issue.get("state"),
                        "author": author,
                        "created_at": issue.get("created_at")
                    })
                return {"issues": formatted_issues, "error": False, "backend": "GitHub REST API"}
            else:
                return {
                    "error": True,
                    "message": f"GitHub API returned status {res.status_code}",
                    "channel": "github",
                    "fallback_tried": True
                }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception listing issues: {str(e)}",
            "channel": "github",
            "fallback_tried": True
        }

def search_repos(query: str, limit: int = 10) -> dict:
    """Searches repositories matching the query."""
    if is_gh_cli_available():
        try:
            res = run_gh_cmd(["api", f"search/repositories?q={query}&per_page={limit}"])
            data = json.loads(res)
            items = data.get("items", [])
            results = []
            for item in items:
                results.append({
                    "name": item.get("full_name"),
                    "description": item.get("description"),
                    "stars": item.get("stargazers_count"),
                    "url": item.get("html_url")
                })
            return {"results": results, "error": False, "backend": "gh CLI"}
        except Exception:
            pass  # Fallback to API
            
    # API Fallback
    try:
        headers = get_headers()
        url = f"https://api.github.com/search/repositories?q={query}&per_page={limit}"
        with httpx.Client(timeout=15.0) as client:
            res = client.get(url, headers=headers)
            if res.status_code == 200:
                data = res.json()
                items = data.get("items", [])
                results = []
                for item in items:
                    results.append({
                        "name": item.get("full_name"),
                        "description": item.get("description"),
                        "stars": item.get("stargazers_count"),
                        "url": item.get("html_url")
                    })
                return {"results": results, "error": False, "backend": "GitHub REST API"}
            else:
                return {
                    "error": True,
                    "message": f"GitHub API returned status {res.status_code}",
                    "channel": "github",
                    "fallback_tried": True
                }
    except Exception as e:
        return {
            "error": True,
            "message": f"Exception searching repositories: {str(e)}",
            "channel": "github",
            "fallback_tried": True
        }

def probe() -> dict:
    """Probes the GitHub channel, checking API connectivity."""
    cli_avail = is_gh_cli_available()
    backend = "gh CLI" if cli_avail else "GitHub REST API"
    
    try:
        headers = get_headers()
        with httpx.Client(timeout=5.0) as client:
            res = client.get("https://api.github.com/zen", headers=headers)
            if res.status_code == 200:
                detail = f"api.github.com/zen responded: '{res.text.strip()}'"
                if cli_avail:
                    detail += " (gh CLI is authenticated)"
                return {
                    "ok": True,
                    "backend": backend,
                    "detail": detail
                }
            else:
                if cli_avail:
                    return {
                        "ok": True,
                        "backend": "gh CLI",
                        "detail": f"gh CLI authenticated. REST API zen probe returned status {res.status_code}"
                    }
                return {
                    "ok": False,
                    "backend": "GitHub REST API",
                    "detail": f"GitHub REST API returned status {res.status_code}"
                }
    except Exception as e:
        if cli_avail:
            return {
                "ok": True,
                "backend": "gh CLI",
                "detail": f"gh CLI authenticated. REST API zen probe failed: {str(e)}"
            }
        return {
            "ok": False,
            "backend": "GitHub REST API",
            "detail": f"Probe error: {str(e)}"
        }
