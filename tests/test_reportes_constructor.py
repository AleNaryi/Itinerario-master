"""Tests del Constructor de Reportes: catálogo, motor whitelistado y endpoints."""
import json as jsonlib
import re

from app.helpers.reportes_catalogo import (
    DIMENSIONES, FILTROS_BUILDER, FUENTE_ALIASES, FUENTE_SCHEMA, FUENTES_SQL,
    METRICAS, MODULO_BUILDER, SOFT_DELETE,
)


def _alias_de_columna(col):
    """Todos los alias calificados presentes en la expresión SQL (p.ej. DATEDIFF(a.x, b.y) → {'a','b'})."""
    return set(re.findall(r'(\w+)\s*\.', str(col)))


# ── consistencia del catálogo (puro, sin BD) ───────────────────────────
def test_toda_fuente_declarada_existe():
    for modulo, config in MODULO_BUILDER.items():
        for cid, cat in config['categorias'].items():
            if cat.get('tipo') == 'legado':
                continue
            assert cat['fuente'] in FUENTES_SQL, f'{modulo}/{cid}: fuente inexistente'


def test_dimensiones_metricas_filtros_existen_en_registros():
    for modulo, config in MODULO_BUILDER.items():
        for cid, cat in config['categorias'].items():
            if cat.get('tipo') == 'legado':
                continue
            for d in cat['dimensiones']:
                assert d in DIMENSIONES, f'{modulo}/{cid}: dimensión {d} sin definir'
            for m in cat['metricas']:
                assert m in METRICAS, f'{modulo}/{cid}: métrica {m} sin definir'
            for f in cat['filtros']:
                assert f in FILTROS_BUILDER, f'{modulo}/{cid}: filtro {f} sin definir'


def test_alias_sql_de_dimension_pertenece_a_su_fuente():
    for modulo, config in MODULO_BUILDER.items():
        for cid, cat in config['categorias'].items():
            if cat.get('tipo') == 'legado':
                continue
            alias_ok = FUENTE_ALIASES[cat['fuente']]
            for d in cat['dimensiones']:
                aliases = _alias_de_columna(DIMENSIONES[d]['sql'])
                assert aliases <= alias_ok, \
                    f'{modulo}/{cid}/{d}: alias {aliases - alias_ok} fuera de la fuente'
            for m in cat['metricas']:
                aliases = _alias_de_columna(METRICAS[m]['sql'])
                assert aliases <= alias_ok, \
                    f'{modulo}/{cid}/{m}: alias {aliases - alias_ok} fuera de la fuente'


def test_toda_fuente_tiene_esquema_y_softdelete_conocidos():
    for fuente in FUENTES_SQL:
        esquema = FUENTE_SCHEMA.get(fuente)
        assert esquema in (None, 'seguridad'), f'{fuente}: esquema desconocido'
        assert fuente in SOFT_DELETE, f'{fuente}: sin declaración de soft-delete'


def test_todo_modulo_tiene_resumen_legado_y_almenos_una_categoria():
    for modulo, config in MODULO_BUILDER.items():
        assert 'resumen' in config['categorias'], f'{modulo}: sin resumen legado'
        constructoras = [c for c in config['categorias'].values()
                         if c.get('tipo') != 'legado']
        assert constructoras, f'{modulo}: sin categorías de constructor'


def test_filtros_declarados_en_categorias_existen_y_tienen_ui_o_coercion():
    for modulo, config in MODULO_BUILDER.items():
        for cid, cat in config['categorias'].items():
            if cat.get('tipo') == 'legado':
                continue
            for f in cat['filtros']:
                spec = FILTROS_BUILDER[f]
                assert 'campo_sql' in spec or f in ('fecha_inicio', 'fecha_fin')


# ── un caso de ejecución por cada módulo incorporado ───────────────────
def _construir(client, payload):
    resp = client.post('/reportes/construir', json=payload)
    assert resp.status_code == 200, resp.data
    return jsonlib.loads(resp.data)


def test_guiones_produccion_por_encargado(client, superadmin):
    data = _construir(client, {
        'modulo': 'guiones', 'categoria': 'produccion',
        'dimension': 'encargado_elemento', 'metricas': ['elementos_conteo'],
    })
    assert isinstance(data['filas'], list)


def test_inventario_valorizacion_por_tipo(client, superadmin):
    data = _construir(client, {
        'modulo': 'inventario', 'categoria': 'valorizacion',
        'dimension': 'inv_tipo',
        'metricas': ['costo_suma', 'recursos_conteo'],
    })
    assert {'costo_suma', 'recursos_conteo'} <= set(data['totales'])


def test_premios_stock_por_estado(client, superadmin):
    data = _construir(client, {
        'modulo': 'premios', 'categoria': 'entregas_stock',
        'dimension': 'pr_estado',
        'metricas': ['premios_conteo', 'pendientes_suma'],
    })
    assert 'pendientes_suma' in data['totales']


def test_balance_cobranza_por_tipo_pago(client, superadmin):
    data = _construir(client, {
        'modulo': 'balance', 'categoria': 'cobranza',
        'dimension': 'tipo_pago', 'metricas': ['pago_suma'],
    })
    assert 'pago_suma' in data['totales']


