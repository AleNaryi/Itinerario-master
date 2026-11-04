from app.database import Database, transaction
import logging

from app.model.validaciones_model import ValidacionesMixin

logger = logging.getLogger(__name__)

PERMISOS_CATALOGO = [
    {'codigo': 'dashboard.view', 'nombre': 'Ver panel principal', 'modulo': 'Dashboard'},
    {'codigo': 'usuario.view', 'nombre': 'Ver lista de usuarios', 'modulo': 'Usuarios'},
    {'codigo': 'usuario.create', 'nombre': 'Crear usuarios', 'modulo': 'Usuarios'},
    {'codigo': 'usuario.edit', 'nombre': 'Editar usuarios', 'modulo': 'Usuarios'},
    {'codigo': 'usuario.delete', 'nombre': 'Eliminar usuarios', 'modulo': 'Usuarios'},
    {'codigo': 'usuario.perfil', 'nombre': 'Ver perfil propio', 'modulo': 'Usuarios'},
    {'codigo': 'guion.view', 'nombre': 'Ver guiones', 'modulo': 'Guion'},
    {'codigo': 'guion.create', 'nombre': 'Crear guiones', 'modulo': 'Guion'},
    {'codigo': 'guion.edit', 'nombre': 'Editar guiones', 'modulo': 'Guion'},
    {'codigo': 'guion.delete', 'nombre': 'Eliminar guiones', 'modulo': 'Guion'},
    {'codigo': 'guion.publish', 'nombre': 'Publicar guiones', 'modulo': 'Guion'},
    {'codigo': 'guion.preview', 'nombre': 'Previsualizar guiones', 'modulo': 'Guion'},
    {'codigo': 'envivo.view', 'nombre': 'Ver pantalla en vivo', 'modulo': 'En Vivo'},
    {'codigo': 'envivo.control', 'nombre': 'Controlar elementos en vivo', 'modulo': 'En Vivo'},
    {'codigo': 'premio.view', 'nombre': 'Ver premios', 'modulo': 'Premios'},
    {'codigo': 'premio.create', 'nombre': 'Crear premios', 'modulo': 'Premios'},
    {'codigo': 'premio.edit', 'nombre': 'Editar premios', 'modulo': 'Premios'},
    {'codigo': 'premio.delete', 'nombre': 'Eliminar premios', 'modulo': 'Premios'},
    {'codigo': 'premio.entregar', 'nombre': 'Entregar premios', 'modulo': 'Premios'},
    {'codigo': 'mantenimiento.view', 'nombre': 'Ver mantenimiento', 'modulo': 'Mantenimiento'},
    {'codigo': 'mantenimiento.edit', 'nombre': 'Editar recursos', 'modulo': 'Mantenimiento'},
    {'codigo': 'mantenimiento.delete', 'nombre': 'Eliminar recursos', 'modulo': 'Mantenimiento'},
    {'codigo': 'gestion_tarea.view', 'nombre': 'Ver tareas', 'modulo': 'Tareas'},
    {'codigo': 'gestion_tarea.create', 'nombre': 'Crear tareas', 'modulo': 'Tareas'},
    {'codigo': 'gestion_tarea.edit', 'nombre': 'Editar tareas', 'modulo': 'Tareas'},
    {'codigo': 'gestion_tarea.delete', 'nombre': 'Eliminar tareas', 'modulo': 'Tareas'},
    {'codigo': 'gestion_tarea.complete', 'nombre': 'Completar tareas propias', 'modulo': 'Tareas'},
    {'codigo': 'gestion_tarea.supervisar', 'nombre': 'Supervisar tareas de todos los usuarios', 'modulo': 'Tareas'},
    {'codigo': 'patrocinador.view', 'nombre': 'Ver patrocinadores', 'modulo': 'Patrocinadores'},
    {'codigo': 'patrocinador.create', 'nombre': 'Crear patrocinadores', 'modulo': 'Patrocinadores'},
    {'codigo': 'patrocinador.edit', 'nombre': 'Editar patrocinadores', 'modulo': 'Patrocinadores'},
    {'codigo': 'patrocinador.delete', 'nombre': 'Eliminar patrocinadores', 'modulo': 'Patrocinadores'},
    {'codigo': 'contrato.view', 'nombre': 'Ver contratos', 'modulo': 'Contratos'},
    {'codigo': 'contrato.create', 'nombre': 'Crear contratos', 'modulo': 'Contratos'},
    {'codigo': 'contrato.edit', 'nombre': 'Editar contratos', 'modulo': 'Contratos'},
    {'codigo': 'contrato.delete', 'nombre': 'Eliminar contratos', 'modulo': 'Contratos'},
    {'codigo': 'balance.view', 'nombre': 'Ver balance', 'modulo': 'Balance'},
    {'codigo': 'balance.create', 'nombre': 'Registrar pagos', 'modulo': 'Balance'},
    {'codigo': 'balance.edit', 'nombre': 'Editar pagos', 'modulo': 'Balance'},
    {'codigo': 'balance.delete', 'nombre': 'Eliminar pagos', 'modulo': 'Balance'},
    {'codigo': 'rol.view', 'nombre': 'Ver roles y permisos', 'modulo': 'Roles'},
    {'codigo': 'rol.edit', 'nombre': 'Editar permisos de usuarios', 'modulo': 'Roles'},
    {'codigo': 'inventario.view', 'nombre': 'Ver inventario de recursos', 'modulo': 'Inventario'},
    {'codigo': 'inventario.create', 'nombre': 'Crear recursos', 'modulo': 'Inventario'},
    {'codigo': 'inventario.edit', 'nombre': 'Editar recursos', 'modulo': 'Inventario'},
    {'codigo': 'inventario.delete', 'nombre': 'Eliminar recursos', 'modulo': 'Inventario'},
    {'codigo': 'inventario.assign', 'nombre': 'Asignar y devolver recursos', 'modulo': 'Inventario'},
    {'codigo': 'reels.view', 'nombre': 'Ver reels', 'modulo': 'Reels'},
    {'codigo': 'reels.create', 'nombre': 'Crear reels', 'modulo': 'Reels'},
    {'codigo': 'reels.edit', 'nombre': 'Editar reels', 'modulo': 'Reels'},
    {'codigo': 'reels.delete', 'nombre': 'Eliminar reels', 'modulo': 'Reels'},
]

