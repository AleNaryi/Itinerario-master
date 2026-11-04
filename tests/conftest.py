"""Fixtures de pytest para Itinerario.

Regla dura: los tests corren SOLO contra las BDs *_test, clonadas desde los
.sql de la raíz. Nunca tocan estadio_db / seguridad reales.
"""
import os
import re
import sys
import uuid
from pathlib import Path

import pymysql
import pytest
from pymysql.constants import CLIENT

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

# nombre original -> nombre de prueba (solo esquemas clonados)
TEST_DBS = {'estadio_db': 'estadio_db_test', 'seguridad': 'seguridad_test'}


def _creds():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'root'),
        'password': os.getenv('DB_PASSWORD', ''),
        'charset': 'utf8mb4',
    }


def _aplicar_dump(conn, archivo):
    """Aplica un .sql de la raíz sobre la BD de prueba.

    Los dumps traen CREATE DATABASE / USE con los nombres reales; se renombra
    únicamente esos tokens backtick-eados para redirigir todo al *_test.
    """
    sql = (ROOT / archivo).read_text(encoding='utf-8')
    sql = re.sub(r'`(estadio_db|seguridad)`', r'`\1_test`', sql)
    with conn.cursor() as cur:
        cur.execute(sql)  # requiere MULTI_STATEMENTS en la conexión
        while cur.nextset():
            pass


@pytest.fixture(scope='session', autouse=True)
def bases_de_prueba():
    from dotenv import load_dotenv
    load_dotenv(ROOT / '.env')
    conn = pymysql.connect(client_flag=CLIENT.MULTI_STATEMENTS, **_creds())
    try:
        with conn.cursor() as cur:
            for test in TEST_DBS.values():
                cur.execute(f'DROP DATABASE IF EXISTS `{test}`')
                cur.execute(f'CREATE DATABASE `{test}` DEFAULT CHARACTER SET utf8mb4')
        _aplicar_dump(conn, 'estadio_db.sql')
        _aplicar_dump(conn, 'seguridad.sql')
    finally:
        conn.close()
    yield


@pytest.fixture()
def app(monkeypatch):
    # apunta la config a las BDs de prueba ANTES de crear la app
    from app import config
    for origen, test in TEST_DBS.items():
        config.DATABASE_CONFIG[origen]['database'] = test
    monkeypatch.setenv('SECRET_KEY', 'clave-de-test')

    # nunca enviar correos reales
    from app.helpers import email_service
    from app.controller import auth_controller
    monkeypatch.setattr(email_service, 'enviar_email_recuperacion', lambda *a, **k: True)
    monkeypatch.setattr(auth_controller, 'enviar_email_recuperacion', lambda *a, **k: True)

    from app import create_app
    application = create_app()
    application.config['TESTING'] = True
    application.config['WTF_CSRF_ENABLED'] = False
    yield application


@pytest.fixture(autouse=True)
def _contexto(app):
    """Empuja un app context para que las llamadas directas a modelos tengan flask.g."""
    with app.app_context():
        yield


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture()
def crear_usuario(app):
    """Crea usuarios directamente en seguridad_test."""
    def _crear(rol='Superadmin', activo=True, password='Clave1234'):
        from werkzeug.security import generate_password_hash
        from app.model.auth_model import UsuarioModel
        email = f'test_{uuid.uuid4().hex[:8]}@prueba.com'
        usuario = UsuarioModel().registrar({
            'nombre': 'Usuario Prueba',
            'email': email,
            'password_hash': generate_password_hash(password),
            'cedula': uuid.uuid4().hex[:10],
            'rol': rol,
        })
        assert usuario is not None, 'No se pudo registrar el usuario de prueba'
        if not activo:
            UsuarioModel().modificar(usuario.id, {'activo': 0})
            usuario = UsuarioModel().obtener_por_id(usuario.id)
        usuario._password = password
        return usuario
    return _crear


@pytest.fixture()
def login(client):
    """Login completo respetando CAPTCHA. Devuelve la respuesta del POST."""
    def _login(usuario, next_page=None, captcha='ABCD'):
        with client.session_transaction() as s:
            s['captcha_code'] = captcha
        url = '/auth/login'
        if next_page:
            url += f'?next={next_page}'
        return client.post(url, data={
            'email': usuario.email,
            'password': getattr(usuario, '_password', ''),
            'captcha_text': captcha,
        })
    return _login


@pytest.fixture()
def superadmin(client, crear_usuario, login):
    """Cliente con sesión iniciada como Superadmin."""
    usuario = crear_usuario(rol='Superadmin')
    login(usuario)
    return usuario
