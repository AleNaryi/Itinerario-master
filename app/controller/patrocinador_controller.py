import json
import logging
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import PATROCINADOR
from app.model.patrocinador_model import PatrocinadorModel
from app.model.auth_model import UsuarioModel

logger = logging.getLogger(__name__)

bp = Blueprint('patrocinador', __name__, url_prefix='/patrocinador')

bp.before_request(verificar_acceso(PATROCINADOR))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('patrocinador', tipo, accion, detalle)


@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    obj_model = PatrocinadorModel()
    mensaje = None

    if request.method == 'POST':
        if 'consultar' in request.form:
            patrocinadores = obj_model.consultar()
            usuarios_map = {}
            try:
                for u in UsuarioModel().consultar(activo=True):
                    usuarios_map[u.id] = u.nombre
            except Exception:
                logger.exception('Error no controlado')
            return jsonify([{
                'id_patrocinador': p['id_patrocinador'],
                'nombre_empresa': p['nombre_empresa'],
                'rif': p['rif'],
                'tipo_contrato': p['tipo_contrato'],
                'nombre_contacto': p['nombre_contacto'] or '',
                'telefono': p['telefono'] or '',
                'email': p['email'] or '',
                'encargado_id': p.get('encargado_id'),
                'encargado_nombre': usuarios_map.get(p.get('encargado_id'), ''),
            } for p in patrocinadores])

        if 'verificar_nombre' in request.form:
            nombre = request.form['verificar_nombre']
            existe = obj_model.verificar_nombre_empresa(nombre)
            return jsonify({'existe': existe})

        if 'buscar' in request.form:
            obj_model.set_id_patrocinador(request.form['id_patrocinador'])
            p = obj_model.obtener_por_id(request.form['id_patrocinador'])
            if p:
                return jsonify({'status': True, 'datos': {
                    'id_patrocinador': p['id_patrocinador'],
                    'nombre_empresa': p['nombre_empresa'],
                    'rif': p['rif'],
                    'tipo_contrato': p['tipo_contrato'],
                    'nombre_contacto': p['nombre_contacto'] or '',
                    'telefono': p['telefono'] or '',
                    'email': p['email'] or '',
                    'encargado_id': p.get('encargado_id'),
                }})
            return jsonify({'status': False, 'datos': None})

        if 'registrar' in request.form:
            if not current_user.tiene_permiso('patrocinador.create'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            try:
                obj_model.set_nombre_empresa(request.form['nombre_empresa'])
                obj_model.set_rif(request.form['rif'])
                obj_model.set_tipo_contrato(request.form['tipo_contrato'])
                obj_model.set_nombre_contacto(request.form.get('nombre_contacto', ''))
                obj_model.set_telefono(request.form.get('telefono', ''))
                obj_model.set_email(request.form.get('email', ''))
                obj_model.set_encargado_id(request.form.get('encargado_id'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            if obj_model.confirmar_registro():
                _registrar_bitacora('create', 'Registrar patrocinador', f'Patrocinador "{request.form["nombre_empresa"]}" registrado')
                mensaje = 'Patrocinador registrado correctamente'
            else:
                mensaje = 'Error al registrar el patrocinador'
            return jsonify({'mensaje': mensaje})

        if 'editar' in request.form:
            if not current_user.tiene_permiso('patrocinador.edit'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            id_p = request.form['editar']
            try:
                obj_model.set_nombre_empresa(request.form['nombre_empresa'])
                obj_model.set_rif(request.form['rif'])
                obj_model.set_tipo_contrato(request.form['tipo_contrato'])
                obj_model.set_nombre_contacto(request.form.get('nombre_contacto', ''))
                obj_model.set_telefono(request.form.get('telefono', ''))
                obj_model.set_email(request.form.get('email', ''))
                obj_model.set_encargado_id(request.form.get('encargado_id'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            if obj_model.confirmar_modificacion(id_p):
                _registrar_bitacora('update', 'Editar patrocinador', f'Patrocinador "{request.form["nombre_empresa"]}" actualizado')
                mensaje = 'Patrocinador actualizado correctamente'
            else:
                mensaje = 'Error al actualizar el patrocinador'
            return jsonify({'mensaje': mensaje})

        if 'eliminar' in request.form:
            if not current_user.tiene_permiso('patrocinador.delete'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            obj_model.set_id_patrocinador(request.form['eliminar'])
            p = obj_model.obtener_por_id(request.form['eliminar'])
            if obj_model.confirmar_eliminacion(request.form['eliminar']):
                _registrar_bitacora('delete', 'Eliminar patrocinador', f'Patrocinador "{p["nombre_empresa"]}" eliminado')
                mensaje = 'Patrocinador eliminado correctamente'
            else:
                mensaje = 'Error al eliminar el patrocinador'
            return jsonify({'mensaje': mensaje})

    todos_usuarios = UsuarioModel().consultar(activo=True)
    encargados = [u for u in todos_usuarios if u.rol in ('Administrador', 'Superadmin')]
    return render_template('patrocinador/patrocinador.html', mensaje=mensaje, encargados=encargados)


@bp.route('/api/obtener/<int:id>')
def api_obtener(id):
    obj_model = PatrocinadorModel()
    p = obj_model.obtener_por_id(id)
    if not p:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify({
        'id_patrocinador': p['id_patrocinador'],
        'nombre_empresa': p['nombre_empresa'],
        'rif': p['rif'],
        'tipo_contrato': p['tipo_contrato'],
        'nombre_contacto': p['nombre_contacto'],
        'telefono': p['telefono'],
        'email': p['email'],
    })
