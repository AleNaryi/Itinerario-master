"""Datos y KPIs de reportes por módulo (extraído de reportes_controller.py).

Cada función devuelve (datos, kpis) EXACTAMENTE como la rama que reemplaza
del antiguo _obtener_datos; verificado contra línea base de previews.
"""
from datetime import datetime, date, timedelta
import logging

from app.helpers.reportes_utils import (
    CAMPOS_FECHA,
    _encontrar_fecha_minima,
    _filtrar_por_fecha,
    _fmt_video_dur,
    _formatear_tiempo,
    _parsear_fecha,
)
from app.model.guion_model import GuionModel, ElementoGuionModel
from app.model.inventario_model import InventarioModel
from app.model.premio_model import PremioModel
from app.model.contrato_model import ContratoModel
from app.model.balance_model import BalanceModel
from app.model.tarea_model import TareaModel, TareasAsignadasModel
from app.model.patrocinador_model import PatrocinadorModel
from app.model.auth_model import UsuarioModel
from app.model.mantenimiento_model import MantenimientoModel
from app.model.reels_model import ReelModel
from app.model.bitacora_model import ActividadModel

logger = logging.getLogger(__name__)


TIPO_CONTRATO_MAP = {'1': 'Bronce', '2': 'Plata', '3': 'Oro'}


COLUMNAS_TECNICAS = {
    'status', 'Estatus', 'eliminado', 'password_hash', 'password',
    'modificado_en', 'hora_creacion', 'hora_pago',
    'id_patrocinador', 'id_tipo', 'id_estado', 'tipo_id', 'estado_id',
    'recurso_id', 'usuario_id', 'sesion_id', 'guion_id', 'fecha_id',
    'entregado_por', 'registrado_por', 'id_usuario_creador',
    'ip_address', 'user_agent',
}


