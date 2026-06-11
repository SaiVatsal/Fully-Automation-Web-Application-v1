import json
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.markdown import Markdown

def render_output(data: dict, fmt: str, title: str = "netreach Output"):
    """Formats and prints response dictionary in requested format (text, json, markdown)."""
    console = Console()
    
    # JSON output rendering
    if fmt == "json":
        json_str = json.dumps(data, indent=2, ensure_ascii=False)
        syntax = Syntax(json_str, "json", theme="monokai", background_color="default")
        console.print(syntax)
        return
        
    # Handle error responses globally
    if data.get("error"):
        error_msg = f"[bold red]Error in {data.get('channel', 'channel')}:[/bold red] {data.get('message')}"
        if fmt == "markdown":
            console.print(f"**Error:** {data.get('message')}")
        else:
            console.print(Panel(error_msg, title="[bold red]Error[/bold red]", border_style="red"))
        return

    # Markdown format rendering
    if fmt == "markdown":
        if "content" in data:  # Web
            console.print(data["content"])
        elif "transcript" in data:  # YouTube Transcript
            if data["transcript"]:
                console.print(f"# Transcript for {data['metadata']['title']}\n\n{data['transcript']}")
            else:
                meta = data["metadata"]
                console.print(f"# Metadata for video: {meta['title']}\n\n**Uploader:** {meta['uploader']}\n**Duration:** {meta['duration']}s\n**Views:** {meta['view_count']}\n\n**Description:**\n{meta['description']}")
        elif "results" in data:  # Multi-result searches
            md_lines = []
            for r in data["results"]:
                if "snippet" in r:  # Web search (DDG)
                    md_lines.append(f"### [{r['title']}]({r['url']})\n{r['snippet']}\n")
                elif "text" in r:  # Tweets search
                    md_lines.append(f"### {r['fullname']} ({r['username']}) - {r['date']}\n{r['text']}\n*Likes: {r['likes']}, Retweets: {r['retweets']}*\n")
                elif "score" in r and "subreddit" in r:  # Reddit search
                    md_lines.append(f"### [{r['title']}]({r['url']}) - /r/{r['subreddit']} (Score: {r['score']})\n{r['selftext']}\n")
                elif "stars" in r:  # GitHub search
                    md_lines.append(f"### [{r['name']}]({r['url']}) - ⭐ {r['stars']}\n{r['description']}\n")
                elif "bvid" in r:  # Bilibili search
                    md_lines.append(f"### {r['title']} ({r['bvid']}) - {r['uploader']}\n{r['description']}\n*Views: {r['view_count']}, Tags: {r['tags']}*\n")
            console.print("\n".join(md_lines))
        elif "username" in data and "text" in data:  # Single Tweet
            console.print(f"# Tweet by {data['fullname']} ({data['username']})\n**Date:** {data['date']}\n\n{data['text']}\n\n*Likes: {data['likes']}, Retweets: {data['retweets']}*")
        elif "comments" in data:  # Reddit post
            md_lines = [f"# {data['title']} (by {data['author']} in /r/{data['subreddit']}, Score: {data['score']})"]
            if data["body"]:
                md_lines.append(f"\n{data['body']}")
            md_lines.append("\n## Top Comments")
            for c in data["comments"]:
                md_lines.append(f"**{c['author']}** (Score: {c['score']}):\n{c['body']}\n")
            console.print("\n".join(md_lines))
        elif "stars" in data and "readme" in data:  # GitHub repo
            console.print(f"# {data['name']} - ⭐ {data['stars']}\n{data['description']}\n\n{data['readme']}")
        elif "issues" in data:  # GitHub issues
            md_lines = [f"# Issues list"]
            for issue in data["issues"]:
                md_lines.append(f"- #{issue['number']} {issue['title']} ({issue['state']}) by {issue['author']} - {issue['created_at']}")
            console.print("\n".join(md_lines))
        elif "feed_title" in data:  # RSS feed
            md_lines = [f"# Feed: {data['feed_title']}"]
            for entry in data["entries"]:
                md_lines.append(f"## [{entry['title']}]({entry['link']})\n**Date:** {entry['published']}\n\n{entry['summary']}\n")
            console.print("\n".join(md_lines))
        elif "bvid" in data:  # Bilibili video
            console.print(f"# {data['title']} (BVID: {data['bvid']}) by {data['uploader']}\n**Views:** {data['view_count']} | **Tags:** {data['tags']}\n\n{data['description']}")
        return

    # Text format (default Rich styling)
    if "content" in data:  # Web page
        console.print(Panel(data["content"], title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
    elif "transcript" in data:  # YouTube transcript
        if data["transcript"]:
            console.print(Panel(data["transcript"], title=f"[bold cyan]Transcript: {data['metadata']['title']}[/bold cyan]", border_style="cyan"))
        else:
            meta = data["metadata"]
            desc = f"[bold]Uploader:[/bold] {meta['uploader']}\n[bold]Duration:[/bold] {meta['duration']}s\n[bold]Views:[/bold] {meta['view_count']}\n\n[bold]Description:[/bold]\n{meta['description']}"
            console.print(Panel(desc, title=f"[bold yellow]No Subtitles found - Video Metadata: {meta['title']}[/bold yellow]", border_style="yellow"))
    elif "results" in data:  # Multiple search/list results
        for idx, r in enumerate(data["results"], 1):
            if "snippet" in r:  # DDG search
                console.print(Panel(f"{r['snippet']}\n\n[blue]{r['url']}[/blue]", title=f"[bold cyan]{idx}. {r['title']}[/bold cyan]", border_style="cyan"))
            elif "text" in r:  # Tweets search
                console.print(Panel(f"{r['text']}\n\n[bold yellow]Likes: {r['likes']} | Retweets: {r['retweets']} | {r['date']}[/bold yellow]", title=f"[bold cyan]{idx}. {r['fullname']} ({r['username']})[/bold cyan]", border_style="cyan"))
            elif "score" in r and "subreddit" in r:  # Reddit search
                console.print(Panel(f"{r['selftext']}\n\n[bold yellow]Score: {r['score']} | /r/{r['subreddit']}[/bold yellow]\n[blue]{r['url']}[/blue]", title=f"[bold cyan]{idx}. {r['title']} (by {r['author']})[/bold cyan]", border_style="cyan"))
            elif "stars" in r:  # GitHub search
                console.print(Panel(f"{r['description']}\n\n[bold yellow]Stars: ⭐ {r['stars']}[/bold yellow]\n[blue]{r['url']}[/blue]", title=f"[bold cyan]{idx}. {r['name']}[/bold cyan]", border_style="cyan"))
            elif "bvid" in r:  # Bilibili search
                console.print(Panel(f"{r['description']}\n\n[bold yellow]Views: {r['view_count']} | Tags: {r['tags']}[/bold yellow]", title=f"[bold cyan]{idx}. {r['title']} ({r['bvid']}) by {r['uploader']}[/bold cyan]", border_style="cyan"))
    elif "username" in data and "text" in data:  # Single tweet
        console.print(Panel(f"{data['text']}\n\n[bold yellow]Likes: {data['likes']} | Retweets: {data['retweets']} | {data['date']}[/bold yellow]", title=f"[bold cyan]Tweet by {data['fullname']} ({data['username']})[/bold cyan]", border_style="cyan"))
    elif "comments" in data:  # Reddit post
        post_str = f"{data['body']}\n\n[bold green]-- Top Comments --[/bold green]"
        for c in data["comments"]:
            post_str += f"\n\n[bold]{c['author']}[/bold] (Score: {c['score']})\n{c['body']}"
        console.print(Panel(post_str, title=f"[bold cyan]{data['title']} (Score: {data['score']} | /r/{data['subreddit']})[/bold cyan]", border_style="cyan"))
    elif "stars" in data and "readme" in data:  # GitHub repo
        console.print(Panel(f"[bold yellow]Stars: ⭐ {data['stars']} | Description: {data['description']}[/bold yellow]", title=f"[bold cyan]Repository: {data['name']}[/bold cyan]", border_style="cyan"))
        console.print(Markdown(data["readme"]))
    elif "issues" in data:  # GitHub issues
        issues_str = ""
        for issue in data["issues"]:
            issues_str += f"[bold cyan]#{issue['number']}[/bold cyan] {issue['title']} ({issue['state']}) by [bold]{issue['author']}[/bold] - [yellow]{issue['created_at']}[/yellow]\n"
        console.print(Panel(issues_str.strip(), title=f"[bold cyan]{title}[/bold cyan]", border_style="cyan"))
    elif "feed_title" in data:  # RSS feed
        for idx, entry in enumerate(data["entries"], 1):
            console.print(Panel(f"{entry['summary']}\n\n[bold yellow]Published: {entry['published']}[/bold yellow]\n[blue]{entry['link']}[/blue]", title=f"[bold cyan]{idx}. {entry['title']}[/bold cyan]", border_style="cyan"))
    elif "bvid" in data:  # Bilibili video
        desc = f"{data['description']}\n\n[bold yellow]Views: {data['view_count']} | Tags: {data['tags']}[/bold yellow]"
        console.print(Panel(desc, title=f"[bold cyan]{data['title']} ({data['bvid']}) by {data['uploader']}[/bold cyan]", border_style="cyan"))
