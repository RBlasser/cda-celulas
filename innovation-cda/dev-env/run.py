"""
Launcher para Asesor Virtual de Auto - Feria Caja de Ahorros con Chainlit.
Incluye parche de compatibilidad para Python 3.14.

En Python 3.14, 'nest_asyncio.apply()' (utilizado internamente por Chainlit CLI)
reemplaza las clases nativas de asyncio con _PyTask, lo que rompe el C task tracker
(_c_current_task) y causa que anyio / Starlette FileResponse lancen NoEventLoopError
al servir archivos estáticos (favicon, css, js).

Neutralizando nest_asyncio.apply antes de importar Chainlit, la aplicación se
ejecuta de manera completamente fluida y estable en Python 3.14.
"""

import sys
import nest_asyncio

# Neutralizar nest_asyncio para evitar que altere asyncio en Python 3.14
nest_asyncio.apply = lambda *args, **kwargs: None

if __name__ == "__main__":
    from chainlit.cli import cli

    # Argumentos predeterminados para Chainlit (sin -w para evitar que watchfiles reinicie al escribir en BD o JSON)
    if len(sys.argv) <= 1:
        sys.argv = ["chainlit", "run", "app.py", "--port", "8000"]

    cli()
