from datetime import datetime
import logging
from app.database import Database

logger = logging.getLogger(__name__)

TIPOS_VALIDOS = {'tarea_asignada', 'tarea_completada'}


class NotificacionModel:
    """Notificaciones in-app por usuario (tabla seguridad.notificaciones)."""

    def _get_db(self):
        return Database.get_connection('seguridad')

    def crear(self, usuario_id, tipo, titulo, mensaje, url=None):
        if tipo not in TIPOS_VALIDOS:
            logger.warning('Tipo de notificación no permitido: %s', tipo)
            return None
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO notificaciones (usuario_id, tipo, titulo, mensaje, url, leida, fecha_creacion)
                       VALUES (%s, %s, %s, %s, %s, 0, NOW())""",
                    (usuario_id, tipo, titulo[:120], mensaje[:255], url)
                )
                return cur.lastrowid
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def listar(self, usuario_id, limite=15):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT id, tipo, titulo, mensaje, url, leida, fecha_creacion
                       FROM notificaciones WHERE usuario_id = %s
                       ORDER BY id DESC LIMIT %s""",
                    (usuario_id, int(limite))
                )
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def contar_no_leidas(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) AS total FROM notificaciones WHERE usuario_id = %s AND leida = 0",
                    (usuario_id,)
                )
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0

    def marcar_leida(self, id_notificacion, usuario_id):
        """Solo marca si la notificación pertenece al usuario (anti-IDOR)."""
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "UPDATE notificaciones SET leida = 1 WHERE id = %s AND usuario_id = %s",
                    (id_notificacion, usuario_id)
                )
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def marcar_todas(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "UPDATE notificaciones SET leida = 1 WHERE usuario_id = %s AND leida = 0",
                    (usuario_id,)
                )
                return True
        except Exception:
            logger.exception('Error de base de datos')
            return False