def test_tareas_carga_por_usuario(client, superadmin):
    data = _construir(client, {
        'modulo': 'tareas', 'categoria': 'carga',
        'dimension': 'tar_usuario',
        'metricas': ['asignaciones_tarea_conteo', 'completadas_pct'],
    })
    assert 'asignaciones_tarea_conteo' in data['totales']


def test_patrocinadores_cartera_por_encargado(client, superadmin):
    data = _construir(client, {
        'modulo': 'patrocinadores', 'categoria': 'cartera_pat',
        'dimension': 'pat_encargado',
        'metricas': ['patrocinadores_conteo', 'activos_conteo'],
    })
    assert 'patrocinadores_conteo' in data['totales']


def test_usuarios_planta_por_rol(client, superadmin):
    data = _construir(client, {
        'modulo': 'usuarios', 'categoria': 'planta',
        'dimension': 'us_rol', 'metricas': ['usuarios_conteo'],
    })
    assert 'usuarios_conteo' in data['totales']


def test_mantenimiento_taller_dias_promedio(client, superadmin):
    data = _construir(client, {
        'modulo': 'mantenimiento', 'categoria': 'taller',
        'dimension': 'man_estado',
        'metricas': ['mantenimientos_conteo', 'dias_promedio'],
    })
    assert 'dias_promedio' in data['totales']


def test_reels_contenido_por_patrocinador(client, superadmin):
    data = _construir(client, {
        'modulo': 'reels', 'categoria': 'contenido',
        'dimension': 'reel_patrocinador',
        'metricas': ['clips_conteo', 'duracion_clip_suma'],
    })
    assert 'clips_conteo' in data['totales']


# ── endpoints ──────────────────────────────────────────────────────────
def _post_json(client, url, payload):
    return client.post(url, json=payload)


def test_catalogo_publico_no_filtra_sql(client, superadmin):
    resp = client.get('/reportes/catalogo/contratos')
    assert resp.status_code == 200
    data = jsonlib.loads(resp.data)
    assert 'resumen' in data['categorias'] and 'ingresos' in data['categorias']
    texto = jsonlib.dumps(data)
    assert 'FROM ' not in texto and 'JOIN ' not in texto  # nada de SQL interno al cliente


def test_catalogo_modulo_sin_constructor_400(client, superadmin):
    # resumen NO entra al constructor (bug latente documentado en auditoría §12)
    resp = client.get('/reportes/catalogo/resumen')
    assert resp.status_code == 400


def test_construir_bitacora_por_accion(client, superadmin):
    payload = {
        'modulo': 'bitacora', 'categoria': 'actividad',
        'dimension': 'accion', 'metricas': ['actividades_conteo'],
    }
    resp = _post_json(client, '/reportes/construir', payload)
    assert resp.status_code == 200, resp.data
    data = jsonlib.loads(resp.data)
    assert isinstance(data['filas'], list)
    assert data['columnas'][0]['key'] == 'dimension'
    assert 'actividades_conteo' in data['totales']


def test_construir_inyeccion_en_dimension_400(client, superadmin):
    payload = {
        'modulo': 'bitacora', 'categoria': 'actividad',
        'dimension': "1; DROP TABLE usuarios", 'metricas': ['actividades_conteo'],
    }
    resp = _post_json(client, '/reportes/construir', payload)
    assert resp.status_code == 400


def test_construir_metrica_fuera_de_catalogo_400(client, superadmin):
    payload = {
        'modulo': 'contratos', 'categoria': 'cartera',
        'dimension': 'nivel', 'metricas': ['monto_inexistente'],
    }
    resp = _post_json(client, '/reportes/construir', payload)
    assert resp.status_code == 400


def test_construir_categoria_desconocida_400(client, superadmin):
    payload = {
        'modulo': 'contratos', 'categoria': 'no_existe',
        'dimension': 'nivel', 'metricas': ['monto_total_suma'],
    }
    resp = _post_json(client, '/reportes/construir', payload)
    assert resp.status_code == 400


def test_construir_contratos_cartera_por_nivel(client, superadmin):
    payload = {
        'modulo': 'contratos', 'categoria': 'cartera',
        'dimension': 'nivel',
        'metricas': ['monto_total_suma', 'registros_conteo'],
        'filtros': {'c_fecha_ini': '2000-01-01'},
    }
    resp = _post_json(client, '/reportes/construir', payload)
    assert resp.status_code == 200, resp.data
    data = jsonlib.loads(resp.data)
    assert len(data['filas']) <= 3  # Bronce/Plata/Oro
    assert {'monto_total_suma', 'registros_conteo'} <= set(data['totales'])


def test_exportar_csv_y_pdf(client, superadmin):
    base = {
        'modulo': 'contratos', 'categoria': 'cartera', 'dimension': 'estatus',
        'metricas': ['registros_conteo'],
    }
    resp_csv = _post_json(client, '/reportes/construir/exportar', {**base, 'formato': 'csv'})
    assert resp_csv.status_code == 200
    assert 'text/csv' in resp_csv.content_type

    resp_pdf = _post_json(client, '/reportes/construir/exportar', {**base, 'formato': 'pdf'})
    assert resp_pdf.status_code == 200, resp_pdf.data
    body = jsonlib.loads(resp_pdf.data)
    dl = client.get(body['descargar'])
    assert dl.status_code == 200
    assert dl.data.startswith(b'%PDF-')
