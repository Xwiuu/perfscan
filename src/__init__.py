# src/__init__.py
# Expõe as funções principais para facilitar a importação no main.py

from .scanner import run_lighthouse, run_backend_check, parse_data
from .ai_engine import analyze_performance

__all__ = ['run_lighthouse', 'run_backend_check', 'parse_data', 'analyze_performance']