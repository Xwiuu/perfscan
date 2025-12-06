import random
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich.align import Align
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn
from rich.table import Table
from rich.layout import Layout
from rich import box

def generate_sparkline(data_points):
    bars = "  ▂▃▅▆▇"
    return "".join([bars[min(int(x / 15), len(bars)-1)] for x in data_points])

class NeuralDashboard:
    def __init__(self, url):
        self.url = url
        self.logs = []
        self.stack = ["Analyzing signatures..."]
        self.security_score = "PENDING"
        self.status_msg = "INITIALIZING"
        
        self.cpu_history = [random.randint(10, 30) for _ in range(20)]
        self.net_history = [random.randint(0, 10) for _ in range(20)]
        
        self.progress = Progress(
            SpinnerColumn("dots12", style="bold #00ff00"),
            TextColumn("[bold #00ff00]{task.description}"),
            BarColumn(bar_width=None, style="dim #003300", complete_style="bold #00ff00"),
            TextColumn("[bold white]{task.percentage:>3.0f}%"),
            expand=True
        )
        self.task_id = self.progress.add_task("Booting...", total=100)

    def update_logs(self, msg):
        ts = datetime.now().strftime("%H:%M:%S")
        self.logs.append(f"[dim green]>{ts}[/] {msg}")
        if len(self.logs) > 10: self.logs.pop(0)

    def tick(self):
        self.cpu_history.pop(0)
        self.cpu_history.append(random.randint(20, 90))
        self.net_history.pop(0)
        self.net_history.append(random.randint(10, 100))

    def get_header(self):
        grid = Table.grid(expand=True)
        grid.add_column(justify="left", ratio=1)
        grid.add_column(justify="center", ratio=1)
        grid.add_column(justify="right", ratio=1)
        
        status_color = "green" if self.status_msg == "SCANNING" else "cyan"
        
        grid.add_row(
            Text(" PERFSCAN v6.0 ", style="bold black on #00ff00"),
            Text(f" ◉ STATUS: {self.status_msg} ", style=f"bold {status_color}"),
            Text(datetime.now().strftime('%H:%M:%S'), style="dim white")
        )
        return Panel(grid, style="green", box=box.HEAVY_EDGE)

    def make_layout(self):
        layout = Layout()
        layout.split_column(Layout(name="header", size=3), Layout(name="body", ratio=1), Layout(name="footer", size=4))
        layout["body"].split_row(Layout(name="left", size=30), Layout(name="center", ratio=2), Layout(name="right", size=30))
        
        layout["header"].update(self.get_header())
        
        # Left Vitals
        cpu_graph = generate_sparkline(self.cpu_history)
        net_graph = generate_sparkline(self.net_history)
        vitals_grid = Table.grid(expand=True)
        vitals_grid.add_row(f"[bold]CORE LOAD[/] [dim]{self.cpu_history[-1]}%[/]")
        vitals_grid.add_row(f"[red]{cpu_graph}[/]")
        vitals_grid.add_row("")
        vitals_grid.add_row(f"[bold]NET UPLINK[/] [dim]{self.net_history[-1]} Mb/s[/]")
        vitals_grid.add_row(f"[cyan]{net_graph}[/]")
        layout["left"].update(Panel(vitals_grid, title="SYSTEM VITALS", border_style="dim green", box=box.ROUNDED))
        
        # Center Logs
        log_text = "\n".join(self.logs)
        layout["center"].update(Panel(Align.left(log_text, vertical="bottom"), title="[bold green] NEURAL LINK OUTPUT [/]", border_style="#00ff00", box=box.HEAVY))
        
        # Right Intel
        intel_grid = Table.grid(expand=True)
        intel_grid.add_row("[bold underline white]TARGET[/]")
        intel_grid.add_row(f"[cyan]{self.url.replace('https://', '')[:22]}[/]")
        intel_grid.add_row("")
        intel_grid.add_row("[bold underline white]STACK SIGNATURE[/]")
        for tech in self.stack[:4]:
            intel_grid.add_row(f"[magenta]⚡ {tech}[/]")
        intel_grid.add_row("")
        intel_grid.add_row("[bold underline white]SECURITY RATING[/]")
        
        if self.security_score == "PENDING":
            intel_grid.add_row("[yellow blink]CALCULATING...[/]")
        else:
            try:
                score_val = int(self.security_score)
                color = "green" if score_val > 80 else "red"
                intel_grid.add_row(f"[bold {color} reverse]  {score_val}/100  [/]")
            except: intel_grid.add_row(str(self.security_score))

        layout["right"].update(Panel(intel_grid, title="TARGET INTEL", border_style="cyan", box=box.ROUNDED))
        layout["footer"].update(Panel(self.progress, border_style="green", box=box.DOUBLE))
        
        return layout