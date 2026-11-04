"""Helpers puros del sistema de reportes (sin acceso a BD ni a Flask).

Extraídos de reportes_controller.py en la Fase 3; cubiertos por
tests/test_reportes_helpers.py.
"""
from datetime import datetime, timedelta


def _parsear_fecha(fecha_str):
    if not fecha_str:
        return None
    for fmt in ('%Y-%m-%d', '%d/%m/%Y'):
        try:
            return datetime.strptime(fecha_str, fmt)
        except ValueError:
            continue
    return None


def _formatear_tiempo(segundos):
    if not segundos or segundos <= 0:
        return '0m'
    h = int(segundos) // 3600
    m = (int(segundos) % 3600) // 60
    if h > 0:
        return f'{h}h {m}m' if m > 0 else f'{h}h'
    return f'{m}m'


def _filtrar_por_fecha(datos, campo_fecha, fecha_inicio, fecha_fin):
    if not fecha_inicio and not fecha_fin:
        return datos
    resultado = []
    fi = _parsear_fecha(fecha_inicio)
    ff = _parsear_fecha(fecha_fin)
    if ff:
        ff = ff + timedelta(days=1)
    for d in datos:
        val = d.get(campo_fecha)
        if not val:
            resultado.append(d)
            continue
        try:
            if hasattr(val, 'date'):
                fecha = val
            else:
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y'):
                    try:
                        fecha = datetime.strptime(str(val)[:10], fmt)
                        break
                    except ValueError:
                        continue
                else:
                    resultado.append(d)
                    continue
            if fi and fecha < fi:
                continue
            if ff and fecha >= ff:
                continue
            resultado.append(d)
        except Exception:
            resultado.append(d)
    return resultado


CAMPOS_FECHA = {
    'guiones': 'creado_en', 'inventario': 'fecha_compra',
    'premios': 'fecha_creacion', 'contratos': 'fecha_inicio',
    'balance': 'fecha_pago', 'tareas': 'fecha_asignacion_tarea',
    'patrocinadores': 'fecha_registro', 'mantenimiento': 'fecha_ingreso',
    'reels': 'creado_en', 'bitacora': 'created_at',
}


def _encontrar_fecha_minima(datos, campo_fecha):
    minima = None
    for d in datos:
        val = d.get(campo_fecha)
        if not val:
            continue
        try:
            if hasattr(val, 'date'):
                fecha = val
            else:
                for fmt in ('%Y-%m-%d %H:%M:%S', '%Y-%m-%d', '%d/%m/%Y'):
                    try:
                        fecha = datetime.strptime(str(val)[:10], fmt)
                        break
                    except ValueError:
                        continue
                else:
                    continue
            if minima is None or fecha < minima:
                minima = fecha
        except Exception:
            continue
    return minima.strftime('%Y-%m-%d') if minima else None


def _ordenar_datos(datos, campo, direccion='asc'):
    if not campo or not datos:
        return datos
    reverse = direccion == 'desc'

    def _clave(d):
        val = d.get(campo)
        if isinstance(val, (int, float)) and not isinstance(val, bool):
            return (0, float(val), '')
        s = str(val if val is not None else '').strip().lower()
        try:
            # montos formateados ('$12,000'), porcentajes y números como texto ordenan numérico
            return (0, float(s.replace('$', '').replace(',', '').replace('%', '')), '')
        except ValueError:
            return (1, 0.0, s)

    return sorted(datos, key=_clave, reverse=reverse)


def _fmt_video_dur(segundos):
    seg = int(segundos or 0)
    m, s = divmod(seg, 60)
    return f"{m}m {s}s" if m > 0 else f"{s}s"
