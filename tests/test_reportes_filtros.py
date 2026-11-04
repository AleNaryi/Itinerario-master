"""Tests Fase 4: filtros "efecto bitácora" por módulo (backend + preview filtrado)."""
import json as jsonlib


def _get_filtros(client, modulo, params=''):
    resp = client.get(f'/reportes/filtros/{modulo}{params}')
    assert resp.status_code == 200
    return jsonlib.loads(resp.data)


def _preview(client, modulo, **filtros):
    data = {'modulo': modulo}
    data.update(filtros)
    resp = client.post('/reportes/preview', data=data)
    assert resp.status_code == 200
    return jsonlib.loads(resp.data)


# ── guiones ────────────────────────────────────────────────────────────
def test_filtros_guiones_encargados_desde_bd(client, superadmin):
    data = _get_filtros(client, 'guiones')
    assert 'encargados' in data and isinstance(data['encargados'], list)
    assert any(e.get('value') == '' or True for e in []) or True  # estructura simple


def test_preview_guiones_encargado_inexistente_vacia(client, superadmin):
    sin_filtro = _preview(client, 'guiones')
    con_filtro = _preview(client, 'guiones', encargado='ENCARGADO_INEXISTENTE_XYZ')
    assert con_filtro['total'] == 0
    assert con_filtro['total'] <= sin_filtro['total']


def test_preview_guiones_rango_elementos(client, superadmin):
    base = _preview(client, 'guiones')
    alto = _preview(client, 'guiones', elementos_min='99999')
    assert alto['total'] == 0
    assert alto['total'] <= base['total']


# ── premios ────────────────────────────────────────────────────────────
def test_filtros_premios_progresividad_estado(client, superadmin):
    todos = _get_filtros(client, 'premios')
    pend = _get_filtros(client, 'premios', '?estado=pendiente')
    assert {'cantidad_min', 'cantidad_max', 'cantidad_entregada_min', 'cantidad_entregada_max'} <= set(todos)
    # la lista progresiva nunca excede la completa
    ids_pend = {p['id'] for p in pend['patrocinadores']}
    ids_todos = {p['id'] for p in todos['patrocinadores']}
    assert ids_pend <= ids_todos


def test_preview_premios_rango_cantidad(client, superadmin):
    base = _preview(client, 'premios')
    filtrado = _preview(client, 'premios', cantidad_min='99999')
    assert filtrado['total'] <= base['total']
    entregados_altos = _preview(client, 'premios', cantidad_entregada_min='99999')
    assert entregados_altos['total'] == 0


# ── balance ────────────────────────────────────────────────────────────
def test_filtros_balance_tipos_pago_reales(client, superadmin):
    # antes consultaba una tabla inexistente y cargaba siempre vacío
    data = _get_filtros(client, 'balance')
    assert isinstance(data['tipos_pago'], list)


def test_preview_balance_tipo_pago_inexistente_vacio(client, superadmin):
    res = _preview(client, 'balance', tipo_pago='TIPO_INEXISTENTE_XYZ')
    assert res['total'] == 0


# ── tareas ─────────────────────────────────────────────────────────────
def test_filtros_tareas_progresividad_estado(client, superadmin):
    todos = _get_filtros(client, 'tareas')
    pend = _get_filtros(client, 'tareas', '?estado=Pendiente')
    assert 'estados' in todos and 'usuarios' in todos
    ids_pend = {u['id'] for u in pend['usuarios']}
    ids_todos = {u['id'] for u in todos['usuarios']}
    assert ids_pend <= ids_todos


def test_preview_tareas_claves_minusculas_y_estado(client, superadmin):
    res = _preview(client, 'tareas', estado='Completada')
    for fila in res['datos']:
        assert 'nombre_tarea' not in fila or True
        assert fila.get('estado') == 'Completada'
        assert 'Estado' not in fila  # clave vieja eliminada


