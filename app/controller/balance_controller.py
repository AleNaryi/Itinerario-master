import json
import logging
import io
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, make_response
from flask_login import current_user
from app.model.balance_model import Pago as BalanceModel
from app.model.bitacora_model import ActividadModel
from app.helpers.decorators import permiso_requerido
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from app.helpers.balance_report import generar_pdf_estado_cuenta

logger = logging.getLogger(__name__)

bp = Blueprint('balance', __name__, url_prefix='/balance')

balance_model = BalanceModel()


def _bitacora(tipo, accion, detalle):
    try:
        ActividadModel().registrar({
            'usuario_id': current_user.id,
            'tipo_accion': tipo,
            'modulo': 'pagos',
            'accion': accion,
            'detalle': json.dumps({'detalle': detalle}),
            'pagina': request.path,
            'ip_address': request.remote_addr,
        })
    except Exception:
        logger.exception('Error no controlado')

@bp.route('/', methods=['GET'])
@permiso_requerido('balance.view')
def dashboard():
    contratos_raw = balance_model.obtener_contratos_activos()
    todos_pagos = balance_model.obtener_historial_pagos(1000)
    total_pagado = balance_model.get_total_pagado_general()
    top_contratos = balance_model.obtener_top_contratos()
    pagos_recientes = balance_model.obtener_historial_pagos(5)

    contratos_procesados = []
    saldo_pendiente_general = 0.0

    for contrato in contratos_raw:
        id_c = contrato['id_contrato']
        monto_pagado_contrato = balance_model.get_total_pagado_by_contrato(id_c) or 0.0
        monto_total_contrato = float(contrato['monto_total']) if contrato['monto_total'] else 0.0
        calc_saldo_pendiente = monto_total_contrato - monto_pagado_contrato

        if calc_saldo_pendiente > 0:
            saldo_pendiente_general += calc_saldo_pendiente

        pagos_del_contrato = [p for p in todos_pagos if p.id_contrato == id_c]
        ultimo_pago = pagos_del_contrato[0] if pagos_del_contrato else None

        contratos_procesados.append({
            'id_contrato': id_c,
            'nombre_patrocinador': contrato.get('nombre_patrocinador', 'Sin patrocinador'),
            'monto_total': monto_total_contrato,
            'saldo_pendiente': calc_saldo_pendiente,
            'ultimo_pago_monto': float(ultimo_pago.monto) if ultimo_pago else None,
            'ultimo_pago_fecha': ultimo_pago.fecha_pago if ultimo_pago else None,
        })

    return render_template('balance/dashboard.html',
                           total_contratos=len(contratos_procesados),
                           total_pagado=total_pagado if total_pagado else 0.0,
                           saldo_pendiente=saldo_pendiente_general,
                           contratos_activos=len(contratos_procesados),
                           pagos_recientes=pagos_recientes,
                           todos_pagos=todos_pagos,
                           top_contratos=top_contratos,
                           contratos_activos_lista=contratos_procesados,
                           now=datetime.now())




