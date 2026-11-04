from datetime import datetime
import logging
from app.database import Database, transaction
from app.config import DATABASE_CONFIG
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class TareaModel(ValidacionesMixin, CrudInterface):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__nombre_tarea = None
        self.__instruccion = None
        self.__id_usuario_creador = None
        self.__id_tarea = None

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_nombre_tarea(self, valor):
        self.__nombre_tarea = valor

    def set_instruccion(self, valor):
        self.__instruccion = valor

    def set_id_usuario_creador(self, valor):
        self.__id_usuario_creador = valor

    def _validar_datos_tarea(self) -> bool:
        self.limpiar_errores()
        datos = {'nombre_tarea': self.__nombre_tarea, 'instruccion': self.__instruccion}
        if not self.validar_obligatorios(['nombre_tarea', 'instruccion'], datos):
            return False
        if not self.validar_longitud(self.__nombre_tarea, 3, 50, 'Nombre de la tarea'):
            return False
        if not self.validar_longitud(self.__instruccion, 10, 1000, 'Instruccion'):
            return False
        return True

    def confirmar_registro(self):
        if not self._validar_datos_tarea():
            return False
        return self._registrar()

    def _registrar(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO tareas (Nombre_Tarea, Instruccion, id_usuario_creador, Estatus) VALUES (%s, %s, %s, 1)",
                    (self.__nombre_tarea, self.__instruccion, self.__id_usuario_creador)
                )
                return cur.lastrowid
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def consultar(self, activas=True):
        try:
            db = self._get_db()
            sql = "SELECT * FROM tareas"
            params = []
            if activas:
                sql += " WHERE Estatus = 1"
            sql += " ORDER BY id_tarea DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id_tarea):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM tareas WHERE id_tarea = %s", (id_tarea,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def modificar(self, id_tarea, datos):
        try:
            db = self._get_db()
            sets = []
            params = []
            for campo in ['Nombre_Tarea', 'Instruccion']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            if sets:
                params.append(id_tarea)
                with db.cursor() as cur:
                    cur.execute(f"UPDATE tareas SET {', '.join(sets)} WHERE id_tarea = %s", params)
            return self.obtener_por_id(id_tarea)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def confirmar_modificacion(self, id_tarea):
        self.__id_tarea = id_tarea
        if not self._validar_datos_tarea():
            return False
        return self._modificar(id_tarea)

    def _modificar(self, id_tarea):
        return bool(self.modificar(id_tarea, {
            'Nombre_Tarea': self.__nombre_tarea,
            'Instruccion': self.__instruccion,
        }))

    def confirmar_eliminacion(self, id_tarea):
        self.__id_tarea = id_tarea
        return self._eliminar(id_tarea)

    def _eliminar(self, id_tarea):
        try:
            tarea = self.obtener_por_id(id_tarea)
            if not tarea:
                return None
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("UPDATE tareas SET Estatus = 0 WHERE id_tarea = %s", (id_tarea,))
            return tarea
        except Exception:
            logger.exception('Error de base de datos')
            return None


class TareasAsignadasModel:
    def _get_db(self):
        return Database.get_connection('estadio_db')

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = """SELECT ta.*, t.Nombre_Tarea
                     FROM tareas_asignadas ta
                     JOIN tareas t ON ta.id_tarea = t.id_tarea
                     WHERE ta.Estatus = 1"""
            params = []
            if filtros.get('id_usuario'):
                sql += " AND ta.id_usuario = %s"
                params.append(filtros['id_usuario'])
            if filtros.get('id_tarea'):
                sql += " AND ta.id_tarea = %s"
                params.append(filtros['id_tarea'])
            sql += " ORDER BY ta.fecha_asignacion_tarea DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id_asignacion):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT ta.*, t.Nombre_Tarea
                       FROM tareas_asignadas ta
                       JOIN tareas t ON ta.id_tarea = t.id_tarea
                       WHERE ta.id_asignacion = %s""",
                    (id_asignacion,)
                )
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def obtener_por_usuario(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT ta.*, t.Nombre_Tarea, t.Instruccion
                       FROM tareas_asignadas ta
                       JOIN tareas t ON ta.id_tarea = t.id_tarea
                       WHERE ta.id_usuario = %s AND ta.Estatus = 1 AND t.Estatus = 1
                       ORDER BY ta.fecha_asignacion_tarea DESC""",
                    (usuario_id,)
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
                    """INSERT INTO tareas_asignadas
                       (id_tarea, id_usuario, Estado, fecha_asignacion_tarea, Estatus)
                       VALUES (%s, %s, %s, %s, 1)""",
                    (
                        datos['id_tarea'],
                        datos['id_usuario'],
                        datos.get('Estado', 'Pendiente'),
                        datos.get('fecha_asignacion_tarea', datetime.now()),
                    )
                )
                return self.obtener_por_id(cur.lastrowid)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def asignar_a_usuarios(self, id_tarea, ids_usuarios, titulo_tarea, asignador):
        """Asigna la tarea a varios usuarios y notifica a cada uno.
        Una sola transacción: asignaciones + notificaciones (escritura cruzada al
        esquema de seguridad configurado, mismo servidor).
        Devuelve (asignados, omitidos_duplicados)."""
        # nombre de esquema desde config (soporta *_test); nunca input del cliente
        esquema_seg = DATABASE_CONFIG['seguridad']['database']
        asignados, omitidos = [], []
        try:
            with transaction('estadio_db'):
                db = self._get_db()
                with db.cursor() as cur:
                    for uid in ids_usuarios:
                        cur.execute(
                            "SELECT id_asignacion FROM tareas_asignadas "
                            "WHERE id_tarea = %s AND id_usuario = %s AND Estatus = 1",
                            (id_tarea, uid)
                        )
                        if cur.fetchone():
                            omitidos.append(uid)
                            continue
                        cur.execute(
                            """INSERT INTO tareas_asignadas
                               (id_tarea, id_usuario, Estado, fecha_asignacion_tarea, Estatus)
                               VALUES (%s, %s, 'Pendiente', NOW(), 1)""",
                            (id_tarea, uid)
                        )
                        asignados.append(uid)
                        cur.execute(
                            f"""INSERT INTO {esquema_seg}.notificaciones
                               (usuario_id, tipo, titulo, mensaje, url, leida, fecha_creacion)
                               VALUES (%s, 'tarea_asignada', %s, %s, %s, 0, NOW())""",
                            (
                                uid,
                                'Nueva tarea asignada',
                                f'"{titulo_tarea}" te fue asignada por {asignador}',
                                '/gestion-tarea/mis-tareas',
                            )
                        )
            return asignados, omitidos
        except Exception:
            logger.exception('Error de base de datos')
            return None, None

    def modificar_estado(self, id_asignacion, estado):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "UPDATE tareas_asignadas SET Estado = %s WHERE id_asignacion = %s",
                    (estado, id_asignacion)
                )
        except Exception:
            logger.exception('Error de base de datos')

    def consultar_todas(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT ta.id_asignacion, ta.id_tarea, ta.id_usuario, ta.Estado,
                           ta.fecha_asignacion_tarea,
                           t.Nombre_Tarea, t.Instruccion,
                           u.nombre AS usuario_nombre, u.cedula AS usuario_cedula
                    FROM tareas_asignadas ta
                    JOIN tareas t ON ta.id_tarea = t.id_tarea
                    JOIN seguridad.usuarios u ON ta.id_usuario = u.id
                    WHERE ta.Estatus = 1 AND t.Estatus = 1
                    ORDER BY ta.fecha_asignacion_tarea DESC
                """)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def contar_pendientes(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """SELECT COUNT(*) as total FROM tareas_asignadas ta
                       JOIN tareas t ON ta.id_tarea = t.id_tarea
                       WHERE ta.id_usuario = %s AND ta.Estatus = 1 AND t.Estatus = 1
                       AND ta.Estado != 'Completada'""",
                    (usuario_id,)
                )
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0
