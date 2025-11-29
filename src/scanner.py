import subprocess
import json
import os
import time
from playwright.sync_api import sync_playwright


def detect_tech_stack(html, headers):
    """
    Sherlock Holmes digital: analisa HTML e Headers para descobrir a tecnologia.
    """
    stack = set()
    html = html.lower() if html else ""
    headers_str = str(headers).lower() if headers else ""

    # Frameworks & Libs
    if "/_next/" in html or "__next_data__" in html:
        stack.update(["Next.js", "React"])
    elif "react" in html:
        stack.add("React")

    if "vue" in html or "data-v-" in html:
        stack.add("Vue.js")
    if "nuxt" in html:
        stack.add("Nuxt.js")

    if "wordpress" in html or "wp-content" in html:
        stack.add("WordPress")
    if "woocommerce" in html:
        stack.add("WooCommerce")

    if "laravel" in headers_str:
        stack.add("Laravel")
    if "django" in html:
        stack.add("Django")

    if "vite" in html:
        stack.add("Vite")
    if "tailwind" in html:
        stack.add("Tailwind CSS")
    if "bootstrap" in html:
        stack.add("Bootstrap")
    if "jquery" in html:
        stack.add("jQuery")

    # Infra & Servers
    if "cloudflare" in headers_str:
        stack.add("Cloudflare")
    if "vercel" in headers_str:
        stack.add("Vercel")
    if "netlify" in headers_str:
        stack.add("Netlify")
    if "nginx" in headers_str:
        stack.add("Nginx")

    return list(stack) if stack else ["Tech Genérica"]


def analyze_security_headers(headers):
    """
    Auditoria Real de Segurança (Python puro).
    """
    score = 100
    issues = []

    if not headers:
        return {
            "score": 0,
            "issues": ["Não foi possível ler os headers."],
            "secure_headers_count": 0,
        }

    headers_lower = {k.lower(): v for k, v in headers.items()}

    # 1. SSL/HSTS
    if "strict-transport-security" not in headers_lower:
        score -= 20
        issues.append("Falta HSTS (Strict-Transport-Security)")

    # 2. Clickjacking
    if "x-frame-options" not in headers_lower:
        score -= 20
        issues.append("Vulnerável a Clickjacking (Falta X-Frame-Options)")

    # 3. XSS Protection
    if "x-content-type-options" not in headers_lower:
        score -= 10
        issues.append("Falta X-Content-Type-Options (MIME Sniffing)")

    # 4. Leaks
    if "x-powered-by" in headers_lower:
        score -= 10
        issues.append(
            f"Vazamento de Info: X-Powered-By ({headers_lower['x-powered-by']})"
        )

    if "server" in headers_lower:
        # Penalidade leve, pois é comum, mas bom avisar
        issues.append(f"Info do Servidor exposta: {headers_lower['server']}")

    return {
        "score": max(0, score),
        "issues": issues,
        "secure_headers_count": 5 - len(issues),
    }


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
    except Exception as e:
        return {"error": str(e)}


def run_backend_check(url):
    results = {"ttfb": 0, "headers": {}, "status": 0, "stack": [], "security": {}}

    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(args=["--ignore-certificate-errors"])
            page = browser.new_page()

            start = time.time()
            # Timeout aumentado para sites lentos
            response = page.goto(url, wait_until="domcontentloaded", timeout=60000)
            end = time.time()

            if response:
                # TTFB Seguro
                try:
                    timing = response.request.timing
                    if timing["responseStart"] > 0:
                        results["ttfb"] = int(timing["responseStart"])
                    else:
                        results["ttfb"] = int((end - start) * 1000)
                except:
                    results["ttfb"] = int((end - start) * 1000)

                # Headers & Status (Blindado contra erro de 'int object')
                try:
                    if callable(getattr(response, "all_headers", None)):
                        results["headers"] = response.all_headers()
                    else:
                        results["headers"] = response.headers
                except:
                    results["headers"] = {}

                try:
                    if callable(getattr(response, "status", None)):
                        results["status"] = response.status()
                    else:
                        results["status"] = response.status
                except:
                    results["status"] = 0

                # Detecções
                content = page.content()
                results["stack"] = detect_tech_stack(content, results["headers"])
                results["security"] = analyze_security_headers(results["headers"])

            browser.close()
        except Exception as e:
            results["error"] = str(e)

    return results


def parse_data(lh_data, be_data):
    """
    Normaliza os dados e trata erros caso o Lighthouse falhe.
    """
    # Se o Lighthouse falhou ou veio vazio, cria estrutura dummy
    if not lh_data or "error" in lh_data:
        lh_data = {"audits": {}, "categories": {}}

    audits = lh_data.get("audits", {})
    categories = lh_data.get("categories", {})
    performance = categories.get("performance", {})

    # Tratamento de erro na nota (Score)
    raw_score = performance.get("score") if performance else 0
    # Se raw_score for None, vira 0
    score = (raw_score * 100) if raw_score is not None else 0

    # Extração segura de métricas
    lcp = audits.get("largest-contentful-paint", {}).get("displayValue", "N/A")
    cls = audits.get("cumulative-layout-shift", {}).get("displayValue", "N/A")

    # Extração de Oportunidades
    opportunities = []
    for k, v in audits.items():
        # Verifica se v é um dicionário antes de acessar .get
        if isinstance(v, dict):
            op_score = v.get("score")
            op_type = v.get("details", {}).get("type")

            if op_score is not None and op_score < 0.9 and op_type == "opportunity":
                opportunities.append(
                    {
                        "title": v.get("title", "Otimização"),
                        "savings": v.get("metricSavings", {}).get("LCP", 0),
                    }
                )

    return {
        "score": int(score),
        "stack_detected": be_data.get("stack", []),
        "security_audit": be_data.get("security", {}),
        "metrics": {"LCP": lcp, "CLS": cls, "TTFB": f"{be_data.get('ttfb')} ms"},
        "opportunities": opportunities[:5],
    }
