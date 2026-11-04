import json
from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import PREMIO
from app.model.premio_model import PremioModel

bp = Blueprint('premio', __name__, url_prefix='/premio')

bp.before_request(verificar_acceso(PREMIO))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('premio', tipo, accion, detalle)


@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    obj_model = PremioModel()
    if request.method == 'POST':
        accion = request.form.get('accion', '')

        if accion == 'consultar':
            pendientes = obj_model.obtener_premios_pendientes()
            entregados = obj_model.obtener_premios_entregados()
            return jsonify({
                'pendientes': [
                    {
                        'id': p['id'], 'nombre': p['nombre'], 'descripcion': p['descripcion'],
                        'estado': p['estado'], 'patrocinador_nombre': p['patrocinador_nombre'],
                        'id_patrocinador': p.get('id_patrocinador'), 'foto': p['foto'],
                        'fecha_creacion': str(p['fecha_creacion']) if p['fecha_creacion'] else '',
                        'cantidad': p['cantidad'], 'cantidad_entregada': p['cantidad_entregada'],
                    }
                    for p in pendientes
                ],
                'entregados': [
                    {
                        'id': p['id'], 'nombre': p['nombre'],
                        'patrocinador_nombre': p['patrocinador_nombre'],
                        'foto': p['foto'], 'descripcion': p.get('descripcion', ''),
                        'fecha_entrega': str(p['fecha_entrega']) if p['fecha_entrega'] else '',
                        'entregado_por': p['usuario_nombre'],
                        'cantidad': p['cantidad'], 'cantidad_entregada': p['cantidad_entregada'],
                    }
                    for p in entregados
                ],
            })

        if accion == 'registrar':
            if not current_user.tiene_permiso('premio.create'):
                return jsonify({'error': 'No tienes permiso'}), 403
            obj_model.set_nombre(request.form['nombre'])
            obj_model.set_id_patrocinador(request.form.get('id_patrocinador'))
            obj_model.set_descripcion(request.form.get('descripcion'))
            obj_model.set_cantidad(request.form.get('cantidad', 1))
            foto = request.files.get('foto')
            if foto and foto.filename:
                from app.config import UPLOAD_FOLDER
                from app.helpers.image_optimizer import optimizar_imagen
                import os
                buffer = optimizar_imagen(foto)
                fname = f"premio_{int(__import__('time').time())}.jpg"
                with open(os.path.join(UPLOAD_FOLDER, fname), 'wb') as f:
                    f.write(buffer.read())
                obj_model.set_foto(fname)
            else:
                obj_model.set_foto('default-premio.png')
            ok = obj_model.confirmar_registro()
            if ok:
                _registrar_bitacora('create', 'Registrar premio', f'Premio "{request.form["nombre"]}" registrado')
                return jsonify({'mensaje': 'Premio registrado exitosamente'})
            return jsonify({'error': 'Error al registrar'}), 400

        if accion == 'editar':
            if not current_user.tiene_permiso('premio.edit'):
                return jsonify({'error': 'No tienes permiso'}), 403
            obj_model.set_nombre(request.form['nombre'])
            obj_model.set_id_patrocinador(request.form.get('id_patrocinador'))
            obj_model.set_descripcion(request.form.get('descripcion'))
            obj_model.set_cantidad(request.form.get('cantidad', 1))
            foto = request.files.get('foto')
            if foto and foto.filename:
                from app.config import UPLOAD_FOLDER
                from app.helpers.image_optimizer import optimizar_imagen
                import os
                buffer = optimizar_imagen(foto)
                fname = f"premio_{int(__import__('time').time())}.jpg"
                with open(os.path.join(UPLOAD_FOLDER, fname), 'wb') as f:
                    f.write(buffer.read())
                obj_model.set_foto(fname)
            ok = obj_model.confirmar_modificacion(request.form.get('id'))
            if ok:
                p = obj_model.obtener_para_api(request.form.get('id'))
                _registrar_bitacora('update', 'Editar premio', f'Premio "{p["nombre"]}" actualizado')
                return jsonify({'mensaje': 'Premio actualizado exitosamente'})
            return jsonify({'error': 'Error al editar'}), 400

        if accion == 'eliminar':
            if not current_user.tiene_permiso('premio.delete'):
                return jsonify({'error': 'No tienes permiso'}), 403
            p = obj_model.obtener_para_api(request.form.get('id'))
            ok = obj_model.confirmar_eliminacion(request.form.get('id'))
            if ok:
                _registrar_bitacora('delete', 'Eliminar premio', f'Premio "{p["nombre"]}" eliminado')
                return jsonify({'mensaje': 'Premio eliminado exitosamente'})
            return jsonify({'error': 'Error al eliminar'}), 400

        if accion == 'entregar':
            if not current_user.tiene_permiso('premio.entregar'):
                return jsonify({'error': 'No tienes permiso'}), 403
            raw_cantidad = request.form.get('cantidad_entregar', '1')
            raw_patrocinador = request.form.get('id_patrocinador')
            if not str(raw_cantidad).isdigit() or not raw_patrocinador or not str(raw_patrocinador).isdigit():
                return jsonify({'error': 'Cantidad o patrocinador inválido'}), 400
            cantidad_entregar = int(raw_cantidad)
            p = obj_model.obtener_para_api(request.form.get('id_premio'))
            ok = obj_model.entregar(
                request.form.get('id_premio'), request.form.get('id_patrocinador'),
                request.form.get('descripcion'), current_user.id, cantidad_entregar,
            )
            if ok:
                _registrar_bitacora('update', 'Entregar premio', f'Premio "{p["nombre"]}" entregado')
                return jsonify({'mensaje': 'Premio entregado exitosamente'})
            return jsonify({'error': 'Error al entregar'}), 400

        if accion == 'obtener':
            p = obj_model.obtener_para_api(request.form.get('id'))
            if p:
                return jsonify({
                    'id': p['id'], 'nombre': p['nombre'], 'id_patrocinador': p['id_patrocinador'],
                    'descripcion': p['descripcion'], 'foto': p['foto'],
                    'cantidad': p['cantidad'], 'cantidad_entregada': p['cantidad_entregada'],
                })
            return jsonify({'error': 'Premio no encontrado'}), 404

        return jsonify({'error': 'Accion no reconocida'}), 400

    pendientes = obj_model.obtener_premios_pendientes()
    entregados = obj_model.obtener_premios_entregados()
    patrocinadores = obj_model.obtener_patrocinadores()
    return render_template(
        'premio/dashboard.html',
        pendientes=pendientes,
        entregados=entregados,
        patrocinadores=patrocinadores,
    )
