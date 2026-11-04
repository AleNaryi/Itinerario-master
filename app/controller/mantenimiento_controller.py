import json
from datetime import date
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import MANTENIMIENTO
from app.model.mantenimiento_model import (RecursoModel, MantenimientoModel,
                                            HistorialMantenimientoModel)

bp = Blueprint('mantenimiento', __name__, url_prefix='/mantenimiento')

ESTADOS_RECURSO = {1: 'Disponible', 2: 'Asignado', 3: 'En Mantenimiento', 4: 'Dañado', 5: 'Baja'}

bp.before_request(verificar_acceso(MANTENIMIENTO))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('mantenimiento', tipo, accion, detalle)


@bp.route('/')
def dashboard():
    recurso_model = RecursoModel()
    manto_model = MantenimientoModel()
    recursos = recurso_model.consultar()
    mantenimientos = manto_model.consultar()
    mantos_por_recurso = {}
    for m in mantenimientos:
        mantos_por_recurso.setdefault(m['recurso_id'], []).append(m)
    for r in recursos:
        r['mantenimientos'] = mantos_por_recurso.get(r['id'], [])
    total = recurso_model.contar()
    en_mantenimiento = recurso_model.contar(estado_id=3)
    de_baja = recurso_model.contar(estado_id=5)
    return render_template('mantenimiento/dashboard.html',
                           recursos=recursos, total=total,
                           en_mantenimiento=en_mantenimiento,
                           de_baja=de_baja,
                           estados=ESTADOS_RECURSO)


@bp.route('/ingresar/<int:recurso_id>', methods=['GET', 'POST'])
def ingresar(recurso_id):
    recurso_model = RecursoModel()
    manto_model = MantenimientoModel()
    historial_model = HistorialMantenimientoModel()
    recurso = recurso_model.obtener_por_id(recurso_id)
    if not recurso:
        flash('Recurso no encontrado', 'danger')
        return redirect(url_for('mantenimiento.dashboard'))
    if recurso['estado_id'] != 1:
        flash(f'El recurso "{recurso["nombre"]}" no está disponible para mantenimiento', 'warning')
        return redirect(url_for('mantenimiento.dashboard'))
    if request.method == 'POST':
        fecha_ingreso = request.form.get('fecha_ingreso', '').strip()
        diagnostico = request.form.get('diagnostico', '').strip()
        observaciones = request.form.get('observaciones', '').strip()
        manto_model.set_recurso_id(recurso['id'])
        manto_model.set_usuario_id(current_user.id)
        manto_model.set_fecha_ingreso(fecha_ingreso)
        manto_model.set_diagnostico(diagnostico)
        manto_model.set_observaciones(observaciones)
        manto = manto_model.confirmar_registro()
        if not manto:
            flash('Error al registrar mantenimiento', 'danger')
            return render_template('mantenimiento/ingresar.html', recurso=recurso)
        recurso_model.modificar(recurso['id'], {'estado_id': 3})
        historial_model.registrar({
            'mantenimiento_id': manto['id'],
            'usuario_id': current_user.id,
            'accion': 'ingreso',
            'descripcion': f'Ingreso a mantenimiento. Diagnóstico: {diagnostico}',
        })
        _registrar_bitacora('create', 'Ingresar a mantenimiento',
                              f'Recurso "{recurso["nombre"]}" ingresado a mantenimiento')
        flash(f'Recurso "{recurso["nombre"]}" ingresado a mantenimiento', 'success')
        return redirect(url_for('mantenimiento.ver', id=manto['id']))
    return render_template('mantenimiento/ingresar.html', recurso=recurso)


@bp.route('/ver/<int:id>')
def ver(id):
    manto_model = MantenimientoModel()
    mantenimiento = manto_model.obtener_por_id(id)
    if not mantenimiento:
        flash('Mantenimiento no encontrado', 'danger')
        return redirect(url_for('mantenimiento.dashboard'))
    return render_template('mantenimiento/detalle.html',
                           mantenimiento=mantenimiento,
                           recurso=mantenimiento['recurso'],
                           historial=mantenimiento['historial'],
                           estados=ESTADOS_RECURSO)