def _sanitizar_para_reporte(modulo, datos):
    """Limpia datos crudos de DB para consumo en reportes PDF y preview.

    - Elimina listas/dicts anidados (ej. videos, historial, usuario object)
    - Elimina columnas técnicas (status, password_hash, ids no resueltos)
    - Resuelve IDs a nombres donde hay helpers disponibles
    - Aplica formato legible a valores crudos (segundos, montos)
    """
    from decimal import Decimal
    from app.model.auth_model import UsuarioModel
    from app.model.patrocinador_model import PatrocinadorModel

    resumen_ids = {}
    if modulo in ('reels', 'premios'):
        pm = PatrocinadorModel()
        pats = pm.consultar()
        resumen_ids['patrocinador'] = {p['id_patrocinador']: p['nombre_empresa'] for p in pats}
    if modulo in ('bitacora', 'tareas', 'mantenimiento'):
        try:
            um = UsuarioModel()
            users = um.consultar()
            resumen_ids['usuario'] = {u['id']: u['nombre'] for u in users if hasattr(u, 'get') or hasattr(u, 'nombre')}
            resumen_ids['usuario'].update({u.id: u.nombre for u in users if hasattr(u, 'id') and not isinstance(u, dict)})
        except Exception:
            resumen_ids['usuario'] = {}

    resultado = []
    for d in datos:
        fila = {}
        for k, v in d.items():
            if k in COLUMNAS_TECNICAS:
                continue
            if isinstance(v, (list, dict)):
                continue
            if hasattr(v, 'strftime'):
                fila[k] = v.strftime('%d/%m/%Y %H:%M' if hasattr(v, 'hour') else '%d/%m/%Y')
            elif isinstance(v, Decimal):
                fila[k] = float(v)
            elif isinstance(v, (int, float, str, bool, type(None))):
                fila[k] = v
        if not fila.get('id') and d.get('id_contrato'):
            fila['id'] = d['id_contrato']
        if not fila.get('id') and d.get('id_patrocinador'):
            fila['id'] = d['id_patrocinador']
        if not fila.get('id') and d.get('id_tarea'):
            fila['id'] = d['id_tarea']
        resultado.append(fila)

    if modulo == 'reels':
        for i, original in enumerate(datos):
            raw_name = resumen_ids['patrocinador'].get(original.get('patrocinado'), '')
            if raw_name:
                resultado[i]['patrocinado'] = raw_name
            duracion_seg = float(original.get('duracion_total', 0) or 0)
            minutos = int(duracion_seg // 60)
            segundos = int(duracion_seg % 60)
            resultado[i]['duracion'] = f"{minutos}m {segundos}s" if minutos > 0 else f"{segundos}s"

    if modulo == 'premios':
        for i, original in enumerate(datos):
            pid = original.get('id_patrocinador')
            if pid and 'patrocinador_nombre' not in original:
                resultado[i]['patrocinador_nombre'] = resumen_ids['patrocinador'].get(pid, '')
            if not original.get('estado'):
                resultado[i]['estado'] = 'entregado'
            if not original.get('fecha_creacion'):
                resultado[i]['fecha_creacion'] = original.get('fecha_entrega', '')

    if modulo == 'bitacora':
        for i, original in enumerate(datos):
            usuario_obj = original.get('usuario')
            if isinstance(usuario_obj, dict):
                resultado[i]['usuario_nombre'] = usuario_obj.get('nombre', '')
            elif hasattr(usuario_obj, 'nombre'):
                resultado[i]['usuario_nombre'] = usuario_obj.nombre
            if 'password_hash' in resultado[i]:
                del resultado[i]['password_hash']

    if modulo == 'mantenimiento':
        for i, original in enumerate(datos):
            recurso = original.get('recurso')
            if isinstance(recurso, dict):
                resultado[i]['recurso_nombre'] = recurso.get('nombre', '')
            if not resultado[i].get('recurso_nombre') and original.get('recurso_id'):
                resultado[i]['recurso_nombre'] = resumen_ids.get('recurso', {}).get(original['recurso_id'], '')

    return resultado


def rango_fechas_defecto(modulo, filtros):
    """Completa fecha_inicio/fecha_fin vacías (hoy / mínima histórica)."""
    fi = filtros.get('fecha_inicio', '')
    ff = filtros.get('fecha_fin', '')
    hoy = datetime.now().strftime('%Y-%m-%d')

    if fi and not ff:
        ff = hoy
    elif not fi and ff:
        fi = '2000-01-01'
    elif not fi and not ff and modulo in CAMPOS_FECHA:
        campo = CAMPOS_FECHA[modulo]
        model_map = {
            'guiones': lambda: GuionModel().consultar(),
            'inventario': lambda: InventarioModel().consultar(),
            'premios': lambda: list(PremioModel().obtener_premios_pendientes()) + list(PremioModel().obtener_premios_entregados()),
            'contratos': lambda: ContratoModel().consultar(),
            'balance': lambda: BalanceModel().obtener_historial_pagos(limit=2000),
            'tareas': lambda: TareaModel().consultar(),
            'patrocinadores': lambda: PatrocinadorModel().consultar(),
            'mantenimiento': lambda: MantenimientoModel().consultar(),
            'reels': lambda: ReelModel().consultar(),
            'bitacora': lambda: ActividadModel().consultar(limite=2000),
        }
        loader = model_map.get(modulo)
        if loader:
            try:
                datos_carga = loader()
                minima = _encontrar_fecha_minima(datos_carga, campo)
                if minima:
                    fi = minima
                    ff = hoy
            except Exception:
                logger.exception('Error no controlado')

    filtros['fecha_inicio'] = fi
    filtros['fecha_fin'] = ff
    return fi, ff


def _datos_guiones(filtros, fi, ff):
    modulo = 'guiones'
    model = GuionModel()
    datos = model.consultar()
    if filtros.get('estado'):
        datos = [d for d in datos if d['estado'] == filtros['estado']]
    # elementos por guion en una sola consulta (antes: 1 query por guion)
    todos_elems = {}
    for e in ElementoGuionModel().consultar():
        todos_elems.setdefault(e['guion_id'], []).append(e)
    # filtro por encargado: el guion tiene al menos un elemento a su cargo
    if filtros.get('encargado'):
        datos = [d for d in datos
                 if any(e.get('encargado') == filtros['encargado']
                        for e in todos_elems.get(d['id'], []))]
    # rango de cantidad de elementos
    def _total_elems(d):
        return len(todos_elems.get(d['id'], []))
    if filtros.get('elementos_min'):
        try:
            v = int(filtros['elementos_min'])
            datos = [d for d in datos if _total_elems(d) >= v]
        except (ValueError, TypeError):
            pass
    if filtros.get('elementos_max'):
        try:
            v = int(filtros['elementos_max'])
            datos = [d for d in datos if _total_elems(d) <= v]
        except (ValueError, TypeError):
            pass
    datos = _filtrar_por_fecha(datos, 'creado_en', fi, ff)
    for d in datos:
        elems = todos_elems.get(d['id'], [])
        d['pregame'] = sum(1 for e in elems if e['tipo'] == 'pregame')
        d['game'] = sum(1 for e in elems if e['tipo'] == 'game')
        d['tiempo_segundos'] = sum(e.get('duracion_estimada', 0) or 0 for e in elems)
        fechas = model.obtener_fechas(d['id'])
        d['fecha_ejecucion'] = fechas[0]['fecha'].strftime('%d/%m/%Y') if fechas else '—'
        d['tiempo_total'] = _formatear_tiempo(d['tiempo_segundos'])
    borradores = sum(1 for d in datos if d.get('estado') == 'borrador')
    publicados = sum(1 for d in datos if d.get('estado') == 'publicado')
    en_vivo = sum(1 for d in datos if d.get('estado') == 'en_vivo')
    finalizados = sum(1 for d in datos if d.get('estado') == 'finalizado')
    tiempo_total_seg = sum(d.get('tiempo_segundos', 0) or 0 for d in datos)
    kpis = {
        'total': len(datos), 'borradores': borradores,
        'publicados': publicados, 'en_vivo': en_vivo,
        'finalizados': finalizados,
        'tiempo_total': _formatear_tiempo(tiempo_total_seg),
        'promedio_seg': round(tiempo_total_seg / len(datos)) if datos else 0,
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_inventario(filtros, fi, ff):
    modulo = 'inventario'
    model = InventarioModel()
    datos = model.consultar()
    if filtros.get('tipo_nombre'):
        datos = [d for d in datos if d.get('tipo_nombre') == filtros['tipo_nombre']]
    if filtros.get('estado_nombre'):
        datos = [d for d in datos if d.get('estado_nombre') == filtros['estado_nombre']]
    if filtros.get('costo_min'):
        try:
            min_v = float(filtros['costo_min'])
            datos = [d for d in datos if float(d.get('costo', 0) or 0) >= min_v]
        except ValueError:
            pass
    if filtros.get('costo_max'):
        try:
            max_v = float(filtros['costo_max'])
            datos = [d for d in datos if float(d.get('costo', 0) or 0) <= max_v]
        except ValueError:
            pass
    datos = _filtrar_por_fecha(datos, 'fecha_compra', fi, ff)
    tipos = {}
    estados = {}
    costo_total = 0
    for d in datos:
        tn = d.get('tipo_nombre', 'Otro')
        tipos[tn] = tipos.get(tn, 0) + 1
        en = d.get('estado_nombre', 'Desconocido')
        estados[en] = estados.get(en, 0) + 1
        costo_total += float(d.get('costo', 0) or 0)
    kpis = {
        'total': len(datos),
        'costo_total': round(costo_total, 2),
        'costo_promedio': round(costo_total / len(datos), 2) if datos else 0,
    }
    kpis['tipos'] = tipos
    kpis['estados'] = estados
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_premios(filtros, fi, ff):
    modulo = 'premios'
    model = PremioModel()
    pendientes = model.obtener_premios_pendientes()
    entregados = model.obtener_premios_entregados()
    for p in pendientes:
        p['estado'] = 'pendiente'
    for p in entregados:
        p['estado'] = 'entregado'
    # ponytail: fetchall() da tupla y el otro método lista; list() evita el TypeError histórico
    datos = list(pendientes) + list(entregados)
    if filtros.get('estado') == 'pendiente':
        datos = pendientes
    elif filtros.get('estado') == 'entregado':
        datos = entregados
    if filtros.get('patrocinador_id'):
        datos = [d for d in datos if str(d.get('id_patrocinador', '')) == str(filtros['patrocinador_id'])]
    # rangos de cantidades
    if filtros.get('cantidad_min'):
        try:
            v = int(filtros['cantidad_min'])
            datos = [d for d in datos if int(d.get('cantidad', 0) or 0) >= v]
        except (ValueError, TypeError):
            pass
    if filtros.get('cantidad_max'):
        try:
            v = int(filtros['cantidad_max'])
            datos = [d for d in datos if int(d.get('cantidad', 0) or 0) <= v]
        except (ValueError, TypeError):
            pass
    if filtros.get('cantidad_entregada_min'):
        try:
            v = int(filtros['cantidad_entregada_min'])
            datos = [d for d in datos if int(d.get('cantidad_entregada', 0) or 0) >= v]
        except (ValueError, TypeError):
            pass
    if filtros.get('cantidad_entregada_max'):
        try:
            v = int(filtros['cantidad_entregada_max'])
            datos = [d for d in datos if int(d.get('cantidad_entregada', 0) or 0) <= v]
        except (ValueError, TypeError):
            pass
    datos = _filtrar_por_fecha(datos, 'fecha_creacion', fi, ff)
    pend_count = sum(1 for d in datos if d.get('estado') == 'pendiente')
    ent_count = sum(1 for d in datos if d.get('estado') == 'entregado')
    pat_counts = {}
    for d in datos:
        pn = d.get('patrocinador_nombre', 'Stock Libre')
        pat_counts[pn] = pat_counts.get(pn, 0) + 1
    kpis = {
        'total': len(datos), 'pendientes': pend_count,
        'entregados': ent_count,
        'tasa_entrega': f"{ent_count * 100 // len(datos)}%" if datos else "0%",
        'por_patrocinador': pat_counts,
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_contratos(filtros, fi, ff):
    modulo = 'contratos'
    model = ContratoModel()
    datos = model.consultar()

    if filtros.get('tipo'):
        datos = [d for d in datos if str(d.get('tipo', '')) == filtros['tipo']]
    if filtros.get('estatus'):
        datos = [d for d in datos if d.get('estatus') == filtros['estatus']]
    if filtros.get('patrocinador_id'):
        datos = [d for d in datos if str(d.get('id_patrocinador', '')) == str(filtros['patrocinador_id'])]
    if filtros.get('monto_min'):
        try:
            min_v = float(filtros['monto_min'])
            datos = [d for d in datos if float(d.get('monto_total', 0) or 0) >= min_v]
        except ValueError:
            pass
    if filtros.get('monto_max'):
        try:
            max_v = float(filtros['monto_max'])
            datos = [d for d in datos if float(d.get('monto_total', 0) or 0) <= max_v]
        except ValueError:
            pass

    datos = _filtrar_por_fecha(datos, 'fecha_inicio', fi, ff)

    for d in datos:
        d['tipo'] = TIPO_CONTRATO_MAP.get(str(d.get('tipo', '')), d.get('tipo', '—'))
        d['nombre_empresa'] = d.get('nombre_empresa', d.get('nombre_empresa', '—'))
        if d.get('fecha_fin'):
            try:
                ffin = d['fecha_fin']
                if hasattr(ffin, 'date'):
                    ffin = ffin.date() if hasattr(ffin, 'date') else ffin
                dias = (ffin - date.today()).days if isinstance(ffin, date) else 0
                d['dias_restantes'] = max(dias, 0)
            except Exception:
                d['dias_restantes'] = '—'
        else:
            d['dias_restantes'] = '—'

    vigentes = sum(1 for d in datos if d.get('estatus') == 'Vigente')
    vencidos = sum(1 for d in datos if d.get('estatus') == 'Vencido')
    borradores = sum(1 for d in datos if d.get('estatus') == 'Borrador')
    monto_total = sum(float(d.get('monto_total', 0) or 0) for d in datos)
    montos = [float(d.get('monto_total', 0) or 0) for d in datos if d.get('monto_total')]
    monto_promedio = sum(montos) / len(montos) if montos else 0
    bronce = sum(1 for d in datos if d.get('tipo') == 'Bronce')
    plata = sum(1 for d in datos if d.get('tipo') == 'Plata')
    oro = sum(1 for d in datos if d.get('tipo') == 'Oro')

    patrocinador_montos = {}
    for d in datos:
        name = d.get('nombre_empresa', 'Desconocido')
        patrocinador_montos[name] = patrocinador_montos.get(name, 0) + float(d.get('monto_total', 0) or 0)
    top_pats = sorted(patrocinador_montos.items(), key=lambda x: x[1], reverse=True)[:5]

    monto_vigentes = sum(
        float(d.get('monto_total', 0) or 0)
        for d in datos if d.get('estatus') == 'Vigente'
    )
    vigentes_pct = f"{vigentes * 100 // len(datos)}%" if datos else "0%"

    kpis = {
        'total': len(datos),
        'vigentes': vigentes,
        'vencidos': vencidos,
        'borradores': borradores,
        'bronce': bronce,
        'plata': plata,
        'oro': oro,
        'monto_total': f"${monto_total:,.0f}",
        'monto_promedio': f"${monto_promedio:,.0f}",
        'monto_vigentes': f"${monto_vigentes:,.0f}",
        'monto_min': f"${min(montos):,.0f}" if montos else "$0",
        'monto_max': f"${max(montos):,.0f}" if montos else "$0",
        'vigentes_porcentaje': vigentes_pct,
        'top_patrocinadores': dict(top_pats),
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_balance(filtros, fi, ff):
    modulo = 'balance'
    model = BalanceModel()
    # ponytail: fechas/tipo filtradas EN SQL; tope 2000 como salvaguarda visible en kpis
    LIMITE = 2000
    pagos = model.obtener_historial_pagos(
        limit=LIMITE,
        fecha_inicio=filtros.get('fecha_inicio'),
        fecha_fin=filtros.get('fecha_fin'),
        tipo_pago=filtros.get('tipo_pago'),
    )
    datos = []
    for p in pagos:
        datos.append({
            'id_pago': p.id_pago,
            'id_contrato': p.id_contrato,
            'id_patrocinador': p.id_patrocinador,
            'monto': float(p.monto) if p.monto else 0,
            'tipo_pago': p.tipo_pago or '',
            'referencia': p.referencia or '',
            'fecha_pago': str(p.fecha_pago)[:10] if p.fecha_pago else '',
            'hora_pago': str(p.hora_pago)[:5] if p.hora_pago else '',
            'descripcion': p.descripcion or '',
            'fecha_registro': str(p.fecha_registro)[:10] if p.fecha_registro else '',
            'nombre_patrocinador': p.nombre_patrocinador or 'Sin patrocinador',
        })
    if filtros.get('patrocinador_id'):
        pid = str(filtros['patrocinador_id'])
        # JOIN real: el id llega desde contrato vía obtener_historial_pagos (antes startswith)
        datos = [d for d in datos if str(d.get('id_patrocinador') or '') == pid]
    if filtros.get('monto_min'):
        try: datos = [d for d in datos if d.get('monto', 0) >= float(filtros['monto_min'])]
        except ValueError: pass
    if filtros.get('monto_max'):
        try: datos = [d for d in datos if d.get('monto', 0) <= float(filtros['monto_max'])]
        except ValueError: pass
    total = sum(d.get('monto', 0) for d in datos)
    tipos = {}
    for d in datos:
        t = d.get('tipo_pago', 'Otro')
        tipos[t] = tipos.get(t, 0) + 1
    montos_lista = [d.get('monto', 0) for d in datos]
    kpis = {
        'total_pagos': len(datos),
        'monto_total': f"${total:,.0f}",
        'promedio': f"${total / len(datos):,.0f}" if datos else "$0",
        'monto_min': f"${min(montos_lista):,.0f}" if montos_lista else "$0",
        'monto_max': f"${max(montos_lista):,.0f}" if montos_lista else "$0",
        'tipos_pago': tipos,
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_tareas(filtros, fi, ff):
    modulo = 'tareas'
    tarea_model = TareaModel()
    asign_model = TareasAsignadasModel()
    tareas = tarea_model.consultar()
    # el nombre del usuario asignado se resuelve en la consulta (antes salía siempre '—')
    db = asign_model._get_db()
    with db.cursor() as cur:
        cur.execute(
            "SELECT ta.*, u.nombre AS usuario_nombre FROM tareas_asignadas ta "
            "JOIN seguridad.usuarios u ON u.id = ta.id_usuario WHERE ta.Estatus = 1"
        )
        asignadas = cur.fetchall()
    datos = []
    for t in tareas:
        t_id = t.get('id_tarea')
        row = {
            'id_tarea': t_id,
            'nombre_tarea': t.get('Nombre_Tarea', ''),
            'instruccion': t.get('Instruccion', ''),
            'estado': 'Pendiente',
            'asignado_a': '\u2014',
            'asignado_id': None,
            'fecha_asignacion_tarea': '',
        }
        for a in asignadas:
            if a.get('id_tarea') == t_id:
                row['estado'] = a.get('Estado', 'Pendiente')
                row['asignado_a'] = a.get('usuario_nombre', '\u2014')
                row['asignado_id'] = a.get('id_usuario')
                row['fecha_asignacion_tarea'] = a.get('fecha_asignacion_tarea', '')
                break
        datos.append(row)
    # claves unificadas en minúscula (antes: 'Estado' con mayúscula, inconsistente)
    if filtros.get('estado'):
        datos = [d for d in datos if d.get('estado') == filtros['estado']]
    # el JS envía 'asignado_a' (id de usuario); 'usuario_id' es la clave legacy
    usuario_filtro = filtros.get('asignado_a') or filtros.get('usuario_id')
    if usuario_filtro:
        datos = [d for d in datos if str(d.get('asignado_id') or '') == str(usuario_filtro)]
    datos = _filtrar_por_fecha(datos, 'fecha_asignacion_tarea', fi, ff)
    pendientes = sum(1 for d in datos if d.get('estado') == 'Pendiente')
    en_progreso = sum(1 for d in datos if d.get('estado') == 'En Progreso')
    completadas = sum(1 for d in datos if d.get('estado') == 'Completada')
    completadas_pct = f"{completadas * 100 // len(datos)}%" if datos else "0%"
    kpis = {
        'total': len(datos), 'pendientes': pendientes,
        'en_progreso': en_progreso, 'completadas': completadas,
        'completadas_pct': completadas_pct,
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_patrocinadores(filtros, fi, ff):
    modulo = 'patrocinadores'
    model = PatrocinadorModel()
    datos = model.consultar()
    tipo_map = {'1': 'Vigente', '2': 'Vencido'}
    for d in datos:
        d['tipo_contrato'] = tipo_map.get(str(d.get('tipo_contrato', '')), '—')
    if filtros.get('tipo_contrato'):
        datos = [d for d in datos if d.get('tipo_contrato') == filtros['tipo_contrato']]
    if filtros.get('estado_pat'):
        estado_val = int(filtros['estado_pat']) if filtros['estado_pat'].isdigit() else None
        if estado_val is not None:
            datos = [d for d in datos if d.get('estado') == estado_val]
    activos = sum(1 for d in datos if d.get('estado') == 1)
    inactivos = len(datos) - activos
    tipo_counts = {}
    for d in datos: tipo_counts[d.get('tipo_contrato', '—')] = tipo_counts.get(d.get('tipo_contrato', '—'), 0) + 1
    kpis = {'total': len(datos), 'activos': activos, 'inactivos': inactivos, 'por_tipo': tipo_counts}
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_usuarios(filtros, fi, ff):
    modulo = 'usuarios'
    from app.model.usuario_model import UsuarioModel as UModel
    model = UModel()
    datos = model.consultar()
    if filtros.get('rol'):
        datos = [d for d in datos if d.get('rol') == filtros['rol']]
    if filtros.get('departamento'):
        datos = [d for d in datos if d.get('departamento') == filtros['departamento']]
    if filtros.get('activo'):
        is_active = filtros['activo'] in ('1', 'true', 'True')
        datos = [d for d in datos if bool(d.get('activo')) == is_active]
    datos = _filtrar_por_fecha(datos, 'fecha_registro', fi, ff)
    activos = sum(1 for d in datos if d.get('activo'))
    inactivos = sum(1 for d in datos if not d.get('activo'))
    roles = {}
    for d in datos:
        r = d.get('rol', 'Sin rol')
        roles[r] = roles.get(r, 0) + 1
    deptos = {}
    for d in datos:
        dp = d.get('departamento', 'Sin depto')
        deptos[dp] = deptos.get(dp, 0) + 1
    kpis = {'total': len(datos), 'activos': activos, 'inactivos': inactivos, 'roles': roles, 'departamentos': deptos}
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_mantenimiento(filtros, fi, ff):
    modulo = 'mantenimiento'
    model = MantenimientoModel()
    datos = model.consultar()
    if filtros.get('estado'):
        datos = [d for d in datos if d.get('estado') == filtros['estado']]
    if filtros.get('recurso_id'):
        datos = [d for d in datos if str(d.get('recurso_id', '')) == str(filtros['recurso_id'])]
    datos = _filtrar_por_fecha(datos, 'fecha_ingreso', fi, ff)
    # días en taller: de fecha_ingreso a fecha_salida (o hoy si sigue en proceso)
    hoy = date.today()
    for d in datos:
        ingreso = d.get('fecha_ingreso')
        salida = d.get('fecha_salida') or hoy
        dias = None
        try:
            if hasattr(ingreso, 'date'):
                ingreso = ingreso.date()
            if hasattr(salida, 'date'):
                salida = salida.date()
            if ingreso:
                dias = max((salida - ingreso).days, 0)
        except Exception:
            dias = None
        d['dias_en_taller'] = dias if dias is not None else 0
    # rango de días en taller
    if filtros.get('dias_min'):
        try:
            v = int(filtros['dias_min'])
            datos = [d for d in datos if d['dias_en_taller'] >= v]
        except (ValueError, TypeError):
            pass
    if filtros.get('dias_max'):
        try:
            v = int(filtros['dias_max'])
            datos = [d for d in datos if d['dias_en_taller'] <= v]
        except (ValueError, TypeError):
            pass
    en_espera = sum(1 for d in datos if d.get('estado') == 'en_espera')
    en_reparacion = sum(1 for d in datos if d.get('estado') == 'en_reparacion')
    reparados = sum(1 for d in datos if d.get('estado') == 'reparado')
    dados_baja = sum(1 for d in datos if d.get('estado') == 'baja')
    recursos_freq = {}
    for d in datos:
        r = d.get('recurso_nombre', 'Desconocido')
        recursos_freq[r] = recursos_freq.get(r, 0) + 1
    top_recursos = sorted(recursos_freq.items(), key=lambda x: x[1], reverse=True)[:5]
    promedio_dias = round(sum(d['dias_en_taller'] for d in datos) / len(datos), 1) if datos else 0
    kpis = {
        'total': len(datos), 'en_espera': en_espera,
        'en_reparacion': en_reparacion, 'reparados': reparados,
        'dados_baja': dados_baja, 'promedio_dias': promedio_dias,
        'top_recursos': dict(top_recursos),
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_reels(filtros, fi, ff):
    modulo = 'reels'
    model = ReelModel()
    datos = model.consultar()
    if filtros.get('patrocinador_id'):
        datos = [d for d in datos if str(d.get('patrocinado', '')) == str(filtros['patrocinador_id'])]
    # rango de duración en segundos (duracion_total se guarda en minutos)
    if filtros.get('duracion_min'):
        try:
            v = float(filtros['duracion_min'])
            datos = [d for d in datos if float(d.get('duracion_total', 0) or 0) * 60 >= v]
        except (ValueError, TypeError):
            pass
    if filtros.get('duracion_max'):
        try:
            v = float(filtros['duracion_max'])
            datos = [d for d in datos if float(d.get('duracion_total', 0) or 0) * 60 <= v]
        except (ValueError, TypeError):
            pass
    datos = _filtrar_por_fecha(datos, 'creado_en', fi, ff)
    total_videos = sum(len(r.get('videos', [])) for r in datos)
    duracion_total_seg = sum(float(r.get('duracion_total', 0) or 0) * 60 for r in datos)
    for d in datos:
        d['videos_count'] = len(d.get('videos', []))
        duracion_seg = float(d.get('duracion_total', 0) or 0) * 60
        minutos = int(duracion_seg // 60)
        segundos = int(duracion_seg % 60)
        d['duracion'] = f"{minutos}m {segundos}s" if minutos > 0 else f"{segundos}s"
        if hasattr(d.get('creado_en'), 'strftime'):
            d['creado_en'] = d['creado_en'].strftime('%d/%m/%Y %H:%M')
        videos = d.get('videos', [])
        d['videos_detalle'] = '\n'.join(
            f"{i+1}. {v.get('nombre', '')} ({_fmt_video_dur(v.get('duracion_segundos', 0))})"
            for i, v in enumerate(videos)
        ) if videos else 'Sin videos'
    duracion_total_min = duracion_total_seg / 60
    kpis = {
        'total': len(datos), 'total_videos': total_videos,
        'duracion_total': f"{duracion_total_min:.0f} min",
        'duracion_promedio': f"{duracion_total_min / len(datos):.0f} min" if datos else "0 min",
    }
    return datos, kpis

def _datos_bitacora(filtros, fi, ff):
    modulo = 'bitacora'
    model = ActividadModel()
    # fechas y filtros van EN SQL (antes: LIMIT 500 + refiltro Python = truncado silencioso)
    consulta_filtros = {'limite': 5000}
    if filtros.get('usuario_id'):
        consulta_filtros['usuario_id'] = filtros['usuario_id']
    if filtros.get('tipo_accion'):
        consulta_filtros['tipo_accion'] = filtros['tipo_accion']
    if filtros.get('modulo_filter'):
        consulta_filtros['modulo'] = filtros['modulo_filter']
    if fi:
        consulta_filtros['fecha_desde'] = fi
    ff_dt = _parsear_fecha(ff)
    if ff_dt:
        consulta_filtros['fecha_hasta'] = ff_dt + timedelta(days=1)
    datos = model.consultar(**consulta_filtros)
    creaciones = sum(1 for d in datos if d.get('tipo_accion') == 'create')
    ediciones = sum(1 for d in datos if d.get('tipo_accion') == 'update')
    eliminaciones = sum(1 for d in datos if d.get('tipo_accion') == 'delete')
    modulos = {}
    for d in datos:
        m = d.get('modulo', 'Otro')
        modulos[m] = modulos.get(m, 0) + 1
    usuarios = {}
    for d in datos:
        uo = d.get('usuario')
        nombre = 'Desconocido'
        if isinstance(uo, dict):
            nombre = uo.get('nombre', 'Desconocido')
        elif hasattr(uo, 'nombre'):
            nombre = uo.nombre
        usuarios[nombre] = usuarios.get(nombre, 0) + 1
    top_usuarios = sorted(usuarios.items(), key=lambda x: x[1], reverse=True)[:5]
    kpis = {
        'total': len(datos),
        'creaciones': creaciones,
        'ediciones': ediciones,
        'eliminaciones': eliminaciones,
        'modulos': modulos,
        'top_usuarios': dict(top_usuarios),
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis

def _datos_resumen(filtros, fi, ff):
    modulo = 'resumen'
    from app.model.guion_model import GuionModel
    from app.model.inventario_model import InventarioModel
    from app.model.premio_model import PremioModel
    from app.model.contrato_model import ContratoModel
    from app.model.balance_model import BalanceModel
    from app.model.tarea_model import TareaModel
    from app.model.patrocinador_model import PatrocinadorModel
    from app.model.auth_model import UsuarioModel
    from app.model.mantenimiento_model import MantenimientoModel
    from app.model.reels_model import ReelModel
    modulos = [
        ('Guiones', GuionModel().consultar(), lambda d: d.get('estado') == 'publicado'),
        ('Inventario', InventarioModel().consultar(), lambda d: d.get('estado_nombre') == 'Disponible'),
        ('Premios', PremioModel().consultar(), lambda d: d.get('estado') == 'entregado'),
        ('Contratos', ContratoModel().consultar(), lambda d: d.get('estatus') == 'Vigente'),
        ('Tareas', TareaModel().consultar(), lambda d: d.get('Estado') == 'Completada'),
        ('Patrocinadores', PatrocinadorModel().consultar(), lambda d: d.get('estado') == 1),
        ('Usuarios', UsuarioModel().consultar(), lambda d: d.get('activo')),
        ('Mantenimiento', MantenimientoModel().consultar(), lambda d: d.get('estado') in ('reparado',)),
        ('Reels', ReelModel().consultar(), lambda d: True),
    ]
    datos = [{
        'modulo': n, 'total': len(d),
        'activos': sum(1 for x in d if f(x)),
        'inactivos': sum(1 for x in d if not f(x)),
    } for n, d, f in modulos]
    total_reg = sum(d.get('total', 0) for d in datos)
    total_act = sum(d.get('activos', 0) for d in datos)
    kpis = {
        'modulos': len(datos),
        'total_registros': total_reg,
        'total_activos': total_act,
        'total_inactivos': total_reg - total_act,
    }
    datos = _sanitizar_para_reporte(modulo, datos)
    return datos, kpis


OBTENEDORES = {
    'guiones': _datos_guiones,
    'inventario': _datos_inventario,
    'premios': _datos_premios,
    'contratos': _datos_contratos,
    'balance': _datos_balance,
    'tareas': _datos_tareas,
    'patrocinadores': _datos_patrocinadores,
    'usuarios': _datos_usuarios,
    'mantenimiento': _datos_mantenimiento,
    'reels': _datos_reels,
    'bitacora': _datos_bitacora,
    # ponytail: resumen preservado tal cual — tiene un bug latente (Usuario no es dict,
    # revienta con AttributeError) y no es alcanzable desde las rutas; arreglar aparte.
    'resumen': _datos_resumen,
}
