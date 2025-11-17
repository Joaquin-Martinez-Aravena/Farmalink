"""
Configuración de MongoDB para FarmaLink - VERSIÓN SÍNCRONA
ADVERTENCIA: Esta versión puede tener menor rendimiento bajo carga alta
"""
import os
from datetime import datetime
from typing import Optional, Dict, Any, List
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
import logging

logger = logging.getLogger(__name__)

# URL de conexión desde variables de entorno
# Leemos la variable de entorno MONGODB_URL; no hardcodeamos credenciales en el código.
MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    # No levantamos una excepción en tiempo de importación para evitar
    # romper `import app.main` cuando la variable de entorno no esté presente
    # (por ejemplo en entornos de desarrollo sin MongoDB configurado).
    logger.warning("MONGODB_URL no está configurada; las operaciones de MongoDB fallarán hasta configurarla.")

# Cliente síncrono de MongoDB
mongo_client: Optional[MongoClient] = None
mongo_db = None

# Nombre de la base de datos
DB_NAME = "farmalink_nosql"


def get_database():
    """Obtiene la base de datos MongoDB (Síncrono)"""
    global mongo_db
    if not MONGODB_URL:
        raise ValueError("❌ MONGODB_URL no está configurada en las variables de entorno")

    if mongo_db is None:
        global mongo_client
        # Cliente creado bajo demanda
        mongo_client = MongoClient(MONGODB_URL,tls = True)
        mongo_db = mongo_client[DB_NAME]
    return mongo_db


def init_mongodb():
    """Inicializa MongoDB y crea índices (Síncrono)"""
    try:
        db = get_database()
        
        # Verificar conexión
        db.command("ping")
        logger.info("✅ Conectado a MongoDB exitosamente")
        
        # Crear índices para logs_auditoria
        db.logs_auditoria.create_index([("timestamp", -1)])
        db.logs_auditoria.create_index([("tabla_afectada", 1), ("timestamp", -1)])
        db.logs_auditoria.create_index([("usuario.id_usuario", 1)])
        
        # Crear índices para alertas
        db.alertas.create_index([("estado", 1), ("prioridad", -1), ("fecha_creacion", -1)])
        db.alertas.create_index([("tipo", 1), ("fecha_creacion", -1)])
        
        # Crear índices para configuraciones
        db.configuraciones.create_index([("clave", 1)], unique=True)
        
        logger.info("✅ Índices MongoDB creados/verificados")
        
        # Insertar configuraciones por defecto si no existen
        insertar_configuraciones_default(db)
        
    except Exception as e:
        logger.error(f"❌ Error al inicializar MongoDB: {e}")
        raise


def insertar_configuraciones_default(db):
    """Inserta configuraciones por defecto (Síncrono)"""
    configuraciones_default = [
        {
            "clave": "dias_alerta_vencimiento",
            "valor": 30,
            "descripcion": "Días antes del vencimiento para generar alerta",
            "tipo": "NUMBER",
            "ultima_modificacion": datetime.now(),
            "modificado_por": {"id_usuario": 1, "nombre": "Sistema"}
        },
        {
            "clave": "umbral_stock_critico",
            "valor": 10,
            "descripcion": "Cantidad mínima para considerar stock crítico",
            "tipo": "NUMBER",
            "ultima_modificacion": datetime.now(),
            "modificado_por": {"id_usuario": 1, "nombre": "Sistema"}
        }
    ]
    
    for config in configuraciones_default:
        try:
            db.configuraciones.insert_one(config)
            logger.info(f"✅ Configuración '{config['clave']}' insertada")
        except DuplicateKeyError:
            pass  # Ya existe


def close_mongodb():
    """Cierra la conexión a MongoDB (Síncrono)"""
    global mongo_client
    if mongo_client:
        mongo_client.close()
        logger.info("🔌 Conexión MongoDB cerrada")


# ===========================================
# FUNCIONES HELPER PARA LOGS DE AUDITORÍA
# ===========================================