@bp.route('/agregar-nota/<int:id>', methods=['POST'])
def agregar_nota(id):
    manto_model = MantenimientoModel()
    historial_model = HistorialMantenimientoModel()
    mantenimiento = manto_model.obtener_por_id(id)
    if not mantenimiento:
        flash('Mantenimiento no encontrado', 'danger')
        return redirect(url_for('mantenimiento.dashboard'))
    descripcion = request.form.get('descripcion', '').strip()
    if not descripcion:
        flash('La descripción de la nota es obligatoria', 'warning')
        return redirect(url_for('mantenimiento.ver', id=id))
    if len(descripcion) > 500:
        flash('La nota no puede exceder 500 caracteres', 'warning')
        return redirect(url_for('mantenimiento.ver', id=id))
    historial_model.registrar({
        'mantenimiento_id': mantenimiento['id'],
        'usuario_id': current_user.id,
        'accion': 'nota',
        'descripcion': descripcion,
    })
    _registrar_bitacora('update', 'Agregar nota',
                          f'Nota a mantenimiento de "{mantenimiento["recurso"]["nombre"]}": {descripcion[:80]}')
    flash('Nota agregada al seguimiento', 'success')
    return redirect(url_for('mantenimiento.ver', id=mantenimiento['id']))


@bp.route('/reparar/<int:id>', methods=['POST'])
def reparar(id):
    manto_model = MantenimientoModel()
    recurso_model = RecursoModel()
    historial_model = HistorialMantenimientoModel()
    manto = manto_model.obtener_por_id(id)
    if not manto:
        flash('Mantenimiento no encontrado', 'danger')
        return redirect(url_for('mantenimiento.dashboard'))
    if manto['estado'] == 'en_espera':
        manto_model.modificar(id, {'estado': 'en_reparacion'})
        accion = 'reparar'
        descripcion = 'Se inició el proceso de reparación.'
    elif manto['estado'] == 'en_reparacion':
        manto_model.modificar(id, {'estado': 'reparado'})
        recurso_model.modificar(manto['recurso_id'], {'estado_id': 1})
        accion = 'reparar'
        descripcion = 'Recurso reparado exitosamente.'
    else:
        flash('No se puede cambiar el estado actual', 'warning')
        return redirect(url_for('mantenimiento.ver', id=id))
    historial_model.registrar({
        'mantenimiento_id': id,
        'usuario_id': current_user.id,
        'accion': accion,
        'descripcion': descripcion,
    })
    _registrar_bitacora('update', 'Reparar recurso',
                          f'Mantenimiento de "{manto["recurso"]["nombre"]}": {descripcion}')
    return redirect(url_for('mantenimiento.ver', id=id))


@bp.route('/dar-baja/<int:id>', methods=['POST'])
def dar_baja(id):
    manto_model = MantenimientoModel()
    recurso_model = RecursoModel()
    historial_model = HistorialMantenimientoModel()
    manto = manto_model.obtener_por_id(id)
    if not manto:
        flash('Mantenimiento no encontrado', 'danger')
        return redirect(url_for('mantenimiento.dashboard'))
    if manto['estado'] not in ['en_espera', 'en_reparacion']:
        flash('No se puede dar de baja este mantenimiento', 'warning')
        return redirect(url_for('mantenimiento.ver', id=id))
    manto_model.modificar(id, {'estado': 'baja'})
    recurso_model.modificar(manto['recurso_id'], {'estado_id': 5})
    historial_model.registrar({
        'mantenimiento_id': id,
        'usuario_id': current_user.id,
        'accion': 'baja',
        'descripcion': 'Recurso dado de baja del inventario.',
    })
    _registrar_bitacora('delete', 'Dar de baja',
                          f'Recurso "{manto["recurso"]["nombre"] if manto["recurso"] else ""}" dado de baja')
    return redirect(url_for('mantenimiento.ver', id=id))


@bp.route('/finalizar/<int:id>', methods=['POST'])
def finalizar(id):
    manto_model = MantenimientoModel()
    historial_model = HistorialMantenimientoModel()
    manto = manto_model.obtener_por_id(id)
    if not manto:
        flash('Mantenimiento no encontrado', 'danger')
        return redirect(url_for('mantenimiento.dashboard'))
    manto_model.modificar(id, {'estado': 'finalizado', 'fecha_salida': date.today()})
    historial_model.registrar({
        'mantenimiento_id': id,
        'usuario_id': current_user.id,
        'accion': 'finalizar',
        'descripcion': 'Mantenimiento finalizado.',
    })
    _registrar_bitacora('update', 'Finalizar mantenimiento',
                          f'Mantenimiento de "{manto["recurso"]["nombre"]}" finalizado')
    return redirect(url_for('mantenimiento.ver', id=id))
