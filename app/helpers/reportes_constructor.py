"""Motor del Constructor de Reportes: arma y ejecuta la consulta agregada.

REGLA DE ORO: todo identificador (fuente, dimensión, métrica, filtro) se valida
contra app/helpers/reportes_catalogo.py. Los valores viajan SIEMPRE como %s.
Cualquier identificador fuera de catálogo → ConstructorError (HTTP 400).
"""
import logging
from datetime import datetime, timedelta

from app.helpers.reportes_catalogo import (
    DIMENSIONES, FILTROS_BUILDER, FUENTE_SCHEMA, FUENTES_SQL,
    GRANOS_TEMPORALES, LIMITE_FILAS, METRICAS, MODULO_BUILDER,
    SOFT_DELETE, DEFAULT_SCHEMA,
)
from app.helpers.reportes_utils import _parsear_fecha

logger = logging.getLogger(__name__)

FORMATO_FECHA = '%Y-%m-%d'


class ConstructorError(ValueError):
    """Petición inválida según catálogo → HTTP 400."""


def _validar(modulo, peticion):
    config = MODULO_BUILDER.get(modulo)
    if not config:
        raise ConstructorError('Módulo no disponible en el constructor')
    categoria = peticion.get('categoria', '')
    if categoria == 'resumen':
        raise ConstructorError("Usa el flujo clásico para 'Resumen general'")
    cat = config['categorias'].get(categoria)
    if not cat or cat.get('tipo') == 'legado':
        raise ConstructorError('Categoría no válida')
    if cat.get('fuente') not in FUENTES_SQL:
        raise ConstructorError('Fuente de datos no configurada')
    return config, cat


def _sql_dimension(dim_id, grano=None):
    dim = DIMENSIONES[dim_id]
    col = dim['sql']
    if dim['tipo'] != 'temporal':
        return col
    formato = GRANOS_TEMPORALES.get(grano or dim.get('grano', 'mes'))
    return f"DATE_FORMAT({col}, '{formato}')"


def _coercer_valor(coercion, valor):
    valor = str(valor or '').strip()
    if not valor:
        return None
    try:
        if coercion == 'entero':
            return int(valor) if valor.isdigit() else None
        if coercion in ('float_min', 'float_max'):
            return float(valor.replace(',', '.'))
        if coercion == 'texto':
            return valor
        if coercion == 'fecha':
            dt = _parsear_fecha(valor)
            return dt.strftime(FORMATO_FECHA) if dt else None
    except (ValueError, TypeError):
        return None
    return None


def _wheres_filtros(cat, filtros_recibidos):
    """Convierte filtros del request en (wheres, params) SOLO si están en catálogo."""
    wheres, params = [], []
    declarados = {f: FILTROS_BUILDER[f] for f in cat.get('filtros', [])}
    # rango_fecha declara un solo id que abre min/max con sufijos _ini/_fin
    for fid, spec in declarados.items():
        if spec['coercion'] == 'rango_fecha':
            campo = spec['campo_sql']
            ini = _coercer_valor('fecha', filtros_recibidos.get(f'{fid}_ini'))
            fin = _coercer_valor('fecha', filtros_recibidos.get(f'{fid}_fin'))
            if ini:
                wheres.append(f"{campo} >= %s")
                params.append(ini)
            if fin:
                wheres.append(f"{campo} <= %s")
                params.append(fin + ' 23:59:59' if len(fin) == 10 else fin)
            continue
        valor = _coercer_valor(spec['coercion'], filtros_recibidos.get(fid))
        if valor is None:
            continue
        op = '<=' if spec['coercion'] == 'float_max' else '>=' if spec['coercion'] == 'float_min' else '='
        wheres.append(f"{spec['campo_sql']} {op} %s")
        params.append(valor)
    return wheres, params


def construir_sql(cat, dimension_id, grano, metricas_ids, filtros_recibidos):
    fuente = FUENTES_SQL[cat['fuente']]
    select = [_sql_dimension(dimension_id, grano)]
    group_by = [select[0]]
    for mid in metricas_ids:
        met = METRICAS[mid]
        if met.get('sin_agg'):
            # el sql ya trae la agregación completa (ej. % sobre CASE/SUM/COUNT)
            select.append(met['sql'])
        else:
            select.append(f"{met['agg']}({met['sql']})")
    where = []
    soft = SOFT_DELETE.get(cat['fuente'])
    if soft:
        where.append(soft)
    w_f, p_f = _wheres_filtros(cat, filtros_recibidos)
    where.extend(w_f)
    sql = f"SELECT {', '.join(select)} {fuente}"
    if where:
        sql += " WHERE " + " AND ".join(where)
    sql += " GROUP BY " + ", ".join(group_by)
    limite = int(cat.get('limite') or LIMITE_FILAS)
    sql += f" ORDER BY 2 DESC LIMIT {limite}"  # primera métrica descendente
    return sql, p_f


def _etiquetar(dim_id, valor):
    dim = DIMENSIONES[dim_id]
    if dim['tipo'] == 'mapa':
        return dim['mapa'].get(str(valor), str(valor))
    return str(valor)


