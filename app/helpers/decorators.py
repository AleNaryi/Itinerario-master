# app/helpers/decorators.py
# Decoradores reutilizables para permisos

from functools import wraps
from flask import flash, jsonify, redirect, request, url_for
from flask_login import current_user


def permiso_requerido(codigo):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if not current_user.is_authenticated:
                if request.is_json:
                    return jsonify({'error': 'No autenticado'}), 401
                return redirect(url_for('auth.login'))
            if not current_user.tiene_permiso(codigo):
                if request.is_json:
                    return jsonify({'error': 'No tienes permiso para esta accion'}), 403
                flash('No tienes permiso para acceder a esta pagina', 'danger')
                return redirect(url_for('dashboard.panel'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def verificar_acceso(permiso_map):
    """Crea un before_request que verifica permiso_map[request.endpoint].

    Uso:
        bp.before_request(verificar_acceso(PERMISSION_MAP))
    """
    def _before_request():
        if not current_user.is_authenticated:
            if request.method == 'POST':
                return jsonify({'error': 'No autenticado'}), 401
            return redirect(url_for('auth.login'))
        permiso = permiso_map.get(request.endpoint)
        if permiso and not current_user.tiene_permiso(permiso):
            if request.method == 'POST':
                return jsonify({'error': 'No tienes permiso para esta accion'}), 403
            flash('No tienes permiso para acceder a esta pagina', 'danger')
            return redirect(url_for('dashboard.panel'))
    return _before_request
