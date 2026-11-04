import json
import logging
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import ROL
from app.model.rol_model import (RolModel, PermisoModel, RolPermisoModel,
                                  UsuarioPermisoModel, DashboardVisibilidadModel,
                                  MODULOS_DASHBOARD_INFO)

logger = logging.getLogger(__name__)

bp = Blueprint('rol', __name__, url_prefix='/roles')

bp.before_request(verificar_acceso(ROL))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('rol', tipo, accion, detalle)


@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    if request.method == 'POST':
        if request.form.get('listar_usuarios'):
            obj_model = RolModel()
            data = obj_model.listar_usuarios_con_roles()
            return jsonify([
                {'id': u['id'], 'nombre': u['nombre'], 'email': u.get('email', ''),
                 'rol': u.get('rol', 'Sin rol'), 'id_rol': u.get('id_rol', '')}
                for u in data
            ])
        return jsonify({'error': 'Acción no reconocida'})
    obj_model = RolModel()
    roles = obj_model.consultar()
    usuarios = obj_model.listar_usuarios_con_roles()
    enriched = []
    try:
        from app.database import Database
        db = Database.get_connection('seguridad')
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM permisos")
            total_posible = cur.fetchone()['cnt']
            for r in roles:
                cur.execute("SELECT COUNT(*) as cnt FROM rol_permiso WHERE rol_id = %s", (r['id'],))
                total_p = cur.fetchone()['cnt']
                cur.execute("SELECT COUNT(*) as cnt FROM usuarios WHERE rol = %s", (r['nombre'],))
                cant_u = cur.fetchone()['cnt']
                enriched.append({
                    'nombre': r['nombre'],
                    'total_permisos': total_p,
                    'cant_usuarios': cant_u,
                    'total_posible': total_posible,
                    'rol': r,
                })
    except Exception:
        logger.exception('Error calculando resumen de roles')
        enriched = [{'nombre': r['nombre'], 'total_permisos': 0, 'cant_usuarios': 0, 'total_posible': 0, 'rol': r} for r in roles]
    dashboard_data = obj_model.obtener_datos_dashboard()
    return render_template('rol/dashboard.html', roles=enriched, usuarios=usuarios, dashboard_data=dashboard_data)


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    if request.method == 'POST':
        permiso_ids = request.form.getlist('permisos')
        up_model = UsuarioPermisoModel()
        ok = up_model.actualizar_permisos(id, permiso_ids)
        if ok:
            usuario = up_model.obtener_usuario_con_permisos(id)
            _registrar_bitacora('update', 'Editar permisos usuario', f'Permisos del usuario "{usuario["nombre"]}" actualizados')
            flash('Permisos de usuario actualizados correctamente', 'success')
        else:
            flash('Error al actualizar permisos', 'danger')
        return redirect(url_for('rol.dashboard'))
    up_model = UsuarioPermisoModel()
    usuario = up_model.obtener_usuario_con_permisos(id)
    if not usuario:
        return jsonify({'error': 'Usuario no encontrado'}), 404
    p_model = PermisoModel()
    permisos_agrupados = p_model.obtener_por_modulos()
    rp_model = RolPermisoModel()
    permisos_rol = {p['id'] for p in rp_model.obtener_permisos_por_rol(usuario['id_rol'])} if usuario.get('id_rol') else set()
    permisos_individuales = {p['id'] for p in (usuario.get('permisos_extra') or [])}
    dv_model = DashboardVisibilidadModel()
    dashboard_base_rol = dv_model.obtener_modulos_visibles_rol(usuario['id_rol']) if usuario.get('id_rol') else set()
    dashboard_vis_user = dv_model.obtener_por_usuario(id)
    dashboard_user_overrides = set(dashboard_vis_user.keys())
    return render_template('rol/editar_permisos.html', usuario=usuario,
                           permisos_agrupados=permisos_agrupados,
                           permisos_rol=permisos_rol,
                           permisos_individuales=permisos_individuales,
                           modulos_dashboard_info=MODULOS_DASHBOARD_INFO,
                           dashboard_base_rol=dashboard_base_rol,
                           dashboard_vis_user=dashboard_vis_user,
                           dashboard_user_overrides=dashboard_user_overrides)


@bp.route('/editar-rol/<int:id>', methods=['GET', 'POST'])
def editar_rol(id):
    if request.method == 'POST':
        permiso_ids = request.form.getlist('permisos')
        rp_model = RolPermisoModel()
        rp_model.set_id_rol(id)
        ok = rp_model.actualizar_permisos(permiso_ids)
        if ok:
            rol = rp_model.obtener_rol_con_permisos(id)
            _registrar_bitacora('update', 'Editar permisos rol', f'Permisos del rol "{rol["nombre"]}" actualizados')
            flash('Permisos del rol actualizados correctamente', 'success')
        else:
            flash('Error al actualizar permisos del rol', 'danger')
        return redirect(url_for('rol.dashboard'))
    rp_model = RolPermisoModel()
    rol = rp_model.obtener_rol_con_permisos(id)
    if not rol:
        return jsonify({'error': 'Rol no encontrado'}), 404
    p_model = PermisoModel()
    permisos_agrupados = p_model.obtener_por_modulos()
    permisos_del_rol = {p['id'] for p in (rol.get('permisos') or [])}
    dv_model = DashboardVisibilidadModel()
    dashboard_visibles_rol = dv_model.obtener_modulos_visibles_rol(id)
    total_usuarios = 0
    try:
        from app.database import Database
        db = Database.get_connection('seguridad')
        with db.cursor() as cur:
            cur.execute("SELECT COUNT(*) as cnt FROM usuarios WHERE rol = (SELECT nombre FROM roles WHERE id = %s)", (id,))
            total_usuarios = cur.fetchone()['cnt']
    except Exception:
        logger.exception('Error no controlado')
    return render_template('rol/editar_rol.html', rol=rol,
                           permisos_agrupados=permisos_agrupados,
                           permisos_del_rol=permisos_del_rol,
                           modulos_dashboard_info=MODULOS_DASHBOARD_INFO,
                           dashboard_visibles_rol=dashboard_visibles_rol,
                           total_usuarios=total_usuarios)


@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        nombre = request.form.get('nombre')
        permiso_ids = request.form.getlist('permisos')
        r_model = RolModel()
        r_model.set_nombre(nombre)
        id_rol = r_model.confirmar_registro()
        if id_rol and permiso_ids:
            from app.database import transaction
            try:
                pids_validos = [int(pid) for pid in permiso_ids if str(pid).isdigit()]
                with transaction('seguridad') as conn:
                    with conn.cursor() as cur:
                        for pid in pids_validos:
                            cur.execute(
                                "INSERT INTO rol_permiso (rol_id, permiso_id) VALUES (%s, %s)",
                                (id_rol, pid),
                            )
            except Exception:
                logger.exception('Error insertando permisos del rol')
        if id_rol:
            _registrar_bitacora('create', 'Crear rol', f'Rol "{nombre}" creado')
            flash('Rol creado correctamente', 'success')
        else:
            flash('Error al crear el rol', 'danger')
        return redirect(url_for('rol.dashboard'))
    p_model = PermisoModel()
    permisos_agrupados = p_model.obtener_por_modulos()
    return render_template('rol/crear_rol.html', permisos_agrupados=permisos_agrupados, flash=flash)