def ejecutar(modulo, peticion):
    """Devuelve dataset genérico; levanta ConstructorError si algo no es válido."""
    config, cat = _validar(modulo, peticion)

    dimension_id = peticion.get('dimension', '')
    if dimension_id not in cat['dimensiones']:
        raise ConstructorError('Dimensión no válida para esta categoría')

    metricas_validas = list(cat['metricas'])
    metricas_ids = [m for m in (peticion.get('metricas') or cat.get('metricas_default', []))
                    if m in metricas_validas]
    if not metricas_ids:
        raise ConstructorError('Selecciona al menos una métrica válida')

    dim = DIMENSIONES[dimension_id]
    grano = peticion.get('tiempo_grano', 'mes')
    if dim['tipo'] == 'temporal' and grano not in GRANOS_TEMPORALES:
        raise ConstructorError('Grano temporal no válido')
    if dim['tipo'] != 'temporal':
        grano = None

    filtros_recibidos = peticion.get('filtros') or {}
    if not isinstance(filtros_recibidos, dict):
        raise ConstructorError('Filtros inválidos')
    filtros_recibidos = {k: v for k, v in filtros_recibidos.items() if v}

    from app.database import Database
    conn = Database.get_connection(FUENTE_SCHEMA.get(cat['fuente'], DEFAULT_SCHEMA))
    sql, params = construir_sql(cat, dimension_id, grano, metricas_ids, filtros_recibidos)

    logger.info('Constructor SQL [%s/%s]: %s', modulo, cat['nombre'], sql)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        crudas = cur.fetchall()

    limit_alcanzado = len(crudas) >= int(cat.get('limite') or LIMITE_FILAS)
    filas, totales = [], {m: 0.0 for m in metricas_ids}
    for row in crudas:
        valores = list(row.values())
        etiqueta = _etiquetar(dimension_id, valores[0])
        fila = {'dimension': etiqueta}
        for i, mid in enumerate(metricas_ids, start=1):
            num = float(valores[i] or 0)
            fila[mid] = num
            totales[mid] += num
        filas.append(fila)

    dataset = {
        'modulo': modulo,
        'categoria': cat['nombre'],
        'dimension': {'id': dimension_id, 'label': dim['label']},
        'columnas': ([{'key': 'dimension', 'label': dim['label'], 'tipo': 'texto'}]
                     + [{'key': m, 'label': METRICAS[m]['label'],
                         'tipo': METRICAS[m]['formato']} for m in metricas_ids]),
        'filas': filas,
        'totales': totales,
        'serie': ({'grano': grano} if dim['tipo'] == 'temporal' else None),
        'comparacion': None,
        'meta': {
            'filtros_aplicados': filtros_recibidos,
            'generado_en': datetime.now().strftime('%d/%m/%Y %H:%M'),
            'limit_alcanzado': limit_alcanzado,
        },
    }

    comparacion = peticion.get('comparacion', 'ninguna')
    if comparacion == 'periodo_anterior':
        previo = _periodo_anterior(conn, cat, dimension_id, grano, metricas_ids,
                                   filtros_recibidos, totales)
        dataset['comparacion'] = previo
    elif comparacion and comparacion != 'ninguna':
        raise ConstructorError('Modo de comparación no disponible')
    return dataset


def _periodo_anterior(conn, cat, dimension_id, grano, metricas_ids, filtros,
                      totales_actuales):
    """Re-ejecuta desplazando el rango de fechas hacia atrás su propia longitud."""
    fid_fecha = next((f for f in cat.get('filtros', [])
                      if FILTROS_BUILDER[f]['coercion'] == 'rango_fecha'), None)
    if not fid_fecha:
        return None
    ini = _parsear_fecha(filtros.get(f'{fid_fecha}_ini'))
    fin = _parsear_fecha(filtros.get(f'{fid_fecha}_fin'))
    if not (ini and fin and fin > ini):
        return None
    delta = fin - ini
    filtros_previos = dict(filtros)
    filtros_previos[f'{fid_fecha}_ini'] = (ini - delta).strftime(FORMATO_FECHA)
    filtros_previos[f'{fid_fecha}_fin'] = (ini - timedelta(days=1)).strftime(FORMATO_FECHA)
    sql, params = construir_sql(cat, dimension_id, grano, metricas_ids, filtros_previos)
    with conn.cursor() as cur:
        cur.execute(sql, params)
        crudas = cur.fetchall()
    previos_totales = {m: 0.0 for m in metricas_ids}
    for row in crudas:
        for i, mid in enumerate(metricas_ids, start=1):
            previos_totales[mid] += float(list(row.values())[i] or 0)
    variaciones = {}
    for m in metricas_ids:
        base = previos_totales[m]
        actual = totales_actuales.get(m, 0.0)
        if base:
            variaciones[m] = f"{(actual - base) / base * 100:+.0f}%"
        else:
            variaciones[m] = 'Nuevo' if actual else '—'
    return {'modo': 'periodo_anterior',
            'rango_previo': [filtros_previos[f'{fid_fecha}_ini'],
                             filtros_previos[f'{fid_fecha}_fin']],
            'totales_previos': previos_totales,
            'variaciones': variaciones}
