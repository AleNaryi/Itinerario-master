import json
from datetime import date, datetime
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import EN_VIVO
from app import socketio
from app.model.guion_model import GuionModel
from app.model.en_vivo_model import EnVivoModel, SincronizacionModel

bp = Blueprint('en_vivo', __name__, url_prefix='/en-vivo')

INNING_NAMES = {1: '1ro', 2: '2do', 3: '3ro', 4: '4to',
                5: '5to', 6: '6to', 7: '7mo', 8: '8vo', 9: '9no'}

VALID_ESTADOS_ELEMENTO = {'pendiente', 'en_curso', 'completado', 'reiniciado', None}

bp.before_request(verificar_acceso(EN_VIVO))


def _ms(valor):
    """Datetime naive del servidor -> epoch ms para el frontend (None-safe)."""
    if not valor:
        return None
    if isinstance(valor, datetime):
        return int(valor.timestamp() * 1000)
    return None


def _estados_para_cliente(guion_id):
    """Estados actuales + reloj del servidor: fuente única de verdad temporal."""
    return {
        'guion_id': guion_id,
        'servidor_ahora': _ms(datetime.now()),
        'estados': [
            {
                'id': r['id'],
                'estado': r['estado'],
                'inicio_curso': _ms(r.get('inicio_curso')),
            }
            for r in EnVivoModel().obtener_estado_actual(guion_id)
        ],
    }


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('envivo', tipo, accion, detalle)


def _fmt12(hora, duracion_segundos):
    ts = int(hora.total_seconds())
    h = ts // 3600
    m = (ts % 3600) // 60
    ampm = 'AM' if h < 12 else 'PM'
    h12 = h % 12 or 12
    total_min = h * 60 + m + (duracion_segundos // 60)
    eh = (total_min // 60) % 24
    em = total_min % 60
    eampm = 'AM' if eh < 12 else 'PM'
    eh12 = eh % 12 or 12
    return f"{h12}:{m:02d} {ampm} - {eh12}:{em:02d} {eampm}"


def _fmt_pregame(e):
    return {
        'id': e['id'], 'estado': e['estado'],
        'hora': _fmt12(e['hora'], e['duracion_estimada']),
        'contenido': e['contenido'],
        'duracion': e['duracion_estimada'],
        'encargado': e['encargado'],
        'inicio_curso_ms': _ms(e.get('inicio_curso')),
    }


def _fmt_game(e):
    return {
        'id': e['id'], 'estado': e['estado'],
        'hora': f"{INNING_NAMES.get(e['inning'], e['inning'])}° {e['medio_inning'].capitalize()}",
        'contenido': e['contenido'],
        'duracion': e['duracion_estimada'],
        'encargado': e['encargado'],
        'inicio_curso_ms': _ms(e.get('inicio_curso')),
    }


@bp.route('/')
def index():
    envivo_model = EnVivoModel()
    guiones = envivo_model.consultar_guiones_disponibles()
    hay_en_vivo = any(g['estado'] == 'en_vivo' for g in guiones)
    return render_template('en_vivo/index.html', guiones=guiones, hay_en_vivo=hay_en_vivo)


@bp.route('/<int:guion_id>')
def ver(guion_id):
    envivo_model = EnVivoModel()
    guion_model = GuionModel()
    guion = guion_model.obtener_por_id(guion_id)
    if not guion or guion['estado'] != 'en_vivo':
        flash('Este guion no está en vivo. Inícialo primero.', 'warning')
        return redirect(url_for('en_vivo.index'))
    fechas, pregame_raw, game_raw = envivo_model.obtener_elementos_en_vivo(guion_id)
    pregame_data = [_fmt_pregame(e) for e in pregame_raw]
    game_data = [_fmt_game(e) for e in game_raw]
    return render_template('en_vivo/vivo.html', guion=guion, fechas=fechas,
                           pregame=pregame_data, game=game_data,
                           inicio_show_ms=_ms(guion.get('inicio_show')),
                           servidor_ahora_ms=_ms(datetime.now()))


@bp.route('/iniciar/<int:guion_id>')
def iniciar(guion_id):
    envivo_model = EnVivoModel()
    sinc_model = SincronizacionModel()
    if not envivo_model.iniciar(guion_id):
        flash('Ya hay un guion en vivo. Finalízalo primero.', 'warning')
        return redirect(url_for('en_vivo.index'))
    guion = GuionModel().obtener_por_id(guion_id)
    sinc_model.registrar(guion_id, current_user.id, 'iniciar', 'Iniciado')
    _registrar_bitacora('update', 'Iniciar guion en vivo', f'Guión "{guion["nombre"]}" iniciado en vivo')
    flash('Guion iniciado en vivo!', 'success')
    return redirect(url_for('en_vivo.ver', guion_id=guion_id))


@bp.route('/finalizar/<int:guion_id>')
def finalizar(guion_id):
    envivo_model = EnVivoModel()
    sinc_model = SincronizacionModel()
    guion = GuionModel().obtener_por_id(guion_id)
    envivo_model.finalizar(guion_id)
    sinc_model.registrar(guion_id, current_user.id, 'finalizar', 'Finalizado')
    _registrar_bitacora('update', 'Finalizar guion en vivo', f'Guión "{guion["nombre"]}" finalizado')
    flash('Guion finalizado', 'info')
    return redirect(url_for('en_vivo.index'))


@bp.route('/api/sincronizar/<int:guion_id>', methods=['POST'])
def sincronizar(guion_id):
    envivo_model = EnVivoModel()
    sinc_model = SincronizacionModel()
    guion = GuionModel().obtener_por_id(guion_id)
    data = request.get_json()
    estados = data.get('estados', [])
    estados_validos = []
    for e in estados:
        estado_val = e.get('estado')
        if estado_val in VALID_ESTADOS_ELEMENTO and 'id' in e:
            # fix bug: sin `accion` el log de sincronizaciones nunca registraba marcajes
            estados_validos.append({'id': int(e['id']), 'estado': estado_val, 'accion': e.get('accion')})
    descs = envivo_model.sincronizar_estados(guion_id, estados_validos)
    for desc in descs:
        sinc_model.registrar(guion_id, current_user.id, 'sincronizar', desc)
    _registrar_bitacora('update', 'Sincronizar elementos', f'Guión "{guion["nombre"]}": {len(descs)} elemento(s) sincronizado(s)')
    # broadcast con la verdad completa del servidor (estados + relojes)
    socketio.emit('actualizar_estados', _estados_para_cliente(guion_id))
    return jsonify({'success': True})


@bp.route('/log/<int:guion_id>')
def ver_log(guion_id):
    guion_model = GuionModel()
    sinc_model = SincronizacionModel()
    guion = guion_model.obtener_por_id(guion_id)
    if not guion:
        flash('Guión no encontrado', 'danger')
        return redirect(url_for('en_vivo.index'))
    filtro = request.args.get('filtro', 'todos')
    registros = sinc_model.consultar(guion_id, filtro=filtro)
    return render_template('en_vivo/log.html', guion=guion, registros=registros, filtro_activo=filtro)


@bp.route('/api/estado-actual/<int:guion_id>')
def estado_actual(guion_id):
    return jsonify(_estados_para_cliente(guion_id))


@bp.route('/api/guiones-por-fecha', methods=['POST'])
def guiones_por_fecha():
    envivo_model = EnVivoModel()
    data = request.get_json()
    fecha_str = data.get('fecha')
    if not fecha_str:
        return jsonify({'guiones': []})
    try:
        fecha = date.fromisoformat(fecha_str)
    except ValueError:
        return jsonify({'guiones': []})
    result = envivo_model.guiones_por_fecha(fecha)
    return jsonify({'guiones': result})
