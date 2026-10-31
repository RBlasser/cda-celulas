# Reglas del Workspace (Workspace Rules)

## Integridad y Control de Modificación de Documentación
- **No modificar documentación existente sin autorización explícita:** El agente tiene estrictamente prohibido editar, actualizar, corregir o sobrescribir archivos de documentación existentes (`.md`, `.docx`, `.txt`, diagramas de arquitectura, minutas, requerimientos, etc.) sin la autorización o instrucción explícita del usuario.
- **Creación y versiones:** Si se solicitan cambios, nuevas perspectivas o ajustes, se debe confirmar primero si se desea modificar el archivo actual o generar una versión nueva independiente.
- **Preservación y trazabilidad:** Toda documentación acordada, firmada o en proceso de revisión con el cliente (Caja de Ahorros) debe permanecer intacta para salvaguardar la trazabilidad histórica del proyecto.

## Prevención de Loops Infinitos y Control de Consumo de Tokens
- **Detención temprana y comunicación:** Si una depuración o ajuste toma más tiempo de lo esperado o varios intentos sin mejora tangible, el agente debe **detenerse de inmediato** y explicar con claridad al usuario la situación y hallazgos.
- **Apagado de servidores locales y frameworks de testing:** Cuando se trabaje con servidores HTTP locales o herramientas de automatización (Playwright, navegadores headless, etc.), detener todos los procesos y servidores inmediatamente en lugar de dejarlos activos o reintentar en bucle.
- **Cero loops que malgasten tokens:** Queda terminantemente prohibido entrar en bucles de prueba repetitivos que consuman tokens, créditos y tiempo sin aportar una solución clara.

