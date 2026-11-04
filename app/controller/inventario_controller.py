import json
from datetime import date
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import INVENTARIO
from app.model.inventario_model import InventarioModel, TipoRecursoModel

bp = Blueprint('inventario', __name__, url_prefix='/inventario')

bp.before_request(verificar_acceso(INVENTARIO))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('inventario', tipo, accion, detalle)


# ──────────────────────────────────────────────
# SINGLE ENDPOINT — como PHP gestionActivos.php
# $obj_model = new gestionActivosModel();
# if (isset($_POST['action'])) { ... exit; }
# $tipos_activos = $obj_model->cargarTiposActivos();
# require_once 'componentes/llamado_vistas.php';
# ──────────────────────────────────────────────
@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    obj_model = InventarioModel()
    obj_tipo = TipoRecursoModel()
    mensaje = None

    if request.method == 'POST':
        if 'verificar_nombre' in request.form:
            nombre = request.form['verificar_nombre']
            existe = obj_model.verificar_nombre(nombre)
            return jsonify({'existe': existe})

        if 'consultar' in request.form:
            recursos = obj_model.consultar()
            return jsonify([{
                'id_activo': r['id'],
                'tipo': r['tipo_nombre'],
                'Nombre_Activo': r['nombre'],
                'Descripcion_Activo': r['descripcion'],
                'estado_id': r['estado_id'],
                'Estado_Activo': r['estado_nombre'] or 'Disponible',
                'Fecha_adquisicion': str(r['fecha_compra']) if r['fecha_compra'] else '',
            } for r in recursos])

        if 'buscar' in request.form:
            obj_model.set_id_activo(request.form['idActivo'])
            recurso = obj_model.buscar()
            if recurso:
                return jsonify({'status': True, 'datos': {
                    'id_activo': recurso['id'],
                    'id_tipo_activo': recurso['tipo_id'],
                    'id_ubicacion': recurso['estado_id'],
                    'Nombre_Activo': recurso['nombre'],
                    'Descripcion_Activo': recurso['descripcion'],
                    'Fecha_adquisicion': str(recurso['fecha_compra']) if recurso['fecha_compra'] else '',
                    'Estado_Activo': recurso['estado_nombre'] or 'Disponible',
                }})
            return jsonify({'status': False, 'datos': None})

        if 'registrar' in request.form:
            obj_model.set_id_tipo(request.form['id_tipo_activo'])
            obj_model.set_nombre(request.form['Nombre'])
            obj_model.set_descripcion(request.form['Descripcion'])
            obj_model.set_fecha_adquisicion(request.form['Fecha_adquisicion'])

            if obj_model.confirmar_registro():
                _registrar_bitacora('create', 'Registrar activo', f'Activo "{request.form["Nombre"]}" registrado')
                mensaje = "Activo registrado correctamente"
            else:
                mensaje = "Error al registrar el activo"
            return jsonify({'mensaje': mensaje})

        if 'editar' in request.form:
            id_recurso = request.form['editar']
            obj_model.set_id_tipo(request.form['id_tipo_activo'])
            obj_model.set_nombre(request.form['Nombre'])
            obj_model.set_descripcion(request.form['Descripcion'])
            obj_model.set_fecha_adquisicion(request.form['Fecha_adquisicion'])

            if obj_model.confirmar_modificacion(id_recurso):
                _registrar_bitacora('update', 'Editar activo', f'Activo "{request.form["Nombre"]}" actualizado')
                mensaje = "Recurso actualizado correctamente"
            else:
                mensaje = "Error al actualizar el recurso"
            return jsonify({'mensaje': mensaje})

        if 'eliminar' in request.form:
            obj_model.set_id_activo(request.form['idActivo'])
            recurso = obj_model.buscar()
            if obj_model.confirmar_eliminacion(request.form['idActivo']):
                _registrar_bitacora('delete', 'Eliminar activo', f'Activo "{recurso["nombre"]}" eliminado')
                mensaje = "Recurso eliminado correctamente"
            else:
                mensaje = "Error al eliminar el recurso"
            return jsonify({'mensaje': mensaje})

        # --- CRUD TIPOS DE RECURSO ---
        if 'consultar_tipos' in request.form:
            tipos = obj_tipo.consultar()
            return jsonify([{
                'id_tipo_activo': t['id'],
                'Nombre': t['nombre'],
                'Descripcion_tipo': t['descripcion'],
            } for t in (tipos or [])])

        if 'buscar_tipos' in request.form:
            obj_tipo.set_id_tipo(request.form['idTipo'])
            tipo = obj_tipo.buscar_tipo()
            if tipo:
                return jsonify({'status': True, 'datos': {
                    'id_tipo_activo': tipo['id'],
                    'Nombre': tipo['nombre'],
                    'Descripcion_tipo': tipo['descripcion'],
                }})
            return jsonify({'status': False, 'datos': None})

        if 'agregar_tipo_activo' in request.form:
            obj_tipo.set_nombre_tipo(request.form['nombre_tipo_activo'])
            obj_tipo.set_descripcion_tipo(request.form.get('descripcion_tipo_activo', ''))
            if obj_tipo.confirmar_registro():
                _registrar_bitacora('create', 'Agregar tipo de recurso', f'Tipo "{request.form["nombre_tipo_activo"]}" registrado')
                mensaje = "Tipo de recurso registrado correctamente"
            else:
                mensaje = "Error al registrar el tipo de recurso"
            return jsonify({'mensaje': mensaje})

        if 'eliminar_tipo_activo' in request.form:
            obj_tipo.set_id_tipo(request.form['eliminar_tipo_activo'])
            tipo = obj_tipo.buscar_tipo()
            if obj_tipo.confirmar_eliminacion(request.form['eliminar_tipo_activo']):
                _registrar_bitacora('delete', 'Eliminar tipo de recurso', f'Tipo "{tipo["nombre"]}" eliminado')
                mensaje = "Tipo de recurso eliminado correctamente"
            else:
                mensaje = "Error al eliminar el tipo de recurso"
            return jsonify({'mensaje': mensaje})

        if 'editar_tipo_activo' in request.form:
            obj_tipo.set_id_tipo(request.form['editar_tipo_activo'])
            obj_tipo.set_nombre_tipo(request.form['nombre_tipo_activo'])
            obj_tipo.set_descripcion_tipo(request.form.get('descripcion_tipo_activo', ''))
            if obj_tipo.confirmar_modificacion(request.form['editar_tipo_activo']):
                _registrar_bitacora('update', 'Editar tipo de recurso', f'Tipo "{request.form["nombre_tipo_activo"]}" actualizado')
                mensaje = "Tipo de recurso actualizado correctamente"
            else:
                mensaje = "Error al actualizar el tipo de recurso"
            return jsonify({'mensaje': mensaje})

    # --- Fall through: data for view (como PHP $tipos_activos = ...) ---
    tipos_activos = obj_model.obtener_tipos()

    return render_template(
        'inventario/dashboard.html',
        tipos_activos=tipos_activos,
        mensaje=mensaje,
    )


