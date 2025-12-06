import random
import string
import time
from datetime import datetime
from rich.console import Console
from rich.panel import Panel
from rich.live import Live
from rich.text import Text
from rich.align import Align
from rich.table import Table
from rich.prompt import IntPrompt
from rich import box
import pyfiglet
import os

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_intro():
    clear_screen()
    try: f = pyfiglet.Figlet(font='ansi_shadow')
    except: f = pyfiglet.Figlet(font='slant')

    ascii_art = f.renderText("PERFSCAN")
    lines = ascii_art.split("\n")
    height = len(lines) + 2
    
    with Live(console=console, refresh_per_second=20) as live:
        for i in range(25):
            text = Text()
            for line in lines:
                if not line.strip(): 
                    text.append("\n")
                    continue
                new_line = ""
                chars = string.ascii_uppercase + string.digits + "@#&"
                for char in line:
                    new_line += random.choice(chars) if random.random() > 0.7 else char
                
                color = "green" if i > 20 else "white"
                text.append(new_line + "\n", style=f"bold {color}")
            
            panel = Panel(Align.center(text), border_style="green", box=box.DOUBLE, padding=(1, 2), height=height + 4)
            live.update(panel)
            time.sleep(0.04)

        final_art = Text(ascii_art, style="bold #00ff00")
        panel = Panel(
            Align.center(final_art),
            border_style="#00ff00",
            box=box.DOUBLE,
            title="[bold black on #00ff00] SYSTEM V6.0 - ARCHITECT [/]",
            subtitle="[dim]AUTHORIZED ACCESS ONLY[/dim]",
            padding=(1, 2),
            height=height + 4
        )
        live.update(panel)
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
        ("5", "SPIDER CRAWLER (Site Map)"),  # <--- ADICIONE ESTA LINHA
        ("0", "Exit")
    ]
    for k, v in options:
        grid.add_row(f"[{k}]", v)
    
    console.print(Panel(Align.center(grid), title="PROTOCOL SELECTION", border_style="green", expand=False))
    return IntPrompt.ask("\n[bold green]root@perfscan:~$[/] Command", choices=["0","1","2","3","4","5"], default="4")