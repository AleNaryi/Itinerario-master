"""Tests de integración de la vista rediseñada EN VIVO (vivo.html).

Cubre: render de la vista, jerarquía/atributos del contrato frontend,
flag de operación por permiso y el endpoint de sincronización.
"""
import json as jsonlib

import pytest


def _crear_guion_completo(app):
    """Guion + 2 pregame + 2 game en estadio_db_test. Devuelve guion_id."""
    with app.app_context():
        db = __import__('app.database', fromlist=['Database']).Database.get_connection('estadio_db')
        with db.cursor() as cur:
            # regla de negocio: solo UN guion en vivo; cerrar el del test anterior
            cur.execute("UPDATE guiones SET estado = 'finalizado' WHERE estado = 'en_vivo'")
            cur.execute(
                "INSERT INTO guiones (nombre, estado, creado_en, modificado_en, status) "
                "VALUES (%s, %s, NOW(), NOW(), 1)",
                ('Guion Vista Test', 'publicado')
            )
            guion_id = cur.lastrowid
            cur.execute("INSERT INTO guion_fechas (guion_id, fecha) VALUES (%s, CURDATE())", (guion_id,))
            elementos = [
                ('pregame', None, None, 'Intro música', 30, 'Keiver', 1),
                ('pregame', None, None, 'Saludo animador', 60, 'Maria', 2),
                ('game', 1, 'alta', 'Promo especial', 120, 'Keiver', 3),
                ('game', 1, 'baja', 'Dinámica público', 90, 'Maria', 4),
            ]
            for tipo, inning, medio, contenido, dur, encargado, orden in elementos:
                cur.execute(
                    "INSERT INTO elementos_guion (guion_id, tipo, hora, inning, medio_inning, "
                    "contenido, duracion_estimada, encargado, orden, estado) "
                    "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 'pendiente')",
                    (guion_id, tipo, '18:30:00', inning, medio, contenido, dur, encargado, orden)
                )
        return guion_id


def _iniciar(app, guion_id):
    from app.model.en_vivo_model import EnVivoModel
    with app.app_context():
        assert EnVivoModel().iniciar(guion_id) is True
    return True


def test_vista_rechaza_guion_no_en_vivo(client, superadmin):
    resp = client.get('/en-vivo/99999999')
    assert resp.status_code == 302
    assert '/en-vivo/' in resp.headers['Location']


def test_vista_renderiza_contrato_frontend(client, app, superadmin):
    """La página contiene los anclajes que el JS rediseñado necesita."""
    guion_id = _crear_guion_completo(app)
    _iniciar(app, guion_id)

    resp = client.get(f'/en-vivo/{guion_id}')
    html = resp.data.decode('utf-8')

    # header rediseñado
    for marcador in ('progresoFill', 'connChip', 'pendChip', 'filtroEncargado',
                     'btnFinalizar', 'themeToggle', 'vivo-viewer-count'):
        assert marcador in html, f'falta {marcador} en la vista'
    assert 'EN VIVO' in html
    assert 'Logo-blanco.png' in html

    # elementos con atributos de datos para cronómetro/filtro
    assert 'data-duracion="120"' in html      # promo especial (segundos, NO minutos)
    assert 'data-encargado="Keiver"' in html

    # operador: puede operar
    assert 'data-puede-operar="1"' in html

    # hero inicial: primer elemento quedó en_curso al iniciar
    assert 'en_curso' in html


def test_espectador_ve_pero_flag_operacion_apagado(client, app, crear_usuario):
    """Usuario solo con envivo.view: ve la vista pero sin flag de operar; API lo rechaza."""
    guion_id = _crear_guion_completo(app)
    _iniciar(app, guion_id)

    usuario = crear_usuario(rol='SoloVer')
    with app.app_context():
        db = __import__('app.database', fromlist=['Database']).Database.get_connection('seguridad')
        with db.cursor() as cur:
            cur.execute("SELECT id FROM permisos WHERE codigo = 'envivo.view'")
            pid = cur.fetchone()['id']
            cur.execute(
                "INSERT INTO usuario_permiso (usuario_id, permiso_id, fecha_asignacion) "
                "VALUES (%s, %s, NOW())", (usuario.id, pid)
            )

    with client.session_transaction() as s:
        s['captcha_code'] = 'ABCD'
    resp = client.post('/auth/login', data={
        'email': usuario.email,
        'password': getattr(usuario, '_password', ''),
        'captcha_text': 'ABCD',
    })
    assert resp.status_code == 302

    page = client.get(f'/en-vivo/{guion_id}')
    html = page.data.decode('utf-8')
    assert page.status_code == 200
    assert 'data-puede-operar=""' in html

    api = client.post(
        f'/en-vivo/api/sincronizar/{guion_id}',
        json={'estados': [{'id': 1, 'estado': 'completado'}]},
    )
    assert api.status_code == 403


