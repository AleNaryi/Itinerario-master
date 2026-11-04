from app.database import Database
import logging
from werkzeug.security import generate_password_hash
from app.model.interfaces import CrudInterface
from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)


class UsuarioModel(ValidacionesMixin, CrudInterface):
    VALID_ROLES = {'Superadmin', 'Administrador', 'Usuario'}
    VALID_DEPARTAMENTOS = {'Producción', 'Técnica', 'Comercial', 'Administración', 'Operaciones', 'Medios', 'Palco de Operaciones'}

    def __init__(self):
        super().__init__()
        self.db_name = 'seguridad'
        self.__id = None
        self.__nombre = None
        self.__email = None
        self.__cedula = None
        self.__rol = None
        self.__departamento = None
        self.__telefono = None
        self.__password = None
        self.__activo = True

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_nombre(self, valor):
        self.__nombre = valor

    def set_email(self, valor):
        self.__email = valor

    def set_cedula(self, valor):
        self.__cedula = valor

    def set_rol(self, valor):
        if valor not in self.VALID_ROLES:
            raise ValueError(f'Rol inválido: {valor}')
        self.__rol = valor

    def set_departamento(self, valor):
        if valor and valor not in self.VALID_DEPARTAMENTOS:
            raise ValueError(f'Departamento inválido: {valor}')
        self.__departamento = valor

    def set_telefono(self, valor):
        self.__telefono = valor

    def set_password(self, valor):
        self.__password = valor

    def set_activo(self, valor):
        self.__activo = valor in (True, 'true', '1', 1, 'True')

    def _validar_datos_usuario(self) -> bool:
        self.limpiar_errores()
        datos = {
            'nombre': self.__nombre,
            'email': self.__email,
            'cedula': self.__cedula,
            'rol': self.__rol,
        }
        if not self.validar_obligatorios(['nombre', 'email', 'cedula', 'rol'], datos):
            return False
        if not self.validar_longitud(self.__nombre, 2, 50, 'Nombre'):
            return False
        if not self.validar_longitud(self.__email, 5, 150, 'Email'):
            return False
        if not self.validar_email(self.__email):
            return False
        if self.__cedula and not self.validar_longitud(self.__cedula, 6, 10, 'Cedula'):
            return False
        if self.__telefono and not self.validar_longitud(self.__telefono, 9, 16, 'Telefono'):
            return False
        if self.__password and not self.validar_longitud(self.__password, 8, 30, 'Contrasena'):
            return False
        return True

    def confirmar_registro(self):
        return self._registrar()

    def _registrar(self):
        if not self._validar_datos_usuario():
            return False
        try:
            db = self._get_db()
            sql = """INSERT INTO usuarios
                     (nombre, email, password_hash, cedula, rol, departamento, telefono, activo, fecha_registro)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    self.__nombre, self.__email,
                    generate_password_hash(self.__password) if self.__password else '',
                    self.__cedula, self.__rol,
                    self.__departamento or 'Medios', self.__telefono or '',
                    1 if self.__activo else 0,
                ))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def consultar(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM usuarios ORDER BY nombre")
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def confirmar_modificacion(self, id):
        self.__id = id
        return self._modificar(id)

    def _modificar(self, id):
        if not self._validar_datos_usuario():
            return False
        try:
            db = self._get_db()
            sets = ["nombre = %s", "email = %s", "cedula = %s", "rol = %s",
                    "departamento = %s", "telefono = %s", "activo = %s"]
            params = [self.__nombre, self.__email, self.__cedula, self.__rol,
                      self.__departamento or 'Medios', self.__telefono or '',
                      1 if self.__activo else 0]
            if self.__password:
                sets.append("password_hash = %s")
                params.append(generate_password_hash(self.__password))
            params.append(id)
            with db.cursor() as cur:
                cur.execute(
                    f"UPDATE usuarios SET {', '.join(sets)} WHERE id = %s",
                    params
                )
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def confirmar_eliminacion(self, id):
        self.__id = id
        return self._eliminar(id)

    def _eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def cambiar_password(self, id, password_actual, password_nueva):
        try:
            from app.model.auth_model import Usuario
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
                row = cur.fetchone()
                if not row:
                    return 'Usuario no encontrado'
                usuario = Usuario(**row)
                if not usuario.check_password(password_actual):
                    return 'Contraseña actual incorrecta'
                if len(password_nueva) < 8 or len(password_nueva) > 30:
                    return 'La nueva contraseña debe tener entre 8 y 30 caracteres'
                cur.execute(
                    "UPDATE usuarios SET password_hash = %s WHERE id = %s",
                    (generate_password_hash(password_nueva), id)
                )
                return True
        except Exception:
            logger.exception('Error de base de datos')
            return 'Error al cambiar la contraseña'

    def verificar_email(self, email):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT COUNT(*) as total FROM usuarios WHERE email = %s", (email,))
                row = cur.fetchone()
                return row['total'] > 0 if row else False
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def verificar_cedula(self, cedula):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT COUNT(*) as total FROM usuarios WHERE cedula = %s", (cedula,))
                row = cur.fetchone()
                return row['total'] > 0 if row else False
        except Exception:
            logger.exception('Error de base de datos')
            return False
