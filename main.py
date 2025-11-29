import sys
import time
import asyncio
import os
import random
import string
from datetime import datetime

from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.markdown import Markdown
from rich.layout import Layout
from rich import box
import pyfiglet

# Importa módulos locais
from src.scanner import run_lighthouse, run_backend_check, parse_data
from src.ai_engine import analyze_performance

console = Console()

# --- 1. UTILITÁRIOS GRÁFICOS ---


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def generate_sparkline(data_points):
    """Gera um mini gráfico de linha (  ▂▃▅▆▇)"""
    bars = "  ▂▃▅▆▇"
    return "".join([bars[min(int(x / 15), len(bars) - 1)] for x in data_points])


def get_header(status="IDLE"):
    """Cabeçalho com Status Pulsante"""
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="center", ratio=1)
    grid.add_column(justify="right", ratio=1)

    # Status Colorido
    status_color = (
        "green"
        if status == "SCANNING"
        else "cyan" if status == "AI THINKING" else "white"
    )

    grid.add_row(
        Text(" PERFSCAN v5.0 ", style="bold black on #00ff00"),
        Text(f" ◉ SYSTEM STATUS: {status} ", style=f"bold {status_color}"),
        Text(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), style="dim white"),
    )
    return Panel(grid, style="green", box=box.HEAVY_EDGE)


def show_intro():
    """INTRODUÇÃO CINEMATOGRÁFICA (DECODIFICAÇÃO)"""
    clear_screen()
    try:
        f = pyfiglet.Figlet(font="ansi_shadow")
    except:
        f = pyfiglet.Figlet(font="slant")

    ascii_art = f.renderText("PERFSCAN")
    lines = ascii_art.split("\n")
    height = len(lines) + 2

    subtitle = "NEURAL NETWORK ANALYSIS TOOL // ONLINE"
    chars = string.ascii_uppercase + string.digits + "@#$%&"

    with Live(console=console, refresh_per_second=20) as live:
        # Fase 1: Decode do Título (Glitch)
        for i in range(25):
            text = Text()
            for line in lines:
                if not line.strip():
                    text.append("\n")
                    continue
                new_line = ""
                for char in line:
                    if char == " " or random.random() > 0.8:
                        new_line += char
                    else:
                        new_line += random.choice(chars) if i < 20 else char

                color = (
                    random.choice(["green", "bright_green", "white"])
                    if i > 22
                    else "green"
                )
                text.append(new_line + "\n", style=f"bold {color}")

            panel = Panel(
                Align.center(text),
                border_style="green",
                box=box.DOUBLE,
                padding=(1, 2),
                height=height + 4,
            )
            live.update(panel)
            time.sleep(0.04)

        # Fase 2: Decode do Subtítulo
        final_art = Text(ascii_art, style="bold #00ff00")
        for i in range(len(subtitle) + 5):
            display_sub = ""
            for idx, char in enumerate(subtitle):
                if idx < i:
                    display_sub += char
                else:
                    display_sub += random.choice(chars)

            # Monta Grid
            content = Table.grid(expand=True)
            content.add_column(justify="center")
            content.add_row(final_art)
            content.add_row(Text(display_sub[: len(subtitle)], style="bold cyan"))

            panel = Panel(
                content,
                border_style="#00ff00",
                box=box.DOUBLE,
                title="[bold black on #00ff00] SYSTEM ROOT [/]",
                subtitle="[dim]AUTHORIZED ACCESS ONLY[/dim]",
                padding=(1, 2),
                height=height + 4,
            )
            live.update(panel)
            time.sleep(0.02)

    time.sleep(0.5)


def show_menu():
    console.print("")
    grid = Table.grid(padding=(0, 2))
    grid.add_column(justify="right", style="bold cyan")
    grid.add_column(justify="left", style="white")

    options = [
        ("1", "Frontend Scan"),
        ("2", "Security Audit"),
        ("3", "Backend Latency"),
        ("4", "FULL SYSTEM SCAN"),
        ("0", "Exit"),
    ]
    for k, v in options:
        grid.add_row(f"[{k}]", v)

    console.print(
        Panel(
            Align.center(grid),
            title="PROTOCOL SELECTION",
            border_style="green",
            expand=False,
        )
    )
    return IntPrompt.ask(
        "\n[bold green]root@perfscan:~$[/] Command",
        choices=["0", "1", "2", "3", "4"],
        default="4",
    )


# --- 2. DASHBOARD "GOD MODE" ---


class NeuralDashboard:
    def __init__(self, url):
        self.url = url
        self.logs = []
        self.stack = ["Analyzing signatures..."]
        self.security_score = "PENDING"
        self.status_msg = "INITIALIZING"

        # Dados para gráficos vivos
        self.cpu_history = [random.randint(10, 30) for _ in range(20)]
        self.net_history = [random.randint(0, 10) for _ in range(20)]

        self.progress = Progress(
            # CORRIGIDO AQUI: Spinner como argumento posicional
            SpinnerColumn("dots12", style="bold #00ff00"),
            TextColumn("[bold #00ff00]{task.description}"),
            BarColumn(
                bar_width=None, style="dim #003300", complete_style="bold #00ff00"
            ),
            TextColumn("[bold white]{task.percentage:>3.0f}%"),
            expand=True,
        )
        self.task_id = self.progress.add_task("Booting...", total=100)

    def update_logs(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[dim green]>{ts}[/] {msg}")
        if len(self.logs) > 10:
            self.logs.pop(0)

    def tick(self):
        """Atualiza os dados falsos para dar vida ao layout"""
        # Simula CPU variando
        self.cpu_history.pop(0)
        self.cpu_history.append(random.randint(20, 90))
        # Simula Rede
        self.net_history.pop(0)
        self.net_history.append(random.randint(10, 100))

    def make_layout(self):
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="body", ratio=1),
            Layout(name="footer", size=4),
        )
        layout["body"].split_row(
            Layout(name="left", size=30),
            Layout(name="center", ratio=2),
            Layout(name="right", size=30),
        )

        # 1. Header Dinâmico
        layout["header"].update(get_header(self.status_msg))

        # 2. Left: System Vitals (Com Sparklines)
        cpu_graph = generate_sparkline(self.cpu_history)
        net_graph = generate_sparkline(self.net_history)

        vitals_grid = Table.grid(expand=True)
        vitals_grid.add_row(f"[bold]CORE LOAD[/] [dim]{self.cpu_history[-1]}%[/]")
        vitals_grid.add_row(f"[red]{cpu_graph}[/]")
        vitals_grid.add_row("")
        vitals_grid.add_row(f"[bold]NET UPLINK[/] [dim]{self.net_history[-1]} Mb/s[/]")
        vitals_grid.add_row(f"[cyan]{net_graph}[/]")
        vitals_grid.add_row("")
        vitals_grid.add_row("[bold]ACTIVE THREADS:[/]")
        vitals_grid.add_row(f"[yellow]{random.randint(4, 12)} workers online[/]")

        layout["left"].update(
            Panel(
                vitals_grid,
                title="SYSTEM VITALS",
                border_style="dim green",
                box=box.ROUNDED,
            )
        )

        # 3. Center: Terminal Logs
        log_text = "\n".join(self.logs)
        layout["center"].update(
            Panel(
                Align.left(log_text, vertical="bottom"),
                title="[bold green] NEURAL LINK OUTPUT [/]",
                border_style="#00ff00",
                box=box.HEAVY,
                padding=(0, 1),
            )
        )

        # 4. Right: Target Intel (Visual Hacker)
        intel_grid = Table.grid(expand=True)
        intel_grid.add_row("[bold underline white]TARGET[/]")
        intel_grid.add_row(f"[cyan]{self.url.replace('https://', '')[:22]}[/]")
        intel_grid.add_row("")

        intel_grid.add_row("[bold underline white]STACK SIGNATURE[/]")
        if len(self.stack) > 1:
            for tech in self.stack[:4]:
                intel_grid.add_row(f"[magenta]⚡ {tech}[/]")
        else:
            intel_grid.add_row("[dim blink]Scanning...[/]")

        intel_grid.add_row("")
        intel_grid.add_row("[bold underline white]SECURITY RATING[/]")

        if self.security_score == "PENDING":
            intel_grid.add_row("[yellow blink]CALCULATING...[/]")
        else:
            try:
                score_val = int(self.security_score)
                color = "green" if score_val > 80 else "red"
                intel_grid.add_row(f"[bold {color} reverse]  {score_val}/100  [/]")
            except:
                intel_grid.add_row("[red]ERROR[/]")

        layout["right"].update(
            Panel(
                intel_grid, title="TARGET INTEL", border_style="cyan", box=box.ROUNDED
            )
        )

        # 5. Footer: Progress
        layout["footer"].update(
            Panel(self.progress, border_style="green", box=box.DOUBLE)
        )

        return layout


