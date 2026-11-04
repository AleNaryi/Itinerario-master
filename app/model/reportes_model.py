import json
import logging
import os
from app.database import Database

logger = logging.getLogger(__name__)


class ReporteModel:
    def __init__(self):
        self.db_name = 'seguridad'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO reportes_generados
                       (usuario_id, modulo, tipo_reporte, filtros, archivo_ruta, archivo_nombre, archivo_tamano)
                       VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                    (datos['usuario_id'], datos['modulo'], datos['tipo_reporte'],
                     json.dumps(datos.get('filtros', {})), datos['archivo_ruta'],
                     datos['archivo_nombre'], datos.get('archivo_tamano', 0))
                )
                return cur.lastrowid
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def listar(self, usuario_id=None, limite=50):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                sql = """SELECT r.*, u.nombre as usuario_nombre
                         FROM reportes_generados r
                         LEFT JOIN usuarios u ON r.usuario_id = u.id"""
                params = []
                if usuario_id:
                    sql += " WHERE r.usuario_id = %s"
                    params.append(usuario_id)
                sql += " ORDER BY r.creado_en DESC LIMIT %s"
                params.append(limite)
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT r.*, u.nombre as usuario_nombre
                       FROM reportes_generados r
                       LEFT JOIN usuarios u ON r.usuario_id = u.id
                       WHERE r.id = %s""", (id,)
                )
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def eliminar(self, id):
        try:
            reporte = self.obtener_por_id(id)
            if not reporte:
                return False
            base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'reportes')
            filepath = os.path.join(base_dir, reporte['archivo_ruta'])
            if os.path.exists(filepath):
                os.remove(filepath)
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM reportes_generados WHERE id = %s", (id,))
            return True
        except Exception:
            logger.exception('Error de base de datos')
            return False
