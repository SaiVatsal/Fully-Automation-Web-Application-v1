# netreach

`netreach` is a production-ready, zero-paid-API Python CLI tool designed to give AI agents (and human operators) full read access to the internet across multiple platforms: web pages, YouTube, Twitter/X, Reddit, GitHub, Bilibili, and RSS feeds. It leverages free, open-source tools with robust backends and fallbacks to ensure stable, reliable operation.

---

## Installation

To install `netreach` globally in editable mode:

```bash
# Clone the repository and navigate into it
cd "C:\Antigravity\Fully Automation"

# Install using pip in editable mode
pip install -e .
```

> [!TIP]
> Twitter/X scraper `snscrape` frequently changes and might require the development version to circumvent API limitations. If Twitter requests fail, run:
> `pip install git+https://github.com/JustAnotherArchivist/snscrape.git`

---

## Platform Support Matrix

| Channel | Out-of-the-Box? | Optional Configuration Key | Description / Fallback |
| :--- | :--- | :--- | :--- |
| **Web** | Yes | None | Reads webpages via Jina Reader (`r.jina.ai`) as clean markdown. |
| **YouTube** | Yes | None | Captures transcripts and search results using `yt-dlp`. |
| **Twitter/X** | Yes | `twitter_cookies` | Uses `snscrape` with a rotation of public **Nitter** web scrapers as fallback. |
| **Reddit** | Yes | `reddit_user_agent` | Resolves posts, comments, and search results via public `.json` endpoints. |
| **GitHub** | Yes | `github_token` | Uses authenticated `gh` CLI if present, falling back to public REST API. |
| **Bilibili** | Yes | `bilibili_sessdata` | Fetches details and searches public API. Cookie unlocks age-restricted content. |
| **RSS** | Yes | None | Retrieves and parses Atom/RSS feeds using `feedparser`. |
| **Search** | Yes | None | Free search using the `duckduckgo_search` library (with 1s rate-limiting safety). |

---

## Quick Start (One Command per Channel)

Test any command using default output formatting (`text`), or specify `--format json` or `--format markdown`.

### 1. Web
```bash
netreach web "https://example.com"
```

### 2. YouTube
```bash
netreach youtube transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
netreach youtube search "python programming" --limit 5
```

### 3. Twitter/X
```bash
netreach twitter tweet "https://twitter.com/jack/status/20"
netreach twitter search "openai" --limit 5
```

### 4. Reddit
```bash
netreach reddit post "https://www.reddit.com/r/python/comments/12345/example/"
netreach reddit search "asyncio" --subreddit python --limit 3
```

### 5. GitHub
```bash
netreach github repo "torvalds/linux"
netreach github issues "torvalds/linux" --limit 5
netreach github search "machine learning" --limit 5
```

### 6. Bilibili
```bash
netreach bilibili video "BV1xx411c7mD"
netreach bilibili search "cooking" --limit 3
```

### 7. RSS Feed
```bash
netreach rss "https://news.ycombinator.com/rss" --limit 5
```

### 8. Web Search
```bash
netreach search "best Python web frameworks 2026" --limit 10
```

---

## Diagnostics & Configuration

### Check Health & Backends
Run `netreach doctor` to verify channel health. It sends live, lightweight probes to verify connectivity and lists the backend currently active:
```bash
netreach doctor
```

### Managing Credentials
Configure optional credentials such as API tokens or session cookies:
```bash
# Set a configuration key
netreach config set github_token ghp_yourtokenhere

# List active configurations (sensitive tokens are masked)
netreach config show
```

---

## Troubleshooting
If you encounter errors:
1. Run `netreach doctor` to pinpoint the failing channel.
2. Verify that your internet connection is active.
3. If GitHub rate-limits you, register a GitHub token using `netreach config set github_token YOUR_TOKEN`.
4. If Twitter fails, verify if Nitter instances are blocked, or update `snscrape` as mentioned in the Tip section.
