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

    # Índices para búsquedas ágiles
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_clientes_cedula ON clientes (cedula);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversaciones_session ON conversaciones (session_id);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_mensajes_session ON mensajes_log (session_id);")

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


# Inicializar automáticamente al importar el módulo
init_db()
