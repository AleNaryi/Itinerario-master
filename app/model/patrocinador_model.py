from app.database import Database
import logging
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class PatrocinadorModel(ValidacionesMixin, CrudInterface):
    VALID_TIPO_CONTRATO = {'1', '2', '3'}
    VALID_ESTADO = {0, 1}

    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self.__id_patrocinador = None
        self.__nombre_empresa = None
        self.__rif = None
        self.__nombre_contacto = None
        self.__telefono = None
        self.__email = None
        self.__tipo_contrato = None
        self.__encargado_id = None

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_id_patrocinador(self, valor):
        self.__id_patrocinador = valor

    def set_nombre_empresa(self, valor):
        self.__nombre_empresa = valor

    def set_rif(self, valor):
        self.__rif = valor

    def set_nombre_contacto(self, valor):
        self.__nombre_contacto = valor

    def set_telefono(self, valor):
        self.__telefono = valor

    def set_email(self, valor):
        self.__email = valor

    def set_tipo_contrato(self, valor):
        if str(valor) not in self.VALID_TIPO_CONTRATO:
            raise ValueError(f'Tipo de contrato inválido: {valor}')
        self.__tipo_contrato = valor

    def set_encargado_id(self, valor):
        if valor is not None and valor != '' and str(valor).isdigit():
            self.__encargado_id = int(valor)
        elif valor is None or valor == '':
            self.__encargado_id = None
        else:
            raise ValueError(f'Encargado inválido: {valor}')

    def _validar_datos_patrocinador(self) -> bool:
        self.limpiar_errores()
        datos = {
            'nombre_empresa': self.__nombre_empresa,
            'rif': self.__rif,
            'tipo_contrato': str(self.__tipo_contrato or ''),
            'encargado_id': self.__encargado_id,
        }
        if not self.validar_obligatorios(['nombre_empresa', 'rif', 'tipo_contrato', 'encargado_id'], datos):
            return False
        if not self.validar_longitud(self.__nombre_empresa, 2, 150, 'Nombre de empresa'):
            return False
        if not self.validar_rif(self.__rif):
            return False
        if not self.validar_email(self.__email):
            return False
        return True

    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_patrocinador():
            return False
        try:
            db = self._get_db()
            sql = """INSERT INTO patrocinadores
                     (nombre_empresa, rif, tipo_contrato, nombre_contacto, telefono, email, estado, encargado_id)
                     VALUES (%s, %s, %s, %s, %s, %s, 1, %s)"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self.__nombre_empresa, self.__rif, self.__tipo_contrato,
                    self.__nombre_contacto or '', self.__telefono or '', self.__email or '',
                    self.__encargado_id
                ))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def consultar(self, activos=True):
        try:
            db = self._get_db()
            sql = "SELECT * FROM patrocinadores"
            params = []
            if activos:
                sql += " WHERE estado = 1"
            sql += " ORDER BY nombre_empresa ASC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id_patrocinador):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM patrocinadores WHERE id_patrocinador = %s", (id_patrocinador,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def confirmar_modificacion(self, id):
        self.__id_patrocinador = id
        return self._modificar(id)

    def _modificar(self, id):
        if not self._validar_datos_patrocinador():
            return False
        try:
            db = self._get_db()
            sql = """UPDATE patrocinadores SET nombre_empresa = %s, rif = %s,
                     tipo_contrato = %s, nombre_contacto = %s, telefono = %s, email = %s, encargado_id = %s
                     WHERE id_patrocinador = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self.__nombre_empresa, self.__rif, self.__tipo_contrato,
                    self.__nombre_contacto or '', self.__telefono or '', self.__email or '',
                    self.__encargado_id, id
                ))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def confirmar_eliminacion(self, id):
        self.__id_patrocinador = id
        return self._eliminar(id)

    def _eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("UPDATE patrocinadores SET estado = 0 WHERE id_patrocinador = %s", (id,))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def verificar_nombre_empresa(self, nombre):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT COUNT(*) as total FROM patrocinadores WHERE nombre_empresa = %s AND estado = 1",
                    (nombre,)
                )
                row = cur.fetchone()
                return row['total'] > 0 if row else False
        except Exception:
            logger.exception('Error de base de datos')
            return False
