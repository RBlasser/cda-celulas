"""
Launcher para Asesor Virtual de Auto - Feria Caja de Ahorros con Chainlit.
Incluye:
- Detección dinámica de puerto disponible para evitar conflictos en Windows.
- Parche de compatibilidad para Python 3.14 (neutralización de nest_asyncio.apply).
"""

import sys
import socket
import nest_asyncio

# Neutralizar nest_asyncio para evitar que altere asyncio en Python 3.14
nest_asyncio.apply = lambda *args, **kwargs: None

def find_available_port(preferred_ports=[8000, 8001, 8002, 8005, 8010]):
    for port in preferred_ports:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            try:
                s.bind(('127.0.0.1', port))
                return port
            except OSError:
                continue
    # Si ninguno preferido está disponible, asignar puerto efímero del SO
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

if __name__ == "__main__":
    from chainlit.cli import cli

    # Si no se pasó --port, buscar el primer puerto libre
    has_port = any(arg in sys.argv for arg in ["--port", "-p"])
    if not has_port:
        free_port = find_available_port()
        if len(sys.argv) <= 1:
            sys.argv = ["chainlit", "run", "app.py", "--port", str(free_port)]
        else:
            sys.argv.extend(["--port", str(free_port)])

    print("=" * 70)
    print("  CAJA DE AHORROS DE PANAMÁ - ASESOR VIRTUAL FERIA AUTOS")
    print("  Iniciando servidor Chainlit...")
    print("=" * 70)

    cli()
