from app.database import Database
import logging
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class RecursoModel(ValidacionesMixin):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM recursos WHERE eliminado = 0"
            params = []
            if filtros.get('estado_id'):
                sql += " AND estado_id = %s"
                params.append(filtros['estado_id'])
            sql += " ORDER BY creado_en DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM recursos WHERE id = %s", (id,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def contar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT COUNT(*) as total FROM recursos WHERE eliminado = 0"
            params = []
            if filtros.get('estado_id'):
                sql += " AND estado_id = %s"
                params.append(filtros['estado_id'])
            with db.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0

    def modificar(self, id, datos):
        try:
            db = self._get_db()
            sets = []
            params = []
            for campo in ['nombre', 'descripcion', 'tipo_id', 'estado_id', 'fecha_compra', 'costo']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            if not sets:
                return self.obtener_por_id(id)
            sets.append("modificado_en = NOW()")
            params.append(id)
            with db.cursor() as cur:
                cur.execute(f"UPDATE recursos SET {', '.join(sets)} WHERE id = %s", params)
            return self.obtener_por_id(id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def verificar_nombre(self, nombre):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as total FROM recursos WHERE nombre = %s AND eliminado = 0",
                    (nombre,)
                )
                row = cur.fetchone()
                return row['total'] > 0 if row else False
        except Exception:
            logger.exception('Error de base de datos')
            return False


class MantenimientoModel(ValidacionesMixin):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__recurso_id = None
        self.__usuario_id = None
        self.__fecha_ingreso = None
        self.__diagnostico = None
        self.__observaciones = None

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_recurso_id(self, valor):
        self.__recurso_id = valor

    def set_usuario_id(self, valor):
        self.__usuario_id = valor

    def set_fecha_ingreso(self, valor):
        self.__fecha_ingreso = valor

    def set_diagnostico(self, valor):
        self.__diagnostico = valor

    def set_observaciones(self, valor):
        self.__observaciones = valor

    def _validar_datos_mantenimiento(self) -> bool:
        self.limpiar_errores()
        if not self.validar_obligatorio(self.__recurso_id, 'Recurso'):
            return False
        if not self.validar_obligatorio(self.__usuario_id, 'Usuario'):
            return False
        if not self.validar_fecha(self.__fecha_ingreso, 'Fecha de ingreso'):
            return False
        if not self.validar_obligatorio(self.__diagnostico, 'Diagnostico'):
            return False
        if self.__diagnostico and not self.validar_longitud(self.__diagnostico, 10, 500, 'Diagnostico'):
            return False
        if self.__observaciones and not self.validar_longitud(self.__observaciones, 5, 500, 'Observaciones'):
            return False
        return True

    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_mantenimiento():
            return None
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO mantenimientos (recurso_id, usuario_id, estado,
                       fecha_ingreso, diagnostico, observaciones, creado_en)
                       VALUES (%s, %s, 'en_espera', %s, %s, %s, NOW())""",
                    (
                        self.__recurso_id, self.__usuario_id,
                        self.__fecha_ingreso, self.__diagnostico or '',
                        self.__observaciones or '',
                    )
                )
                new_id = cur.lastrowid
            return self.obtener_por_id(new_id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def consultar(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM mantenimientos ORDER BY creado_en DESC"
                )
                items = cur.fetchall()
            for m in items:
                self._cargar_relaciones(m)
            return items
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def _cargar_relaciones(self, m):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM recursos WHERE id = %s", (m['recurso_id'],))
                recurso_row = cur.fetchone()
                if recurso_row:
                    m['recurso'] = recurso_row
                cur.execute("SELECT nombre FROM seguridad.usuarios WHERE id = %s", (m['usuario_id'],))
                user_row = cur.fetchone()
                m['usuario_nombre'] = user_row['nombre'] if user_row else 'Desconocido'
                cur.execute(
                    "SELECT * FROM historial_mantenimiento WHERE mantenimiento_id = %s ORDER BY creado_en ASC",
                    (m['id'],)
                )
                m['historial'] = cur.fetchall()
                for h in m['historial']:
                    cur.execute("SELECT nombre FROM seguridad.usuarios WHERE id = %s", (h['usuario_id'],))
                    u_row = cur.fetchone()
                    h['usuario_nombre'] = u_row['nombre'] if u_row else 'Desconocido'
        except Exception:
            logger.exception('Error de base de datos')

    def obtener_por_id(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM mantenimientos WHERE id = %s", (id,))
                m = cur.fetchone()
            if not m:
                return None
            self._cargar_relaciones(m)
            return m
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def modificar(self, id, datos):
        try:
            db = self._get_db()
            sets = []
            params = []
            for campo in ['estado', 'fecha_salida', 'diagnostico', 'observaciones']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            if sets:
                params.append(id)
                with db.cursor() as cur:
                    cur.execute(f"UPDATE mantenimientos SET {', '.join(sets)} WHERE id = %s", params)
            return self.obtener_por_id(id)
        except Exception:
            logger.exception('Error de base de datos')
            return None


class HistorialMantenimientoModel:
    def __init__(self):
        self.db_name = 'estadio_db'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM historial_mantenimiento WHERE 1=1"
            params = []
            if filtros.get('mantenimiento_id'):
                sql += " AND mantenimiento_id = %s"
                params.append(filtros['mantenimiento_id'])
            sql += " ORDER BY creado_en ASC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO historial_mantenimiento
                       (mantenimiento_id, usuario_id, accion, descripcion, creado_en)
                       VALUES (%s, %s, %s, %s, NOW())""",
                    (datos['mantenimiento_id'], datos['usuario_id'],
                     datos['accion'], datos.get('descripcion', ''))
                )
                new_id = cur.lastrowid
            return {'id': new_id, **datos}
        except Exception:
            logger.exception('Error de base de datos')
            return None
