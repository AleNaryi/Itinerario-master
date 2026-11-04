import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import USUARIO
from app.model.usuario_model import UsuarioModel
from app.model.rol_model import RolModel

bp = Blueprint('usuario', __name__, url_prefix='/usuarios')

bp.before_request(verificar_acceso(USUARIO))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('usuario', tipo, accion, detalle)


@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    obj_model = UsuarioModel()
    mensaje = None

    if request.method == 'POST':
        if 'consultar' in request.form:
            usuarios = obj_model.consultar()
            return jsonify([{
                'id': u['id'],
                'nombre': u['nombre'],
                'email': u['email'],
                'cedula': u['cedula'],
                'rol': u['rol'],
                'departamento': u['departamento'],
                'telefono': u['telefono'] or '',
                'activo': u['activo'],
                'fecha_registro': str(u['fecha_registro']) if u['fecha_registro'] else '',
            } for u in usuarios])

        if 'buscar' in request.form:
            u = obj_model.obtener_por_id(request.form['id'])
            if u:
                return jsonify({'status': True, 'datos': {
                    'id': u['id'],
                    'nombre': u['nombre'],
                    'email': u['email'],
                    'cedula': u['cedula'],
                    'rol': u['rol'],
                    'departamento': u['departamento'],
                    'telefono': u['telefono'] or '',
                    'activo': u['activo'],
                }})
            return jsonify({'status': False, 'datos': None})

        if 'registrar' in request.form:
            if not current_user.tiene_permiso('usuario.create'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            pwd = request.form.get('password', '')
            if len(pwd) < 8 or len(pwd) > 30:
                return jsonify({'error': 'La contraseña debe tener entre 8 y 30 caracteres'}), 400
            try:
                obj_model.set_nombre(request.form['nombre'])
                obj_model.set_email(request.form['email'])
                obj_model.set_cedula(request.form['cedula'])
                obj_model.set_rol(request.form['rol'])
                obj_model.set_departamento(request.form.get('departamento', 'Medios'))
                obj_model.set_telefono(request.form.get('telefono', ''))
                obj_model.set_password(pwd)
                obj_model.set_activo(request.form.get('activo'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

            if obj_model.confirmar_registro():
                _registrar_bitacora('create', 'Registrar usuario', f'Usuario "{request.form["nombre"]}" registrado')
                mensaje = 'Usuario registrado correctamente'
            else:
                mensaje = 'Error al registrar el usuario'
            return jsonify({'mensaje': mensaje})

        if 'editar' in request.form:
            if not current_user.tiene_permiso('usuario.edit'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            id_u = request.form['editar']
            try:
                pwd = request.form.get('password', '')
                if pwd and (len(pwd) < 8 or len(pwd) > 30):
                    return jsonify({'error': 'La contraseña debe tener entre 8 y 30 caracteres'}), 400
                obj_model.set_nombre(request.form['nombre'])
                obj_model.set_email(request.form['email'])
                obj_model.set_cedula(request.form['cedula'])
                obj_model.set_rol(request.form['rol'])
                obj_model.set_departamento(request.form.get('departamento', 'Medios'))
                obj_model.set_telefono(request.form.get('telefono', ''))
                obj_model.set_password(pwd)
                obj_model.set_activo(request.form.get('activo'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400

            if obj_model.confirmar_modificacion(id_u):
                _registrar_bitacora('update', 'Editar usuario', f'Usuario "{request.form["nombre"]}" actualizado')
                mensaje = 'Usuario actualizado correctamente'
            else:
                mensaje = 'Error al actualizar el usuario'
            return jsonify({'mensaje': mensaje})

        if 'eliminar' in request.form:
            if not current_user.tiene_permiso('usuario.delete'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            id_u = request.form['eliminar']
            if str(id_u) == str(current_user.id):
                return jsonify({'mensaje': 'No puedes eliminar tu propio usuario'})
            usuario = obj_model.obtener_por_id(id_u)
            if obj_model.confirmar_eliminacion(id_u):
                _registrar_bitacora('delete', 'Eliminar usuario', f'Usuario "{usuario["nombre"]}" eliminado')
                mensaje = 'Usuario eliminado correctamente'
            else:
                mensaje = 'Error al eliminar el usuario'
            return jsonify({'mensaje': mensaje})

        if 'verificar_email' in request.form:
            existe = obj_model.verificar_email(request.form['verificar_email'])
            return jsonify({'existe': existe})

        if 'verificar_cedula' in request.form:
            existe = obj_model.verificar_cedula(request.form['verificar_cedula'])
            return jsonify({'existe': existe})

    roles = RolModel().consultar()
    return render_template('usuario/dashboard.html', roles=roles, mensaje=mensaje)


@bp.route('/ver/<int:id>')
def ver(id):
    obj_model = UsuarioModel()
    usuario = obj_model.obtener_por_id(id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('usuario.dashboard'))
    return render_template('usuario/ver.html', usuario=usuario)


@bp.route('/perfil')
def perfil():
    return render_template('usuario/perfil.html', usuario=current_user)


@bp.route('/cambiar-contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    if request.method == 'POST':
        obj_model = UsuarioModel()
        actual = request.form.get('password_actual', '')
        nueva = request.form.get('password_nueva', '')
        confirmar = request.form.get('confirmar_password', '')

        if nueva != confirmar:
            flash('Las contraseñas no coinciden', 'danger')
            return render_template('usuario/cambiar_password.html')
        if len(nueva) < 8 or len(nueva) > 30:
            flash('La nueva contraseña debe tener entre 8 y 30 caracteres', 'danger')
            return render_template('usuario/cambiar_password.html')

        result = obj_model.cambiar_password(current_user.id, actual, nueva)
        if result is True:
            _registrar_bitacora('update', 'Cambiar contraseña', f'Contraseña del usuario "{current_user.nombre}" cambiada')
            flash('Contraseña actualizada. Por favor inicia sesión nuevamente.', 'success')
            return redirect(url_for('auth.login'))
        flash(result, 'danger')

    return render_template('usuario/cambiar_password.html')
