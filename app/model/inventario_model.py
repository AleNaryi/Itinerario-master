from app.database import Database
import logging
from app.model.auth_model import UsuarioModel
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class InventarioModel(ValidacionesMixin, CrudInterface):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__id = None
        self.__nombre = None
        self.__descripcion = None
        self.__tipo_id = None
        self.__estado_id = 1
        self.__fecha_compra = None
        self.__costo = None
        self.__asignacion_recurso_id = None
        self.__asignacion_usuario_id = None
        self.__asignacion_fecha_devolucion = None
        self.__asignacion_notas = None
        self.__asignacion_estado_id = 1

    def _get_db(self):
        return Database.get_connection(self.db_name)

    # ---- SETTERS ----
    def set_nombre(self, valor):
        self.__nombre = valor

    def set_descripcion(self, valor):
        self.__descripcion = valor

    def set_estado_id(self, valor):
        self.__estado_id = valor

    def set_costo(self, valor):
        self.__costo = valor

    def set_recurso_id(self, valor):
        self.__asignacion_recurso_id = valor

    def set_usuario_id(self, valor):
        self.__asignacion_usuario_id = valor

    def set_fecha_devolucion_esperada(self, valor):
        self.__asignacion_fecha_devolucion = valor

    def set_notas(self, valor):
        self.__asignacion_notas = valor

    def set_estado_asignacion_id(self, valor):
        self.__asignacion_estado_id = valor

    # ---- PHP-COMPATIBLE SETTER ALIASES ----
    def set_id_activo(self, valor):
        self.__id = valor

    def set_id_tipo(self, valor):
        self.__tipo_id = valor

    def set_id_ubicacion(self, valor):
        self.set_estado_id(valor)

    def set_fecha_adquisicion(self, valor):
        self.__fecha_compra = valor

    # ---- VALIDACION PRIVADA ----
    def _validar_datos_recurso(self) -> bool:
        self.limpiar_errores()
        datos = {
            'nombre': self.__nombre,
            'descripcion': self.__descripcion,
            'tipo_id': self.__tipo_id,
            'fecha_compra': self.__fecha_compra,
            'costo': self.__costo,
        }
        if not self.validar_obligatorios(['nombre', 'tipo_id'], datos):
            return False
        if not self.validar_entero_positivo(self.__tipo_id, 'Tipo de recurso'):
            return False
        if not self.validar_longitud(self.__nombre, 2, 50, 'Nombre'):
            return False
        if self.__descripcion and not self.validar_longitud(self.__descripcion, 5, 500, 'Descripción'):
            return False
        if self.__fecha_compra:
            if not self.validar_fecha(self.__fecha_compra, 'Fecha de compra'):
                return False
            if not self.validar_fecha_no_futura(self.__fecha_compra, 'Fecha de compra'):
                return False
        if self.__costo is not None and str(self.__costo).strip() != '':
            try:
                if float(self.__costo) <= 0:
                    self.errores.append('El campo Costo debe ser mayor a 0')
                    return False
            except (ValueError, TypeError):
                self.errores.append('El campo Costo debe ser numérico')
                return False
        return True

    # ---- CRUD RECURSOS (estilo PHP) ----
    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_recurso():
            return False
        try:
            db = self._get_db()
            sql = """INSERT INTO recursos (nombre, descripcion, tipo_id, estado_id, fecha_compra, costo, creado_en)
                     VALUES (%s, %s, %s, %s, %s, %s, NOW())"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self.__nombre, self.__descripcion, self.__tipo_id,
                    self.__estado_id, self.__fecha_compra, self.__costo
                ))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def consultar(self, solo_activos=True, tipo_id=None, estado_id=None):
        try:
            db = self._get_db()
            sql = """SELECT r.*, t.nombre as tipo_nombre, e.nombre as estado_nombre
                     FROM recursos r
                     LEFT JOIN tipo_recurso t ON r.tipo_id = t.id
                     LEFT JOIN estado_recurso e ON r.estado_id = e.id
                     WHERE 1=1"""
            params = []
            if solo_activos:
                sql += " AND r.eliminado = 0"
            if tipo_id:
                sql += " AND r.tipo_id = %s"
                params.append(tipo_id)
            if estado_id:
                sql += " AND r.estado_id = %s"
                params.append(estado_id)
            sql += " ORDER BY r.creado_en DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def confirmar_modificacion(self, id):
        self.__id = id
        return self._modificar(id)

    def _modificar(self, id):
        if not self._validar_datos_recurso():
            return False
        if not self.validar_entero_positivo(id, 'id_recurso'):
            return False
        try:
            db = self._get_db()
            sql = """UPDATE recursos
                     SET nombre = %s, descripcion = %s, tipo_id = %s,
                         estado_id = %s, fecha_compra = %s,
                         costo = %s, modificado_en = NOW()
                     WHERE id = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self.__nombre, self.__descripcion, self.__tipo_id,
                    self.__estado_id, self.__fecha_compra, self.__costo, id
                ))
                return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def buscar(self):
        try:
            db = self._get_db()
            sql = """SELECT r.*, t.nombre as tipo_nombre, e.nombre as estado_nombre
                     FROM recursos r
                     LEFT JOIN tipo_recurso t ON r.tipo_id = t.id
                     LEFT JOIN estado_recurso e ON r.estado_id = e.id
                     WHERE r.id = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (self.__id,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def confirmar_eliminacion(self, id):
        self.__id = id
        return self._eliminar(id)

    def _eliminar(self, id):
        try:
            db = self._get_db()
            sql = "UPDATE recursos SET eliminado = 1, modificado_en = NOW() WHERE id = %s"
            with db.cursor() as cur:
                cur.execute(sql, (id,))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def cambiar_estado(self, recurso_id, nuevo_estado):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "UPDATE recursos SET estado_id = %s, modificado_en = NOW() WHERE id = %s",
                    (nuevo_estado, recurso_id)
                )
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    # ---- HELPERS ADICIONALES (dropdowns, conteos) ----
    def obtener_por_id(self, id):
        self.__id = id
        return self.buscar()

    # ---- TIPOS DE RECURSO (delegados a TipoRecursoModel) ----
    def obtener_tipos(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM tipo_recurso ORDER BY nombre")
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    # ---- ESTADOS ----
    def obtener_estados(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM estado_recurso ORDER BY id")
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_estados_asignacion(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM estado_asignacion ORDER BY id")
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    # ---- ASIGNACIONES ----
    def consultar_asignaciones(self, recurso_id=None, usuario_id=None, estado_asig_id=None):
        try:
            db = self._get_db()
            sql = """SELECT a.*, r.nombre as recurso_nombre, e.nombre as estado_asignacion_nombre,
                            u.nombre as usuario_nombre
                     FROM asignaciones_recursos a
                     JOIN recursos r ON a.recurso_id = r.id
                     LEFT JOIN estado_asignacion e ON a.estado_asignacion_id = e.id
                     LEFT JOIN seguridad.usuarios u ON a.usuario_id = u.id
                     WHERE 1=1"""
            params = []
            if recurso_id:
                sql += " AND a.recurso_id = %s"
                params.append(recurso_id)
            if usuario_id:
                sql += " AND a.usuario_id = %s"
                params.append(usuario_id)
            if estado_asig_id:
                sql += " AND a.estado_asignacion_id = %s"
                params.append(estado_asig_id)
            sql += " ORDER BY a.fecha_asignacion DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_asignacion(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT a.*, r.nombre as recurso_nombre, e.nombre as estado_asignacion_nombre,
                              u.nombre as usuario_nombre
                       FROM asignaciones_recursos a
                       JOIN recursos r ON a.recurso_id = r.id
                       LEFT JOIN estado_asignacion e ON a.estado_asignacion_id = e.id
                       LEFT JOIN seguridad.usuarios u ON a.usuario_id = u.id
                       WHERE a.id = %s""",
                    (id,)
                )
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def obtener_asignacion_activa(self, recurso_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM asignaciones_recursos WHERE recurso_id = %s AND fecha_devolucion_real IS NULL LIMIT 1",
                    (recurso_id,)
                )
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def registrar_asignacion(self):
        try:
            db = self._get_db()
            sql = """INSERT INTO asignaciones_recursos
                     (recurso_id, usuario_id, fecha_devolucion_esperada, notas, estado_asignacion_id, fecha_asignacion)
                     VALUES (%s, %s, %s, %s, %s, NOW())"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self.__asignacion_recurso_id,
                    self.__asignacion_usuario_id,
                    self.__asignacion_fecha_devolucion,
                    self.__asignacion_notas,
                    self.__asignacion_estado_id,
                ))
                new_id = cur.lastrowid
            return self.obtener_asignacion(new_id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def devolver_recurso(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """UPDATE asignaciones_recursos
                       SET fecha_devolucion_real = NOW(), estado_asignacion_id = 2
                       WHERE id = %s""",
                    (id,)
                )
            return self.obtener_asignacion(id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def tiene_asignaciones_pendientes(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as total FROM asignaciones_recursos WHERE recurso_id = %s AND fecha_devolucion_real IS NULL",
                    (id,)
                )
                row = cur.fetchone()
                return row['total'] > 0 if row else False
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def total_asignaciones(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as total FROM asignaciones_recursos WHERE recurso_id = %s", (id,)
                )
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0

    # ---- VALIDACIONES AJAX ----
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

    # ---- USUARIOS (cross-DB) ----
    def obtener_usuarios(self):
        try:
            return UsuarioModel().consultar()
        except Exception:
            logger.exception('Error de base de datos')
            return []


class TipoRecursoModel(ValidacionesMixin, CrudInterface):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__id_tipo = None
        self.__nombre_tipo = None
        self.__descripcion_tipo = None

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_id_tipo(self, valor):
        self.__id_tipo = valor

    def set_nombre_tipo(self, valor):
        self.__nombre_tipo = valor

    def set_descripcion_tipo(self, valor):
        self.__descripcion_tipo = valor

    def consultar(self):
        return self._consultar_tipos()

    def _consultar_tipos(self):
        try:
            db = self._get_db()
            sql = "SELECT * FROM tipo_recurso WHERE 1=1"
            with db.cursor() as cur:
                cur.execute(sql)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def buscar_tipo(self):
        try:
            db = self._get_db()
            sql = "SELECT * FROM tipo_recurso WHERE id = %s"
            with db.cursor() as cur:
                cur.execute(sql, (self.__id_tipo,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def _validar_datos_recurso(self) -> bool:
        self.limpiar_errores()
        datos = {'nombre': self.__nombre_tipo}
        if not self.validar_obligatorios(['nombre'], datos):
            return False
        if not self.validar_longitud(self.__nombre_tipo, 2, 50, 'Nombre'):
            return False
        return True

    def confirmar_registro(self):
        if not self._validar_datos_recurso():
            return False
        return self._registrar_tipo()

    def _registrar_tipo(self):
        try:
            db = self._get_db()
            sql = "INSERT INTO tipo_recurso (nombre, descripcion) VALUES (%s, %s)"
            with db.cursor() as cur:
                cur.execute(sql, (self.__nombre_tipo, self.__descripcion_tipo))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def confirmar_modificacion(self, id_tipo):
        self.__id_tipo = id_tipo
        if not self._validar_datos_recurso():
            return False
        return self._modificar_tipo(id_tipo)

    def _modificar_tipo(self, id_tipo):
        try:
            db = self._get_db()
            sql = "UPDATE tipo_recurso SET nombre = %s, descripcion = %s WHERE id = %s"
            with db.cursor() as cur:
                cur.execute(sql, (self.__nombre_tipo, self.__descripcion_tipo, id_tipo))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def confirmar_eliminacion(self, id_tipo):
        self.__id_tipo = id_tipo
        return self._eliminar_tipo(id_tipo)

    def _eliminar_tipo(self, id_tipo):
        try:
            db = self._get_db()
            sql = "DELETE FROM tipo_recurso WHERE id = %s"
            with db.cursor() as cur:
                cur.execute(sql, (id_tipo,))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False
