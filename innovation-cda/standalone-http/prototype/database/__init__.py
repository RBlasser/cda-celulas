"""
Paquete de base de datos SQLite para Caja de Ahorros.
"""

from .db_manager import (
    init_db,
    guardar_cliente,
    actualizar_perfil_cliente,
    guardar_chat_json,
    obtener_cliente,
    obtener_conversacion,
    registrar_log_servidor,
    registrar_log_ai,
    registrar_log_auditoria,
    obtener_config,
    guardar_config,
    obtener_logs,
    obtener_todos_los_clientes,
    obtener_todas_las_conversaciones,
    DB_PATH,
)

__all__ = [
    "init_db",
    "guardar_cliente",
    "actualizar_perfil_cliente",
    "guardar_chat_json",
    "obtener_cliente",
    "obtener_conversacion",
    "registrar_log_servidor",
    "registrar_log_ai",
    "registrar_log_auditoria",
    "obtener_config",
    "guardar_config",
    "obtener_logs",
    "obtener_todos_los_clientes",
    "obtener_todas_las_conversaciones",
    "DB_PATH",
]