# ──────────────────────────────────────────────
# RUTAS ADICIONALES (asignaciones, detalle)
# ──────────────────────────────────────────────
@bp.route('/ver/<int:id>')
def ver(id):
    obj_model = InventarioModel()
    obj_model.set_id_activo(id)
    recurso = obj_model.buscar()
    if not recurso:
        flash('Recurso no encontrado', 'danger')
        return redirect(url_for('inventario.dashboard'))
    asignaciones = obj_model.consultar_asignaciones(recurso_id=id)
    return render_template('inventario/ver.html',
                           recurso=recurso,
                           asignaciones=asignaciones)


@bp.route('/gestion-asignaciones')
def gestion_asignaciones():
    obj_model = InventarioModel()
    asignaciones = obj_model.consultar_asignaciones()
    recursos = obj_model.consultar()
    usuarios = obj_model.obtener_usuarios()
    estados_asignacion = obj_model.obtener_estados_asignacion()
    return render_template('inventario/gestion_asignaciones.html',
                           asignaciones=asignaciones,
                           recursos=recursos,
                           usuarios=usuarios,
                           estados_asignacion=estados_asignacion)


@bp.route('/asignar/<int:recurso_id>', methods=['GET', 'POST'])
def asignar(recurso_id):
    obj_model = InventarioModel()
    obj_model.set_id_activo(recurso_id)
    recurso = obj_model.buscar()
    if not recurso:
        flash('Recurso no encontrado', 'danger')
        return redirect(url_for('inventario.dashboard'))

    if request.method == 'POST':
        usuario_id = request.form.get('usuario_id')
        fecha_devolucion = request.form.get('fecha_devolucion_esperada') or None
        notas = request.form.get('notas', '').strip()

        errores = []
        if not usuario_id or not usuario_id.isdigit():
            errores.append('Debe seleccionar un usuario')
        if fecha_devolucion:
            try:
                date.fromisoformat(fecha_devolucion)
            except ValueError:
                errores.append('La fecha de devolución no es válida')
        if obj_model.obtener_asignacion_activa(recurso_id):
            errores.append('El recurso ya est\u00e1 asignado actualmente')
        if recurso['estado_id'] != 1:
            errores.append('El recurso no est\u00e1 disponible para asignación')

        if not errores:
            obj_model.set_recurso_id(recurso_id)
            obj_model.set_usuario_id(int(usuario_id))
            obj_model.set_fecha_devolucion_esperada(fecha_devolucion)
            obj_model.set_notas(notas)
            obj_model.set_estado_asignacion_id(1)
            asignacion = obj_model.registrar_asignacion()
            if asignacion:
                obj_model.cambiar_estado(recurso_id, 2)
                _registrar_bitacora('update', 'Asignar recurso', f'Recurso "{recurso["nombre"]}" asignado a usuario #{usuario_id}')
                flash(f'Recurso "{recurso["nombre"]}" asignado correctamente', 'success')
                return redirect(url_for('inventario.ver', id=recurso_id))
            errores.append('Error al registrar la asignación')

        for err in errores:
            flash(err, 'danger')

    usuarios = obj_model.obtener_usuarios()
    return render_template('inventario/asignar.html',
                           recurso=recurso, usuarios=usuarios)


