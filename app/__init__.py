import os
import pymysql
from pathlib import Path
from dotenv import load_dotenv
from flask import Flask, session, request, redirect, url_for, flash
from flask_wtf.csrf import CSRFProtect
from flask_socketio import SocketIO, join_room
from flask_login import LoginManager, current_user, logout_user

load_dotenv()

csrf = CSRFProtect()
# ponytail: mismo origen por defecto; SOCKET_ALLOWED_ORIGINS="https://a.com,https://b.com" si algún día hay dominios externos
_origins_env = os.getenv('SOCKET_ALLOWED_ORIGINS', '')
socketio = SocketIO(cors_allowed_origins=[o.strip() for o in _origins_env.split(',') if o.strip()] or None)
usuarios_conectados = {}
login_manager = LoginManager()
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Por favor inicia sesión para acceder'
login_manager.login_message_category = 'warning'


def sala_usuario(user_id):
    return f'user_{user_id}'


def emitir_notificacion(user_ids, payload):
    """Empuja una notificación en vivo a las salas privadas de los usuarios."""
    for uid in set(user_ids):
        socketio.emit('notificacion_nueva', payload, room=sala_usuario(uid))


def create_app():
    _root = Path(__file__).resolve().parent.parent
    app = Flask(__name__,
                template_folder=str(_root / 'app' / 'view'),
                static_folder=str(_root / 'app' / 'static'))

    secret_key = os.getenv('SECRET_KEY')
    if not secret_key:
        raise RuntimeError("SECRET_KEY no definida: agrega SECRET_KEY al archivo .env (genera una con 'python3 -c \"import secrets; print(secrets.token_hex(32))\"')")
    app.config['SECRET_KEY'] = secret_key
    app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
    app.config['WTF_CSRF_TIME_LIMIT'] = None

    csrf.init_app(app)
    socketio.init_app(app)
    login_manager.init_app(app)

    from app.database import Database
    Database.init_app(app)





    @login_manager.user_loader
    def load_user(user_id):
        try: ##agg estas lineas para devolver los errores elegantemente
            from app.model.auth_model import UsuarioModel
            return UsuarioModel().obtener_por_id(int(user_id))
        except pymysql.err.OperationalError:
            return None

    with app.app_context(): #seed_permisos_iniciales() envuelto en try/except para ignorar error si DB está caída al iniciar
        try:
            from app.model.rol_model import RolModel
            RolModel().seed_permisos_iniciales()
        except pymysql.err.OperationalError:
            pass


    from app.controller.auth_controller import bp as auth_bp
    from app.controller.dashboard_controller import bp as dashboard_bp
    from app.controller.usuario_controller import bp as usuario_bp
    from app.controller.guion_controller import bp as guion_bp
    from app.controller.en_vivo_controller import bp as en_vivo_bp
    from app.controller.mantenimiento_controller import bp as mantenimiento_bp
    from app.controller.premio_controller import bp as premio_bp
    from app.controller.contrato_controller import bp as contrato_bp
    from app.controller.balance_controller import bp as balance_bp
    from app.controller.gestion_tarea_controller import bp as gestion_tarea_bp
    from app.controller.patrocinador_controller import bp as patrocinador_bp
    from app.controller.bitacora_controller import bp as bitacora_bp
    from app.controller.rol_controller import bp as rol_bp
    from app.controller.inventario_controller import bp as inventario_bp
    from app.controller.reels_controller import bp as reels_bp
    from app.controller.reportes_controller import bp as reportes_bp
    from app.controller.chat_controller import bp as chat_bp
    from app.controller.notificaciones_controller import bp as notificaciones_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(usuario_bp)
    app.register_blueprint(guion_bp)
    app.register_blueprint(en_vivo_bp)
    app.register_blueprint(mantenimiento_bp)
    app.register_blueprint(premio_bp)
    app.register_blueprint(contrato_bp)
    app.register_blueprint(balance_bp)
    app.register_blueprint(gestion_tarea_bp)
    app.register_blueprint(patrocinador_bp)
    app.register_blueprint(bitacora_bp)
    app.register_blueprint(rol_bp)
    app.register_blueprint(inventario_bp)
    app.register_blueprint(reels_bp)
    app.register_blueprint(reportes_bp)
    app.register_blueprint(chat_bp)
    app.register_blueprint(notificaciones_bp)

    @app.before_request
    def verificar_sesion_unica():
        if request.endpoint and (request.endpoint.startswith('static') or request.endpoint in ('auth.login', 'auth.logout')):
            return
        if current_user.is_authenticated:
            from app.model.bitacora_model import SesionModel
            sid = session.get('bitacora_sesion_id')
            if sid:
                db_sesion = SesionModel().obtener_por_id(sid)
                if not db_sesion or db_sesion.get('fin_sesion'):
                    flash('Tu sesión fue cerrada desde otro dispositivo', 'warning')
                    logout_user()
                    session.pop('bitacora_sesion_id', None)
                    return redirect(url_for('auth.login'))

                    

    @socketio.on('connect')
    def handle_connect():
        # Rechaza sockets anónimos; la identidad SIEMPRE sale de la sesión, nunca del cliente
        if not current_user.is_authenticated:
            return False

    @socketio.on('registrar_usuario')
    def handle_registrar_usuario(data):
        from flask import request
        sid = request.sid
        usuarios_conectados[sid] = {
            'user_id': current_user.id,
            'nombre': current_user.nombre,
            'pagina': data.get('pagina', '/'),
            'en_vivo_id': data.get('en_vivo_id')
        }
        # sala privada: las notificaciones solo llegan a los sockets de su dueño
        join_room(sala_usuario(current_user.id))
        _emit_usuarios_actualizados()

    @socketio.on('cambio_pagina')
    def handle_cambio_pagina(data):
        from flask import request
        sid = request.sid
        if sid in usuarios_conectados:
            usuarios_conectados[sid]['pagina'] = data.get('pagina', '/')
            usuarios_conectados[sid]['en_vivo_id'] = data.get('en_vivo_id')
            _emit_usuarios_actualizados()

    @socketio.on('disconnect')
    def handle_disconnect():
        from flask import request
        sid = request.sid
        usuarios_conectados.pop(sid, None)
        _emit_usuarios_actualizados()

    def _emit_usuarios_actualizados():
        unicos = {}
        for u in usuarios_conectados.values():
            uid = u.get('user_id')
            if uid and uid not in unicos:
                unicos[uid] = u
        total = len(unicos)
        usuarios_lista = [
            {'nombre': u['nombre'], 'pagina': u['pagina'], 'en_vivo_id': u['en_vivo_id']}
            for u in unicos.values()
        ]
        socketio.emit('usuarios_actualizados', {
            'count': total,
            'usuarios': usuarios_lista
        })

    @app.errorhandler(404)
    def not_found(error):
        from flask import render_template
        return render_template('error/error.html', codigo=404), 404

    @app.errorhandler(500)
    def internal_error(error):
        from flask import render_template
        return render_template('error/error.html', codigo=500), 500

    @app.errorhandler(pymysql.err.OperationalError)
    def db_connection_error(error):
        from flask import render_template
        return render_template('error/error.html', codigo=500), 500


    return app
