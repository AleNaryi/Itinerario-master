"""Tests de permisos por ruta."""
from app.model.bitacora_model import SesionModel


def _login_rapido(client, crear_usuario, rol):
    usuario = crear_usuario(rol=rol)
    with client.session_transaction() as s:
        s['captcha_code'] = 'ABCD'
    resp = client.post('/auth/login', data={
        'email': usuario.email,
        'password': getattr(usuario, '_password', ''),
        'captcha_text': 'ABCD',
    })
    assert resp.status_code == 302
    return usuario


def test_anonimo_redirige_al_login(client):
    resp = client.get('/usuarios/')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_superadmin_accede(client, crear_usuario):
    _login_rapido(client, crear_usuario, 'Superadmin')
    assert client.get('/usuarios/').status_code == 200
    assert client.get('/dashboard').status_code == 200


def test_usuario_sin_permiso_es_rechazado(client, crear_usuario):
    # rol inexistente => permisos vacíos => rechazo
    _login_rapido(client, crear_usuario, 'SinPermisos')
    resp = client.get('/usuarios/')
    assert resp.status_code == 302
    assert '/dashboard' in resp.headers['Location']


def test_post_json_sin_permiso_devuelve_403(client, crear_usuario):
    _login_rapido(client, crear_usuario, 'SinPermisos')
    resp = client.post('/inventario/crear', json={'nombre': 'x'})
    assert resp.status_code == 403