@bp.route('/asignar_desde_gestion', methods=['POST'])
def asignar_desde_gestion():
    obj_model = InventarioModel()
    recurso_id = request.form.get('recurso_id')
    usuario_id = request.form.get('usuario_id')
    fecha_devolucion = request.form.get('fecha_devolucion_esperada') or None
    notas = request.form.get('notas', '').strip()

    errores = []
    if not recurso_id or not recurso_id.isdigit():
        errores.append('Debe seleccionar un recurso')
    if not usuario_id or not usuario_id.isdigit():
        errores.append('Debe seleccionar un usuario')
    if fecha_devolucion:
        try:
            date.fromisoformat(fecha_devolucion)
        except ValueError:
            errores.append('La fecha de devolución no es válida')

    if not errores:
        obj_model.set_id_activo(int(recurso_id))
        recurso = obj_model.buscar()
        if not recurso:
            errores.append('Recurso no encontrado')
        elif obj_model.obtener_asignacion_activa(int(recurso_id)):
            errores.append('El recurso ya est\u00e1 asignado actualmente')
        elif recurso['estado_id'] != 1:
            errores.append('El recurso no est\u00e1 disponible para asignación')

    if not errores:
        obj_model.set_recurso_id(int(recurso_id))
        obj_model.set_usuario_id(int(usuario_id))
        obj_model.set_fecha_devolucion_esperada(fecha_devolucion)
        obj_model.set_notas(notas)
        obj_model.set_estado_asignacion_id(1)
        asignacion = obj_model.registrar_asignacion()
        if asignacion:
            obj_model.cambiar_estado(int(recurso_id), 2)
            _registrar_bitacora('update', 'Asignar recurso', f'Recurso "{recurso["nombre"]}" asignado a usuario #{usuario_id}')
            flash('Recurso asignado correctamente', 'success')
        else:
            errores.append('Error al registrar la asignación')

    for err in errores:
        flash(err, 'danger')

    return redirect(url_for('inventario.gestion_asignaciones'))