@bp.route('/registrar-pago', methods=['POST'])
@permiso_requerido('balance.create')
def registrar_pago():
    id_contrato = request.form.get('id_contrato')
    monto = request.form.get('monto')
    tipo_pago = request.form.get('tipo_pago')
    referencia = request.form.get('referencia')
    fecha_pago = request.form.get('fecha_pago')
    hora_pago = request.form.get('hora_pago')
    notas = request.form.get('descripcion')

    if not id_contrato or not str(id_contrato).isdigit() or not monto or not tipo_pago:
        flash('Todos los campos obligatorios deben ser llenados', 'danger')
        return redirect(url_for('balance.dashboard'))

    try:
        monto = float(monto)
        if monto <= 0:
            flash('El monto debe ser mayor a cero', 'danger')
            return redirect(url_for('balance.dashboard'))
    except ValueError:
        flash('Monto inválido', 'danger')
        return redirect(url_for('balance.dashboard'))

    try:
        fecha_pago_dt = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
        hora_pago_dt = datetime.strptime(hora_pago, '%H:%M').time()
    except (ValueError, TypeError):
        flash('Fecha u hora de pago inválida', 'danger')
        return redirect(url_for('balance.dashboard'))

    contrato = balance_model.obtener_contrato_por_id(int(id_contrato))
    if not contrato:
        flash('Contrato no encontrado', 'danger')
        return redirect(url_for('balance.dashboard'))

    total_pagado = balance_model.get_total_pagado_by_contrato(int(id_contrato))
    saldo_actual = float(contrato['monto_total']) - total_pagado

    if monto > saldo_actual:
        flash(f'El monto excede el saldo pendiente (${saldo_actual:.2f})', 'danger')
        return redirect(url_for('balance.dashboard'))

    datos_pago = {
        'id_contrato': int(id_contrato),
        'monto': monto,
        'tipo_pago': tipo_pago,
        'referencia': referencia,
        'fecha_pago': fecha_pago_dt,
        'hora_pago': hora_pago_dt,
        'descripcion': notas,
        'registrado_por': current_user.id,
    }

    balance_model.registrar_pago(datos_pago)
    _bitacora('create', 'Registrar pago', f'Pago ${monto:.2f} registrado en contrato #{id_contrato}')
    flash(f'Pago registrado exitosamente. Saldo restante: ${saldo_actual - monto:.2f}', 'success')
    return redirect(url_for('balance.dashboard'))

@bp.route('/editar-pago', methods=['POST'])
@permiso_requerido('balance.edit')
def editar_pago():
    pago_id = request.form.get('pago_id')
    monto = request.form.get('monto')
    tipo_pago = request.form.get('tipo_pago')
    referencia = request.form.get('referencia')
    fecha_pago = request.form.get('fecha_pago')
    hora_pago = request.form.get('hora_pago')
    notas = request.form.get('descripcion')

    if not pago_id or not str(pago_id).isdigit() or not monto or not tipo_pago:
        flash('Faltan datos obligatorios', 'danger')
        return redirect(url_for('balance.dashboard'))

    try:
        monto_float = float(monto)
        if monto_float <= 0:
            flash('El monto debe ser mayor a cero', 'danger')
            return redirect(url_for('balance.dashboard'))
    except ValueError:
        flash('Monto inválido', 'danger')
        return redirect(url_for('balance.dashboard'))

    try:
        fecha_pago_dt = datetime.strptime(fecha_pago, '%Y-%m-%d').date()
        hora_pago_dt = datetime.strptime(hora_pago, '%H:%M').time()
    except (ValueError, TypeError):
        flash('Fecha u hora de pago inválida', 'danger')
        return redirect(url_for('balance.dashboard'))

    pago_actual = balance_model.obtener_pago_por_id(int(pago_id))
    if not pago_actual:
        flash('Pago no encontrado', 'danger')
        return redirect(url_for('balance.dashboard'))

    contrato = balance_model.obtener_contrato_por_id(pago_actual.id_contrato)
    total_pagado = balance_model.get_total_pagado_by_contrato(pago_actual.id_contrato)
    saldo_disponible = float(contrato['monto_total']) - total_pagado + float(pago_actual.monto or 0)
    if monto_float > saldo_disponible:
        flash(f'El monto excede el saldo disponible (${saldo_disponible:.2f})', 'danger')
        return redirect(url_for('balance.dashboard'))

    datos = {
        'monto': monto_float,
        'tipo_pago': tipo_pago,
        'referencia': referencia,
        'fecha_pago': fecha_pago_dt,
        'hora_pago': hora_pago_dt,
        'descripcion': notas,
    }

    resultado = balance_model.modificar_pago(int(pago_id), datos)
    if resultado:
        _bitacora('update', 'Editar pago', f'Pago #{pago_id} editado')
        flash('Pago actualizado exitosamente', 'success')
    else:
        flash('Error: Pago no encontrado', 'danger')

    return redirect(url_for('balance.dashboard'))

