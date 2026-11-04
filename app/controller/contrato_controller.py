import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import CONTRATO
from app.model.contrato_model import ContratoModel
from app.model.patrocinador_model import PatrocinadorModel

bp = Blueprint('contrato', __name__, url_prefix='/contratos')

bp.before_request(verificar_acceso(CONTRATO))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('contrato', tipo, accion, detalle)


@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    obj_model = ContratoModel()
    mensaje = None

    if request.method == 'POST':
        if 'consultar' in request.form:
            contratos = obj_model.consultar()
            return jsonify([{
                'id_contrato': c['id_contrato'],
                'nombre_empresa': c['nombre_empresa'] or 'Sin patrocinador',
                'fecha_inicio': str(c['fecha_inicio']) if c['fecha_inicio'] else '',
                'fecha_fin': str(c['fecha_fin']) if c['fecha_fin'] else '',
                'tipo': str(c['tipo'] or ''),
                'monto_total': float(c['monto_total']) if c['monto_total'] is not None else None,
                'estatus': c['estatus'] or 'Borrador',
            } for c in contratos])

        if 'buscar' in request.form:
            obj_model.set_id_contrato(request.form['id_contrato'])
            c = obj_model.obtener_por_id(request.form['id_contrato'])
            if c:
                return jsonify({'status': True, 'datos': {
                    'id_contrato': c['id_contrato'],
                    'id_patrocinador': c['id_patrocinador'],
                    'fecha_inicio': str(c['fecha_inicio']) if c['fecha_inicio'] else '',
                    'fecha_fin': str(c['fecha_fin']) if c['fecha_fin'] else '',
                    'tipo': str(c['tipo'] or ''),
                    'monto_total': float(c['monto_total']) if c['monto_total'] is not None else '',
                    'estatus': c['estatus'] or 'Borrador',
                    'nombre_empresa': c['nombre_empresa'] or '',
                }})
            return jsonify({'status': False, 'datos': None})

        if 'registrar' in request.form:
            if not current_user.tiene_permiso('contrato.create'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            try:
                obj_model.set_id_patrocinador(request.form['id_patrocinador'])
                obj_model.set_fecha_inicio(request.form['fecha_inicio'])
                obj_model.set_fecha_fin(request.form['fecha_fin'])
                obj_model.set_tipo(request.form['tipo'])
                obj_model.set_monto_total(request.form.get('monto_total') or None)
                obj_model.set_estatus(request.form.get('estatus', 'Borrador'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            if obj_model.confirmar_registro():
                c = obj_model.obtener_por_id(obj_model._id_contrato)
                _registrar_bitacora('create', 'Registrar contrato', f'Contrato de {c["nombre_empresa"]} registrado')
                mensaje = 'Contrato registrado correctamente'
            else:
                mensaje = 'Error al registrar el contrato'
            return jsonify({'mensaje': mensaje})

        if 'editar' in request.form:
            if not current_user.tiene_permiso('contrato.edit'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            id_c = request.form['editar']
            try:
                obj_model.set_id_patrocinador(request.form['id_patrocinador'])
                obj_model.set_fecha_inicio(request.form['fecha_inicio'])
                obj_model.set_fecha_fin(request.form['fecha_fin'])
                obj_model.set_tipo(request.form['tipo'])
                obj_model.set_monto_total(request.form.get('monto_total') or None)
                obj_model.set_estatus(request.form.get('estatus', 'Borrador'))
            except ValueError as e:
                return jsonify({'error': str(e)}), 400
            if obj_model.confirmar_modificacion(id_c):
                c = obj_model.obtener_por_id(id_c)
                _registrar_bitacora('update', 'Editar contrato', f'Contrato de {c["nombre_empresa"]} actualizado')
                mensaje = 'Contrato actualizado correctamente'
            else:
                mensaje = 'Error al actualizar el contrato'
            return jsonify({'mensaje': mensaje})

        if 'eliminar' in request.form:
            if not current_user.tiene_permiso('contrato.delete'):
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            obj_model.set_id_contrato(request.form['eliminar'])
            c = obj_model.obtener_por_id(request.form['eliminar'])
            if obj_model.confirmar_eliminacion(request.form['eliminar']):
                _registrar_bitacora('delete', 'Eliminar contrato', f'Contrato de {c["nombre_empresa"]} eliminado')
                mensaje = 'Contrato eliminado correctamente'
            else:
                mensaje = 'Error al eliminar el contrato'
            return jsonify({'mensaje': mensaje})

    patrocinadores = obj_model.obtener_patrocinadores()
    return render_template('contrato/contrato.html',
                           patrocinadores=patrocinadores,
                           mensaje=mensaje)


@bp.route('/api/obtener/<int:id>')
def api_obtener(id):
    obj_model = ContratoModel()
    c = obj_model.obtener_por_id(id)
    if not c:
        return jsonify({'error': 'No encontrado'}), 404
    return jsonify({
        'id_contrato': c['id_contrato'],
        'id_patrocinador': c['id_patrocinador'],
        'fecha_inicio': c['fecha_inicio'].isoformat() if c['fecha_inicio'] else '',
        'fecha_fin': c['fecha_fin'].isoformat() if c['fecha_fin'] else '',
        'estatus': c['estatus'],
        'tipo': str(c['tipo'] or ''),
        'monto_total': float(c['monto_total']) if c['monto_total'] is not None else "",
        'nombre_empresa': c['nombre_empresa'] or '',
    })
