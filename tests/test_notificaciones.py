"""Multi-asignación de tareas (varios empleados / departamento completo)
y notificaciones in-app con su API."""
import pytest

from app.model.tarea_model import TareaModel
from app.model.auth_model import UsuarioModel


def _filas(app, db_name, sql, params=()):
    with app.app_context():
        from app.database import Database
        with Database.get_connection(db_name).cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchall()


@pytest.fixture()
def usuarios_depto(app, crear_usuario):
    """2 usuarios en 'Medios' y 1 en 'Palco de Operaciones'.
    Rol Superadmin para no acoplar el test al mapa de permisos.
    Se devuelven los objetos originales (conservan _password para login)."""
    um = UsuarioModel()
    usuarios = []
    for depto in ['Medios', 'Medios', 'Palco de Operaciones']:
        u = crear_usuario()
        assert um.modificar(u.id, {'departamento': depto}) is not None
        usuarios.append(u)
    return usuarios


def _crear_tarea(app, creador_id, nombre='Tarea de prueba'):
    tm = TareaModel()
    tm.set_nombre_tarea(nombre)
    tm.set_instruccion('Instruccion suficientemente larga para validar')
    tm.set_id_usuario_creador(creador_id)
    return tm.confirmar_registro()


def _asignar(client, tid, **destinos):
    data = {'asignar': 'true', 'id_tarea': str(tid)}
    data.update(destinos)
    return client.post('/gestion-tarea/', data=data)


def _login_como(app, usuario):
    """Cliente nuevo con sesión sembrada directamente.
    El flujo HTTP de login ya está cubierto por test_auth; aquí solo importa
    la identidad para las rutas de notificaciones/tareas."""
    from app.model.bitacora_model import SesionModel
    c = app.test_client()
    with app.app_context():
        sesion = SesionModel().registrar({
            'usuario_id': usuario.id,
            'ip_address': '127.0.0.1',
            'user_agent': 'pytest',
        })
    with c.session_transaction() as s:
        s['_user_id'] = str(usuario.id)
        s['_fresh'] = True
        if sesion:
            s['bitacora_sesion_id'] = sesion['id']
    return c


def _reset_usuario_cache():
    """El _contexto autouse mantiene un app context vivo durante todo el test y
    flask_login cachea el usuario en g._login_user. Sin esto, todos los requests
    del test seguirían viendo al PRIMER usuario que se resolvió."""
    from flask import g
    g.pop('_login_user', None)


def test_asignacion_multiple_crea_asignaciones_y_notificaciones(app, client, superadmin, usuarios_depto):
    u1, u2, u3 = usuarios_depto
    tid = _crear_tarea(app, superadmin.id)

    r = _asignar(client, tid, **{'id_usuarios': [str(u1.id), str(u2.id)]})
    assert r.get_json()['success'] is True
    assert r.get_json()['asignados'] == 2

    filas = _filas(app, 'estadio_db', "SELECT id_usuario FROM tareas_asignadas WHERE id_tarea=%s AND Estatus=1", (tid,))
    assert sorted(f['id_usuario'] for f in filas) == sorted([u1.id, u2.id])

    for u in (u1, u2):
        notifs = _filas(app, 'seguridad', "SELECT tipo, leida FROM notificaciones WHERE usuario_id=%s", (u.id,))
        assert len(notifs) == 1 and notifs[0]['tipo'] == 'tarea_asignada' and notifs[0]['leida'] == 0
    assert _filas(app, 'seguridad', "SELECT COUNT(*) c FROM notificaciones WHERE usuario_id=%s", (u3.id,))[0]['c'] == 0

    # reasignar a los mismos: se omite sin duplicar fila ni notificación
    r2 = _asignar(client, tid, **{'id_usuarios': [str(u1.id), str(u2.id)]})
    assert r2.get_json()['asignados'] == 0 and r2.get_json()['omitidos'] == 2
    assert len(_filas(app, 'estadio_db', "SELECT id_asignacion FROM tareas_asignadas WHERE id_tarea=%s AND Estatus=1", (tid,))) == 2