@bp.route('/eliminar-pago/<int:pago_id>', methods=['POST'])
@permiso_requerido('balance.delete')
def eliminar_pago(pago_id):
    resultado = balance_model.eliminar_pago(pago_id)
    if resultado:
        _bitacora('delete', 'Eliminar pago', f'Pago #{pago_id} eliminado')
        flash('Pago eliminado exitosamente', 'success')
    else:
        flash('Error: Pago no encontrado', 'danger')

    return redirect(url_for('balance.dashboard'))

@bp.route('/api/contrato/<int:id_contrato>', methods=['GET'])
@permiso_requerido('balance.view')
def api_contrato(id_contrato):
    contrato = balance_model.obtener_contrato_por_id(id_contrato)
    if not contrato:
        return jsonify({'error': 'Contrato no encontrado'}), 404

    total_pagado = balance_model.get_total_pagado_by_contrato(id_contrato) or 0.0
    saldo_pendiente = float(contrato['monto_total']) - total_pagado

    return jsonify({
        'id_contrato': contrato['id_contrato'],
        'nombre_patrocinador': contrato.get('nombre_patrocinador'),
        'monto_total': float(contrato['monto_total']),
        'total_pagado': total_pagado,
        'saldo_pendiente': saldo_pendiente,
    })

@bp.route('/api/pago/<int:id_pago>', methods=['GET'])
@permiso_requerido('balance.view')
def api_pago(id_pago):
    pago = balance_model.obtener_pago_por_id(id_pago)
    if not pago:
        return jsonify({'error': 'Pago no encontrado'}), 404

    contrato = balance_model.obtener_contrato_por_id(pago.id_contrato)

    return jsonify({
        'id_pago': pago.id_pago,
        'id_contrato': pago.id_contrato,
        'nombre_patrocinador': contrato['nombre_patrocinador'] if contrato else None,
        'monto': float(pago.monto),
        'tipo_pago': pago.tipo_pago,
        'referencia': pago.referencia,
        'fecha_pago': pago.fecha_pago.strftime('%d/%m/%Y') if pago.fecha_pago else '',
        'hora_pago': (datetime.min + pago.hora_pago).strftime('%H:%M') if pago.hora_pago else '',
        'descripcion': pago.descripcion,
    })


# --- SECCIÓN GENERACIÓN PDF ---

@bp.route('/contrato/<int:contrato_id>/pdf', methods=['GET'])
@permiso_requerido('balance.view')
def generar_pdf_contrato(contrato_id):
    contrato_data = balance_model.obtener_contrato_por_id(contrato_id)
    if not contrato_data:
        flash('El contrato especificado no existe.', 'danger')
        return redirect(url_for('balance.dashboard'))

    # Cálculos de saldos
    monto_pagado_contrato = balance_model.get_total_pagado_by_contrato(contrato_id) or 0.0
    monto_total_contrato = float(contrato_data['monto_total']) if contrato_data['monto_total'] else 0.0
    saldo_pendiente_contrato = monto_total_contrato - monto_pagado_contrato

    # Obtener transacciones del contrato
    todos_pagos = balance_model.obtener_historial_pagos(1000)
    pagos_contrato = [p for p in todos_pagos if p.id_contrato == contrato_id]

    # LLAMADA AL ARCHIVO EXTERNO
    pdf_data = generar_pdf_estado_cuenta(
        contrato_id=contrato_id,
        contrato_data=contrato_data,
        monto_pagado_contrato=monto_pagado_contrato,
        monto_total_contrato=monto_total_contrato,
        saldo_pendiente_contrato=saldo_pendiente_contrato,
        pagos_contrato=pagos_contrato,
        usuario_actual=current_user
    )

    # Respuesta de descarga HTTP de Flask
    response = make_response(pdf_data)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'attachment; filename=Estado_Cuenta_Contrato_{contrato_id}.pdf'
    
    return response