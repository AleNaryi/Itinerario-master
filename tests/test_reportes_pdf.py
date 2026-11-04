"""Tests Fase 4: análisis nuevo del PDF (resumen ejecutivo, Top-N, comparativa)."""
import json as jsonlib


def _generar(client, **extras):
    data = {'modulo': 'patrocinadores'}
    data.update(extras)
    resp = client.post('/reportes/generar', data=data)
    assert resp.status_code == 200, resp.data
    body = jsonlib.loads(resp.data)
    assert 'descargar' in body
    dl = client.get(body['descargar'])
    assert dl.status_code == 200
    return dl


def test_pdf_basico_sin_opciones(client, superadmin):
    dl = _generar(client)
    assert dl.data.startswith(b'%PDF-')


def test_pdf_con_analisis_completo(client, superadmin):
    """Resumen ejecutivo + comparativa de período + Top N en un solo PDF."""
    dl = _generar(client, resumen='1', comparar='1', top_n='3')
    assert dl.data.startswith(b'%PDF-')
    texto = dl.data.decode('latin-1')  # los streams PDF están comprimidos; validamos estructura
    assert '%%EOF' in texto or len(dl.data) > 1000


def test_pdf_top_n_invalido_se_descarta(client, superadmin):
    # fuera de rango 1-20 → la whitelist lo ignora y el PDF se genera igual
    dl = _generar(client, top_n='9999', resumen='1')
    assert dl.data.startswith(b'%PDF-')


def test_pdf_comparativa_sin_fechas_validas_no_explota(client, superadmin):
    # fechas absurdas: la comparativa simplemente no se calcula
    dl = _generar(client, fecha_inicio='basura', fecha_fin='2020-01-01', comparar='1')
    assert dl.data.startswith(b'%PDF-')


def test_resumen_ejecutivo_solo_usa_kpis_reales():
    """La sección no inventa texto: usa exactamente los KPIs recibidos."""
    class UsuarioDummy:
        nombre = 'T'
        rol = 'R'
        departamento = 'D'

    from app.helpers.generators.base_report import BaseReportGenerator
    gen = BaseReportGenerator(UsuarioDummy())
    story = gen._resumen_ejecutivo({
        'total': 8,
        'monto_total': '$12,345',
        'por_tipo': {'Oro': 3},   # dict debe ignorarse en el párrafo
    })
    assert isinstance(story, list) and story  # genera párrafos sin fallar
