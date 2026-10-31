"""
Launcher para Asistente de Formalización de Préstamos Personales (CDA).
Detecta puertos disponibles dinámicamente para evitar errores WinError 10013 / WSAEADDRINUSE.
Abre automáticamente el navegador en la consola local.
"""

import os
import sys
import socket
import webbrowser
import threading
import time
from pathlib import Path

# Asegurar que el directorio del script esté siempre en sys.path
SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

def find_available_port(preferred_ports=[8085, 8080, 8090, 8095, 8888]):
    for port in preferred_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def open_browser_delayed(url):
    time.sleep(1.2)
    webbrowser.open(url)

if __name__ == "__main__":
    port = find_available_port()
    url = f"http://127.0.0.1:{port}"
    
    print("=" * 70)
    print("  CAJA DE AHORROS DE PANAMÁ - CÉLULA DE INNOVACIÓN")
    print("  Copiloto Inteligente de Formalización de Préstamos Personales")
    print(f"  Servidor HTTP local disponible en: {url}")
    print("=" * 70)
    
    threading.Thread(target=open_browser_delayed, args=(url,), daemon=True).start()

    import uvicorn
    from app import app
    
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="info")
