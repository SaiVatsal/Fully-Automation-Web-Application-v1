# Skill: netreach — AI Agent Internet Reading & Searching Tool

This skill explains how an AI agent can use the `netreach` CLI tool to query, search, and parse content from the internet across multiple services using only free, open-source APIs and public scrapers.

---

## Command Reference

| Command | Action Description | Example Command |
| :--- | :--- | :--- |
| `netreach web <url>` | Read webpage clean markdown content via Jina. | `netreach web "https://python.org" --format markdown` |
| `netreach youtube transcript <url>` | Retrieve plain-text transcript of a YouTube video. | `netreach youtube transcript "https://www.youtube.com/watch?v=dQw4w9WgXcQ"` |
| `netreach youtube search <query>` | Search YouTube videos by keyword. | `netreach youtube search "llm agents" --limit 3` |
| `netreach twitter tweet <url>` | Read a specific tweet by its web link. | `netreach twitter tweet "https://twitter.com/jack/status/20"` |
| `netreach twitter search <query>` | Find tweets using keyword search. | `netreach twitter search "openai" --limit 5` |
| `netreach reddit post <url>` | Read a Reddit post and its top 5 comments. | `netreach reddit post "https://reddit.com/r/python/comments/12345"` |
| `netreach reddit search <query>` | Search Reddit posts, optionally filtering by subreddit. | `netreach reddit search "asyncio" --subreddit python --limit 3` |
| `netreach github repo <owner/repo>` | Get repository details, stars, and raw README. | `netreach github repo "torvalds/linux"` |
| `netreach github issues <owner/repo>` | List open/closed issues in a repository. | `netreach github issues "torvalds/linux" --limit 5` |
| `netreach github search <query>` | Search GitHub repositories by keyword. | `netreach github search "transformers" --limit 5` |
| `netreach bilibili video <bvid>` | Read details of a Bilibili video by its BV ID. | `netreach bilibili video "BV1xx411c7mD"` |
| `netreach bilibili search <query>` | Search Bilibili videos by keyword. | `netreach bilibili search "tutorial" --limit 3` |
| `netreach rss <feed_url>` | Parse recent entries from an Atom or RSS feed. | `netreach rss "https://news.ycombinator.com/rss" --limit 5` |
| `netreach search <query>` | Search the web using DuckDuckGo (1s delay). | `netreach search "best python web frameworks 2026"` |
| `netreach doctor` | Run health checks and print diagnostic table. | `netreach doctor` |
| `netreach config set <key> <value>` | Save credentials to local configuration. | `netreach config set github_token ghp_xxxxx` |
| `netreach config show` | View current configurations with masked values. | `netreach config show` |

---

## Output Formats
Every command supports `--format text` (default, with Rich styling), `--format json` (raw machine-readable API response), and `--format markdown` (standard clean markdown).

### JSON Output Format Example
```json
$ netreach search "python" --limit 1 --format json
{
  "results": [
    {
      "title": "Welcome to Python.org",
      "url": "https://www.python.org/",
      "snippet": "The official home of the Python Programming Language. Python is a programming language that lets you work quickly and integrate systems more effectively."
    }
  ],
  "error": false
}
```

### Markdown Output Format Example
```markdown
$ netreach web "https://example.com" --format markdown
# Example Domain

This domain is for use in illustrative examples in documents. You may use this
domain in literature without prior coordination or asking for permission.

[More information...](https://www.iana.org/domains/reserved)
```

---

## Configuration Guidelines
Configuration settings are saved locally to `~/.netreach/config.yaml`.

* **No Setup Required**: `web`, `youtube`, `rss`, and `search` work out-of-the-box without config.
* **Optional Credentials**:
  * Set `github_token` using `netreach config set github_token ghp_xxx` to read private repos and increase API limits.
  * Set `bilibili_sessdata` to access age-restricted Bilibili videos.
  * Set `twitter_cookies` if using authenticated Twitter scraping.

---

## Diagnostics
If a channel fails:
1. Execute `netreach doctor`.
2. Inspect the diagnostic table to check active backends and failure reasons.
3. Apply the listed "Fix Hint" (e.g. updating packages or configuring tokens).
