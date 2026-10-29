# 🗄️ Base de Datos SQLite • Asesor Virtual de Auto (Caja de Ahorros)

Subfolder dedicado para el almacenamiento persistente de la información de clientes prospectos y el registro estructurado de conversaciones en formato JSON.

---

## Ubicación del Archivo
- **Ruta local:** `innovation-cda/dev-env/database/cda_feria_autos.db`
- **Gestor:** [db_manager.py](file:///c:/Users/rblasser/OneDrive%20-%20Latinex/Escritorio/PROJECTS/CDA/celulas/innovation-cda/dev-env/database/db_manager.py)
- **Seguridad:** Los archivos `.db` están excluidos del control de versiones (`.gitignore`) para resguardar la privacidad de los datos personales (PII) de los clientes de la feria.

---

## Estructura de Tablas

### 1. `clientes` (Datos de Precalificación del Formulario)
| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | Identificador numérico del cliente |
| `session_id` | TEXT UNIQUE | Identificador único de sesión de chat |
| `nombre` | TEXT NOT NULL | Nombre y apellido completo |
| `cedula` | TEXT NOT NULL | Cédula de identidad personal o pasaporte |
| `celular` | TEXT NOT NULL | Número telefónico de contacto |
| `correo` | TEXT NOT NULL | Correo electrónico |
| `fecha_registro`| TIMESTAMP | Fecha y hora de captura en el formulario |
| `ultima_actividad`| TIMESTAMP | Última interacción del cliente |

### 2. `conversaciones` (Historial de Chat en JSON y Cotización)
| Columna | Tipo | Descripción |
| :--- | :--- | :--- |
| `id` | INTEGER PRIMARY KEY | Identificador de la conversación |
| `session_id` | TEXT UNIQUE | Identificador único de la sesión |
| `cliente_id` | INTEGER | Llave foránea hacia `clientes.id` |
| `chat_json` | TEXT NOT NULL | **Historial completo del chat serializado en JSON** (`[{"role": "user", "content": ...}, ...]`) |
| `total_mensajes`| INTEGER | Cantidad total de turnos de diálogo |
| `ultimo_mensaje`| TEXT | Vista previa del último mensaje |
| `pase_digital` | TEXT | Código de turno emitido (`CDA-AUTO-XXXX`) |
| `precio_cotizado`| REAL | Valor de venta del vehículo simulado |
| `cuota_estimada`| REAL | Letra mensual calculada al centavo |
| `fecha_inicio` | TIMESTAMP | Inicio de la conversación |
| `fecha_actualizacion` | TIMESTAMP | Última actualización |

### 3. `mensajes_log` (Bitácora de Auditoría por Mensaje)
Permite consultas analíticas o reportería mensaje por mensaje:
- `session_id`, `role`, `content`, `timestamp`.

---

## Consultas de Ejemplo (SQL)

### Ver todos los clientes registrados y su Pase Digital:
```sql
SELECT 
    c.id, c.nombre, c.cedula, c.celular, c.correo,
    cv.pase_digital, cv.precio_cotizado, cv.cuota_estimada, cv.total_mensajes
FROM clientes c
LEFT JOIN conversaciones cv ON c.session_id = cv.session_id
ORDER BY c.fecha_registro DESC;
```

### Extraer el chat completo en formato JSON de un cliente:
```sql
SELECT chat_json 
FROM conversaciones 
WHERE session_id = 'tu-session-id';
```