PERMISOS_POR_ROL = {
    'Superadmin': [p['codigo'] for p in PERMISOS_CATALOGO],
    'Administrador': [p['codigo'] for p in PERMISOS_CATALOGO if not p['codigo'].startswith('rol.')],
    'Usuario': [
        'dashboard.view', 'guion.view', 'envivo.view',
        'usuario.perfil', 'usuario.view',
        'premio.view', 'mantenimiento.view',
        'patrocinador.view', 'contrato.view',
        'balance.view', 'gestion_tarea.view',
        'inventario.view', 'reels.view',
    ],
}


class RolModel(ValidacionesMixin):
    def __init__(self):
        super().__init__()
        self.db_name = 'seguridad'
        self.__nombre = None

    def _get_db(self):
        return Database.get_connection(self.db_name)

    def set_nombre(self, valor):
        self.__nombre = valor

    def _validar_datos_rol(self) -> bool:
        self.limpiar_errores()
        datos = {'nombre': self.__nombre}
        if not self.validar_obligatorios(['nombre'], datos):
            return False
        if not self.validar_longitud(self.__nombre, 2, 50, 'Nombre del rol'):
            return False
        return True

    def confirmar_registro(self):
        if not self._validar_datos_rol():
            return False
        return self._registrar()

    def _registrar(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO roles (nombre, descripcion) VALUES (%s, %s)",
                    (self.__nombre, '')
                )
                return cur.lastrowid
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM roles WHERE 1=1"
            params = []
            if filtros.get('nombre'):
                sql += " AND nombre = %s"
                params.append(filtros['nombre'])
            sql += " ORDER BY nombre"
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_nombre(self, nombre):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM roles WHERE nombre = %s", (nombre,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def listar_usuarios_con_roles(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT u.id, u.nombre, u.email, r.nombre as rol, r.id as id_rol
                    FROM usuarios u
                    LEFT JOIN roles r ON u.rol = r.nombre
                    WHERE u.activo = 1
                    ORDER BY u.nombre
                """)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_datos_dashboard(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT COUNT(*) as total FROM roles")
                total_roles = cur.fetchone()['total']
                cur.execute("SELECT COUNT(*) as total FROM usuarios WHERE activo = 1")
                total_usuarios = cur.fetchone()['total']
                cur.execute("SELECT COUNT(*) as total FROM permisos")
                total_permisos = cur.fetchone()['total']
            return {
                'total_roles': total_roles,
                'total_usuarios': total_usuarios,
                'total_permisos': total_permisos,
            }
        except Exception:
            logger.exception('Error de base de datos')
            return {'total_roles': 0, 'total_usuarios': 0, 'total_permisos': 0}

    def _asegurar_schema(self):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                for tabla in ['permisos', 'roles', 'rol_permiso']:
                    cur.execute(f"SHOW KEYS FROM {tabla} WHERE Key_name = 'PRIMARY'")
                    if not cur.fetchone():
                        cur.execute(f"ALTER TABLE {tabla} ADD PRIMARY KEY (id)")
                    try:
                        cur.execute(f"ALTER TABLE {tabla} MODIFY id int(11) NOT NULL AUTO_INCREMENT")
                    except Exception:
                        logger.exception('Error de base de datos')
        except Exception:
            logger.exception('Error de base de datos')

    def _asegurar_permisos_roles(self, roles, permiso_model):
        rol_permiso_model = RolPermisoModel()
        for r in roles:
            existentes = rol_permiso_model.obtener_permisos_por_rol(r['id'])
            if existentes:
                continue
            codigos = PERMISOS_POR_ROL.get(r['nombre'], [])
            for codigo in codigos:
                permiso = permiso_model.obtener_por_codigo(codigo)
                if permiso:
                    rol_permiso_model.registrar({'rol_id': r['id'], 'permiso_id': permiso['id']})

    def seed_permisos_iniciales(self):
        self._asegurar_schema()
        permiso_model = PermisoModel()
        for p in PERMISOS_CATALOGO:
            if not permiso_model.obtener_por_codigo(p['codigo']):
                permiso_model.registrar(p)

        roles = self.consultar()
        if roles:
            self._asegurar_permisos_roles(roles, permiso_model)
            return

        rol_permiso_model = RolPermisoModel()
        for nombre_rol, desc in [('Superadmin', 'Acceso total al sistema'),
                                  ('Administrador', 'Acceso administrativo excepto roles'),
                                  ('Usuario', 'Acceso basico de lectura')]:
            self.set_nombre(nombre_rol)
            id_rol = self.confirmar_registro()
            if not id_rol:
                continue
            codigos = PERMISOS_POR_ROL.get(nombre_rol, [])
            for codigo in codigos:
                permiso = permiso_model.obtener_por_codigo(codigo)
                if permiso:
                    rol_permiso_model.registrar({'rol_id': id_rol, 'permiso_id': permiso['id']})


class PermisoModel:
    def _get_db(self):
        return Database.get_connection('seguridad')

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM permisos WHERE 1=1"
            params = []
            if filtros.get('modulo'):
                sql += " AND modulo = %s"
                params.append(filtros['modulo'])
            sql += " ORDER BY modulo, nombre"
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
                cur.execute("SELECT * FROM permisos WHERE id = %s", (id,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def obtener_por_codigo(self, codigo):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM permisos WHERE codigo = %s", (codigo,))
                return cur.fetchone()
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def obtener_por_modulos(self):
        permisos = self.consultar()
        agrupados = {}
        for p in permisos:
            agrupados.setdefault(p['modulo'], []).append(p)
        return agrupados

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO permisos (nombre, codigo, modulo, descripcion) VALUES (%s, %s, %s, %s)",
                    (datos['nombre'], datos['codigo'], datos['modulo'], datos.get('descripcion', ''))
                )
                return self.obtener_por_id(cur.lastrowid)
        except Exception:
            logger.exception('Error de base de datos')
            return None

    def modificar(self, id, datos):
        try:
            db = self._get_db()
            sets, params = [], []
            for campo in ['nombre', 'codigo', 'modulo', 'descripcion']:
                if campo in datos:
                    sets.append(f"{campo} = %s")
                    params.append(datos[campo])
            if not sets:
                return False
            params.append(id)
            with db.cursor() as cur:
                cur.execute(f"UPDATE permisos SET {', '.join(sets)} WHERE id = %s", params)
                return cur.rowcount > 0
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM permisos WHERE id = %s", (id,))
        except Exception:
            logger.exception('Error de base de datos')


class RolPermisoModel:
    def __init__(self):
        self.__id_rol = None

    def _get_db(self):
        return Database.get_connection('seguridad')

    def set_id_rol(self, valor):
        self.__id_rol = valor

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM rol_permiso WHERE 1=1"
            params = []
            if filtros.get('rol_id'):
                sql += " AND rol_id = %s"
                params.append(filtros['rol_id'])
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_rol(self, rol_id):
        return self.consultar(rol_id=rol_id)

    def obtener_permisos_por_rol(self, rol_id):
        try:
            db = self._get_db()
            sql = """SELECT p.* FROM permisos p
                     JOIN rol_permiso rp ON p.id = rp.permiso_id
                     WHERE rp.rol_id = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (rol_id,))
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO rol_permiso (rol_id, permiso_id) VALUES (%s, %s)",
                    (datos['rol_id'], datos['permiso_id'])
                )
        except Exception:
            logger.exception('Error de base de datos')

    def eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM rol_permiso WHERE id = %s", (id,))
        except Exception:
            logger.exception('Error de base de datos')

    def actualizar_permisos(self, permiso_ids):
        try:
            pids_validos = [int(pid) for pid in permiso_ids if str(pid).isdigit()]
            with transaction('seguridad') as conn:
                with conn.cursor() as cur:
                    cur.execute("DELETE FROM rol_permiso WHERE rol_id = %s", (self.__id_rol,))
                    for pid in pids_validos:
                        cur.execute(
                            "INSERT INTO rol_permiso (rol_id, permiso_id) VALUES (%s, %s)",
                            (self.__id_rol, pid)
                        )
            return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_rol_con_permisos(self, rol_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM roles WHERE id = %s", (rol_id,))
                row = cur.fetchone()
                if not row:
                    return None
                cur.execute("""
                    SELECT p.* FROM permisos p
                    JOIN rol_permiso rp ON p.id = rp.permiso_id
                    WHERE rp.rol_id = %s
                """, (rol_id,))
                row['permisos'] = cur.fetchall()
                return row
        except Exception:
            logger.exception('Error de base de datos')
            return None


class UsuarioPermisoModel:
    def _get_db(self):
        return Database.get_connection('seguridad')

    def consultar(self, **filtros):
        try:
            db = self._get_db()
            sql = "SELECT * FROM usuario_permiso WHERE 1=1"
            params = []
            if filtros.get('usuario_id'):
                sql += " AND usuario_id = %s"
                params.append(filtros['usuario_id'])
            with db.cursor() as cur:
                cur.execute(sql, params)
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def obtener_por_usuario(self, usuario_id):
        return self.consultar(usuario_id=usuario_id)

    def obtener_permisos_por_usuario(self, usuario_id):
        try:
            db = self._get_db()
            sql = """SELECT p.* FROM permisos p
                     JOIN usuario_permiso up ON p.id = up.permiso_id
                     WHERE up.usuario_id = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (usuario_id,))
                return cur.fetchall()
        except Exception:
            logger.exception('Error de base de datos')
            return []

    def registrar(self, datos):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "INSERT INTO usuario_permiso (usuario_id, permiso_id) VALUES (%s, %s)",
                    (datos['usuario_id'], datos['permiso_id'])
                )
        except Exception:
            logger.exception('Error de base de datos')

    def eliminar(self, id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM usuario_permiso WHERE id = %s", (id,))
        except Exception:
            logger.exception('Error de base de datos')

    def sincronizar_usuario_permisos(self, usuario_id, permiso_ids, permiso_ids_rol):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT permiso_id FROM usuario_permiso WHERE usuario_id = %s",
                    (usuario_id,)
                )
                existentes = {r['permiso_id'] for r in cur.fetchall()}

                nuevos = set(permiso_ids) - existentes - set(permiso_ids_rol)
                for pid in nuevos:
                    cur.execute(
                        "INSERT INTO usuario_permiso (usuario_id, permiso_id, fecha_asignacion) VALUES (%s, %s, NOW())",
                        (usuario_id, pid)
                    )

                sobrantes = existentes - set(permiso_ids) - set(permiso_ids_rol)
                if sobrantes:
                    placeholders = ','.join(['%s'] * len(sobrantes))
                    cur.execute(
                        f"DELETE FROM usuario_permiso WHERE usuario_id = %s AND permiso_id IN ({placeholders})",
                        (usuario_id, *sobrantes)
                    )
                return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_permisos_usuario(self, usuario_id, rol_nombre):
        try:
            db = self._get_db()
            sql = """SELECT p.codigo FROM permisos p
                     JOIN rol_permiso rp ON p.id = rp.permiso_id
                     JOIN roles r ON r.id = rp.rol_id
                     WHERE r.nombre = %s
                     UNION
                     SELECT p.codigo FROM permisos p
                     JOIN usuario_permiso up ON p.id = up.permiso_id
                     WHERE up.usuario_id = %s"""
            with db.cursor() as cur:
                cur.execute(sql, (rol_nombre, usuario_id))
                return {r['codigo'] for r in cur.fetchall()}
        except Exception:
            logger.exception('Error de base de datos')
            return set()

    def actualizar_permisos(self, usuario_id, permiso_ids):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT permiso_id FROM usuario_permiso WHERE usuario_id = %s",
                    (usuario_id,)
                )
                existentes = {r['permiso_id'] for r in cur.fetchall()}

                nuevos = set(int(p) for p in permiso_ids) - existentes
                for pid in nuevos:
                    cur.execute(
                        "INSERT INTO usuario_permiso (usuario_id, permiso_id, fecha_asignacion) VALUES (%s, %s, NOW())",
                        (usuario_id, pid)
                    )

                sobrantes = existentes - set(int(p) for p in permiso_ids)
                if sobrantes:
                    placeholders = ','.join(['%s'] * len(sobrantes))
                    cur.execute(
                        f"DELETE FROM usuario_permiso WHERE usuario_id = %s AND permiso_id IN ({placeholders})",
                        (usuario_id, *sobrantes)
                    )
                return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_usuario_con_permisos(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("""
                    SELECT u.*, r.nombre as rol, r.id as id_rol
                    FROM usuarios u
                    LEFT JOIN roles r ON u.rol = r.nombre
                    WHERE u.id = %s
                """, (usuario_id,))
                row = cur.fetchone()
                if not row:
                    return None
                cur.execute("""
                    SELECT p.* FROM permisos p
                    JOIN usuario_permiso up ON p.id = up.permiso_id
                    WHERE up.usuario_id = %s
                """, (usuario_id,))
                row['permisos_extra'] = cur.fetchall()
                return row
        except Exception:
            logger.exception('Error de base de datos')
            return None


class DashboardVisibilidadModel:
    def _get_db(self):
        return Database.get_connection('seguridad')

    def obtener_por_rol(self, rol_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("SELECT * FROM dashboard_visibilidad WHERE rol_id = %s", (rol_id,))
                return {r['modulo_key']: r for r in cur.fetchall()}
        except Exception:
            logger.exception('Error de base de datos')
            return {}

    def obtener_modulos_visibles_rol(self, rol_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT modulo_key FROM dashboard_visibilidad WHERE rol_id = %s AND visible = 1",
                    (rol_id,)
                )
                return {r['modulo_key'] for r in cur.fetchall()}
        except Exception:
            logger.exception('Error de base de datos')
            return set()

    def guardar_para_rol(self, rol_id, modulos_visibles):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute("DELETE FROM dashboard_visibilidad WHERE rol_id = %s", (rol_id,))
                for mk in MODULOS_DASHBOARD:
                    visible = 1 if mk in modulos_visibles else 0
                    cur.execute(
                        "INSERT INTO dashboard_visibilidad (rol_id, modulo_key, visible) VALUES (%s, %s, %s)",
                        (rol_id, mk, visible)
                    )
                return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_por_usuario(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT * FROM usuario_dashboard_vis WHERE usuario_id = %s",
                    (usuario_id,)
                )
                return {r['modulo_key']: r for r in cur.fetchall()}
        except Exception:
            logger.exception('Error de base de datos')
            return {}

    def obtener_modulos_visibles_usuario(self, usuario_id):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT modulo_key FROM usuario_dashboard_vis WHERE usuario_id = %s AND visible = 1",
                    (usuario_id,)
                )
                return {r['modulo_key'] for r in cur.fetchall()}
        except Exception:
            logger.exception('Error de base de datos')
            return set()

    def guardar_para_usuario(self, usuario_id, modulos_visibles):
        try:
            db = self._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "DELETE FROM usuario_dashboard_vis WHERE usuario_id = %s",
                    (usuario_id,)
                )
                for mk in MODULOS_DASHBOARD:
                    visible = 1 if mk in modulos_visibles else 0
                    cur.execute(
                        "INSERT INTO usuario_dashboard_vis (usuario_id, modulo_key, visible) VALUES (%s, %s, %s)",
                        (usuario_id, mk, visible)
                    )
                return True
        except Exception:
            logger.exception('Error de base de datos')
            return False

    def obtener_modulos_visibles_final(self, usuario_id, rol_nombre):
        try:
            rol_model = RolModel()
            rol = rol_model.obtener_por_nombre(rol_nombre)
            vis_rol = self.obtener_por_rol(rol['id']) if rol else {}
            vis_user = self.obtener_por_usuario(usuario_id)
            modulos = set(MODULOS_DASHBOARD)
            for mk in modulos.copy():
                if mk in vis_user:
                    if not vis_user[mk]['visible']:
                        modulos.discard(mk)
                elif mk in vis_rol:
                    if not vis_rol[mk]['visible']:
                        modulos.discard(mk)
            return modulos
        except Exception:
            logger.exception('Error de base de datos')
            return set(MODULOS_DASHBOARD)


MODULOS_DASHBOARD = ['guion', 'mantenimiento', 'premio', 'contrato', 'balance',
                     'tarea', 'patrocinador', 'usuario', 'inventario', 'reels',
                     'rol', 'actividad', 'enlinea']

MODULO_PERMISO_MAP = {
    'guion': 'guion.view',
    'mantenimiento': 'mantenimiento.view',
    'premio': 'premio.view',
    'contrato': 'contrato.view',
    'balance': 'balance.view',
    'tarea': 'gestion_tarea.view',
    'patrocinador': 'patrocinador.view',
    'usuario': 'usuario.view',
    'inventario': 'inventario.view',
    'reels': 'reels.view',
    'rol': 'rol.view',
    'actividad': 'rol.view',
    'enlinea': 'dashboard.view',
}

MODULOS_DASHBOARD_INFO = {
    'guion': {'nombre': 'Guion', 'icono': 'fa-scroll', 'color': '#4e73df'},
    'mantenimiento': {'nombre': 'Mantenimiento', 'icono': 'fa-tools', 'color': '#1cc88a'},
    'premio': {'nombre': 'Premios', 'icono': 'fa-gift', 'color': '#f6c23e'},
    'contrato': {'nombre': 'Contratos', 'icono': 'fa-file-contract', 'color': '#e74a3b'},
    'balance': {'nombre': 'Balance', 'icono': 'fa-balance-scale', 'color': '#36b9cc'},
    'tarea': {'nombre': 'Tareas', 'icono': 'fa-tasks', 'color': '#858796'},
    'patrocinador': {'nombre': 'Patrocinadores', 'icono': 'fa-handshake', 'color': '#f8f9fc'},
    'usuario': {'nombre': 'Usuarios', 'icono': 'fa-users', 'color': '#5a5c69'},
    'inventario': {'nombre': 'Inventario', 'icono': 'fa-boxes', 'color': '#0ea5e9'},
    'reels': {'nombre': 'Reels', 'icono': 'fa-video', 'color': '#d946ef'},
    'rol': {'nombre': 'Roles', 'icono': 'fa-user-shield', 'color': '#64748b'},
    'actividad': {'nombre': 'Actividad', 'icono': 'fa-chart-line', 'color': '#3a3b45'},
    'enlinea': {'nombre': 'En línea', 'icono': 'fa-wifi', 'color': '#224abe'},
}