def test_departamento_completo_asigna_solo_a_sus_activos(app, client, superadmin, usuarios_depto):
    u1, u2, u3 = usuarios_depto
    tid = _crear_tarea(app, superadmin.id)

    # 'Medios' ya trae miembros del seed: el esperado es dinámico
    um = UsuarioModel()
    esperados = sorted(u.id for u in um.consultar(departamento='Medios', activo=1))
    assert set([u1.id, u2.id]).issubset(set(esperados)) and u3.id not in esperados

    r = _asignar(client, tid, departamento='Medios')
    body = r.get_json()
    assert body['success'] is True and body['asignados'] == len(esperados)

    filas = _filas(app, 'estadio_db', "SELECT id_usuario FROM tareas_asignadas WHERE id_tarea=%s AND Estatus=1", (tid,))
    assert sorted(f['id_usuario'] for f in filas) == esperados
    # combinado con selección individual: dedupe (solo entra el que faltaba)
    r2 = _asignar(client, tid, departamento='Medios', **{'id_usuarios': [str(u3.id)]})
    assert r2.get_json()['asignados'] == 1 and r2.get_json()['omitidos'] == len(esperados)
    assert len(_filas(app, 'estadio_db', "SELECT id_asignacion FROM tareas_asignadas WHERE id_tarea=%s AND Estatus=1", (tid,))) == len(esperados) + 1


def test_api_devuelve_solo_las_propias_y_marca_leidas(app, client, superadmin, usuarios_depto):
    u1, u2, _ = usuarios_depto
    tid = _crear_tarea(app, superadmin.id)
    _asignar(client, tid, departamento='Medios')

    n_u2 = _filas(app, 'seguridad', "SELECT id FROM notificaciones WHERE usuario_id=%s", (u2.id,))[0]['id']

    c_u1 = _login_como(app, u1)
    _reset_usuario_cache()
    data = c_u1.get('/notificaciones/api').get_json()
    assert data['count'] == 1 and data['items'][0]['tipo'] == 'tarea_asignada'
    ids_propios = {i['id'] for i in data['items']}
    assert n_u2 not in ids_propios

    # no puede marcar la notificación de otro
    r_ajena = c_u1.post('/notificaciones/leer', data={'id': str(n_u2)})
    assert r_ajena.get_json()['success'] is False

    propia = data['items'][0]['id']
    assert c_u1.post('/notificaciones/leer', data={'id': str(propia)}).get_json()['success'] is True
    assert c_u1.get('/notificaciones/api').get_json()['count'] == 0

    # nueva tarea asignada y "marcar todas"
    _reset_usuario_cache()
    tid2 = _crear_tarea(app, superadmin.id, nombre='Tarea segunda ronda')
    _asignar(client, tid2, departamento='Medios')
    _reset_usuario_cache()
    assert c_u1.get('/notificaciones/api').get_json()['count'] == 1
    c_u1.post('/notificaciones/leer-todas')
    _reset_usuario_cache()
    assert c_u1.get('/notificaciones/api').get_json()['count'] == 0

    # sin sesión: la API es privada
    _reset_usuario_cache()
    anon = app.test_client()
    assert anon.get('/notificaciones/api').status_code in (301, 302)


def test_completar_notifica_al_creador(app, client, superadmin, usuarios_depto):
    u1, _, _ = usuarios_depto
    tid = _crear_tarea(app, superadmin.id)
    _asignar(client, tid, **{'id_usuarios': [str(u1.id)]})

    c_u1 = _login_como(app, u1)
    _reset_usuario_cache()
    asig = _filas(app, 'estadio_db',
                  "SELECT id_asignacion FROM tareas_asignadas WHERE id_tarea=%s AND id_usuario=%s",
                  (tid, u1.id))[0]
    resp = c_u1.post('/gestion-tarea/completar', data={'id_asignacion': str(asig['id_asignacion'])},
                     follow_redirects=True)

    creador_notifs = _filas(app, 'seguridad',
                            "SELECT tipo, mensaje FROM notificaciones WHERE usuario_id=%s", (superadmin.id,))
    assert any(n['tipo'] == 'tarea_completada' for n in creador_notifs), resp.status_code
    # quien completó NO recibe auto-notificación
    propias = _filas(app, 'seguridad', "SELECT tipo FROM notificaciones WHERE usuario_id=%s", (u1.id,))
    assert all(n['tipo'] != 'tarea_completada' for n in propias)
