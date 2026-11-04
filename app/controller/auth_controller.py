import json
import logging
import secrets
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_user, logout_user, current_user
from app.model.auth_model import UsuarioModel, PasswordResetTokenModel
from app.helpers.email_service import enviar_email_recuperacion
from app.model.bitacora_model import SesionModel

logger = logging.getLogger(__name__)

bp = Blueprint('auth', __name__, url_prefix='/auth')


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('auth', tipo, accion, detalle)


def _generar_captcha():
    chars_clean = '23456789ABCDEFGHJKLMNPQRSTUVWXYZ'
    code = ''.join(secrets.choice(chars_clean) for _ in range(4))
    session['captcha_code'] = code

    colors = ['#1e40af', '#b91c1c', '#15803d', '#7c3aed', '#92400e', '#be185d']
    pastel_bg = ['#ede9fe', '#fce7f3', '#dbeafe', '#d1fae5', '#fef3c7', '#ffe4e6']
    params = []
    for i, ch in enumerate(code):
        params.append({
            'char': ch,
            'rot': secrets.randbelow(41) - 20,
            'size': 20 + secrets.randbelow(9),
            'color': colors[secrets.randbelow(len(colors))],
            'bg': pastel_bg[secrets.randbelow(len(pastel_bg))],
        })
    return {'chars': params}


def _validar_captcha(form):
    expected = session.pop('captcha_code', None)
    if not expected:
        return False
    user_input = form.get('captcha_text', '').strip().upper()
    return user_input == expected


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard.panel'))
    usuario_model = UsuarioModel()
    sesion_model = SesionModel()
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        remember = 'remember' in request.form

        if not _validar_captcha(request.form):
            flash('Resuelve el CAPTCHA para continuar', 'danger')
            captcha = _generar_captcha()
            return render_template('login.html', captcha_params=captcha)

        usuario = usuario_model.obtener_por_email(email)
        if usuario and usuario.check_password(password):
            if not usuario.activo:
                flash('Cuenta desactivada. Contacte al administrador.', 'danger')
                captcha = _generar_captcha()
                return render_template('login.html', captcha_params=captcha)
            # Takeover: cerrar sesiones abiertas previas del mismo usuario
            try:
                for s in sesion_model.consultar(usuario_id=usuario.id):
                    if not s.get('fin_sesion'):
                        sesion_model.cerrar_sesion(s['id'])
            except Exception:
                logger.exception('Error no controlado')
            login_user(usuario, remember=remember)
            usuario_model.actualizar_ultimo_acceso(usuario.id)
            sesion = sesion_model.registrar({
                'usuario_id': usuario.id,
                'ip_address': request.remote_addr,
                'user_agent': request.user_agent.string if request.user_agent else None,
            })
            if sesion:
                session['bitacora_sesion_id'] = sesion['id']
            _registrar_bitacora('login', 'Inicio de sesión', f'Usuario {usuario.email} inició sesión')
            flash(f'¡Bienvenido {usuario.nombre}!', 'success')
            next_page = request.args.get('next')
            # ponytail: solo rutas internas; bloquea absolutas ("http://..."), protocol-relative ("//evil.com") y "\evil.com"
            if not next_page or not next_page.startswith('/') or next_page.startswith('//') or '\\' in next_page:
                next_page = None
            return redirect(next_page or url_for('dashboard.panel'))
        else:
            flash('Email o contraseña incorrectos', 'danger')
    captcha = _generar_captcha()
    return render_template('login.html', captcha_params=captcha)


@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()

        if not _validar_captcha(request.form):
            flash('Resuelve el CAPTCHA para continuar', 'danger')
            captcha = _generar_captcha()
            return render_template('forgot_password.html', captcha_params=captcha)

        if not email:
            flash('Ingresa un correo electronico', 'danger')
            captcha = _generar_captcha()
            return render_template('forgot_password.html', captcha_params=captcha)

        usuario = UsuarioModel().obtener_por_email(email)
        if usuario:
            limite = 3
            recientes = PasswordResetTokenModel().contar_solicitudes_recientes(usuario.id)
            if recientes < limite:
                token = PasswordResetTokenModel().crear_token(usuario.id)
                token_url = url_for('auth.reset_password', token=token, _external=True)
                enviado = enviar_email_recuperacion(usuario.email, usuario.nombre, token_url)

        flash('Si el correo esta registrado, recibiras un enlace de recuperacion.', 'info')
        captcha = _generar_captcha()
        return render_template('forgot_password.html', captcha_params=captcha)

    captcha = _generar_captcha()
    return render_template('forgot_password.html', captcha_params=captcha)


@bp.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    pr_model = PasswordResetTokenModel()
    registro = pr_model.validar_token(token)
    if not registro:
        flash('El enlace no es valido o ha expirado.', 'danger')
        return redirect(url_for('auth.forgot_password'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm = request.form.get('confirm', '')

        if len(password) < 8 or len(password) > 30:
            flash('La contrasena debe tener entre 8 y 30 caracteres', 'danger')
            return render_template('reset_password.html', token=token)

        if password != confirm:
            flash('Las contrasenas no coinciden', 'danger')
            return render_template('reset_password.html', token=token)

        usuario_id = registro['usuario_id']
        usuario = UsuarioModel().obtener_por_id(usuario_id)
        if not usuario:
            flash('Usuario no encontrado', 'danger')
            return redirect(url_for('auth.forgot_password'))

        usuario.set_password(password)
        UsuarioModel().modificar(usuario_id, {'password_hash': usuario.password_hash})
        pr_model.marcar_usado(registro['id'])

        flash('Contrasena restablecida exitosamente', 'success')
        return redirect(url_for('auth.reset_success'))

    return render_template('reset_password.html', token=token)


@bp.route('/refresh-captcha')
def refresh_captcha():
    params = _generar_captcha()
    return params


@bp.route('/validate-login', methods=['POST'])
def validate_login():
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '')
    captcha_text = request.form.get('captcha_text', '').strip().upper()
    expected = session.get('captcha_code', '')

    if not expected or captcha_text != expected:
        return {'valid': False, 'field': 'captcha', 'message': 'Codigo incorrecto'}

    usuario = UsuarioModel().obtener_por_email(email)
    if not usuario or not usuario.check_password(password):
        return {'valid': False, 'field': 'credentials', 'message': 'Email o contrasena incorrectos'}

    if not usuario.activo:
        return {'valid': False, 'field': 'credentials', 'message': 'Cuenta desactivada'}

    return {'valid': True}


@bp.route('/reset-success')
def reset_success():
    return render_template('reset_success.html')


@bp.route('/logout')
def logout():
    sesion_model = SesionModel()
    sesion_id = session.pop('bitacora_sesion_id', None)
    if sesion_id:
        sesion_model.cerrar_sesion(sesion_id)
    _registrar_bitacora('logout', 'Cierre de sesión', f'Usuario {current_user.email} cerró sesión')
    logout_user()
    flash('Sesión cerrada correctamente', 'info')
    return redirect(url_for('auth.login'))
