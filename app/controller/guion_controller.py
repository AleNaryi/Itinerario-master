import json
from datetime import date, time
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import GUION
from app.model.guion_model import (GuionModel, ElementoGuionModel, _parsear_duracion)

bp = Blueprint('guion', __name__, url_prefix='/guiones')

bp.before_request(verificar_acceso(GUION))


def _usuarios_choices():
    from app.model.auth_model import UsuarioModel
    um = UsuarioModel()
    usuarios = um.consultar()
    return [(u.nombre, u.nombre) for u in usuarios]


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('guion', tipo, accion, detalle)


@bp.route('/', methods=['GET'])
def dashboard():
    guion_model = GuionModel()
    elemento_model = ElementoGuionModel()
    guiones = guion_model.consultar()
    total = len(guiones)
    borradores = sum(1 for g in guiones if g['estado'] == 'borrador')
    publicados = sum(1 for g in guiones if g['estado'] == 'publicado')
    for g in guiones:
        elems = elemento_model.consultar(guion_id=g['id'])
        g['pregame_count'] = sum(1 for e in elems if e['tipo'] == 'pregame')
        g['game_count'] = sum(1 for e in elems if e['tipo'] == 'game')
        g['fechas'] = guion_model.obtener_fechas(g['id'])
    return render_template('guion/dashboard.html', guiones=guiones, total=total,
                           borradores=borradores, publicados=publicados)


@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    guion_model = GuionModel()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        tiempo_inning_str = request.form.get('tiempo_inning', '').strip()
        hoy = date.today()
        nombre_con_fecha = f"{nombre} - {hoy}"
        guion_model.set_nombre(nombre_con_fecha)
        guion_model.set_fecha(hoy)
        if tiempo_inning_str:
            guion_model.set_tiempo_inning(_parsear_duracion(tiempo_inning_str))
        id = guion_model.confirmar_registro()
        if not id:
            flash('Error al crear el guion', 'danger')
            return render_template('guion/crear.html')
        _registrar_bitacora('create', 'Crear guion', f'Guion "{nombre_con_fecha}" creado')
        return redirect(url_for('guion.agregar_elementos', id=id))
    return render_template('guion/crear.html')


