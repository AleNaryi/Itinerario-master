import json
import logging
from app.database import Database

logger = logging.getLogger(__name__)


class ChatModel:
    def __init__(self):
        self.db_name = 'estadio_db'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def guardar(self, usuario_id, mensaje, respuesta, contexto=None):
        try:
            db = self._get_db()
            ctx = json.dumps(contexto, ensure_ascii=False) if contexto else None
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO historial_chat (usuario_id, mensaje_usuario, respuesta_ia, contexto)
                       VALUES (%s, %s, %s, %s)""",
                    (usuario_id, mensaje, respuesta, ctx)
                )
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def historial(self, usuario_id, limite=20):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT mensaje_usuario, respuesta_ia, created_at
                       FROM historial_chat
                       WHERE usuario_id = %s
                       ORDER BY created_at DESC LIMIT %s""",
                    (usuario_id, limite)
                )
                return list(reversed(cur.fetchall()))
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def contar_por_usuario(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as total FROM historial_chat WHERE usuario_id = %s",
                    (usuario_id,)
                )
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0
