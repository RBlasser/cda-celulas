# Regla: Cero Sobreingeniería, Cero Fallback Functions y Cero Mockdata

## Directiva de Robustez y Fallo Explícito (Fail-Fast)
- **Cero sobreingeniería:** Mantener las implementaciones simples, directas y ajustadas estrictamente al alcance funcional requerido. No crear capas innecesarias, abstracciones prematuras ni complejidad accidental.
- **Cero funciones fallback:** No implementar mecanismos de *fallback* silenciosos que oculten fallos de infraestructura, errores de API o respuestas inválidas.
- **Cero datos simulados (Mock Data):** No utilizar datos simulados (*mockdata* o *placeholders* inventados) en los flujos de lógica. Si una dependencia, archivo o llamada falla, debe fallar explícitamente (`fail-fast`) mostrando el error real para su diagnóstico y resolución.