@bp.route('/agregar-elemento/<int:id>', methods=['GET', 'POST'])
def agregar_elementos(id):
    guion_model = GuionModel()
    elemento_model = ElementoGuionModel()
    guion = guion_model.obtener_por_id(id)
    if not guion:
        flash('Guión no encontrado', 'danger')
        return redirect(url_for('guion.dashboard'))
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        hora_str = request.form.get('hora', '')
        inning_str = request.form.get('inning', '')
        medio_inning = request.form.get('medio_inning', '')
        contenido = request.form.get('contenido', '').strip()
        duracion_str = request.form.get('duracion_estimada', '')
        encargado = request.form.get('encargado', '')
        errores = []
        if tipo not in ('pregame', 'game'):
            errores.append('Tipo de elemento inválido')
        if not contenido:
            errores.append('El contenido es obligatorio')
        if tipo == 'pregame' and not hora_str:
            errores.append('Para Pre-Game debes indicar una hora')
        elif tipo == 'game' and (not inning_str or not medio_inning):
            errores.append('Para Game debes seleccionar inning y medio')
        horas_ocupadas, innings_ocupados = elemento_model.obtener_ocupados(id)
        if tipo == 'pregame' and hora_str:
            if hora_str in horas_ocupadas:
                errores.append('Esa hora ya esta ocupada')
        elif tipo == 'game' and inning_str and medio_inning:
            clave = f"{inning_str}-{medio_inning}"
            if clave in innings_ocupados:
                errores.append('Ese inning ya esta ocupado')
        if errores:
            for e in errores:
                flash(e, 'warning')
        else:
            hora = None
            try:
                if tipo == 'pregame' and hora_str:
                    hora_parts = hora_str.split(':')
                    hora = time(int(hora_parts[0]), int(hora_parts[1]))
                inning = int(inning_str) if inning_str else None
            except (ValueError, IndexError):
                flash('Hora o inning inválidos', 'warning')
                return redirect(url_for('guion.agregar_elementos', id=id))
            ultimo_orden = elemento_model.obtener_ultimo_orden(id, tipo)
            elemento_model.set_guion_id(id)
            elemento_model.set_tipo(tipo)
            elemento_model.set_contenido(contenido)
            elemento_model.set_duracion_estimada(_parsear_duracion(duracion_str))
            elemento_model.set_hora(hora)
            elemento_model.set_inning(inning)
            elemento_model.set_medio_inning(medio_inning or None)
            elemento_model.set_encargado(encargado)
            elemento_model.set_orden(ultimo_orden + 1)
            elemento_model.set_fecha_id(None)
            if not elemento_model.confirmar_registro():
                flash('Error al agregar elemento', 'danger')
            else:
                guion = guion_model.obtener_por_id(id)
                _registrar_bitacora('create', 'Agregar elemento', f'Elemento {tipo} agregado a guion "{guion["nombre"]}"')
                if request.form.get('submit_final'):
                    flash('Guion creado exitosamente!', 'success')
                    return redirect(url_for('guion.dashboard'))
                flash('Elemento agregado', 'success')
            return redirect(url_for('guion.agregar_elementos', id=id))
    fechas = guion_model.obtener_fechas(id)
    pregame, game = elemento_model.obtener_por_guion_ordenados(id)
    elementos = pregame + game
    horas_usadas, innings_usados = elemento_model.obtener_ocupados(id)
    tiempo_total_seg = sum(e['duracion_estimada'] for e in elementos)
    return render_template('guion/agregar_elementos.html', guion=guion, fechas=fechas,
                           elementos=elementos, horas_usadas=list(horas_usadas),
                           innings_usados=innings_usados, tiempo_total_seg=tiempo_total_seg,
                           tiempo_inning=guion['tiempo_inning'],
                           usuarios_choices=_usuarios_choices())


