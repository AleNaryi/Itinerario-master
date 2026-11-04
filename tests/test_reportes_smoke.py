"""Tests de humo para /reportes — red de seguridad del refactor de Fase 3.

Congelan la respuesta observable (status + claves JSON) ANTES de mover código.
"""
import json as jsonlib

MODULOS_SMOKE = ['patrocinadores', 'guiones']


def test_anonimo_no_entra_a_reportes(client):
    resp = client.get('/reportes/')
    assert resp.status_code == 302
    assert '/auth/login' in resp.headers['Location']


def test_dashboard_reportes_autenticado(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    login(usuario)
    resp = client.get('/reportes/')
    assert resp.status_code == 200
    assert b'reportes' in resp.data.lower()


def test_preview_respuesta_estable(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    login(usuario)
    for modulo in MODULOS_SMOKE:
        resp = client.post('/reportes/preview', data={'modulo': modulo})
        assert resp.status_code == 200, f'preview de {modulo} falló'
        data = jsonlib.loads(resp.data)
        assert set(data.keys()) >= {'datos', 'total', 'kpis', 'modulo'}
        assert isinstance(data['datos'], list)
        assert data['total'] == len(data['datos'])
        assert isinstance(data['kpis'], dict)


def test_preview_modulo_invalido(client, crear_usuario, login):
    usuario = crear_usuario(rol='Superadmin')
    login(usuario)
    resp = client.post('/reportes/preview', data={'modulo': 'no_existe'})
    assert resp.status_code == 400
