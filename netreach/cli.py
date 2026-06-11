import sys
import click
from netreach.doctor import run_doctor
from netreach.cli_formatter import render_output

def format_option(f):
    """Reusable decorator for adding --format option to Click commands."""
    return click.option(
        "--format",
        type=click.Choice(["text", "json", "markdown"]),
        default="text",
        help="Output format (text, json, markdown)."
    )(f)

@click.group()
def cli():
    """netreach: Internet reading and searching tool for AI agents and CLI users."""
    pass

# --- Web Channel ---
@cli.command(name="web")
@click.argument("url")
@format_option
def cmd_web(url, format):
    """Fetches clean markdown from any webpage using Jina Reader API."""
    from netreach.channels.web import fetch_web
    res = fetch_web(url)
    render_output(res, format, title=f"Web Reader: {url}")
    if res.get("error"):
        sys.exit(1)

# --- YouTube Channel ---
@cli.group(name="youtube")
def youtube_group():
    """Extract transcripts or search YouTube videos."""
    pass

@youtube_group.command(name="transcript")
@click.argument("url")
@format_option
def cmd_youtube_transcript(url, format):
    """Extracts caption transcripts from a YouTube video URL."""
    from netreach.channels.youtube import get_youtube_transcript
    res = get_youtube_transcript(url)
    render_output(res, format, title="YouTube Transcript")
    if res.get("error"):
        sys.exit(1)

@youtube_group.command(name="search")
@click.argument("query")
@click.option("--limit", type=int, default=5, help="Maximum number of search results.")
@format_option
def cmd_youtube_search(query, limit, format):
    """Searches YouTube videos by keyword query."""
    from netreach.channels.youtube import search_youtube
    res = search_youtube(query, limit=limit)
    render_output(res, format, title=f"YouTube Search: '{query}'")
    if res.get("error"):
        sys.exit(1)

# --- Twitter/X Channel ---
@cli.group(name="twitter")
def twitter_group():
    """Read individual tweets or search Twitter/X."""
    pass

@twitter_group.command(name="tweet")
@click.argument("url")
@format_option
def cmd_twitter_tweet(url, format):
    """Reads a tweet's content and metadata by its URL."""
    from netreach.channels.twitter import get_tweet
    res = get_tweet(url)
    render_output(res, format, title="Twitter Tweet")
    if res.get("error"):
        sys.exit(1)

@twitter_group.command(name="search")
@click.argument("query")
@click.option("--limit", type=int, default=10, help="Maximum number of tweets.")
@format_option
def cmd_twitter_search(query, limit, format):
    """Searches Twitter/X using snscrape / Nitter fallback."""
    from netreach.channels.twitter import search_tweets
    res = search_tweets(query, limit=limit)
    render_output(res, format, title=f"Twitter Search: '{query}'")
    if res.get("error"):
        sys.exit(1)

# --- Reddit Channel ---
@cli.group(name="reddit")
def reddit_group():
    """Read Reddit posts or search Reddit."""
    pass

@reddit_group.command(name="post")
@click.argument("url")
@format_option
def cmd_reddit_post(url, format):
    """Reads a Reddit post and its top 5 comments by URL."""
    from netreach.channels.reddit import get_post
    res = get_post(url)
    render_output(res, format, title="Reddit Post")
    if res.get("error"):
        sys.exit(1)

@reddit_group.command(name="search")
@click.argument("query")
@click.option("--subreddit", type=str, default=None, help="Optional subreddit filter.")
@click.option("--limit", type=int, default=10, help="Maximum number of posts.")
@format_option
def cmd_reddit_search(query, subreddit, limit, format):
    """Searches Reddit posts by keyword query."""
    from netreach.channels.reddit import search_reddit
    res = search_reddit(query, subreddit=subreddit, limit=limit)
    render_output(res, format, title=f"Reddit Search: '{query}'")
    if res.get("error"):
        sys.exit(1)

# --- GitHub Channel ---
@cli.group(name="github")
def github_group():
    """Query GitHub repositories, issues, or search repositories."""
    pass

@github_group.command(name="repo")
@click.argument("owner_repo")
@format_option
def cmd_github_repo(owner_repo, format):
    """Fetches description, stars count, and README for a owner/repo."""
    from netreach.channels.github import get_repo
    res = get_repo(owner_repo)
    render_output(res, format, title=f"GitHub Repository: {owner_repo}")
    if res.get("error"):
        sys.exit(1)

