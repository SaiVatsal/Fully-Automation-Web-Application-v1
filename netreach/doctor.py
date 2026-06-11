import importlib
from rich.console import Console
from rich.table import Table

CHANNELS = {
    "web": ("netreach.channels.web", "Check internet connection or r.jina.ai status."),
    "youtube": ("netreach.channels.youtube", "Ensure yt-dlp is installed and up to date."),
    "twitter": ("netreach.channels.twitter", "Ensure snscrape is updated or check Nitter instance urls."),
    "reddit": ("netreach.channels.reddit", "Check if Reddit is blocking requests or adjust User-Agent."),
    "github": ("netreach.channels.github", "Authenticate gh CLI or verify github_token in config.yaml."),
    "bilibili": ("netreach.channels.bilibili", "Check bilibili_sessdata cookie in config.yaml if blocked."),
    "rss": ("netreach.channels.rss", "Check feed URL accessibility or internet connection."),
    "search": ("netreach.channels.search", "DuckDuckGo might be rate-limiting. Try again later."),
}

def run_doctor() -> bool:
    """Runs a live network probe on all channels and prints the results using Rich."""
    console = Console()
    
    table = Table(title="[bold white]netreach Diagnostics (Doctor Report)[/bold white]", title_justify="left")
    table.add_column("Channel Name", style="cyan", no_wrap=True)
    table.add_column("Backend in Use", style="magenta")
    table.add_column("Status", style="bold")
    table.add_column("Fix Hint", style="yellow")
    
    console.print("[bold green]Running live network probes on all channels...[/bold green]\n")
    
    all_ok = True
    for channel, (module_path, fix_hint) in CHANNELS.items():
        try:
            module = importlib.import_module(module_path)
            res = module.probe()
            
            if res.get("ok"):
                status_str = "[green]✓ OK[/green]"
                hint = "-"
            else:
                status_str = "[red]✗ FAIL[/red]"
                hint = f"{fix_hint} Detail: {res.get('detail', 'Unknown error')}"
                all_ok = False
                
            table.add_row(channel, res.get("backend", "Unknown"), status_str, hint)
        except Exception as e:
            table.add_row(channel, "Error loading", "[red]✗ FAIL[/red]", f"Failed to import/run channel: {str(e)}")
            all_ok = False
            
    console.print(table)
    return all_ok
