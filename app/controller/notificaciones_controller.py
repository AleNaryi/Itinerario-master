from datetime import datetime

from flask import Blueprint, request, jsonify, redirect, url_for
from flask_login import current_user
from app.model.notificacion_model import NotificacionModel

bp = Blueprint('notificaciones', __name__, url_prefix='/notificaciones')

ICONOS = {'tarea_asignada': 'fa-clipboard-list', 'tarea_completada': 'fa-check-circle'}


def _hace(fecha):
    """Tiempo relativo estilo red social: 'hace 5 min', 'hace 2 h'..."""
    if not fecha:
        return ''
    delta = (datetime.now() - fecha).total_seconds()
    if delta < 60:
        return 'hace un momento'
    if delta < 3600:
        return f'hace {int(delta // 60)} min'
    if delta < 86400:
        return f'hace {int(delta // 3600)} h'
    return fecha.strftime('%d/%m/%Y')


# data propia del usuario autenticado: no requiere código de permiso
@bp.before_request
def _requerir_login():
    if not current_user.is_authenticated:
        return redirect(url_for('auth.login'))


@bp.route('/api')
def api():
    modelo = NotificacionModel()
    items = []
    for r in modelo.listar(current_user.id, limite=15):
        items.append({
            'id': r['id'],
            'tipo': r['tipo'],
            'icono': ICONOS.get(r['tipo'], 'fa-bell'),
            'titulo': r['titulo'],
            'mensaje': r['mensaje'],
            'url': r.get('url') or '',
            'leida': bool(r['leida']),
            'hace': _hace(r['fecha_creacion']),
        })
    return jsonify({'count': modelo.contar_no_leidas(current_user.id), 'items': items})


@bp.route('/leer', methods=['POST'])
def leer():
    id_notificacion = request.form.get('id')
    if not id_notificacion or not str(id_notificacion).isdigit():
        return jsonify({'success': False, 'error': 'Notificación inválida'}), 400
    ok = NotificacionModel().marcar_leida(int(id_notificacion), current_user.id)
    return jsonify({'success': bool(ok)})


@bp.route('/leer-todas', methods=['POST'])
def leer_todas():
    NotificacionModel().marcar_todas(current_user.id)
    return jsonify({'success': True})