def registrar_auditoria(
    accion: str,
    tabla_afectada: str,
    id_registro: int,
    usuario: Dict[str, Any],
    datos_anteriores: Optional[Dict] = None,
    datos_nuevos: Optional[Dict] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
):
    """Registra una acción en los logs de auditoría (Síncrono)"""
    try:
        db = get_database()
        
        log = {
            "accion": accion,
            "tabla_afectada": tabla_afectada,
            "id_registro": id_registro,
            "usuario": usuario,
            "timestamp": datetime.now(),
            "ip_address": ip_address,
            "user_agent": user_agent
        }
        
        if datos_anteriores:
            log["datos_anteriores"] = datos_anteriores
        if datos_nuevos:
            log["datos_nuevos"] = datos_nuevos
        
        db.logs_auditoria.insert_one(log)
        logger.debug(f"📝 Log de auditoría registrado: {accion} en {tabla_afectada}")
        
    except Exception as e:
        logger.error(f"❌ Error al registrar auditoría: {e}")


# ===========================================
# FUNCIONES HELPER PARA LOG DE ALERTAS
# ===========================================

def registrar_log_alerta(
    mensaje: str,
    tipo: str = "INFO",
    producto: Optional[str] = None,
    lote: Optional[str] = None,
    categoria: Optional[str] = None,
    detalles: Optional[str] = None,
) -> Optional[str]:
    """Registra una entrada en la colección logs_alertas (historial)."""
    try:
        db = get_database()

        doc = {
            "mensaje": mensaje,
            "tipo": tipo,          # VENCIMIENTO / INGRESO_LOTE / STOCK / INFO
            "fecha": datetime.now()
        }

        if producto:
            doc["producto"] = producto
        if lote:
            doc["lote"] = lote
        if categoria:
            doc["categoria"] = categoria
        if detalles:
            doc["detalles"] = detalles

        result = db.logs_alertas.insert_one(doc)
        logger.info(f"🧾 Log de alerta registrado: {mensaje}")
        return str(result.inserted_id)

    except Exception as e:
        logger.error(f"❌ Error al registrar log de alerta: {e}")
        return None
    

def crear_alerta(
    tipo: str,
    prioridad: str,
    mensaje: str,
    detalles: Dict[str, Any],
) -> Optional[str]:
    """
    Versión simple: solo guarda en logs_alertas como historial.
    """
    try:
        alerta_id = registrar_log_alerta(
            mensaje=mensaje,
            tipo=tipo,
            producto=detalles.get("producto"),
            lote=detalles.get("lote"),
            categoria=detalles.get("categoria"),
            detalles=detalles.get("descripcion"),
        )

        logger.info(f"🚨 Alerta creada: {tipo} - {prioridad}")
        return alerta_id

    except Exception as e:
        logger.error(f"❌ Error al crear alerta: {e}")
        return None

def obtener_alertas_pendientes(limite: int = 50) -> List[Dict]:
    """Obtiene las alertas pendientes (Síncrono)"""
    try:
        db = get_database()
        
        # Orden de prioridad
        orden_prioridad = {"CRITICA": 4, "ALTA": 3, "MEDIA": 2, "BAJA": 1}
        
        alertas = list(db.alertas.find(
            {"estado": "PENDIENTE"}
        ).sort("fecha_creacion", -1).limit(limite))
        
        # Convertir ObjectId a string
        for alerta in alertas:
            alerta["_id"] = str(alerta["_id"])
        
        # Ordenar por prioridad
        alertas.sort(key=lambda x: orden_prioridad.get(x["prioridad"], 0), reverse=True)
        
        return alertas
        
    except Exception as e:
        logger.error(f"❌ Error al obtener alertas: {e}")
        return []


def marcar_alerta_vista(alerta_id: str, usuario: Dict[str, Any]):
    """Marca una alerta como vista (Síncrono)"""
    try:
        db = get_database()
        from bson import ObjectId
        
        db.alertas.update_one(
            {"_id": ObjectId(alerta_id)},
            {
                "$set": {
                    "estado": "VISTA",
                    "fecha_vista": datetime.now(),
                    "vista_por": usuario
                }
            }
        )
        logger.info(f"👁️ Alerta {alerta_id} marcada como vista")
        
    except Exception as e:
        logger.error(f"❌ Error al marcar alerta vista: {e}")


def resolver_alerta(
    alerta_id: str,
    usuario: Dict[str, Any],
    notas_resolucion: Optional[str] = None
):
    """Marca una alerta como resuelta (Síncrono)"""
    try:
        db = get_database()
        from bson import ObjectId
        
        update_data = {
            "estado": "RESUELTA",
            "fecha_resuelta": datetime.now(),
            "resuelto_por": usuario
        }
        
        if notas_resolucion:
            update_data["notas_resolucion"] = notas_resolucion
        
        db.alertas.update_one(
            {"_id": ObjectId(alerta_id)},
            {"$set": update_data}
        )
        logger.info(f"✅ Alerta {alerta_id} resuelta por {usuario['nombre']}")
        
    except Exception as e:
        logger.error(f"❌ Error al resolver alerta: {e}")


# ===========================================
# FUNCIONES HELPER PARA CONFIGURACIONES
# ===========================================

def obtener_configuracion(clave: str) -> Optional[Any]:
    """Obtiene el valor de una configuración (Síncrono)"""
    try:
        db = get_database()
        config = db.configuraciones.find_one({"clave": clave})
        return config["valor"] if config else None
    except Exception as e:
        logger.error(f"❌ Error al obtener configuración {clave}: {e}")
        return None


def actualizar_configuracion(
    clave: str,
    valor: Any,
    usuario: Dict[str, Any]
):
    """Actualiza una configuración (Síncrono)"""
    try:
        db = get_database()
        
        db.configuraciones.update_one(
            {"clave": clave},
            {
                "$set": {
                    "valor": valor,
                    "ultima_modificacion": datetime.now(),
                    "modificado_por": usuario
                }
            },
            upsert=True
        )
        logger.info(f"⚙️ Configuración '{clave}' actualizada")
        
    except Exception as e:
        logger.error(f"❌ Error al actualizar configuración: {e}")


# ===========================================
# FUNCIONES HELPER PARA LOGS DE ERRORES
# ===========================================

def registrar_error(
    nivel: str,
    mensaje: str,
    stack_trace: Optional[str] = None,
    endpoint: Optional[str] = None,
    metodo_http: Optional[str] = None,
    usuario: Optional[Dict] = None,
    contexto: Optional[Dict] = None
):
    """Registra un error del sistema (Síncrono)"""
    try:
        db = get_database()
        
        error_log = {
            "nivel": nivel,
            "mensaje": mensaje,
            "timestamp": datetime.now(),
        }
        
        if stack_trace:
            error_log["stack_trace"] = stack_trace
        if endpoint:
            error_log["endpoint"] = endpoint
        if metodo_http:
            error_log["metodo_http"] = metodo_http
        if usuario:
            error_log["usuario"] = usuario
        if contexto:
            error_log["contexto"] = contexto
        
        db.logs_errores.insert_one(error_log)
        logger.debug(f"📋 Error registrado: {nivel} - {mensaje}")
        
    except Exception as e:
        logger.error(f"❌ Error al registrar error: {e}")


# ===========================================
# FUNCIONES HELPER PARA SESIONES
# ===========================================

def iniciar_sesion(
    id_usuario: int,
    nombre_usuario: str,
    rol: str,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None
) -> Optional[str]:
    """Registra el inicio de sesión de un usuario (Síncrono)"""
    try:
        db = get_database()
        
        sesion = {
            "id_usuario": id_usuario,
            "nombre_usuario": nombre_usuario,
            "rol": rol,
            "fecha_inicio": datetime.now(),
            "fecha_fin": None,
            "ip_address": ip_address,
            "user_agent": user_agent,
            "acciones_realizadas": []
        }
        
        result = db.sesiones_usuario.insert_one(sesion)
        logger.info(f"🔐 Sesión iniciada para usuario {nombre_usuario}")
        return str(result.inserted_id)
        
    except Exception as e:
        logger.error(f"❌ Error al iniciar sesión: {e}")
        return None


def finalizar_sesion(sesion_id: str):
    """Registra el fin de sesión de un usuario (Síncrono)"""
    try:
        db = get_database()
        from bson import ObjectId
        
        sesion = db.sesiones_usuario.find_one({"_id": ObjectId(sesion_id)})
        
        if sesion:
            duracion = (datetime.now() - sesion["fecha_inicio"]).total_seconds()
            
            db.sesiones_usuario.update_one(
                {"_id": ObjectId(sesion_id)},
                {
                    "$set": {
                        "fecha_fin": datetime.now(),
                        "duracion_total_segundos": int(duracion)
                    }
                }
            )
            logger.info(f"🔓 Sesión finalizada: {sesion_id}")
        
    except Exception as e:
        logger.error(f"❌ Error al finalizar sesión: {e}")