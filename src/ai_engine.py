import requests
import json

OLLAMA_API = "http://localhost:11434/api/generate"
PRIMARY_MODEL = "llama3.2"  # <--- MUDANÇA CRUCIAL

def query_ollama(model, prompt):
    payload = {
        "model": model, 
        "prompt": prompt, 
        "stream": False,
        "options": {
            "num_ctx": 2048, # Reduzido de 4096 para 2048 (Mais rápido)
            "temperature": 0.2,
            "top_p": 0.9
        }
    }
    try:
        # Aumentado para 180 segundos (3 minutos) para garantir
        r = requests.post(OLLAMA_API, json=payload, timeout=180)
        
        if r.status_code == 200:
            response_json = r.json()
            return response_json.get("response", "")
        else:
            return f"Erro status {r.status_code}"
            
    except requests.exceptions.Timeout:
        return "⚠️ Erro: O modelo demorou mais de 3 minutos e foi cancelado."
    except Exception as e:
        return f"Erro conexão: {str(e)}"

def analyze_performance(data_summary):
    stack = ", ".join(data_summary.get("stack_detected", ["HTML/Standard"]))
    
    # Prompt focado em QUALIDADE TÉCNICA
    prompt_engineer = f"""
    Você é um Engenheiro de Software Sênior.
    Stack do site: {stack}
    Dados JSON: {json.dumps(data_summary)}
    
    Regras:
    1. NÃO INVENTE CÓDIGO. Use apenas boas práticas reais.
    2. Responda em Português do Brasil.
    3. Seja curto e profissional.
    
    Tarefa:
    Identifique o maior gargalo técnico com base nos números e sugira uma solução real para {stack}.
    """
    
    print(f"DEBUG: Consultando Llama 3.2...")
    tech_analysis = query_ollama(PRIMARY_MODEL, prompt_engineer)
    
    return f"""
# ⚡ Relatório Técnico ({stack})

{tech_analysis}

---
*Gerado por PerfScan v3.5 + Llama 3.2*
"""