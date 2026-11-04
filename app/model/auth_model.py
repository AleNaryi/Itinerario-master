import pymysql
import logging
from app.database import Database
from werkzeug.security import generate_password_hash, check_password_hash

logger = logging.getLogger(__name__)


class Usuario:
    def __init__(self, id=None, nombre=None, email=None, password_hash=None,
                 cedula=None, rol=None, departamento=None, telefono=None,
                 activo=True, fecha_registro=None, ultimo_acceso=None, **kwargs):
        self.id = id
        self.nombre = nombre
        self.email = email
        self.password_hash = password_hash
        self.cedula = cedula
        self.rol = rol
        self.departamento = departamento
        self.telefono = telefono
        self.activo = bool(activo) if activo is not None else True
        self.fecha_registro = fecha_registro
        self.ultimo_acceso = ultimo_acceso
        self.__permisos_cache = None
        for k, v in kwargs.items():
            setattr(self, k, v)

    def set_password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def check_password(self, pwd):
        return check_password_hash(self.password_hash, pwd)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return self.activo

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)

    def is_superadmin(self):
        return self.rol == 'Superadmin'

    def is_admin(self):
        return self.rol in ('Administrador', 'Superadmin')

    def tiene_permiso(self, codigo):
        if self.rol == 'Superadmin':
            return True
        if self.__permisos_cache is None:
            from app.model.rol_model import UsuarioPermisoModel
            self.__permisos_cache = UsuarioPermisoModel().obtener_permisos_usuario(self.id, self.rol)
        return codigo in self.__permisos_cache

    def __repr__(self):
        return f'<Usuario {self.nombre}>'


class UsuarioModel:
    def consultar(self, **filtros):
        try:
            db = Database.get_connection('seguridad')
            sql = "SELECT * FROM usuarios WHERE 1=1"
            params = []
            if filtros.get('rol'):
                sql += " AND rol = %s"
                params.append(filtros['rol'])
            if filtros.get('departamento'):
                sql += " AND departamento = %s"
                params.append(filtros['departamento'])
            if filtros.get('activo') is not None:
                sql += " AND activo = %s"
                params.append(1 if filtros['activo'] else 0)
            sql += " ORDER BY nombre"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return [Usuario(**r) for r in cur.fetchall()]
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def departamentos_activos(self):
        try:
            db = Database.get_connection('seguridad')
            with db.cursor() as cur:
                cur.execute(
                    """SELECT DISTINCT departamento FROM usuarios
                       WHERE activo = 1 AND departamento IS NOT NULL AND departamento != ''
                       ORDER BY departamento"""
                )
                return [r['departamento'] for r in cur.fetchall()]
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def filtrar_ids_activos(self, ids):
        """De una lista de ids, devuelve los que existen y están activos (whitelist)."""
        if not ids:
            return []
        try:
            db = Database.get_connection('seguridad')
            with db.cursor() as cur:
                cur.execute(
                    f"SELECT id FROM usuarios WHERE activo = 1 AND id IN ({', '.join(['%s'] * len(ids))})",
                    tuple(int(i) for i in ids)
                )
                return sorted(r['id'] for r in cur.fetchall())
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_id(self, id):
        try:
            db = Database.get_connection('seguridad')
            with db.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE id = %s", (id,))
                row = cur.fetchone()
                return Usuario(**row) if row else None
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def obtener_por_email(self, email):
        try:
            db = Database.get_connection('seguridad')
            with db.cursor() as cur:
                cur.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
                row = cur.fetchone()
                return Usuario(**row) if row else None
        except pymysql.err.OperationalError:
            raise
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def contar(self, **filtros):
        try:
            db = Database.get_connection('seguridad')
            sql = "SELECT COUNT(*) as total FROM usuarios WHERE 1=1"
            params = []
            if filtros.get('rol'):
                sql += " AND rol = %s"
                params.append(filtros['rol'])
            with db.cursor() as cur:
                cur.execute(sql, params)
                row = cur.fetchone()
                return row['total'] if row else 0
        except Exception:
            logger.exception('Error de base de datos')
            return 0

    def registrar(self, datos):
        try:
            db = Database.get_connection('seguridad')
            sql = """INSERT INTO usuarios (nombre, email, password_hash, cedula, rol,
                     departamento, telefono, activo, fecha_registro)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())"""
            with db.cursor() as cur:
                cur.execute(sql, (
                    datos['nombre'], datos['email'], datos['password_hash'],
                    datos['cedula'], datos.get('rol', 'Usuario'),
                    datos.get('departamento', 'Medios'), datos.get('telefono', ''),
                    1,
                ))
                new_id = cur.lastrowid
            return self.obtener_por_id(new_id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def modificar(self, id, datos):
        try:
            db = Database.get_connection('seguridad')
            sets = []
            params = []
            for campo in ['nombre', 'email', 'rol', 'departamento', 'telefono',
                          'password_hash', 'activo']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            if sets:
                sql = f"UPDATE usuarios SET {', '.join(sets)} WHERE id = %s"
                params.append(id)
                with db.cursor() as cur:
                    cur.execute(sql, params)
            return self.obtener_por_id(id)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def eliminar(self, id):
        try:
            db = Database.get_connection('seguridad')
            with db.cursor() as cur:
                cur.execute("DELETE FROM usuarios WHERE id = %s", (id,))
        except Exception:
            logger.exception('Error de base de datos')

    def actualizar_ultimo_acceso(self, id):
        try:
            db = Database.get_connection('seguridad')
            with db.cursor() as cur:
                cur.execute("UPDATE usuarios SET ultimo_acceso = NOW() WHERE id = %s", (id,))
        except Exception:
            logger.exception('Error de base de datos')


class PasswordResetTokenModel:
    def __init__(self):
        self.db_name = 'seguridad'

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def crear_token(self, usuario_id, horas=24):
        import secrets
        from datetime import datetime, timedelta
        token = secrets.token_hex(32)
        expires = datetime.now() + timedelta(hours=horas)
        db = self._get_db()
        with db.cursor() as cur:
            cur.execute(
                "INSERT INTO password_reset_tokens (usuario_id, token, expires_at) VALUES (%s, %s, %s)",
                (usuario_id, token, expires)
            )
        return token

    def validar_token(self, token):
        from datetime import datetime
        db = self._get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT * FROM password_reset_tokens WHERE token = %s AND used = 0 AND expires_at > NOW()",
                (token,)
            )
            return cur.fetchone()

    def marcar_usado(self, token_id):
        db = self._get_db()
        with db.cursor() as cur:
            cur.execute("UPDATE password_reset_tokens SET used = 1 WHERE id = %s", (token_id,))

    def limpiar_expirados(self):
        db = self._get_db()
        with db.cursor() as cur:
            cur.execute("DELETE FROM password_reset_tokens WHERE expires_at <= NOW()")

    def contar_solicitudes_recientes(self, usuario_id, minutos=15):
        from datetime import datetime, timedelta
        hace = datetime.now() - timedelta(minutes=minutos)
        db = self._get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) AS total FROM password_reset_tokens WHERE usuario_id = %s AND created_at > %s",
                (usuario_id, hace)
            )
            row = cur.fetchone()
            return row['total'] if row else 0
