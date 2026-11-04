import json
import logging
from app.database import Database
from app.model.auth_model import UsuarioModel

logger = logging.getLogger(__name__)


class ActividadModel:
    def __init__(self):
        self.db_name = 'seguridad'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def _cargar_nombres_usuario(self, items):
        user_ids = set()
        for item in items:
            if item.get('usuario_id'):
                user_ids.add(item['usuario_id'])
        if not user_ids:
            return
        user_model = UsuarioModel()
        for uid in user_ids:
            user = user_model.obtener_por_id(uid)
            for item in items:
                if item.get('usuario_id') == uid:
                    item['usuario'] = user

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM actividad_usuario WHERE 1=1"
            params = []
            if filtros.get('usuario_id'):
                sql += " AND usuario_id = %s"
                params.append(filtros['usuario_id'])
            if filtros.get('modulo'):
                sql += " AND modulo = %s"
                params.append(filtros['modulo'])
            if filtros.get('tipo_accion'):
                sql += " AND tipo_accion = %s"
                params.append(filtros['tipo_accion'])
            if filtros.get('fecha_desde'):
                sql += " AND created_at >= %s"
                params.append(filtros['fecha_desde'])
            if filtros.get('fecha_hasta'):
                sql += " AND created_at <= %s"
                params.append(filtros['fecha_hasta'])
            sql += " ORDER BY created_at DESC"
            if filtros.get('limite'):
                sql += " LIMIT %s"
                params.append(filtros['limite'])
            with db.cursor() as cur:
                cur.execute(sql, params)
                items = list(cur.fetchall())
            for item in items:
                d = item.get('detalle')
                if isinstance(d, str) and d.startswith('{'):
                    try:
                        parsed = json.loads(d)
                        if isinstance(parsed, dict):
                            item['detalle'] = parsed.get('d', parsed.get('detalle', d))
                    except (json.JSONDecodeError, TypeError, ValueError):
                        pass
            self._cargar_nombres_usuario(items)
            return items
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def _extraer_detalle(self, detalle):
        if detalle is None:
            return None
        if isinstance(detalle, str):
            try:
                parsed = json.loads(detalle)
                if isinstance(parsed, dict) and 'detalle' in parsed:
                    return json.dumps({'d': parsed['detalle']}, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError, ValueError):
                pass
            return detalle
        if isinstance(detalle, dict):
            return json.dumps({'d': detalle.get('detalle', str(detalle))}, ensure_ascii=False)
        return json.dumps({'d': str(detalle)}, ensure_ascii=False)

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO actividad_usuario
                       (sesion_id, usuario_id, tipo_accion, modulo, accion, detalle, pagina, ip_address, created_at)
                       VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())""",
                    (
                        datos.get('sesion_id'), datos['usuario_id'],
                        datos['tipo_accion'], datos['modulo'],
                        datos.get('accion', ''),
                        self._extraer_detalle(datos.get('detalle')),
                        datos.get('pagina'), datos.get('ip_address'),
                    )
                )
                return self._get_db(), cur.lastrowid
        except Exception:
            logger.exception('Error de base de datos')
            return None, None

    def obtener_modulos_distintos(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT DISTINCT modulo FROM actividad_usuario WHERE modulo IS NOT NULL")
                return [r['modulo'] for r in cur.fetchall()]
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_acciones_distintas(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT DISTINCT tipo_accion FROM actividad_usuario WHERE tipo_accion IS NOT NULL")
                return [r['tipo_accion'] for r in cur.fetchall()]
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_usuarios_distintos(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT DISTINCT a.usuario_id, COALESCE(u.nombre, 'Usuario ' || a.usuario_id) AS nombre
                       FROM actividad_usuario a
                       LEFT JOIN seguridad.usuarios u ON a.usuario_id = u.id
                       WHERE a.usuario_id IS NOT NULL
                       ORDER BY nombre"""
                )
                return [{'id': r['usuario_id'], 'nombre': r['nombre']} for r in cur.fetchall()]
        except Exception:
            logger.exception('Error de base de datos')
            return []


class SesionModel:
    def __init__(self):
        self.db_name = 'seguridad'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def _cargar_nombres_usuario(self, items):
        user_ids = set()
        for item in items:
            if item.get('usuario_id'):
                user_ids.add(item['usuario_id'])
        if not user_ids:
            return
        user_model = UsuarioModel()
        for uid in user_ids:
            user = user_model.obtener_por_id(uid)
            for item in items:
                if item.get('usuario_id') == uid:
                    item['usuario'] = user

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM sesiones_usuario WHERE 1=1"
            params = []
            if filtros.get('usuario_id'):
                sql += " AND usuario_id = %s"
                params.append(filtros['usuario_id'])
            sql += " ORDER BY inicio_sesion DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                items = list(cur.fetchall())
            self._cargar_nombres_usuario(items)
            return items
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id_registro):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM sesiones_usuario WHERE id = %s", (id_registro,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO sesiones_usuario (usuario_id, inicio_sesion, ip_address, user_agent) VALUES (%s, NOW(), %s, %s)",
                    (datos['usuario_id'], datos.get('ip_address'), datos.get('user_agent'))
                )
                return self.obtener_por_id(cur.lastrowid)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def cerrar_sesion(self, sesion_id):
        try:
            from datetime import datetime
            s = self.obtener_por_id(sesion_id)
            if not s:
                return None
            fin = datetime.utcnow()
            duracion = None
            if s['inicio_sesion']:
                duracion = int((fin - s['inicio_sesion']).total_seconds())
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "UPDATE sesiones_usuario SET fin_sesion = %s, duracion_segundos = %s WHERE id = %s",
                    (fin, duracion, sesion_id)
                )
            return self.obtener_por_id(sesion_id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def cerrar_sesiones_abandonadas(self):
        # ponytail: al reiniciar el servidor, cierra sesiones que quedaron abiertas
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "UPDATE sesiones_usuario SET fin_sesion = NOW(), duracion_segundos = 0 WHERE fin_sesion IS NULL"
                )
            return True
        except Exception:
            logger.exception('Error de base de datos')
            return False


class CambioModel:
    def __init__(self):
        self.db_name = 'seguridad'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM cambios_por_modulo WHERE 1=1"
            params = []
            if filtros.get('actividad_id'):
                sql += " AND actividad_id = %s"
                params.append(filtros['actividad_id'])
            if filtros.get('tabla_afectada'):
                sql += " AND tabla_afectada = %s"
                params.append(filtros['tabla_afectada'])
            if filtros.get('actividad_ids'):
                ids = filtros['actividad_ids']
                placeholders = ', '.join(['%s'] * len(ids))
                sql += f" AND actividad_id IN ({placeholders})"
                params.extend(ids)
            sql += " ORDER BY created_at DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return list(cur.fetchall())
        except Exception:
            logger.exception('Error de base de datos')
            return []
