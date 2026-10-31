"""
Paquete de base de datos SQLite para Caja de Ahorros.
"""

from .db_manager import (
    init_db,
    guardar_cliente,
    guardar_chat_json,
    obtener_cliente,
    obtener_conversacion,
    DB_PATH,
)

__all__ = [
    "init_db",
    "guardar_cliente",
    "guardar_chat_json",
    "obtener_cliente",
    "obtener_conversacion",
    "DB_PATH",
]