def test_sincronizar_operador_funciona(client, app, superadmin):
    guion_id = _crear_guion_completo(app)
    _iniciar(app, guion_id)

    with app.app_context():
        db = __import__('app.database', fromlist=['Database']).Database.get_connection('estadio_db')
        with db.cursor() as cur:
            cur.execute("SELECT id FROM elementos_guion WHERE guion_id = %s ORDER BY orden LIMIT 1", (guion_id,))
            elem_id = cur.fetchone()['id']

    resp = client.post(
        f'/en-vivo/api/sincronizar/{guion_id}',
        json={'estados': [{'id': elem_id, 'estado': 'completado', 'accion': 'completar'}]},
    )
    body = jsonlib.loads(resp.data)
    assert resp.status_code == 200 and body['success'] is True

    # estado persistido + log registrado (sincronizaciones vive en seguridad)
    with app.app_context():
        db = __import__('app.database', fromlist=['Database']).Database.get_connection('estadio_db')
        with db.cursor() as cur:
            cur.execute("SELECT estado FROM elementos_guion WHERE id = %s", (elem_id,))
            assert cur.fetchone()['estado'] == 'completado'
        db_seg = __import__('app.database', fromlist=['Database']).Database.get_connection('seguridad')
        with db_seg.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) t FROM sincronizaciones "
                "WHERE guion_id = %s AND nombre = 'sincronizar'",
                (guion_id,)
            )
            assert cur.fetchone()['t'] >= 1


def test_relojes_servidor(client, app, superadmin):
    """El servidor es la única fuente de verdad temporal: inicio_curso por elemento,
    inicio_show del guion, servidor_ahora para compensar relojes de clientes."""
    import time

    guion_id = _crear_guion_completo(app)
    assert _iniciar(app, guion_id)

    r1 = client.get(f'/en-vivo/api/estado-actual/{guion_id}').get_json()
    assert 'servidor_ahora' in r1
    estados = {e['id']: e for e in r1['estados']}
    activos = [e for e in estados.values() if e['estado'] == 'en_curso']
    assert len(activos) == 1 and isinstance(activos[0]['inicio_curso'], int)
    primero = activos[0]['id']
    assert all(estados[i]['inicio_curso'] is None for i in estados if i != primero)

    # avanzar: completar primero, segundo pasa a en_curso con su propio reloj
    client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': primero, 'estado': 'completado', 'accion': 'completar'},
        {'id': primero + 0},  # ruido: id sin estado debe ignorarse
    ]})
    # el frontend manda también el avance; lo hacemos explícito:
    ids_ordenados = sorted(estados.keys())
    segundo = [i for i in ids_ordenados if i != primero][0]
    client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': segundo, 'estado': 'en_curso'},
    ]})
    r2 = client.get(f'/en-vivo/api/estado-actual/{guion_id}').get_json()
    est2 = {e['id']: e for e in r2['estados']}
    assert est2[primero]['inicio_curso'] is None          # salió de en_curso -> se limpia
    t_segundo = est2[segundo]['inicio_curso']
    assert isinstance(t_segundo, int)

    # reiniciar el evento (salir y volver a en_curso) RENUEVA su reloj
    time.sleep(1.1)  # DATETIME tiene precisión de segundos
    client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': segundo, 'estado': 'pendiente', 'accion': 'reiniciar'},
    ]})
    time.sleep(1.1)
    client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': segundo, 'estado': 'en_curso', 'accion': 'reiniciar'},
    ]})
    r3 = client.get(f'/en-vivo/api/estado-actual/{guion_id}').get_json()
    est3 = {e['id']: e for e in r3['estados']}
    assert est3[segundo]['inicio_curso'] > t_segundo      # reloj reiniciado para todos

    # finalizar limpia todo
    client.get(f'/en-vivo/finalizar/{guion_id}')
    with app.app_context():
        db = __import__('app.database', fromlist=['Database']).Database.get_connection('estadio_db')
        with db.cursor() as cur:
            cur.execute("SELECT inicio_show FROM guiones WHERE id = %s", (guion_id,))
            assert cur.fetchone()['inicio_show'] is None
            cur.execute("SELECT COUNT(*) t FROM elementos_guion WHERE guion_id = %s AND inicio_curso IS NOT NULL", (guion_id,))
            assert cur.fetchone()['t'] == 0


