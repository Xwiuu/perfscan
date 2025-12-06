import sys
import asyncio
import time
import os
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.live import Live
from rich import box
from rich.prompt import Prompt

# IMPORTS DA ARQUITETURA MVC (Sherlock + Neural Engine + UI)
from src.ui.banners import show_intro, show_menu, clear_screen
from src.ui.dashboard import NeuralDashboard
from src.core.scanner import run_lighthouse, run_backend_check, parse_data
from src.core.ai import analyze_performance
from src.core.crawler import run_crawler
from src.utils.pdf_generator import generate_pdf

console = Console()

def save_report_disk(url, content, prefix="AUDIT"):
    """Salva o relatório em Markdown na pasta reports"""
    if not os.path.exists("reports"): os.makedirs("reports")
    safe_url = url.replace("http://", "").replace("https://", "").replace("/", "_")
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"reports/{prefix}_{safe_url}_{timestamp}.md"
    with open(filename, "w", encoding="utf-8") as f: f.write(content)
    return filename

async def run_scan_flow(url, mode):
    """Fluxo Principal: Scan + Segurança + IA Consultora"""
    dash = NeuralDashboard(url)
    
    with Live(dash.make_layout(), refresh_per_second=15, console=console) as live:
        def step(msg, prog, status="SCANNING"):
            dash.update_logs(msg)
            dash.status_msg = status
            dash.progress.update(dash.task_id, completed=prog, description=status)
            for _ in range(5): 
                dash.tick()
                live.update(dash.make_layout())
                time.sleep(0.05)

        step("Initializing handshake protocols...", 5)
        
        # 1. Frontend (Lighthouse)
        step(f"Injecting Lighthouse probe...", 10, "FRONTEND SCAN")
        lh_data = await asyncio.to_thread(run_lighthouse, url)
        step("[bold green]Frontend metrics captured.[/]", 30)

        # 2. Backend & Security (Sherlock 2.0)
        step("Analyzing server headers, SSL & deep stack...", 40, "DEEP SCAN")
        be_data = await asyncio.to_thread(run_backend_check, url)
        
        # Atualiza a UI com dados reais
        if "stack" in be_data: dash.stack = be_data["stack"]
        if "security" in be_data: dash.security_score = str(be_data["security"].get("score", 0))
        
        step("Security audit & Tech detection complete.", 60)

        # 3. AI Processing
        step("Normalizing data structures for LLM...", 70, "DATA PROCESSING")
        parsed = parse_data(lh_data, be_data)
        
        step("[bold magenta]ENGAGING LLAMA 3.2 EXECUTIVE MODE...[/]", 80, "AI ANALYSIS")
        step("[dim]Drafting detailed technical dossier...[/]", 85)
        
        # Tempo extra para a IA pensar (Relatório longo demora mais)
        for _ in range(20):
            dash.tick()
            live.update(dash.make_layout())
            time.sleep(0.1)
            
        report = await asyncio.to_thread(analyze_performance, parsed)
        
        step("[bold green]AUDIT COMPLETE. DOSSIER READY.[/]", 100, "FINISHED")
        await asyncio.sleep(1)

    return report

async def run_crawler_flow(url):
    """Fluxo Secundário: Spider Crawler"""
    dash = NeuralDashboard(url)
    
    with Live(dash.make_layout(), refresh_per_second=15, console=console) as live:
        dash.status_msg = "SPIDER BOT"
        dash.update_logs("[bold yellow]🕷️  RELEASING STEALTH SPIDER (V4.0)...[/]")
        dash.progress.update(dash.task_id, description="MAPPING")
        
        # Roda o crawler
        data = await asyncio.to_thread(run_crawler, url)
        
        # Efeito Matrix dos links encontrados
        total_pages = len(data.get('scanned_pages', []))
        if total_pages == 0: total_pages = 1 
        
        for i, page in enumerate(data.get('scanned_pages', [])):
            progress = ((i + 1) / total_pages) * 100
            clean_page = page.replace(url, "")
            if not clean_page: clean_page = "/"
            
            dash.update_logs(f"[green]FOUND NODE: {clean_page}[/]")
            dash.progress.update(dash.task_id, completed=progress)
            dash.tick()
            live.update(dash.make_layout())
            time.sleep(0.05)
        
        dash.update_logs(f"[bold cyan]MAP COMPLETE. {len(data.get('internal_links', []))} LINKS INDEXED.[/]")
        dash.status_msg = "FINISHED"
        live.update(dash.make_layout())
        time.sleep(1)
        
        internal_list = "\n".join([f"- {link}" for link in data.get('internal_links', [])[:50]])
        external_list = "\n".join([f"- {link}" for link in data.get('external_links', [])])
        
        return f"""
# 🕸️ Mapeamento Tático do Site

**Alvo:** {url}
**Total de Páginas Escaneadas:** {data.get('total_scanned', 0)}

## 🔗 Estrutura Interna (Top 50)
{internal_list}

## 🌍 Conexões Externas
{external_list}

---
*Mapeado por PerfScan v6.0*
"""

def main():
    while True:
        show_intro()
        mode = show_menu()
        
        if mode == 0: break
            
        url = Prompt.ask("\n[bold green]root@perfscan:~$[/] Target URL")
        if not url.startswith("http"): url = "http://" + url
        
        try:
            # ROTEAMENTO DE MODOS
            if mode == 5:
                report = asyncio.run(run_crawler_flow(url))
                prefix = "MAP"
                border_color = "green"
            else:
                report = asyncio.run(run_scan_flow(url, mode))
                prefix = "AUDIT"
                border_color = "white"
            
            # EXIBIÇÃO NO TERMINAL (ESTILO DOCUMENTO CONFIDENCIAL)
            console.rule(f"[bold {border_color}] RELATÓRIO FINAL [/bold {border_color}]")
            console.print(
                Panel(
                    Markdown(report), 
                    border_style=border_color, 
                    box=box.DOUBLE_EDGE, # Borda dupla chique
                    title=f"[bold black on {border_color}] PERFSCAN INTELLIGENCE REPORT [/]",
                    subtitle="[dim]Role para cima para ler o dossiê completo[/dim]",
                    padding=(1, 2)
                )
            )
            
            # SALVAMENTO EM DISCO (MD)
            fname = save_report_disk(url, report, prefix)
            console.print(f"\n[bold black on green] MARKDOWN SAVED: {fname} [/]")
            
            # GERAÇÃO DE PDF
            console.print("[bold yellow]📄 GENERATING EXECUTIVE PDF...[/]")
            try:
                pdf_file = asyncio.run(asyncio.to_thread(generate_pdf, report, fname))
                console.print(f"[bold black on cyan] PDF EXPORTED: {pdf_file} [/]")
            except Exception as pdf_err:
                console.print(f"[red]❌ PDF Generation Failed (Check dependencies): {pdf_err}[/]")
            
        except Exception as e:
            console.print_exception()
        
        if Prompt.ask("\n[bold]New Mission?[/]", choices=["y", "n"], default="y") == "n": break

if __name__ == "__main__":
    main()