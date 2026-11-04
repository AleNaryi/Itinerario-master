from datetime import datetime, date, timezone
import logging
from app.database import Database
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class PremioModel(ValidacionesMixin, CrudInterface):
    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__id = None
        self.__nombre = None
        self.__id_patrocinador = None
        self.__descripcion = None
        self.__foto = None
        self.__cantidad = 1

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_nombre(self, valor):
        self.__nombre = valor

    def set_id_patrocinador(self, valor):
        self.__id_patrocinador = valor

    def set_descripcion(self, valor):
        self.__descripcion = valor

    def set_foto(self, valor):
        self.__foto = valor

    def set_cantidad(self, valor):
        try:
            self.__cantidad = max(1, int(valor))
        except (ValueError, TypeError):
            self.__cantidad = 1

    def _validar_datos_premio(self) -> bool:
        self.limpiar_errores()
        datos = {'nombre': self.__nombre, 'id_patrocinador': self.__id_patrocinador}
        if not self.validar_obligatorios(['nombre', 'id_patrocinador'], datos):
            return False
        if not self.validar_longitud(self.__nombre, 2, 50, 'Nombre'):
            return False
        if not self.validar_entero_positivo(self.__id_patrocinador, 'Patrocinador'):
            return False
        if self.__descripcion and not self.validar_longitud(self.__descripcion, 1, 500, 'Descripción'):
            return False
        return True

    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_premio():
            return False
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    """INSERT INTO premios
                       (nombre, id_patrocinador, descripcion, estado,
                        fecha_creacion, hora_creacion, foto, cantidad, estatus)
                       VALUES (%s, %s, %s, 'pendiente', %s, %s, %s, %s, FALSE)""",
                    (
                        self.__nombre, self.__id_patrocinador,
                        self.__descripcion or '',
                        date.today(), datetime.now().time(),
                        self.__foto or 'default-premio.png',
                        self.__cantidad,
                    )
                )
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM premios WHERE estatus = FALSE"
            params = []
            if filtros.get('estado'):
                sql += " AND estado = %s"
                params.append(filtros['estado'])
            sql += " ORDER BY fecha_creacion DESC, hora_creacion DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def contar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT COUNT(*) as total FROM premios WHERE estatus = FALSE"
            params = []
            if filtros.get('estado'):
                sql += " AND estado = %s"
                params.append(filtros['estado'])
            with db.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0

    def confirmar_modificacion(self, id):
        self.__id = id
        return self._modificar(id)

    def _modificar(self, id_registro):
        if not self._validar_datos_premio():
            return False
        try:
            sets = ["nombre = %s", "id_patrocinador = %s", "descripcion = %s", "cantidad = %s"]
            params = [self.__nombre, self.__id_patrocinador, self.__descripcion or '', self.__cantidad]
            if self.__foto:
                sets.append("foto = %s")
                params.append(self.__foto)
            params.append(id_registro)
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(f"UPDATE premios SET {', '.join(sets)} WHERE id = %s", params)
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def confirmar_eliminacion(self, id):
        self.__id = id
        return self._eliminar(id)

    def _eliminar(self, id_registro):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("UPDATE premios SET estatus = TRUE WHERE id = %s", (id_registro,))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_premios_pendientes(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.estado, p.id_patrocinador,
                           p.foto, p.fecha_creacion, p.hora_creacion,
                           p.cantidad, p.cantidad_entregada,
                           pat.nombre_empresa as patrocinador_nombre
                    FROM premios p
                    LEFT JOIN patrocinadores pat ON p.id_patrocinador = pat.id_patrocinador
                    WHERE p.estado = 'pendiente' AND p.estatus = FALSE
                          AND p.cantidad_entregada < p.cantidad
                    ORDER BY p.fecha_creacion DESC, p.hora_creacion DESC
                """)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_premios_entregados(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT p.id, p.nombre, p.descripcion, p.foto, p.fecha_entrega, p.entregado_por,
                           p.cantidad, p.cantidad_entregada,
                           pat.nombre_empresa as patrocinador_nombre
                    FROM premios p
                    LEFT JOIN patrocinadores pat ON p.id_patrocinador = pat.id_patrocinador
                    WHERE p.estado = 'entregado' AND p.estatus = FALSE
                    ORDER BY p.fecha_entrega DESC
                    LIMIT 100
                """)
                premios = cur.fetchall()
            from app.model.auth_model import UsuarioModel
            um = UsuarioModel()
            for p in premios:
                if p['entregado_por']:
                    user = um.obtener_por_id(p['entregado_por'])
                    p['usuario_nombre'] = user.nombre if user else '\u2014'
                else:
                    p['usuario_nombre'] = '\u2014'
            return premios
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_patrocinadores(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT id_patrocinador, nombre_empresa FROM patrocinadores WHERE estado = 1 ORDER BY nombre_empresa")
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_para_api(self, premio_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT id, nombre, id_patrocinador, descripcion, foto, cantidad, cantidad_entregada FROM premios WHERE id = %s AND estatus = FALSE", (premio_id,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def entregar(self, premio_id, id_patrocinador=None, descripcion=None, entregado_por=None, cantidad_entregar=1):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT cantidad, cantidad_entregada FROM premios WHERE id = %s",
                    (premio_id,)
                )
                actual = cur.fetchone()
                if not actual:
                    return False
                restante = actual['cantidad'] - actual['cantidad_entregada']
                cantidad_entregar = min(int(cantidad_entregar), restante)
                if cantidad_entregar <= 0:
                    return False
                nueva_entregada = actual['cantidad_entregada'] + cantidad_entregar
                nuevo_estado = 'entregado' if nueva_entregada >= actual['cantidad'] else 'pendiente'
                cur.execute(
                    """UPDATE premios
                       SET cantidad_entregada = %s,
                           estado = %s,
                           fecha_entrega = %s,
                           id_patrocinador = %s,
                           descripcion = %s,
                           entregado_por = %s
                       WHERE id = %s""",
                    (nueva_entregada, nuevo_estado, datetime.now(timezone.utc),
                     id_patrocinador, descripcion, entregado_por, premio_id)
                )
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False