def test_vista_expone_relojes_al_template(client, app, superadmin):
    guion_id = _crear_guion_completo(app)
    _iniciar(app, guion_id)
    html = client.get(f'/en-vivo/{guion_id}').data.decode('utf-8')
    assert 'data-inicio-show="' in html and 'data-servidor-ahora="' in html
    assert 'data-inicio="' in html           # elementos con inicio_curso_ms
    assert 'showClockChip' in html and 'showClockTxt' in html


def test_sincronizar_estado_invalido_rechazado(client, app, superadmin):
    guion_id = _crear_guion_completo(app)
    _iniciar(app, guion_id)
    resp = client.post(
        f'/en-vivo/api/sincronizar/{guion_id}',
        json={'estados': [{'id': 1, 'estado': 'estado_hackeado'}]},
    )
    assert resp.status_code == 200  # filtra inválidos y responde success sin aplicarlos


def test_retroceso_cascada_y_bitacora(client, app, superadmin):
    """Contrato del retroceso del frontend: ↩ sobre completado #1 con 2 activo
    debe dejar 1=en_curso y 2=pendiente (cascada), y registrar el reinicio en bitácora."""
    guion_id = _crear_guion_completo(app)
    _iniciar(app, guion_id)

    with app.app_context():
        db = __import__('app.database', fromlist=['Database']).Database.get_connection('estadio_db')
        with db.cursor() as cur:
            cur.execute(
                "SELECT id FROM elementos_guion WHERE guion_id = %s ORDER BY orden", (guion_id,)
            )
            e1, e2, e3, e4 = [r['id'] for r in cur.fetchall()]

    def estados_bd():
        with app.app_context():
            db = __import__('app.database', fromlist=['Database']).Database.get_connection('estadio_db')
            with db.cursor() as cur:
                cur.execute(
                    "SELECT id, estado FROM elementos_guion WHERE guion_id = %s ORDER BY orden",
                    (guion_id,)
                )
                return {r['id']: r['estado'] for r in cur.fetchall()}

    # iniciar deja e1 en_curso; operador completa e1 y el frontend avanza e2
    assert client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': e1, 'estado': 'completado', 'accion': 'completar'},
        {'id': e2, 'estado': 'en_curso'},
    ]}).status_code == 200
    assert estados_bd() == {e1: 'completado', e2: 'en_curso', e3: 'pendiente', e4: 'pendiente'}

    # retroceso sobre e1 (completado): cascada -> e1 en_curso, e2 vuelve a pendiente
    resp = client.post(f'/en-vivo/api/sincronizar/{guion_id}', json={'estados': [
        {'id': e1, 'estado': 'en_curso', 'accion': 'reiniciar'},
        {'id': e2, 'estado': 'pendiente', 'accion': 'reiniciar'},
    ]})
    assert resp.status_code == 200
    assert estados_bd() == {e1: 'en_curso', e2: 'pendiente', e3: 'pendiente', e4: 'pendiente'}

    # la bitácora registra los marcajes gracias al campo accion
    with app.app_context():
        db_seg = __import__('app.database', fromlist=['Database']).Database.get_connection('seguridad')
        with db_seg.cursor() as cur:
            cur.execute(
                "SELECT COUNT(*) t FROM sincronizaciones WHERE guion_id = %s "
                "AND nombre = 'sincronizar' AND descripcion LIKE '%%reiniciado%%'",
                (guion_id,)
            )
            assert cur.fetchone()['t'] >= 1


def test_contrato_csrf_sincronizar():
    """Blindaje del bug del doble clic: el fetch DEBE enviar X-CSRFToken.

    Sin header -> 400 de CSRF. Con token válido de la sesión -> pasa CSRF y
    cae en auth/permisos (401 anónimo), nunca 400.
    """
    import re as _re
    from app import create_app as _create_app

    app_csrf = _create_app()   # instancia aparte: aquí CSRF sigue ACTIVO
    c = app_csrf.test_client()

    page = c.get('/auth/login')
    m = _re.search(r'name="csrf_token"[^>]*value="([^"]+)"', page.data.decode('utf-8'))
    assert m, 'login.html debe exponer el token CSRF'

    sin_header = c.post('/en-vivo/api/sincronizar/1', json={'estados': []})
    assert sin_header.status_code == 400

    con_header = c.post(
        '/en-vivo/api/sincronizar/1',
        json={'estados': []},
        headers={'X-CSRFToken': m.group(1)},
    )
    assert con_header.status_code != 400