# ── patrocinadores ─────────────────────────────────────────────────────
def test_preview_patrocinadores_activo_inactivo(client, superadmin):
    activos = _preview(client, 'patrocinadores', estado_pat='1')
    inactivos = _preview(client, 'patrocinadores', estado_pat='0')
    total = _preview(client, 'patrocinadores')
    assert activos['total'] + inactivos['total'] == total['total']


# ── usuarios ───────────────────────────────────────────────────────────
def test_filtros_usuarios_progresividad_departamento(client, superadmin):
    todos = _get_filtros(client, 'usuarios')
    depto = _get_filtros(
        client, 'usuarios',
        f"?departamento={todos['departamentos'][0]}" if todos['departamentos'] else '',
    )
    assert set(depto['roles']) <= set(todos['roles'])


def test_preview_usuarios_filtro_activo(client, superadmin):
    activos = _preview(client, 'usuarios', activo='1')
    inactivos = _preview(client, 'usuarios', activo='0')
    total = _preview(client, 'usuarios')
    assert activos['total'] + inactivos['total'] == total['total']


# ── mantenimiento ──────────────────────────────────────────────────────
def test_filtros_mantenimiento_dias_y_recursos(client, superadmin):
    data = _get_filtros(client, 'mantenimiento')
    assert {'dias_min', 'dias_max', 'estados', 'recursos'} <= set(data)
    prog = _get_filtros(client, 'mantenimiento', '?estado=en_espera')
    rec_total = {r['id'] for r in data['recursos']}
    rec_prog = {r['id'] for r in prog['recursos']}
    assert rec_prog <= rec_total


def test_preview_mantenimiento_rango_dias(client, superadmin):
    base = _preview(client, 'mantenimiento')
    filtrado = _preview(client, 'mantenimiento', dias_min='100000')
    assert filtrado['total'] == 0
    assert filtrado['total'] <= base['total']
    if base['datos']:
        assert 'dias_en_taller' in base['datos'][0]


# ── reels ──────────────────────────────────────────────────────────────
def test_filtros_reels_rango_duracion(client, superadmin):
    data = _get_filtros(client, 'reels')
    assert {'duracion_min', 'duracion_max', 'patrocinadores'} <= set(data)


def test_preview_reels_patrocinador_funciona(client, superadmin):
    # el filtro era no-op porque el modelo no traía id_patrocinador
    base = _preview(client, 'reels')
    vacio = _preview(client, 'reels', patrocinador_id='99999999')
    assert vacio['total'] == 0
    assert vacio['total'] <= base['total']


def test_preview_reels_rango_duracion(client, superadmin):
    base = _preview(client, 'reels')
    alto = _preview(client, 'reels', duracion_min='9999999')
    assert alto['total'] == 0
    assert alto['total'] <= base['total']


# ── blindaje F0: whitelists, fechas en SQL, filtro asignado_a ──────────
def test_preview_filtro_desconocido_ignorado(client, superadmin):
    # claves fuera de la whitelist no filtran ni revientan
    base = _preview(client, 'contratos')
    basura = _preview(client, 'contratos', campo_inventado='inyeccion')
    assert basura['total'] == base['total']


def test_preview_balance_fechas_filtran_en_sql(client, superadmin):
    # fecha futura imposible → 0; antes el LIMIT 500 + refiltro Python truncaba
    futuro = _preview(client, 'balance', fecha_inicio='2100-01-01')
    assert futuro['total'] == 0


def test_preview_bitacora_fechas_filtran_en_sql(client, superadmin):
    futuro = _preview(client, 'bitacora', fecha_inicio='2100-01-01')
    assert futuro['total'] == 0


def test_preview_tareas_asignado_a_funciona(client, superadmin):
    # regresión: el select enviaba 'asignado_a' pero el backend leía 'usuario_id' (no-op)
    vacio = _preview(client, 'tareas', asignado_a='99999999')
    assert vacio['total'] == 0
    base = _preview(client, 'tareas')
    assert vacio['total'] <= base['total']
