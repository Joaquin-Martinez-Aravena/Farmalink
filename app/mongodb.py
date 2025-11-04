"""
Módulo puente `mongodb` — reexporta funciones desde `mongobd.py`.

Este archivo existe para mantener la compatibilidad con `app.main` que
importa `from .mongodb import ...`.
"""
from .mongobd import (
    get_database,
    init_mongodb,
    close_mongodb,
    registrar_auditoria,
    crear_alerta,
    obtener_alertas_pendientes,
    marcar_alerta_vista,
    resolver_alerta,
    obtener_configuracion,
    actualizar_configuracion,
    registrar_error,
    iniciar_sesion,
    finalizar_sesion,
)

__all__ = [
    "get_database",
    "init_mongodb",
    "close_mongodb",
    "registrar_auditoria",
    "crear_alerta",
    "obtener_alertas_pendientes",
    "marcar_alerta_vista",
    "resolver_alerta",
    "obtener_configuracion",
    "actualizar_configuracion",
    "registrar_error",
    "iniciar_sesion",
    "finalizar_sesion",
]
