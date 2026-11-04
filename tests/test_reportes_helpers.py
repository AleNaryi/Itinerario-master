"""Tests de helpers del módulo reportes — lógica pura, sin BD."""
from datetime import datetime

from app.helpers.reportes_utils import (
    _parsear_fecha,
    _ordenar_datos,
    _formatear_tiempo,
    _filtrar_por_fecha,
)


def test_parsear_fecha():
    assert _parsear_fecha(None) is None
    assert _parsear_fecha('') is None
    assert _parsear_fecha('basura') is None
    assert _parsear_fecha('2024-05-03') == datetime(2024, 5, 3)
    assert _parsear_fecha('03/05/2024') == datetime(2024, 5, 3)


def test_ordenar_datos_insensible_a_mayusculas():
    datos = [{'n': 'carlos'}, {'n': 'Ana'}, {'n': 'zoe'}]
    assert [d['n'] for d in _ordenar_datos(datos, 'n')] == ['Ana', 'carlos', 'zoe']
    assert [d['n'] for d in _ordenar_datos(datos, 'n', 'desc')] == ['zoe', 'carlos', 'Ana']


def test_ordenar_datos_casos_borde():
    vacio = []
    assert _ordenar_datos(vacio, 'n') == vacio
    # sin campo devuelve igual
    datos = [{'a': 1}]
    assert _ordenar_datos(datos, None) is datos


def test_ordenar_datos_numerico_no_lexicografico():
    # regresión: '100' < '20' como string; debe ordenar numérico
    datos = [{'monto': 100}, {'monto': 20}, {'monto': 3}]
    assert [d['monto'] for d in _ordenar_datos(datos, 'monto')] == [3, 20, 100]
    assert [d['monto'] for d in _ordenar_datos(datos, 'monto', 'desc')] == [100, 20, 3]


def test_ordenar_datos_montos_formateados():
    datos = [{'m': '$9,000'}, {'m': '$10,000'}, {'m': '$500'}]
    assert [d['m'] for d in _ordenar_datos(datos, 'm')] == ['$500', '$9,000', '$10,000']


def test_ordenar_datos_mixto_numeros_y_texto():
    # números primero (asc), luego texto alfabético
    datos = [{'v': 'ana'}, {'v': 5}, {'v': 2}, {'v': 'beta'}]
    orden = [d['v'] for d in _ordenar_datos(datos, 'v')]
    assert orden == [2, 5, 'ana', 'beta']


def test_formatear_tiempo():
    assert _formatear_tiempo(0) == '0m'
    assert _formatear_tiempo(None) == '0m'
    assert _formatear_tiempo(300) == '5m'
    assert _formatear_tiempo(7200) == '2h'
    assert _formatear_tiempo(3661) == '1h 1m'


def test_filtrar_por_fecha_incluye_sin_fecha_y_rango():
    dentro = {'f': '2024-05-10 12:00:00'}
    antes = {'f': '2024-01-01 08:00:00'}
    despues = {'f': '2024-12-31 23:00:00'}
    sin_fecha = {'f': None}
    resultado = _filtrar_por_fecha(
        [dentro, antes, despues, sin_fecha], 'f', '2024-05-01', '2024-06-30'
    )
    assert dentro in resultado
    assert sin_fecha in resultado   # registros sin fecha no se descartan
    assert antes not in resultado
    assert despues not in resultado
