import time
from urllib.parse import urlparse, urljoin
from playwright.sync_api import sync_playwright

class WebCrawler:
    def __init__(self, start_url, max_pages=30):
        self.start_url = start_url
        self.domain = urlparse(start_url).netloc
        self.max_pages = max_pages
        self.visited = set()
        self.queue = [start_url]
        self.links_map = {
            "internal": [],
            "external": []
        }

    def is_internal(self, url):
        return self.domain in urlparse(url).netloc

    def _scroll_page(self, page):
        """Rola a página para baixo para ativar Lazy Loading"""
        try:
            for _ in range(5): # Rola 5 vezes
                page.mouse.wheel(0, 15000)
                time.sleep(0.5)
        except:
            pass

    def crawl(self):
        with sync_playwright() as p:
            # MODO STEALTH: Finge ser um usuário real para não ser bloqueado
            browser = p.chromium.launch(
                headless=True, 
                args=["--disable-blink-features=AutomationControlled"]
            )
            
            # Contexto com User Agent de Chrome comum
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                viewport={'width': 1920, 'height': 1080}
            )
            
            page = context.new_page()
            
            while self.queue and len(self.visited) < self.max_pages:
                current_url = self.queue.pop(0)
                
                # Normaliza URL
                if current_url.endswith('/'): current_url = current_url[:-1]
                
                if current_url in self.visited:
                    continue

                try:
                    # Acessa com timeout generoso
                    page.goto(current_url, timeout=20000, wait_until="domcontentloaded")
                    
                    # Rola a página para pegar links do rodapé/lazy load
                    self._scroll_page(page)
                    
                    self.visited.add(current_url)
                    
                    # Extrai hrefs brutos via JS no browser
                    hrefs = page.eval_on_selector_all("a", "elements => elements.map(e => e.getAttribute('href'))")
                    
                    for href in hrefs:
                        if not href: continue
                        
                        # Resolve links relativos (/sobre -> https://site.com/sobre)
                        full_url = urljoin(current_url, href).split('#')[0]
                        
                        # Limpa URLs inválidas
                        if not full_url.startswith('http'): continue
                        if full_url.endswith('/'): full_url = full_url[:-1]

                        if self.is_internal(full_url):
                            if full_url not in self.visited and full_url not in self.queue:
                                self.queue.append(full_url)
                                if full_url not in self.links_map["internal"]:
                                    self.links_map["internal"].append(full_url)
                        else:
                            if full_url not in self.links_map["external"]:
                                self.links_map["external"].append(full_url)

                except Exception as e:
                    pass

            browser.close()
            
        return {
            "scanned_pages": list(self.visited),
            "internal_links": sorted(list(set(self.links_map["internal"]))),
            "external_links": sorted(list(set(self.links_map["external"]))),
            "total_scanned": len(self.visited)
        }

# --- AQUI ESTA A FUNCAO QUE ESTAVA FALTANDO ---
def run_crawler(url):
    spider = WebCrawler(url, max_pages=30)
    return spider.crawl()