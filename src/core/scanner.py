import subprocess
import json
import os
import time
import ssl
import socket
import re
from datetime import datetime
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright


def get_ssl_expiry(url):
    """Verifica a validade do certificado SSL"""
    try:
        hostname = urlparse(url).netloc
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=3) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                not_after = cert["notAfter"]
                # Formato: May 30 12:00:00 2025 GMT
                expiry_date = datetime.strptime(not_after, "%b %d %H:%M:%S %Y %Z")
                days_left = (expiry_date - datetime.now()).days
                return days_left
    except:
        return None


def detect_advanced_stack(html, headers):
    """Sherlock 2.0: Detecção Profunda (Plugins WP, Temas, AI Code)"""
    stack = set()
    details = {"plugins": [], "theme": "Unknown", "ai_code": False}

    html_lower = html.lower()
    headers_str = str(headers).lower()

    # --- 1. Frameworks & Infra (Básico) ---
    if "/_next/" in html:
        stack.update(["Next.js", "React"])
    if "react" in html:
        stack.add("React")
    if "vue" in html or "data-v-" in html:
        stack.add("Vue.js")
    if "laravel" in headers_str:
        stack.add("Laravel")
    if "cloudflare" in headers_str:
        stack.add("Cloudflare")
    if "vercel" in headers_str:
        stack.add("Vercel")

    # --- 2. WordPress Deep Dive ---
    if "wp-content" in html_lower:
        stack.add("WordPress")
        # Tenta achar o tema
        theme_match = re.search(r"wp-content/themes/(.*?)/", html)
        if theme_match:
            details["theme"] = theme_match.group(1)

        # Tenta achar plugins comuns
        plugins = re.findall(r"wp-content/plugins/(.*?)/", html)
        details["plugins"] = list(set(plugins))[:10]  # Top 10 plugins

    # --- 3. AI Code Detection (Heurística) ---
    # Padrões comuns de geradores como V0.dev ou Tailwind genérico de LLM
    if "v0_block" in html or "rounded-lg border bg-card text-card-foreground" in html:
        stack.add("AI Generated Code (V0/Shadcn)")
        details["ai_code"] = True

    return list(stack), details


def analyze_security_headers(headers):
    score = 100
    issues = []
    if not headers:
        return {"score": 0, "issues": ["Headers vazios"]}

    h = {k.lower(): v for k, v in headers.items()}

    if "strict-transport-security" not in h:
        score -= 20
        issues.append("Falta HSTS")
    if "x-frame-options" not in h:
        score -= 20
        issues.append("Falta X-Frame-Options")
    if "x-content-type-options" not in h:
        score -= 10
        issues.append("Falta No-Sniff")
    if "x-powered-by" in h:
        score -= 10
        issues.append(f"Leak: {h['x-powered-by']}")
    if "server" in h:
        issues.append(f"Server Info: {h['server']}")

    return {"score": max(0, score), "issues": issues}


def run_lighthouse(url):
    temp_file = "temp_report.json"
    cmd = [
        "lighthouse",
        url,
        "--output=json",
        f"--output-path={temp_file}",
        "--quiet",
        "--chrome-flags='--headless --no-sandbox --disable-gpu --ignore-certificate-errors'",
    ]
    try:
        subprocess.run(" ".join(cmd), shell=True, check=True, stdout=subprocess.DEVNULL)
        with open(temp_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        if os.path.exists(temp_file):
            os.remove(temp_file)
        return data
    except:
        return {"error": "Lighthouse Failed"}


def run_backend_check(url):
    results = {
        "ttfb": 0,
        "headers": {},
        "stack": [],
        "details": {},
        "ssl_days": 0,
        "html_summary": {},
    }

    # Checa SSL fora do browser (mais rápido)
    results["ssl_days"] = get_ssl_expiry(url)

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(args=["--ignore-certificate-errors"])
            page = browser.new_page()
            start = time.time()
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            end = time.time()

            if response:
                # TTFB
                try:
                    results["ttfb"] = int(response.request.timing["responseStart"])
                except:
                    results["ttfb"] = int((end - start) * 1000)

                # Headers
                try:
                    results["headers"] = response.all_headers()
                except:
                    results["headers"] = {}

                # Análise HTML Profunda
                content = page.content()
                results["stack"], results["details"] = detect_advanced_stack(
                    content, results["headers"]
                )
                results["security"] = analyze_security_headers(results["headers"])

                # Extrai resumo do HTML para a IA
                results["html_summary"] = {
                    "title": page.title(),
                    "h1": (
                        page.eval_on_selector("h1", "e => e.innerText")
                        if page.query_selector("h1")
                        else "Sem H1"
                    ),
                    "meta_desc": (
                        page.eval_on_selector(
                            'meta[name="description"]', "e => e.content"
                        )
                        if page.query_selector('meta[name="description"]')
                        else "Sem Meta Desc"
                    ),
                }

            browser.close()
        except Exception as e:
            results["error"] = str(e)

    return results


def parse_data(lh_data, be_data):
    if not lh_data or "error" in lh_data:
        lh_data = {"audits": {}, "categories": {}}

    audits = lh_data.get("audits", {})
    perf = lh_data.get("categories", {}).get("performance", {})
    score = (perf.get("score") * 100) if perf.get("score") else 0

    lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
    cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")

    return {
        "score": int(score),
        "stack": be_data.get("stack", []),
        "wp_details": be_data.get("details", {}),
        "ssl_days": be_data.get("ssl_days", 0),
        "html_context": be_data.get("html_summary", {}),
        "security": be_data.get("security", {}),
        "metrics": {"LCP": lcp, "CLS": cls, "TTFB": f"{be_data.get('ttfb')} ms"},
    }
