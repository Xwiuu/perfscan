import socket
import dns.resolver
import concurrent.futures
from urllib.parse import urlparse

class ReconScanner:
    def __init__(self, target_url):
        self.target = target_url
        self.domain = urlparse(target_url).netloc
        self.results = {
            "ip": "N/A",
            "open_ports": [],
            "dns_records": {},
            "subdomains": []
        }

    def resolve_ip(self):
        try:
            self.results["ip"] = socket.gethostbyname(self.domain)
        except:
            self.results["ip"] = "Unknown"

    def scan_port(self, port):
        """Verifica se uma porta está aberta (Socket rápido)"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(0.5) # Timeout curto para ser rápido
            result = sock.connect_ex((self.domain, port))
            sock.close()
            if result == 0:
                return port
        except:
            pass
        return None

    def scan_ports_parallel(self):
        """Scan multithread das top 20 portas mais comuns"""
        common_ports = [21, 22, 23, 25, 53, 80, 110, 135, 139, 143, 443, 445, 993, 995, 1433, 3306, 3389, 5432, 8080, 8443]
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            results = executor.map(self.scan_port, common_ports)
        
        self.results["open_ports"] = [p for p in results if p is not None]

    def get_dns_records(self):
        """Extrai registros DNS importantes (MX = Email, TXT = Verificações)"""
        record_types = ['A', 'MX', 'NS', 'TXT']
        for r_type in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, r_type)
                self.results["dns_records"][r_type] = [r.to_text() for r in answers]
            except:
                pass

    def run(self):
        self.resolve_ip()
        self.get_dns_records()
        self.scan_ports_parallel()
        return self.results

def run_recon(url):
    scanner = ReconScanner(url)
    return scanner.run()