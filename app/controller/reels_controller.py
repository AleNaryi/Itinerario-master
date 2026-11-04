import json
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.helpers.permission_map import REELS
from app.model.reels_model import ReelModel, VideoModel
from app.model.patrocinador_model import PatrocinadorModel

bp = Blueprint('reels', __name__, url_prefix='/reels')

bp.before_request(verificar_acceso(REELS))


def _registrar_bitacora(tipo, accion, detalle):
    from app.helpers.bitacora_helper import registrar_bitacora
    registrar_bitacora('reels', tipo, accion, detalle)


def _patrocinadores_select():
    return [(p['id_patrocinador'], p['nombre_empresa']) for p in PatrocinadorModel().consultar(activos=True)]


def _parsear_duracion_minutos(texto):
    if not texto:
        return 0
    texto = str(texto).strip()
    if ',' in texto:
        partes = texto.split(',')
        minutos = int(partes[0]) if partes[0] else 0
        seg_str = (partes[1] or '').ljust(2, '0')[:2]
        return minutos + int(seg_str) / 60.0
    try:
        return float(texto)
    except ValueError:
        return 0


def _procesar_videos_json(reel_id, videos_json):
    if not videos_json:
        return
    video_model = VideoModel()
    try:
        videos_data = json.loads(videos_json)
    except (json.JSONDecodeError, TypeError):
        return
    for v in video_model.consultar_por_reel(reel_id):
        video_model.eliminar(v['id'])
    for i, v_data in enumerate(videos_data):
        try:
            segundos = int(float(v_data.get('duracion', 0)))
        except (ValueError, TypeError):
            segundos = 0
        video_model.registrar({
            'reel_id': reel_id, 'nombre': v_data.get('nombre', ''),
            'duracion_segundos': segundos, 'orden': i + 1,
            'id_patrocinador': v_data.get('patrocinador'),
        })


def _parsear_segundos(texto):
    # ponytail: fallback 0, igual que _procesar_videos_json
    try:
        return max(0, int(float(texto or 0)))
    except (ValueError, TypeError):
        return 0


def _parsear_orden(texto, video_model, reel_id):
    try:
        return int(texto)
    except (ValueError, TypeError):
        return len(video_model.consultar_por_reel(reel_id)) + 1


@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    reel_model = ReelModel()
    if request.method == 'POST' and request.form.get('consultar'):
        data = []
        for r in reel_model.consultar():
            data.append({
                'id': r['id'], 'nombre': r['nombre'],
                'duracion_total': r['duracion_total'], 'videos_count': len(r['videos']),
            })
        return jsonify(data)
    reels = reel_model.consultar()
    return render_template('reels/dashboardreels.html', reels=reels)


@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    reel_model = ReelModel()
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre del reel es obligatorio', 'danger')
            return render_template('reels/agregar_reel.html', patrocinadores=_patrocinadores_select())
        duracion = _parsear_duracion_minutos(request.form.get('duracion_total'))
        reel = reel_model.registrar({
            'nombre': nombre,
            'duracion_total': duracion,
        })
        if reel:
            _procesar_videos_json(reel['id'], request.form.get('videos_json'))
            _registrar_bitacora('create', 'Crear reel', f'Reel "{nombre}" creado')
            flash(f'Reel "{reel["nombre"]}" creado exitosamente', 'success')
            return redirect(url_for('reels.dashboard'))
        flash('Error al crear el reel', 'danger')
    return render_template('reels/agregar_reel.html', patrocinadores=_patrocinadores_select())


@bp.route('/ver/<int:id>')
def ver(id):
    reel_model = ReelModel()
    reel = reel_model.obtener_por_id(id)
    if not reel:
        flash('Reel no encontrado', 'danger')
        return redirect(url_for('reels.dashboard'))
    return render_template('reels/ver_reel.html', reel=reel)


@bp.route('/editar/<int:id>', methods=['GET', 'POST'])
def editar(id):
    reel_model = ReelModel()
    reel = reel_model.obtener_por_id(id)
    if not reel:
        flash('Reel no encontrado', 'danger')
        return redirect(url_for('reels.dashboard'))
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        if not nombre:
            flash('El nombre del reel es obligatorio', 'danger')
            return render_template('reels/editar_reel.html', reel=reel, videos_json='[]',
                                   patrocinadores=_patrocinadores_select(), reel_duracion_texto='')
        duracion = _parsear_duracion_minutos(request.form.get('duracion_total'))
        reel = reel_model.modificar(id, {
            'nombre': nombre,
            'duracion_total': duracion,
        })
        if reel:
            _procesar_videos_json(reel['id'], request.form.get('videos_json'))
            _registrar_bitacora('update', 'Editar reel', f'Reel "{nombre}" editado')
            flash('Reel actualizado exitosamente', 'success')
            return redirect(url_for('reels.ver', id=id))
        flash('Error al actualizar el reel', 'danger')
    videos_json_str = json.dumps([{
        'nombre': v['nombre'], 'duracion': v['duracion_segundos'],
        'patrocinador': v.get('id_patrocinador'),
    } for v in reel['videos']])
    total_seg = int(round((reel['duracion_total'] or 0) * 60))
    mins = total_seg // 60
    segs = total_seg % 60
    reel_duracion_texto = f"{mins},{segs}" if segs else str(mins)
    return render_template('reels/editar_reel.html', reel=reel, videos_json=videos_json_str,
                           patrocinadores=_patrocinadores_select(),
                           reel_duracion_texto=reel_duracion_texto)


@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    reel_model = ReelModel()
    reel = reel_model.obtener_por_id(id)
    if not reel:
        flash('Reel no encontrado', 'danger')
        return redirect(url_for('reels.dashboard'))
    nombre = reel['nombre']
    reel_model.confirmar_eliminacion(id)
    _registrar_bitacora('delete', 'Eliminar reel', f'Reel "{nombre}" eliminado')
    flash(f'Reel "{nombre}" eliminado exitosamente', 'success')
    return redirect(url_for('reels.dashboard'))


@bp.route('/<int:reel_id>/agregar-video', methods=['POST'])
def agregar_video(reel_id):
    video_model = VideoModel()
    nombre = request.form.get('nombre', '').strip()
    if not nombre:
        flash('El nombre del video es obligatorio', 'danger')
        return redirect(url_for('reels.ver', id=reel_id))
    video = video_model.registrar({
        'reel_id': reel_id, 'nombre': nombre,
        'duracion_segundos': _parsear_segundos(request.form.get('duracion_segundos')),
        'orden': _parsear_orden(request.form.get('orden'), video_model, reel_id),
    })
    if video:
        reel = ReelModel().obtener_por_id(reel_id)
        _registrar_bitacora('create', 'Agregar video', f'Video "{nombre}" agregado al reel "{reel["nombre"]}"')
        # ponytail: duración total preserved as entered, not recalculated from videos
        flash(f'Video "{video["nombre"]}" agregado al reel', 'success')
    else:
        flash('Error al agregar el video', 'danger')
    return redirect(url_for('reels.ver', id=reel_id))


@bp.route('/<int:reel_id>/eliminar-video/<int:video_id>', methods=['POST'])
def eliminar_video(reel_id, video_id):
    reel = ReelModel().obtener_por_id(reel_id)
    VideoModel().eliminar(video_id)
    _registrar_bitacora('delete', 'Eliminar video', f'Video #{video_id} eliminado del reel "{reel["nombre"]}"')
    flash('Video eliminado del reel', 'success')
    return redirect(url_for('reels.ver', id=reel_id))
