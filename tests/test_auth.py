"""Tests de auth: login, CAPTCHA, next seguro, reset y sesión única."""
from werkzeug.security import check_password_hash

from app.model.auth_model import PasswordResetTokenModel, UsuarioModel
from app.model.bitacora_model import SesionModel


def test_login_requiere_captcha(client):
    resp = client.post('/auth/login', data={'email': 'a@a.com', 'password': 'x'})
    assert b'CAPTCHA' in resp.data


def test_login_captcha_incorrecto(client):
    with client.session_transaction() as s:
        s['captcha_code'] = 'ABCD'
    resp = client.post('/auth/login', data={
        'email': 'a@a.com', 'password': 'x', 'captcha_text': 'ZZZZ',
    })
    assert b'CAPTCHA' in resp.data


def test_login_credenciales_invalidas(client, crear_usuario):
    crear_usuario()
    with client.session_transaction() as s:
        s['captcha_code'] = 'ABCD'
    resp = client.post('/auth/login', data={
        'email': 'noexiste@prueba.com', 'password': 'mala', 'captcha_text': 'ABCD',
    })
    assert b'incorrectos' in resp.data


def test_login_exitoso_redirige_al_panel(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    resp = login(usuario)
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/dashboard')


def test_login_next_interno_respetado(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    resp = login(usuario, next_page='/usuario')
    assert resp.status_code == 302
    assert resp.headers['Location'].endswith('/usuario')


def test_login_next_externo_bloqueado(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    for malo in ('https://evil.com', '//evil.com', '/\\evil.com'):
        resp = login(usuario, next_page=malo)
        assert resp.status_code == 302
        # nunca sale del sitio: cae al panel
        assert not resp.headers['Location'].startswith(('http://evil', 'https://evil'))
        assert '/dashboard' in resp.headers['Location']


def test_login_usuario_inactivo_bloqueado(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin', activo=False)
    resp = login(usuario)
    assert b'desactivada' in resp.data


def test_reset_password_flujo_completo(app, client, crear_usuario, login):
    from werkzeug.security import check_password_hash
    usuario = crear_usuario(rol='Superadmin')
    token = PasswordResetTokenModel().crear_token(usuario.id)

    resp = client.get(f'/auth/reset-password/{token}')
    assert resp.status_code == 200

    resp = client.post(f'/auth/reset-password/{token}', data={
        'password': 'NuevaClave99', 'confirm': 'NuevaClave99',
    })
    assert resp.status_code == 302

    # el token queda usado
    assert PasswordResetTokenModel().validar_token(token) is None

    # la nueva contraseña funciona; la vieja no
    recargado = UsuarioModel().obtener_por_id(usuario.id)
    assert check_password_hash(recargado.password_hash, 'NuevaClave99')
    assert not check_password_hash(recargado.password_hash, usuario._password)


def test_sesion_unica_cierra_la_anterior(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    login(usuario)
    with client.session_transaction() as s:
        sid = s.get('bitacora_sesion_id')
    assert sid is not None

    # takeover: se cierra esa sesión desde "otro dispositivo"
    SesionModel().cerrar_sesion(sid)

    resp = client.get('/dashboard')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']
