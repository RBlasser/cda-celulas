# Regla: Prevención de Loops Infinitos, Detención Temprana y Control de Consumo de Tokens

## Directiva de Límite de Intentos y Transparencia
- **Prohibidos los loops largos sin resultados:** Si te encuentras en un ciclo iterativo de depuración o prueba y la solución está tomando demasiado tiempo o varios intentos infructuosos, **DETENTE INMEDIATAMENTE** y comunica con total transparencia al usuario qué está ocurriendo, qué se ha descubierto y qué alternativas existen.
- **Detener servidores y procesos locales:** Si se trata de un servidor HTTP, servidor de desarrollo local o pruebas automatizadas (Playwright, Puppeteer, Selenium o frameworks similares), **detén los servidores y procesos en segundo plano inmediatamente** en lugar de dejarlos corriendo o reintentar en bucle.
- **Conservación de recursos y tokens:** Está estrictamente prohibido ejecutar ciclos extensos e iteraciones ciegas que consuman tokens, créditos y tiempo sin aportar mejoras verificables. La prioridad es la comunicación oportuna y la resolución directa.