@github_group.command(name="issues")
@click.argument("owner_repo")
@click.option("--limit", type=int, default=10, help="Maximum number of issues.")
@format_option
def cmd_github_issues(owner_repo, limit, format):
    """Lists issues for a repository."""
    from netreach.channels.github import list_issues
    res = list_issues(owner_repo, limit=limit)
    render_output(res, format, title=f"GitHub Issues: {owner_repo}")
    if res.get("error"):
        sys.exit(1)

@github_group.command(name="search")
@click.argument("query")
@click.option("--type", type=click.Choice(["repos"]), default="repos", help="Type of search (repos).")
@click.option("--limit", type=int, default=10, help="Maximum number of search results.")
@format_option
def cmd_github_search(query, type, limit, format):
    """Searches repositories on GitHub."""
    from netreach.channels.github import search_repos
    res = search_repos(query, limit=limit)
    render_output(res, format, title=f"GitHub Search: '{query}'")
    if res.get("error"):
        sys.exit(1)

# --- Bilibili Channel ---
@cli.group(name="bilibili")
def bilibili_group():
    """Search Bilibili videos or read video details."""
    pass

@bilibili_group.command(name="search")
@click.argument("query")
@click.option("--limit", type=int, default=5, help="Maximum number of videos.")
@format_option
def cmd_bilibili_search(query, limit, format):
    """Searches Bilibili for videos."""
    from netreach.channels.bilibili import search_bilibili
    res = search_bilibili(query, limit=limit)
    render_output(res, format, title=f"Bilibili Search: '{query}'")
    if res.get("error"):
        sys.exit(1)

@bilibili_group.command(name="video")
@click.argument("bvid")
@format_option
def cmd_bilibili_video(bvid, format):
    """Reads Bilibili video details by its BVID."""
    from netreach.channels.bilibili import get_video
    res = get_video(bvid)
    render_output(res, format, title="Bilibili Video details")
    if res.get("error"):
        sys.exit(1)

# --- RSS Channel ---
@cli.command(name="rss")
@click.argument("feed_url")
@click.option("--limit", type=int, default=5, help="Maximum number of feed entries.")
@format_option
def cmd_rss(feed_url, limit, format):
    """Parses RSS/Atom feeds and returns recent entries."""
    from netreach.channels.rss import parse_feed
    res = parse_feed(feed_url, limit=limit)
    render_output(res, format, title=f"RSS Feed: {feed_url}")
    if res.get("error"):
        sys.exit(1)

# --- DuckDuckGo Search Channel ---
@cli.command(name="search")
@click.argument("query")
@click.option("--limit", type=int, default=10, help="Maximum number of search results.")
@format_option
def cmd_search(query, limit, format):
    """Performs a web search using DuckDuckGo."""
    from netreach.channels.search import search_ddg
    res = search_ddg(query, limit=limit)
    render_output(res, format, title=f"DuckDuckGo Search: '{query}'")
    if res.get("error"):
        sys.exit(1)

# --- Diagnostics Command ---
@cli.command(name="doctor")
def cmd_doctor():
    """Runs connectivity checks and health probes for all channels."""
    ok = run_doctor()
    if not ok:
        sys.exit(1)

# --- Config Management ---
@cli.group(name="config")
def config_group():
    """Manage configuration options (~/.netreach/config.yaml)."""
    pass

@config_group.command(name="set")
@click.argument("key")
@click.argument("value")
def cmd_config_set(key, value):
    """Sets a configuration setting key to a value."""
    from netreach.config import set_config_value
    try:
        set_config_value(key, value)
        click.echo(f"Successfully set config key '{key}' to '{value}'.")
    except KeyError as e:
        click.echo(str(e), err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error setting configuration: {str(e)}", err=True)
        sys.exit(1)

@config_group.command(name="show")
def cmd_config_show():
    """Displays current configuration keys with masked tokens."""
    from netreach.config import load_config
    cfg = load_config()
    for k, v in cfg.items():
        val_str = v
        # Mask sensitive configuration credentials
        if k in ("github_token", "bilibili_sessdata", "twitter_cookies") and v:
            val_str = v[:4] + "*" * (len(v) - 4) if len(v) > 4 else "****"
        click.echo(f"{k}: {val_str}")

if __name__ == "__main__":
    cli()
