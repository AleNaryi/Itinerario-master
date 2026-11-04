from app.database import Database
import logging
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class ReelModel(ValidacionesMixin, CrudInterface):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__nombre = None
        self.__duracion_total = 0
        self.__id = None

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def _obtener_videos(self, reel_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT v.*, p.nombre_empresa AS patrocinador_nombre FROM videos v LEFT JOIN patrocinadores p ON v.id_patrocinador = p.id_patrocinador WHERE v.reel_id = %s ORDER BY v.orden ASC",
                    (reel_id,)
                )
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def consultar(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT id, nombre, id_patrocinador AS patrocinado, duracion_total, creado_en, modificado_en FROM reels ORDER BY creado_en DESC")
                reels = cur.fetchall()
            for reel in reels:
                reel['videos'] = self._obtener_videos(reel['id'])
            return reels
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT id, nombre, duracion_total, creado_en, modificado_en FROM reels WHERE id = %s", (id,))
                reel = cur.fetchone()
            if not reel:
                return None
            reel['videos'] = self._obtener_videos(id)
            return reel
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def _validar_datos_recurso(self) -> bool:
        self.limpiar_errores()
        datos = {'nombre': self.__nombre}
        if not self.validar_obligatorios(['nombre'], datos):
            return False
        if self.__nombre and not self.validar_longitud(self.__nombre, 2, 50, 'Nombre'):
            return False
        return True

    def _validar_nombre(self, nombre) -> bool:
        self.limpiar_errores()
        if not self.validar_obligatorio(nombre, 'Nombre'):
            return False
        return self.validar_longitud(nombre, 2, 50, 'Nombre')

    def confirmar_registro(self):
        if not self._validar_datos_recurso():
            return False
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_recurso():
            return False
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO reels (nombre, duracion_total, creado_en) VALUES (%s, %s, NOW())",
                    (self.__nombre, self.__duracion_total)
                )
                return self.obtener_por_id(cur.lastrowid)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def registrar(self, datos):
        if not self._validar_nombre((datos.get('nombre') or '').strip()):
            return None
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO reels (nombre, duracion_total, creado_en) VALUES (%s, %s, NOW())",
                    (datos.get('nombre'), datos.get('duracion_total', 0))
                )
                return self.obtener_por_id(cur.lastrowid)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def modificar(self, id, datos):
        try:
            if 'nombre' in datos and not self._validar_nombre((datos.get('nombre') or '').strip()):
                return None
            sets = []
            params = []
            for campo in ['nombre', 'duracion_total']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            sets.append("modificado_en = NOW()")
            params.append(id)
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(f"UPDATE reels SET {', '.join(sets)} WHERE id = %s", params)
            return self.obtener_por_id(id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def confirmar_modificacion(self, id):
        # ponytail: controller calls modificar(id, datos) directly, satisfies ABC only
        return self.modificar(id, {})

    def confirmar_eliminacion(self, id):
        self.__id = id
        return self._eliminar(id)

    def _eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM videos WHERE reel_id = %s", (id,))
                cur.execute("DELETE FROM reels WHERE id = %s", (id,))
            return True
        except Exception:
            logger.exception('Error de base de datos')
            return False


class VideoModel:
    def _get_db(self):
        return Database.get_connection('estadio_db')

    def consultar_por_reel(self, reel_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT v.*, p.nombre_empresa AS patrocinador_nombre FROM videos v LEFT JOIN patrocinadores p ON v.id_patrocinador = p.id_patrocinador WHERE v.reel_id = %s ORDER BY v.orden ASC",
                    (reel_id,)
                )
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO videos (nombre, duracion_segundos, orden, reel_id, id_patrocinador) VALUES (%s, %s, %s, %s, %s)",
                    (datos.get('nombre'), datos.get('duracion_segundos', 0),
                     datos.get('orden'), datos.get('reel_id'),
                     datos.get('id_patrocinador'))
                )
                id = cur.lastrowid
            return {'id': id, **datos}
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM videos WHERE id = %s", (id,))
        except Exception:
            logger.exception('Error de base de datos')
