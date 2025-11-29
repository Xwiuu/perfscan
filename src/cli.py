import sys
import time
import asyncio
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TimeElapsedColumn
from rich.markdown import Markdown
from rich.align import Align
from rich.text import Text
from rich import box
import pyfiglet

# Importa as lógicas que já criamos
from src.scanner import run_lighthouse, run_backend_check, parse_data
from src.ai_engine import analyze_performance

# Configuração do Console Neon
console = Console()

def print_banner():
    """Imprime o título ASCII neon"""
    f = pyfiglet.Figlet(font='slant')
    title = f.renderText("PerfScan CLI")
    
    # Cria o painel de cabeçalho
    text = Text(title, style="bold #00FF00")
    console.print(Panel(
        Align.center(text),
        subtitle="[bold #00FFFF] Performance | Segurança | Backend [/]",
        border_style="#00FF00",
        box=box.DOUBLE
    ))
    console.print("")

def save_report(url, content):
    import os
    from datetime import datetime
    if not os.path.exists("reports"):
        os.makedirs("reports")
    safe_url = url.replace("http://", "").replace("https://", "").replace("/", "_").replace(":", "-")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/CLI_REPORT_{safe_url}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(content)
    return filename

async def main():
    # 1. Verifica argumentos
    if len(sys.argv) < 2:
        console.print("[bold red]❌ ERRO: Faltou a URL![/]")
        console.print("   Uso: [cyan]python cli.py http://exemplo.com[/]")
        return

    url = sys.argv[1]
    print_banner()

    console.print(f"[bold #00FFFF]>>> ALVO IDENTIFICADO: {url}[/]\n")

    # Variáveis para guardar dados
    lh_data = None
    be_data = None
    
    # 2. Barra de Progresso Estilosa
    with Progress(
        SpinnerColumn(style="bold #FF00FF"),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(bar_width=None, style="#00FF00", complete_style="#00FF00"),
        TimeElapsedColumn(),
        console=console
    ) as progress:
        
        # Tarefa 1: Lighthouse
        task1 = progress.add_task("[yellow]Scanner Frontend (Lighthouse)...", total=100)
        
        # Truque pra rodar assíncrono dentro do progress bar sincrono
        # Rodamos o lighthouse (que demora) e simulamos updates visuais se quiser
        # Como o run_lighthouse bloqueia, ele vai parar a barra um pouco, mas ok para CLI simples
        
        lh_data = await asyncio.to_thread(run_lighthouse, url)
        progress.update(task1, advance=100, description="[bold #00FF00]Frontend Finalizado.")

        # Tarefa 2: Backend
        task2 = progress.add_task("[yellow]Scanner Backend & TTFB...", total=100)
        time.sleep(0.5) # Charme visual
        be_data = await asyncio.to_thread(run_backend_check, url)
        progress.update(task2, advance=100, description=f"[bold #00FF00]Backend Check: {be_data.get('ttfb')}ms")

    # 3. Processamento IA (Spinner separado para dar destaque)
    console.print("\n[bold #00FFFF]>>> INICIANDO PROTOCOLO NEURAL (IA)...[/]")
    
    parsed = parse_data(lh_data, be_data)
    ai_report = ""

    # Status animado enquanto a IA pensa
    with console.status("[bold #FF00FF]Carregando modelos locais e raciocinando...[/]", spinner="aesthetic"):
        ai_report = await asyncio.to_thread(analyze_performance, parsed)
    
    console.print("[bold #00FF00]>>> ANÁLISE CONCLUÍDA.[/]\n")

    # 4. Imprime o Relatório Bonito no Terminal
    console.rule("[bold #00FFFF] RELATÓRIO DO MENTOR [/]")
    md = Markdown(ai_report)
    console.print(Panel(md, border_style="#00FFFF", title="Diagnóstico Final", padding=(1, 2)))

    # 5. Salva
    file_saved = save_report(url, ai_report)
    console.print(f"\n[bold green]💾 Relatório salvo em: {file_saved}[/]")

if __name__ == "__main__":
    asyncio.run(main())