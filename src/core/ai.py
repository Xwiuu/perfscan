import requests
import json

# URL da API do Ollama
OLLAMA_API = "http://localhost:11434/api/generate"

# Modelo Inteligente
PRIMARY_MODEL = "llama3.2" 

def query_ollama(prompt):
    payload = {
        "model": PRIMARY_MODEL, 
        "prompt": prompt, 
        "stream": False,
        "options": {
            "num_ctx": 8192,  # AUMENTADO: Mais memória para escrever textos longos
            "temperature": 0.3, # Criatividade controlada
            "top_p": 0.9
        }
    }
    try:
        # Timeout aumentado para 4 minutos (Relatórios longos demoram mais)
        r = requests.post(OLLAMA_API, json=payload, timeout=240)
        
        if r.status_code == 200:
            response_json = r.json()
            return response_json.get("response", "")
        else:
            return f"Erro status {r.status_code}"
            
    except Exception as e:
        return f"Erro conexão IA: {str(e)}"

def analyze_performance(data):
    stack = ", ".join(data.get("stack", ["Standard Web"]))
    
    # Prepara dados de segurança para a IA não se perder
    sec_score = data['security'].get('score', 0)
    sec_issues = "\n".join([f"- {i}" for i in data['security'].get('issues', [])])
    if not sec_issues: sec_issues = "Nenhuma falha crítica detectada nos headers padrão."

    # PROMPT "CONSULTORIA DE ELITE"
    prompt_engineer = f"""
    [ROLE]
    Você é um Arquiteto de Soluções Sênior e Especialista em Cibersegurança.
    Você foi contratado para fazer uma auditoria técnica profunda e impiedosa.
    
    [DADOS DO ALVO]
    - Stack Tecnológica: {stack}
    - SSL Status: {data['ssl_days']} dias restantes.
    - Performance (Lighthouse): {data['score']}/100
    - Métricas Vitais: LCP={data['metrics']['LCP']}, CLS={data['metrics']['CLS']}, TTFB={data['metrics']['TTFB']}
    - Score de Segurança: {sec_score}/100
    - Falhas de Segurança Detectadas:
    {sec_issues}

    [DIRETRIZES DE ESCRITA]
    1. SEJA EXTENSO E DETALHADO. Não economize palavras. Explique o "porquê".
    2. Use linguagem corporativa/técnica de alto nível.
    3. NÃO invente dados. Use os números acima.
    4. Use Tabelas Markdown para organizar dados.
    5. Fale Português do Brasil Formal.

    [ESTRUTURA OBRIGATÓRIA DO RELATÓRIO]
    
    # 📑 Dossiê Técnico de Auditoria: {stack}
    
    ## 1. Resumo Executivo
    (Escreva um parágrafo de alto nível sobre a saúde geral do site. Mencione se está crítico ou estável. Fale sobre o impacto disso no negócio/SEO).

    ## 2. Análise de Infraestrutura e Performance
    (Crie uma tabela comparando os valores atuais com os valores ideais do Google).
    (Explique tecnicamente por que o LCP de {data['metrics']['LCP']} está impactando a conversão de usuários. Cite a tecnologia {stack} na explicação).

    ## 3. Diagnóstico de Cibersegurança
    (Analise o Score de {sec_score}/100).
    (Para cada falha listada nos dados, explique o risco real. Ex: Falta de HSTS permite ataques Man-in-the-Middle).
    (Comente sobre a validade do SSL).

    ## 4. Plano de Correção Tática (Roadmap)
    (Crie uma lista numerada detalhada com comandos ou configurações específicas para {stack}).
    (Ex: Se for Nginx, sugira config do Nginx. Se for WP, sugira plugins).

    ---
    *Confidencial • Auditado por PerfScan v6.0*
    """
    
    # print(f"DEBUG: Gerando relatório longo com {PRIMARY_MODEL}...") 
    tech_analysis = query_ollama(prompt_engineer)
    
    if "Erro" in tech_analysis:
        return f"# ⚠️ Falha na Geração do Relatório\n\n{tech_analysis}"

    return tech_analysis