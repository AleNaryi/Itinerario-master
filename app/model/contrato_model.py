from app.database import Database
import logging
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class ContratoModel(ValidacionesMixin, CrudInterface):
    VALID_TIPO = {'1', '2', '3'}
    VALID_ESTATUS = {'Borrador', 'Vigente', 'Vencido'}

    def __init__(self):
        super().__init__()
        self.db_name = 'estadio_db'
        self._id_contrato = None
        self._id_patrocinador = None
        self._fecha_inicio = None
        self._fecha_fin = None
        self._tipo = None
        self._monto_total = None
        self._estatus = 'Borrador'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_id_contrato(self, valor):
        self._id_contrato = valor

    def set_id_patrocinador(self, valor):
        self._id_patrocinador = valor

    def set_fecha_inicio(self, valor):
        self._fecha_inicio = valor

    def set_fecha_fin(self, valor):
        self._fecha_fin = valor

    def set_tipo(self, valor):
        if str(valor) not in self.VALID_TIPO:
            raise ValueError(f'Tipo de contrato inválido: {valor}')
        self._tipo = valor

    def set_monto_total(self, valor):
        self._monto_total = valor

    def set_estatus(self, valor):
        if valor not in self.VALID_ESTATUS:
            raise ValueError(f'Estatus inválido: {valor}')
        self._estatus = valor

    def _validar_datos_contrato(self) -> bool:
        self.limpiar_errores()
        datos = {
            'id_patrocinador': self._id_patrocinador,
            'fecha_inicio': self._fecha_inicio,
            'fecha_fin': self._fecha_fin,
            'tipo': self._tipo,
        }
        if not self.validar_obligatorios(['id_patrocinador', 'fecha_inicio', 'fecha_fin', 'tipo'], datos):
            return False
        if not self.validar_fecha(self._fecha_inicio, 'Fecha de inicio') or \
           not self.validar_fecha(self._fecha_fin, 'Fecha de fin'):
            return False
        if self._fecha_fin < self._fecha_inicio:
            self.errores.append('La fecha de fin no puede ser anterior a la fecha de inicio')
            return False
        if self._monto_total is not None:
            try:
                monto = float(self._monto_total)
                if monto <= 0:
                    self.errores.append('El monto debe ser mayor a 0')
                    return False
            except (ValueError, TypeError):
                self.errores.append('El monto no es valido')
                return False
        return True

    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_contrato():
            return False
        try:
            db = self._get_db()
            sql = """INSERT INTO contrato
                     (id_patrocinador, fecha_inicio, fecha_fin, tipo, monto_total, estatus, estado)
                     VALUES (%s, %s, %s, %s, %s, %s, 1)"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self._id_patrocinador, self._fecha_inicio, self._fecha_fin,
                    self._tipo, self._monto_total, self._estatus
                ))
                self._id_contrato = cur.lastrowid
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def consultar(self, activos=True):
        try:
            db = self._get_db()
            sql = """SELECT c.*, p.nombre_empresa
                     FROM contrato c
                     LEFT JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador"""
            params = []
            if activos:
                sql += " WHERE c.estado = 1"
            sql += " ORDER BY c.fecha_inicio DESC"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id_contrato):
        try:
            db = self._get_db()
            sql = """SELECT c.*, p.nombre_empresa
                     FROM contrato c
                     LEFT JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador
                     WHERE c.id_contrato = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (id_contrato,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def confirmar_modificacion(self, id):
        self._id_contrato = id
        return self._modificar(id)

    def _modificar(self, id):
        if not self._validar_datos_contrato():
            return False
        try:
            db = self._get_db()
            sql = """UPDATE contrato SET id_patrocinador = %s, fecha_inicio = %s,
                     fecha_fin = %s, tipo = %s, monto_total = %s, estatus = %s
                     WHERE id_contrato = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self._id_patrocinador, self._fecha_inicio, self._fecha_fin,
                    self._tipo, self._monto_total, self._estatus, id
                ))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def confirmar_eliminacion(self, id):
        self._id_contrato = id
        return self._eliminar(id)

    def _eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("UPDATE contrato SET estado = 0 WHERE id_contrato = %s", (id,))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_patrocinadores(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT id_patrocinador, nombre_empresa FROM patrocinadores WHERE estado = 1 ORDER BY nombre_empresa"
                )
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []
