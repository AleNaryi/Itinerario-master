from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import BITACORA
from app.model.bitacora_model import SesionModel, ActividadModel, CambioModel
from app.model.auth_model import UsuarioModel
from datetime import datetime

bp = Blueprint('bitacora', __name__, url_prefix='/bitacora')

bp.before_request(verificar_acceso(BITACORA))


@bp.route('/', methods=['GET'], endpoint='dashboard')
def dashboard():
    sesion_model = SesionModel()
    actividad_model = ActividadModel()
    usuario_model = UsuarioModel()
    sesiones = sesion_model.consultar()
    actividades = actividad_model.consultar()
    usuarios = usuario_model.consultar()
    sesiones_activas = [s for s in sesiones if s['fin_sesion'] is None]
    return render_template('bitacora/dashboard.html',
                           total_sesiones=len(sesiones),
                           sesiones_activas=len(sesiones_activas),
                           total_actividades=len(actividades),
                           actividades_recientes=actividades[:20],
                           usuarios=usuarios)


@bp.route('/usuario/<int:usuario_id>', methods=['GET'], endpoint='reporte_usuario')
def reporte_usuario(usuario_id):
    sesion_model = SesionModel()
    actividad_model = ActividadModel()
    cambio_model = CambioModel()
    usuario_model = UsuarioModel()
    usuario = usuario_model.obtener_por_id(usuario_id)
    if not usuario:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('bitacora.dashboard'))

    fecha_desde = request.args.get('fecha_desde')
    fecha_hasta = request.args.get('fecha_hasta')
    modulo = request.args.get('modulo')
    tipo_accion = request.args.get('tipo_accion')

    if fecha_desde:
        try:
            fecha_desde = datetime.strptime(fecha_desde, '%Y-%m-%d')
        except ValueError:
            fecha_desde = None
    if fecha_hasta:
        try:
            fecha_hasta = datetime.strptime(fecha_hasta, '%Y-%m-%d').replace(hour=23, minute=59, second=59)
        except ValueError:
            fecha_hasta = None

    sesiones = sesion_model.consultar(usuario_id=usuario_id)
    total_sesiones = len(sesiones)
    sesion_activa = next((s for s in sesiones if s['fin_sesion'] is None), None)

    filtros = {'usuario_id': usuario_id}
    if fecha_desde:
        filtros['fecha_desde'] = fecha_desde
    if fecha_hasta:
        filtros['fecha_hasta'] = fecha_hasta
    if modulo:
        filtros['modulo'] = modulo
    if tipo_accion:
        filtros['tipo_accion'] = tipo_accion
    actividades = actividad_model.consultar(**filtros)

    tiempo_por_modulo = {}
    actividades_por_modulo = sorted(actividades, key=lambda a: a.get('created_at') or datetime.min)
    for a in actividades_por_modulo:
        mod = a.get('modulo') or 'otros'
        if mod not in tiempo_por_modulo:
            tiempo_por_modulo[mod] = {
                'modulo': mod, 'cantidad': 0,
                'inicio': a.get('created_at'), 'fin': a.get('created_at'), 'tipos': set(),
            }
        t = tiempo_por_modulo[mod]
        t['cantidad'] += 1
        t['tipos'].add(a['tipo_accion'])
        if a.get('created_at'):
            if not t['inicio'] or a['created_at'] < t['inicio']:
                t['inicio'] = a['created_at']
            if not t['fin'] or a['created_at'] > t['fin']:
                t['fin'] = a['created_at']

    for mod, t in tiempo_por_modulo.items():
        if t['inicio'] and t['fin'] and t['inicio'] != t['fin']:
            t['tiempo_estimado'] = (t['fin'] - t['inicio']).total_seconds()
        else:
            t['tiempo_estimado'] = 0
        t['tipos'] = sorted(t['tipos'])

    actividad_ids = [a['id'] for a in actividades]
    cambios = cambio_model.consultar(actividad_ids=actividad_ids) if actividad_ids else []
    modulos_disponibles = actividad_model.obtener_modulos_distintos()
    usuarios = usuario_model.consultar()

    return render_template('bitacora/usuario.html',
                           usuario=usuario,
                           total_sesiones=total_sesiones,
                           sesion_activa=sesion_activa,
                           sesiones=sesiones[:20],
                           actividades=actividades[:50],
                           total_actividades=len(actividades),
                           tiempo_por_modulo=sorted(tiempo_por_modulo.values(),
                                                    key=lambda x: x['tiempo_estimado'], reverse=True),
                           cambios=cambios[:30],
                           total_cambios=len(cambios),
                           modulos_disponibles=modulos_disponibles,
                           usuarios=usuarios,
                           filtros={
                               'fecha_desde': fecha_desde,
                               'fecha_hasta': fecha_hasta,
                               'modulo': modulo,
                               'tipo_accion': tipo_accion,
                           })
