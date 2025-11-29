# ui.py
from textual.widgets import Static
from rich.panel import Panel
from rich.text import Text
from rich.console import Group
from rich.align import Align
from rich import box
import pyfiglet

class RetroTitle(Static):
    """O cabeçalho estilo hacker com título e 'abas'."""
    def render(self):
        f = pyfiglet.Figlet(font='slant')
        title_text = Text(f.renderText("PerfScan"), style="bold #00FF00")
        
        tabs_text = Text(
            " Performance | Segurança | Backend | ", 
            style="bold #00FFFF", 
            justify="center"
        )
        tabs_text.append("COMPLETO", style="bold white on #008800")
        
        content = Group(Align.center(title_text), Align.center(tabs_text))
        return Panel(content, style="#00FF00", box=box.DOUBLE)

class Waveform(Static):
    def render(self):
        wave = " ▂▃▅▆▇█▇▆▅▃▂ ▂▃▅▆▇█▓▒░░▒▓█▇▆▅▃▂ ▂▃▅▆▇█"
        return Panel(Align.center(Text(wave, style="bold #00FFFF")), title="FLUXO DE DADOS", style="#00FFFF")