# --- 3. FLUXO PRINCIPAL ---


async def run_scan_flow(url, mode):
    dash = NeuralDashboard(url)

    # Refresh rate alto para animação fluida
    with Live(dash.make_layout(), refresh_per_second=15, console=console) as live:

        def step(msg, prog, status="SCANNING"):
            dash.update_logs(msg)
            dash.status_msg = status
            dash.progress.update(dash.task_id, completed=prog, description=status)

            # Animação dos gráficos
            for _ in range(5):
                dash.tick()
                live.update(dash.make_layout())
                time.sleep(0.05)

        step("Initializing handshake protocols...", 5)

        # Lighthouse
        step(f"Injecting Lighthouse probe into {url}...", 10, "FRONTEND SCAN")
        lh_data = await asyncio.to_thread(run_lighthouse, url)
        step("[bold green]Frontend metrics captured.[/]", 30)

        # Backend
        step("Analyzing server headers & latency...", 40, "DEEP SCAN")
        be_data = await asyncio.to_thread(run_backend_check, url)

        if "stack" in be_data:
            dash.stack = be_data["stack"]
        if "security" in be_data:
            dash.security_score = str(be_data["security"].get("score", 0))

        step("Security audit complete.", 60)

        # AI
        step("Normalizing data structures for LLM...", 70, "DATA PROCESSING")
        parsed = parse_data(lh_data, be_data)

        step("[bold magenta]ENGAGING LLAMA 3.2 NEURAL ENGINE...[/]", 80, "AI THINKING")
        step("[dim]Synthesizing professional report...[/]", 85)

        # Espera um pouco mais na IA para dar efeito
        for _ in range(10):
            dash.tick()
            live.update(dash.make_layout())
            time.sleep(0.1)

        report = await asyncio.to_thread(analyze_performance, parsed)

        step("[bold green]AUDIT COMPLETE. SYSTEM STANDBY.[/]", 100, "FINISHED")
        await asyncio.sleep(1)

    return report


def save_report_disk(url, content):
    if not os.path.exists("reports"):
        os.makedirs("reports")
    safe_url = url.replace("http://", "").replace("https://", "").replace("/", "_")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/AUDIT_{safe_url}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename


def main():
    while True:
        show_intro()

        mode = show_menu()
        if mode == 0:
            break

        url = Prompt.ask("\n[bold green]root@perfscan:~$[/] Target URL")
        if not url.startswith("http"):
            url = "http://" + url

        console.print(f"\n[bold yellow]>>> INITIALIZING SEQUENCE: {url}[/bold yellow]")
        time.sleep(1)

        try:
            report = asyncio.run(run_scan_flow(url, mode))
            console.rule("[bold cyan] MISSION REPORT [/bold cyan]")
            console.print(Panel(Markdown(report), border_style="cyan", box=box.ROUNDED))
            fname = save_report_disk(url, report)
            console.print(f"\n[bold black on green] REPORT SAVED: {fname} [/]")
        except Exception as e:
            console.print_exception()

        if Prompt.ask("\n[bold]Run again?[/]", choices=["y", "n"], default="y") == "n":
            break


if __name__ == "__main__":
    main()
