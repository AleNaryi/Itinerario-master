from flask import Blueprint, render_template, redirect, url_for, jsonify, request
from flask_login import current_user
from app import usuarios_conectados
from app.model.guion_model import ElementoGuionModel
from app.model.guion_model import GuionModel
from app.model.en_vivo_model import EnVivoModel
from app.model.premio_model import PremioModel
from app.model.contrato_model import ContratoModel
from app.model.patrocinador_model import PatrocinadorModel
from app.model.balance_model import BalanceModel
from app.model.mantenimiento_model import RecursoModel
from app.model.tarea_model import TareasAsignadasModel
from app.model.auth_model import UsuarioModel
from app.model.bitacora_model import ActividadModel
from app.model.inventario_model import InventarioModel
from app.model.reels_model import ReelModel
from app.model.rol_model import RolModel, MODULOS_DASHBOARD_INFO, MODULO_PERMISO_MAP

bp = Blueprint('dashboard', __name__, url_prefix='/')

PERMISSION_MAP = {
    'index': {'GET'},
    'panel': {'GET'},
}


@bp.before_request
def before_request():
    endpoint = request.endpoint.rsplit('.', 1)[-1]
    if endpoint == 'index':
        return
    if not current_user.is_authenticated:
        return jsonify({'error': 'No autenticado'}), 401
    perm = PERMISSION_MAP.get(endpoint, set())
    if request.method not in perm:
        return jsonify({'error': 'Sin permiso'}), 403


@bp.route('/')
def index():
    return redirect(url_for('auth.login'))


@bp.route('/dashboard')
def panel():
    total_sockets = len(usuarios_conectados)
    envivo_model = EnVivoModel()
    guion = envivo_model.obtener_en_vivo_actual()
    live = {'activo': False}
    if guion:
        elem_model = ElementoGuionModel()
        elementos = elem_model.consultar(guion_id=guion['id'])
        completados = len([e for e in elementos if e['estado'] == 'completado'])
        en_curso = [e for e in elementos if e['estado'] == 'en_curso']
        actual = en_curso[0] if en_curso else None
        siguientes = []
        if actual:
            idx = next((i for i, e in enumerate(elementos) if e['id'] == actual['id']), -1)
            siguientes = elementos[idx + 1:idx + 4] if idx >= 0 else []
        live = {
            'activo': True,
            'id': guion['id'],
            'nombre': guion['nombre'],
            'completados': completados,
            'total': len(elementos),
            'elemento_actual': actual,
            'siguientes': siguientes,
        }

    modulos_visibles = set()
    for mk, permiso in MODULO_PERMISO_MAP.items():
        if current_user.tiene_permiso(permiso):
            modulos_visibles.add(mk)

    metricas = {}
    guion_model = GuionModel()
    premio_model = PremioModel()
    contrato_model = ContratoModel()
    patrocinador_model = PatrocinadorModel()
    balance_model = BalanceModel()
    recurso_model = RecursoModel()
    tarea_asig_model = TareasAsignadasModel()
    usuario_model = UsuarioModel()

    if 'guion' in modulos_visibles:
        metricas['guion'] = {
            'borrador': guion_model.contar(estado='borrador'),
            'publicado': guion_model.contar(estado='publicado'),
            'en_vivo': guion_model.contar(estado='en_vivo'),
        }

    if 'mantenimiento' in modulos_visibles:
        metricas['mantenimiento'] = {
            'en_mantenimiento': recurso_model.contar(estado_id=3),
            'disponible': recurso_model.contar(estado_id=1),
            'baja': recurso_model.contar(estado_id=5),
        }

    if 'premio' in modulos_visibles:
        metricas['premio'] = {
            'pendiente': premio_model.contar(estado='pendiente'),
            'entregado': premio_model.contar(estado='entregado'),
        }

    if 'contrato' in modulos_visibles:
        contratos = contrato_model.consultar(activos=True)
        metricas['contrato'] = {
            'vigentes': len([c for c in contratos if getattr(c, 'estatus', None) == 'Vigente']),
            'borrador': len([c for c in contratos if getattr(c, 'estatus', None) == 'Borrador']),
            'total': len(contratos),
        }

    if 'balance' in modulos_visibles:
        metricas['balance'] = {
            'total_pagado': balance_model.get_total_pagado_general(),
        }

    if 'tarea' in modulos_visibles:
        tareas_usuario = tarea_asig_model.obtener_por_usuario(current_user.id)
        metricas['tarea'] = {
            'pendientes': len([t for t in tareas_usuario if t.get('Estado', 'Pendiente') != 'Completada']),
            'completadas': len([t for t in tareas_usuario if t.get('Estado') == 'Completada']),
        }

    if 'patrocinador' in modulos_visibles:
        patro = patrocinador_model.consultar(activos=True)
        metricas['patrocinador'] = {'activos': len(patro)}

    if 'usuario' in modulos_visibles:
        metricas['usuario'] = {'total': usuario_model.contar()}

    if 'inventario' in modulos_visibles:
        inv_model = InventarioModel()
        todos = inv_model.consultar()
        disponibles = inv_model.consultar(estado_id=1)
        metricas['inventario'] = {
            'total': len(todos),
            'disponibles': len(disponibles),
        }

    if 'reels' in modulos_visibles:
        reel_model = ReelModel()
        reels = reel_model.consultar()
        metricas['reels'] = {'total': len(reels)}

    if 'rol' in modulos_visibles:
        rol_m = RolModel()
        metricas['rol'] = {'roles': len(rol_m.consultar())}

    actividad_model = ActividadModel()
    actividad = actividad_model.consultar(limite=20) if 'actividad' in modulos_visibles else []

    usuarios_info = []
    for u in usuarios_conectados.values():
        path = u.get('pagina', '/')
        if path.startswith('/dashboard'):
            modulo = 'Inicio'
        elif path.startswith('/usuario'):
            modulo = 'Usuarios'
        elif path.startswith('/guion'):
            modulo = 'Gestión de Guión'
        elif path.startswith('/en-vivo'):
            modulo = 'Guion en Vivo'
        elif path.startswith('/contrato'):
            modulo = 'Contratos'
        elif path.startswith('/patrocinador'):
            modulo = 'Patrocinantes'
        elif path.startswith('/premio'):
            modulo = 'Premios'
        elif path.startswith('/mantenimiento'):
            modulo = 'Mantenimiento'
        elif path.startswith('/gestion-tarea'):
            modulo = 'Tareas'
        elif path.startswith('/balance'):
            modulo = 'Balance'
        elif path.startswith('/bitacora'):
            modulo = 'Bitácora'
        elif path.startswith('/roles'):
            modulo = 'Roles'
        elif path.startswith('/inventario'):
            modulo = 'Inventario'
        elif path.startswith('/reels'):
            modulo = 'Reels'
        else:
            modulo = path
        usuarios_info.append({
            'nombre': u.get('nombre', 'Desconocido'),
            'modulo': modulo,
            'en_vivo': u.get('en_vivo_id') is not None
        })

    return render_template('dashboard/index.html',
                           usuarios_en_linea=total_sockets,
                           usuarios_info=usuarios_info,
                           live=live,
                           metricas=metricas,
                           actividad=actividad,
                           modulos_visibles=modulos_visibles,
                           modulos_dashboard_info=MODULOS_DASHBOARD_INFO)