@bp.route('/devolver/<int:asignacion_id>', methods=['POST'])
def devolver_recurso(asignacion_id):
    obj_model = InventarioModel()
    asignacion = obj_model.obtener_asignacion(asignacion_id)
    if not asignacion:
        flash('Asignación no encontrada', 'danger')
        return redirect(url_for('inventario.gestion_asignaciones'))

    if asignacion['fecha_devolucion_real']:
        flash('Esta asignación ya fue devuelta', 'danger')
        return redirect(url_for('inventario.gestion_asignaciones'))

    obj_model.devolver_recurso(asignacion_id)
    obj_model.cambiar_estado(asignacion['recurso_id'], 1)
    _registrar_bitacora('update', 'Devolver recurso', f'Recurso "{asignacion["recurso_nombre"]}" devuelto')
    flash('Devolución procesada correctamente', 'success')
    return redirect(url_for('inventario.gestion_asignaciones'))


# ──────────────────────────────────────────────
# RUTAS COMPATIBLES CON VISTAS EXISTENTES
# ──────────────────────────────────────────────
@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    obj_model = InventarioModel()
    if request.method == 'POST':
        obj_model.set_nombre(request.form['nombre'])
        obj_model.set_descripcion(request.form.get('descripcion', ''))
        obj_model.set_id_tipo(request.form['tipo_id'])
        obj_model.set_estado_id(1)
        obj_model.set_fecha_adquisicion(request.form.get('fecha_compra') or None)
        obj_model.set_costo(request.form.get('costo') or None)

        if obj_model.confirmar_registro():
            _registrar_bitacora('create', 'Registrar recurso', f'Recurso "{request.form["nombre"]}" creado')
            flash('Recurso creado exitosamente', 'success')
            return redirect(url_for('inventario.dashboard'))
        flash('Error al crear el recurso', 'danger')

    tipos = obj_model.obtener_tipos()
    return render_template('inventario/crear.html', tipos=tipos)


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    obj_model = InventarioModel()
    obj_model.set_id_activo(id)
    recurso = obj_model.buscar()
    if not recurso:
        flash('Recurso no encontrado', 'danger')
        return redirect(url_for('inventario.dashboard'))

    if request.method == 'POST':
        obj_model.set_nombre(request.form['nombre'])
        obj_model.set_descripcion(request.form.get('descripcion', ''))
        obj_model.set_id_tipo(request.form['tipo_id'])
        obj_model.set_estado_id(recurso['estado_id'])
        obj_model.set_fecha_adquisicion(request.form.get('fecha_compra') or None)
        obj_model.set_costo(request.form.get('costo') or None)

        if obj_model.confirmar_modificacion(id):
            _registrar_bitacora('update', 'Editar recurso', f'Recurso "{request.form["nombre"]}" actualizado')
            flash('Recurso actualizado exitosamente', 'success')
            return redirect(url_for('inventario.ver', id=id))
        flash('Error al actualizar el recurso', 'danger')

    tipos = obj_model.obtener_tipos()
    return render_template('inventario/editar.html',
                           recurso=recurso, tipos=tipos)


@bp.route('/eliminar/<int:id>', methods=['GET', 'POST'])
def eliminar(id):
    obj_model = InventarioModel()
    obj_model.set_id_activo(id)
    recurso = obj_model.buscar()
    if not recurso:
        flash('Recurso no encontrado', 'danger')
        return redirect(url_for('inventario.dashboard'))

    if request.method == 'POST':
        if obj_model.tiene_asignaciones_pendientes(id):
            flash('El recurso tiene asignaciones activas pendientes', 'danger')
            return redirect(url_for('inventario.dashboard'))

        if obj_model.confirmar_eliminacion(id):
            _registrar_bitacora('delete', 'Eliminar recurso', f'Recurso "{recurso["nombre"]}" dado de baja')
            flash(f'Recurso "{recurso["nombre"]}" dado de baja', 'success')
            return redirect(url_for('inventario.dashboard'))
        flash('Error al eliminar el recurso', 'danger')

    pendientes = obj_model.tiene_asignaciones_pendientes(id)
    total_asignaciones = obj_model.total_asignaciones(id)
    return render_template('inventario/eliminar.html',
                           recurso=recurso,
                           pendientes=pendientes,
                           total_asignaciones=total_asignaciones)
