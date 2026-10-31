"""
Módulo de Gestión de Base de Datos SQLite para Asesor Virtual de Auto - Caja de Ahorros.
Almacena de forma persistente la información personal del cliente, perfil comercial y el historial completo del chat en formato JSON.
"""

import os
import json
import sqlite3
import datetime
from typing import List, Dict, Any, Optional

# Ruta dedicada para la base de datos SQLite dentro del subfolder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "cda_feria_autos.db")


def get_connection() -> sqlite3.Connection:
    """Retorna una conexión activa a la base de datos SQLite."""
    os.makedirs(BASE_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Inicializa las tablas de la base de datos si no existen."""
    conn = get_connection()
    cursor = conn.cursor()

    # 1. Tabla de Clientes (Información Personal y Perfilación Comercial de Feria)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS clientes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        nombre TEXT NOT NULL,
        cedula TEXT NOT NULL,
        celular TEXT NOT NULL,
        correo TEXT NOT NULL,
        uso_vehiculo TEXT,
        sector_laboral TEXT,
        tipo_abono TEXT,
        momento_compra TEXT,
        temperatura_lead TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        ultima_actividad TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Agregar columnas de perfilación a tablas existentes de forma segura
    for col in ["uso_vehiculo", "sector_laboral", "tipo_abono", "momento_compra", "temperatura_lead"]:
        try:
            cursor.execute(f"ALTER TABLE clientes ADD COLUMN {col} TEXT;")
        except sqlite3.OperationalError:
            pass

    # 2. Tabla de Conversaciones (Historial de Chat en JSON y Cotizaciones)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS conversaciones (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT UNIQUE NOT NULL,
        cliente_id INTEGER,
        chat_json TEXT NOT NULL,
        total_mensajes INTEGER DEFAULT 0,
        ultimo_mensaje TEXT,
        pase_digital TEXT,
        precio_cotizado REAL,
        cuota_estimada REAL,
        fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (cliente_id) REFERENCES clientes (id)
    );
    """)

    # 3. Tabla de Mensajes Individuales (Auditoría paso a paso)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS mensajes_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 4. Tabla de Logs del Servidor / HTTP (Errores y Eventos de la App)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_servidor (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nivel TEXT NOT NULL,
        endpoint TEXT,
        metodo TEXT,
        codigo_estado INTEGER,
        mensaje TEXT NOT NULL,
        detalle_error TEXT,
        ip_origen TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 5. Tabla de Logs de AI Requests (Llamadas a APIs de Agentes / Modelos)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_ai_requests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id TEXT,
        proveedor TEXT NOT NULL,
        modelo TEXT,
        tiempo_ms INTEGER,
        estado TEXT NOT NULL,
        prompt_tokens INTEGER,
        error_detail TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 6. Tabla de Logs de Auditoría y Negocio (Leads, Exportaciones, Configuración, Login)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS logs_auditoria (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo_evento TEXT NOT NULL,
        usuario_origen TEXT,
        detalles TEXT,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Tabla de Configuración Dinámica (Proveedores, API Keys y Parámetros del Sistema)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS configuracion (
        clave TEXT PRIMARY KEY,
        valor TEXT NOT NULL,
        actualizado_el TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Índices para búsquedas ágiles
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_cedula ON clientes (cedula);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversaciones_session ON conversaciones (session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mensajes_session ON mensajes_log (session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_servidor_nivel ON logs_servidor (nivel);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_ai_estado ON logs_ai_requests (estado);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_logs_auditoria_evento ON logs_auditoria (tipo_evento);")

    conn.commit()
    conn.close()


def guardar_cliente(
    session_id: str, 
    nombre: str, 
    cedula: str, 
    celular: str, 
    correo: str,
    uso_vehiculo: Optional[str] = None,
    sector_laboral: Optional[str] = None,
    tipo_abono: Optional[str] = None,
    momento_compra: Optional[str] = None,
    temperatura_lead: Optional[str] = None
) -> int:
    """
    Inserta o actualiza los datos personales del cliente registrados en el formulario previo.
    Retorna el ID del cliente.
    """
    conn = get_connection()
    cursor = conn.cursor()
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    INSERT INTO clientes (
        session_id, nombre, cedula, celular, correo,
        uso_vehiculo, sector_laboral, tipo_abono, momento_compra, temperatura_lead,
        fecha_registro, ultima_actividad
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(session_id) DO UPDATE SET
        nombre = excluded.nombre,
        cedula = excluded.cedula,
        celular = excluded.celular,
        correo = excluded.correo,
        uso_vehiculo = COALESCE(excluded.uso_vehiculo, clientes.uso_vehiculo),
        sector_laboral = COALESCE(excluded.sector_laboral, clientes.sector_laboral),
        tipo_abono = COALESCE(excluded.tipo_abono, clientes.tipo_abono),
        momento_compra = COALESCE(excluded.momento_compra, clientes.momento_compra),
        temperatura_lead = COALESCE(excluded.temperatura_lead, clientes.temperatura_lead),
        ultima_actividad = excluded.ultima_actividad;
    """, (
        session_id, nombre, cedula, celular, correo,
        uso_vehiculo, sector_laboral, tipo_abono, momento_compra, temperatura_lead,
        ahora, ahora
    ))

    conn.commit()
    
    # Obtener el ID asignado
    cursor.execute("SELECT id FROM clientes WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    cliente_id = row["id"] if row else 0
    conn.close()
    return cliente_id


def actualizar_perfil_cliente(session_id: str, perfil_data: Dict[str, Any]):
    """Actualiza los campos de perfilación comercial capturados durante la conversación."""
    conn = get_connection()
    cursor = conn.cursor()
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    cursor.execute("""
    UPDATE clientes SET
        uso_vehiculo = COALESCE(?, uso_vehiculo),
        sector_laboral = COALESCE(?, sector_laboral),
        tipo_abono = COALESCE(?, tipo_abono),
        momento_compra = COALESCE(?, momento_compra),
        temperatura_lead = COALESCE(?, temperatura_lead),
        ultima_actividad = ?
    WHERE session_id = ?;
    """, (
        perfil_data.get("uso_vehiculo"),
        perfil_data.get("sector_laboral"),
        perfil_data.get("tipo_abono"),
        perfil_data.get("momento_compra"),
        perfil_data.get("temperatura_lead"),
        ahora,
        session_id
    ))
    conn.commit()
    conn.close()


def guardar_chat_json(
    session_id: str, 
    messages: List[Dict[str, str]], 
    pase_digital: Optional[str] = None,
    precio: Optional[float] = None,
    cuota: Optional[float] = None
):
    """
    Guarda o actualiza el historial completo del chat como JSON en la base de datos SQLite.
    También actualiza los datos de la cotización si fueron calculados.
    """
    conn = get_connection()
    cursor = conn.cursor()
    ahora = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    chat_json_str = json.dumps(messages, ensure_ascii=False, indent=2)
    total_msgs = len(messages)
    ultimo_msg = messages[-1]["content"][:300] if messages else ""

    # Obtener ID del cliente asociado si existe
    cursor.execute("SELECT id FROM clientes WHERE session_id = ?", (session_id,))
    cliente_row = cursor.fetchone()
    cliente_id = cliente_row["id"] if cliente_row else None

    # Si ya existe una fila de conversación, mantener los valores de cotización si no se proporcionan nuevos
    cursor.execute("SELECT pase_digital, precio_cotizado, cuota_estimada FROM conversaciones WHERE session_id = ?", (session_id,))
    prev = cursor.fetchone()

    pase_final = pase_digital or (prev["pase_digital"] if prev else None)
    precio_final = precio if precio is not None else (prev["precio_cotizado"] if prev else None)
    cuota_final = cuota if cuota is not None else (prev["cuota_estimada"] if prev else None)

    cursor.execute("""
    INSERT INTO conversaciones (
        session_id, cliente_id, chat_json, total_mensajes, ultimo_mensaje,
        pase_digital, precio_cotizado, cuota_estimada, fecha_inicio, fecha_actualizacion
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ON CONFLICT(session_id) DO UPDATE SET
        cliente_id = COALESCE(excluded.cliente_id, conversaciones.cliente_id),
        chat_json = excluded.chat_json,
        total_mensajes = excluded.total_mensajes,
        ultimo_mensaje = excluded.ultimo_mensaje,
        pase_digital = COALESCE(excluded.pase_digital, conversaciones.pase_digital),
        precio_cotizado = COALESCE(excluded.precio_cotizado, conversaciones.precio_cotizado),
        cuota_estimada = COALESCE(excluded.cuota_estimada, conversaciones.cuota_estimada),
        fecha_actualizacion = excluded.fecha_actualizacion;
    """, (
        session_id, cliente_id, chat_json_str, total_msgs, ultimo_msg,
        pase_final, precio_final, cuota_final, ahora, ahora
    ))

    # Registrar el último mensaje en la bitácora individual
    if messages:
        last = messages[-1]
        cursor.execute("""
        INSERT INTO mensajes_log (session_id, role, content, timestamp)
        VALUES (?, ?, ?, ?);
        """, (session_id, last.get("role", "user"), last.get("content", ""), ahora))

    conn.commit()
    conn.close()


def obtener_cliente(session_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene los datos del cliente registrado para una sesión determinada."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM clientes WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def obtener_conversacion(session_id: str) -> Optional[Dict[str, Any]]:
    """Obtiene el registro de la conversación y el historial del chat en formato dict/list."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM conversaciones WHERE session_id = ?", (session_id,))
    row = cursor.fetchone()
    conn.close()
    if not row:
        return None
    d = dict(row)
    try:
        d["mensajes"] = json.loads(d["chat_json"])
    except Exception:
        d["mensajes"] = []
    return d


# =========================================================================
# FUNCIONES DE LOGGING, TRAZABILIDAD Y CONFIGURACIÓN DINÁMICA
# =========================================================================

def registrar_log_servidor(
    nivel: str,
    mensaje: str,
    endpoint: Optional[str] = None,
    metodo: Optional[str] = None,
    codigo_estado: Optional[int] = None,
    detalle_error: Optional[str] = None,
    ip_origen: Optional[str] = None
):
    """Registra eventos y errores del servidor HTTP y la aplicación."""
    try:
        conn = get_connection()
        conn.execute("""
        INSERT INTO logs_servidor (nivel, endpoint, metodo, codigo_estado, mensaje, detalle_error, ip_origen)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (nivel.upper(), endpoint, metodo, codigo_estado, mensaje, detalle_error, ip_origen))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error escribiendo en logs_servidor: {e}")


def registrar_log_ai(
    session_id: str,
    proveedor: str,
    estado: str,
    modelo: Optional[str] = None,
    tiempo_ms: Optional[int] = None,
    prompt_tokens: Optional[int] = None,
    error_detail: Optional[str] = None
):
    """Registra cada ejecución (éxito o fallo) hacia los modelos / APIs de IA."""
    try:
        conn = get_connection()
        conn.execute("""
        INSERT INTO logs_ai_requests (session_id, proveedor, modelo, tiempo_ms, estado, prompt_tokens, error_detail)
        VALUES (?, ?, ?, ?, ?, ?, ?);
        """, (session_id, proveedor, modelo, tiempo_ms, estado.upper(), prompt_tokens, error_detail))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error escribiendo en logs_ai_requests: {e}")


def registrar_log_auditoria(
    tipo_evento: str,
    detalles: str = "",
    usuario_origen: str = "sistema"
):
    """Registra eventos de negocio, cambios de configuración y acciones administrativas."""
    try:
        conn = get_connection()
        conn.execute("""
        INSERT INTO logs_auditoria (tipo_evento, usuario_origen, detalles)
        VALUES (?, ?, ?);
        """, (tipo_evento.upper(), usuario_origen, detalles))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Error escribiendo en logs_auditoria: {e}")


def obtener_config(clave: str, default: str = "") -> str:
    """Obtiene un parámetro de configuración desde SQLite con fallback seguro a variables de entorno."""
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT valor FROM configuracion WHERE clave = ?;", (clave,))
        row = cur.fetchone()
        conn.close()
        if row and row["valor"]:
            return row["valor"]
    except Exception:
        pass
    return os.getenv(clave.upper(), default)


def guardar_config(clave: str, valor: str):
    """Guarda o actualiza un parámetro de configuración en SQLite (API keys, proveedor de IA, etc.)."""
    conn = get_connection()
    conn.execute("""
    INSERT INTO configuracion (clave, valor, actualizado_el)
    VALUES (?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(clave) DO UPDATE SET
        valor = excluded.valor,
        actualizado_el = CURRENT_TIMESTAMP;
    """, (clave, valor))
    conn.commit()
    conn.close()


def obtener_logs(tipo_log: str = "servidor", limite: int = 100) -> List[Dict[str, Any]]:
    """Obtiene los registros más recientes de la tabla de logs especificada."""
    conn = get_connection()
    cur = conn.cursor()
    tabla = "logs_servidor"
    if tipo_log == "ai":
        tabla = "logs_ai_requests"
    elif tipo_log == "auditoria":
        tabla = "logs_auditoria"

    cur.execute(f"SELECT * FROM {tabla} ORDER BY id DESC LIMIT ?;", (limite,))
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def obtener_todos_los_clientes() -> List[Dict[str, Any]]:
    """Retorna todos los clientes registrados cruzados con su Pase Digital para exportación comercial."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT c.*, conv.pase_digital, conv.total_mensajes
    FROM clientes c
    LEFT JOIN conversaciones conv ON c.session_id = conv.session_id
    ORDER BY c.id DESC;
    """)
    rows = [dict(r) for r in cur.fetchall()]
    conn.close()
    return rows


def obtener_todas_las_conversaciones() -> List[Dict[str, Any]]:
    """Retorna todas las conversaciones con su JSON y datos del cliente para exportación o auditoría."""
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
    SELECT conv.session_id, conv.pase_digital, conv.total_mensajes, conv.chat_json,
           c.nombre, c.cedula, c.celular, c.correo, conv.fecha_actualizacion
    FROM conversaciones conv
    LEFT JOIN clientes c ON conv.session_id = c.session_id
    ORDER BY conv.id DESC;
    """)
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        try:
            d["chat_json"] = json.loads(d["chat_json"])
        except Exception:
            pass
        rows.append(d)
    conn.close()
    return rows


# Inicializar automáticamente al importar el módulo
init_db()