@bp.route('/editar-elemento/<int:guion_id>/<int:elemento_id>', methods=['GET', 'POST'])
def editar_elemento(guion_id, elemento_id):
    guion_model = GuionModel()
    elemento_model = ElementoGuionModel()
    guion = guion_model.obtener_por_id(guion_id)
    elemento = elemento_model.obtener_por_id(elemento_id)
    if not guion or not elemento or elemento['guion_id'] != guion_id:
        flash('Elemento no encontrado', 'danger')
        return redirect(url_for('guion.dashboard'))
    if request.method == 'POST':
        tipo = request.form.get('tipo')
        hora_str = request.form.get('hora', '')
        inning_str = request.form.get('inning', '')
        medio_inning = request.form.get('medio_inning', '')
        contenido = request.form.get('contenido', '').strip()
        duracion_str = request.form.get('duracion_estimada', '')
        encargado = request.form.get('encargado', '')
        errores = []
        if tipo not in ('pregame', 'game'):
            errores.append('Tipo de elemento inválido')
        if not contenido:
            errores.append('El contenido es obligatorio')
        if tipo == 'pregame' and not hora_str:
            errores.append('Para Pre-Game debes indicar una hora')
        elif tipo == 'game' and (not inning_str or not medio_inning):
            errores.append('Para Game debes seleccionar inning y medio')
        otros = elemento_model.consultar_excepto(guion_id, elemento_id)
        horas_ocupadas = set()
        innings_ocupados = {}
        for e in otros:
            if e['tipo'] == 'pregame' and e['hora']:
                horas_ocupadas.add(str(e['hora'])[:5])
            elif e['tipo'] == 'game' and e['inning']:
                innings_ocupados[f"{e['inning']}-{e['medio_inning']}"] = e['id']
        if tipo == 'pregame' and hora_str and hora_str in horas_ocupadas:
            errores.append('Esa hora ya est\u00e1 ocupada')
        elif tipo == 'game' and inning_str and medio_inning:
            clave = f"{inning_str}-{medio_inning}"
            if clave in innings_ocupados:
                errores.append('Ese inning ya est\u00e1 ocupado')
        if errores:
            for e in errores:
                flash(e, 'warning')
        else:
            hora = None
            try:
                if tipo == 'pregame' and hora_str:
                    hp = hora_str.split(':')
                    hora = time(int(hp[0]), int(hp[1]))
                inning = int(inning_str) if inning_str else None
            except (ValueError, IndexError):
                flash('Hora o inning inválidos', 'warning')
                return redirect(url_for('guion.editar_elemento', guion_id=guion_id, elemento_id=elemento_id))
            elemento_model.modificar(elemento_id, {
                'tipo': tipo, 'hora': hora, 'inning': inning,
                'medio_inning': medio_inning or None, 'contenido': contenido,
                'duracion_estimada': _parsear_duracion(duracion_str),
                'encargado': encargado, 'fecha_id': None,
            })
            guion = guion_model.obtener_por_id(guion_id)
            _registrar_bitacora('update', 'Editar elemento', f'Elemento de guión "{guion["nombre"]}" editado')
            flash('Elemento actualizado', 'success')
            return redirect(url_for('guion.agregar_elementos', id=guion_id))
    fechas = guion_model.obtener_fechas(guion_id)
    otros = elemento_model.consultar_excepto(guion_id, elemento_id)
    horas_usadas = set()
    innings_usados = {}
    for e in otros:
        if e['tipo'] == 'pregame' and e['hora']:
            horas_usadas.add(str(e['hora'])[:5])
        elif e['tipo'] == 'game' and e['inning']:
            innings_usados[f"{e['inning']}-{e['medio_inning']}"] = e['id']
    return render_template('guion/editar_elemento.html', guion=guion, elemento=elemento,
                           fechas=fechas, horas_usadas=list(horas_usadas),
                           innings_usados=innings_usados, tiempo_inning=guion['tiempo_inning'],
                           usuarios_choices=_usuarios_choices())


@bp.route('/eliminar-elemento/<int:guion_id>/<int:elemento_id>')
def eliminar_elemento(guion_id, elemento_id):
    guion_model = GuionModel()
    elemento_model = ElementoGuionModel()
    elemento = elemento_model.obtener_por_id(elemento_id)
    if not elemento or elemento['guion_id'] != guion_id:
        flash('Elemento no pertenece a este guion', 'danger')
    else:
        guion = guion_model.obtener_por_id(guion_id)
        elemento_model.eliminar(elemento_id)
        _registrar_bitacora('delete', 'Eliminar elemento', f'Elemento de guión "{guion["nombre"]}" eliminado')
        flash('Elemento eliminado', 'warning')
    return redirect(url_for('guion.agregar_elementos', id=guion_id))


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    guion_model = GuionModel()
    guion = guion_model.obtener_por_id(id)
    if not guion:
        flash('Guión no encontrado', 'danger')
        return redirect(url_for('guion.dashboard'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        tiempo_inning_str = request.form.get('tiempo_inning', '').strip()
        errores = []
        if not nombre or len(nombre) < 3:
            errores.append('El nombre debe tener al menos 3 caracteres')
        if errores:
            for e in errores:
                flash(e, 'warning')
        else:
            data = {'nombre': nombre}
            if tiempo_inning_str:
                data['tiempo_inning'] = _parsear_duracion(tiempo_inning_str)
            guion_model.modificar(id, data)
            _registrar_bitacora('update', 'Editar guión', f'Guión "{nombre}" actualizado')
            flash('\u00a1Guión actualizado!', 'success')
            return redirect(url_for('guion.dashboard'))
    return render_template('guion/editar.html', guion=guion)


@bp.route('/previsualizar/<int:id>')
def previsualizar(id):
    guion_model = GuionModel()
    elemento_model = ElementoGuionModel()
    guion = guion_model.obtener_por_id(id)
    if not guion:
        flash('Guión no encontrado', 'danger')
        return redirect(url_for('guion.dashboard'))
    fechas = guion_model.obtener_fechas(id)
    pregame, game = elemento_model.obtener_por_guion_ordenados(id)
    elementos = pregame + game
    tiempo_total_seg = sum(e['duracion_estimada'] for e in elementos)
    return render_template('guion/previsualizar.html', guion=guion, fechas=fechas,
                           pregame=pregame, game=game, tiempo_total_seg=tiempo_total_seg)


@bp.route('/publicar/<int:id>', methods=['GET', 'POST'])
def publicar(id):
    guion_model = GuionModel()
    guion = guion_model.obtener_por_id(id)
    if not guion:
        flash('Guión no encontrado', 'danger')
        return redirect(url_for('guion.dashboard'))
    guion['fechas'] = guion_model.obtener_fechas(id)
    guion['elementos'] = ElementoGuionModel().consultar(guion_id=id)
    if request.method == 'POST':
        guion_model.modificar(id, {'estado': 'publicado'})
        _registrar_bitacora('update', 'Publicar guión', f'Guión "{guion["nombre"]}" publicado')
        flash(f'Guión "{guion["nombre"]}" publicado!', 'success')
        return redirect(url_for('guion.dashboard'))
    return render_template('guion/publicar.html', guion=guion)


@bp.route('/eliminar/<int:id>')
def eliminar(id):
    guion_model = GuionModel()
    guion = guion_model.obtener_por_id(id)
    ok = guion_model.eliminar(id)
    if ok:
        _registrar_bitacora('delete', 'Eliminar guión', f'Guión "{guion["nombre"]}" eliminado')
        flash('Guión eliminado', 'warning')
    else:
        flash('Error al eliminar', 'danger')
    return redirect(url_for('guion.dashboard'))


@bp.route('/replicar/<int:id>', methods=['GET', 'POST'])
def replicar(id):
    guion_model = GuionModel()
    guion = guion_model.obtener_por_id(id)
    if not guion:
        flash('Guión no encontrado', 'danger')
        return redirect(url_for('guion.dashboard'))
    if request.method == 'POST':
        nombre_base = request.form.get('nombre_base', '').strip()
        fechas_json = request.form.get('fechas', '')
        errores = []
        if not nombre_base or len(nombre_base) < 3:
            errores.append('El nombre base debe tener al menos 3 caracteres')
        if not fechas_json:
            errores.append('Debes seleccionar al menos una fecha')
        if errores:
            for e in errores:
                flash(e, 'warning')
            return render_template('guion/replicar.html', guion=guion)
        try:
            fechas_lista = [date.fromisoformat(f) for f in fechas_json.split(',')]
        except ValueError:
            flash('Una de las fechas seleccionadas no es válida', 'danger')
            return render_template('guion/replicar.html', guion=guion)
        ids = guion_model.replicar(id, fechas_lista, nombre_base)
        _registrar_bitacora('create', 'Replicar guión', f'Guión "{guion["nombre"]}" replicado a {len(ids)} fecha(s)')
        flash(f'Guion replicado exitosamente en {len(ids)} fecha(s)', 'success')
        return redirect(url_for('guion.dashboard'))
    nombre_base = guion['nombre'].rsplit(' - ', 1)[0] if ' - ' in guion['nombre'] else guion['nombre']
    guion['elementos'] = ElementoGuionModel().consultar(guion_id=id)
    return render_template('guion/replicar.html', guion=guion, nombre_base=nombre_base)


@bp.route('/verificar-nombre', methods=['POST'])
def verificar_nombre():
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        return jsonify({'existe': False})
    existe = GuionModel().verificar_nombre(nombre)
    return jsonify({'existe': existe})
