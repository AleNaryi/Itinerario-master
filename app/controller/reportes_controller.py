import os
import logging
from datetime import datetime, timedelta, date
from flask import Blueprint, Response, render_template, request, jsonify, send_file
from flask_login import current_user
from app.helpers.decorators import verificar_acceso
from app.model.reportes_model import ReporteModel

bp = Blueprint('reportes', __name__, url_prefix='/reportes')

PERMISSION_MAP = {
    'reportes.dashboard': 'dashboard.view',
}

bp.before_request(verificar_acceso(PERMISSION_MAP))


MODULOS_DISPONIBLES = {
    'guiones': {'nombre': 'Guiones', 'icono': 'fa-scroll'},
    'inventario': {'nombre': 'Inventario', 'icono': 'fa-boxes'},
    'premios': {'nombre': 'Premios', 'icono': 'fa-gift'},
    'contratos': {'nombre': 'Contratos', 'icono': 'fa-file-contract'},
    'balance': {'nombre': 'Balance / Pagos', 'icono': 'fa-balance-scale'},
    'tareas': {'nombre': 'Tareas', 'icono': 'fa-tasks'},
    'patrocinadores': {'nombre': 'Patrocinadores', 'icono': 'fa-handshake'},
    'usuarios': {'nombre': 'Usuarios', 'icono': 'fa-users'},
    'mantenimiento': {'nombre': 'Mantenimiento', 'icono': 'fa-tools'},
    'reels': {'nombre': 'Reels', 'icono': 'fa-video'},
    'bitacora': {'nombre': 'Bitácora', 'icono': 'fa-history'},
}

# Whitelist de filtros aceptados por módulo (claves de request.form).
# Claves fuera de este set se DESCARTAN: no filtran ni aparecen en el header del PDF.
FECHAS = {'fecha_inicio', 'fecha_fin'}
FILTROS_PERMITIDOS = {
    'guiones': {'estado', 'encargado', 'elementos_min', 'elementos_max'},
    'inventario': {'tipo_nombre', 'estado_nombre', 'costo_min', 'costo_max'},
    'premios': {'estado', 'patrocinador_id', 'cantidad_min', 'cantidad_max',
                'cantidad_entregada_min', 'cantidad_entregada_max'},
    'contratos': {'tipo', 'estatus', 'patrocinador_id', 'monto_min', 'monto_max'},
    'balance': {'tipo_pago', 'patrocinador_id', 'monto_min', 'monto_max'},
    'tareas': {'estado', 'asignado_a', 'usuario_id'},  # usuario_id = clave legacy
    'patrocinadores': {'tipo_contrato', 'estado_pat'},
    'usuarios': {'departamento', 'rol', 'activo'},
    'mantenimiento': {'estado', 'recurso_id', 'dias_min', 'dias_max'},
    'reels': {'patrocinador_id', 'duracion_min', 'duracion_max'},
    'bitacora': {'usuario_id', 'tipo_accion', 'modulo_filter'},
}
for _m, _claves in FILTROS_PERMITIDOS.items():
    FILTROS_PERMITIDOS[_m] = _claves | FECHAS


def _filtros_del_request(modulo, excluir=()):
    """Extrae filtros del form aplicando whitelist por módulo."""
    permitidos = FILTROS_PERMITIDOS.get(modulo, set())
    return {k: v for k, v in request.form.items()
            if k not in excluir and k in permitidos and v}



def _filtros_contratos(params):
    from app.model.contrato_model import ContratoModel
    from app.model.patrocinador_model import PatrocinadorModel
    
    tipo = params.get('tipo')
    
    patrocinadores = PatrocinadorModel().consultar()
    if tipo and tipo in TIPO_CONTRATO_MAP:
        contratos = ContratoModel().consultar()
        ids_con_tipo = {c['id_patrocinador'] for c in contratos if str(c.get('tipo', '')) == tipo}
        patrocinadores = [p for p in patrocinadores if p['id_patrocinador'] in ids_con_tipo]
    
    kpi_ranges = {'monto_min': 0, 'monto_max': 9999999}
    try:
        db = ContratoModel()._get_db()
        with db.cursor() as cur:
            cur.execute("SELECT MIN(monto_total), MAX(monto_total) FROM contrato WHERE estado = 1")
            row = cur.fetchone()
            if row and row[0]:
                kpi_ranges = {'monto_min': float(row[0]), 'monto_max': float(row[1])}
    except Exception:
        logger.exception('Error no controlado')
    
    fecha_min = None
    fecha_max = None
    try:
        db = ContratoModel()._get_db()
        with db.cursor() as cur:
            cur.execute("SELECT MIN(fecha_inicio), MAX(fecha_fin) FROM contrato WHERE estado = 1")
            row = cur.fetchone()
            if row and row[0]:
                fecha_min = row[0].strftime('%Y-%m-%d') if hasattr(row[0], 'strftime') else str(row[0])[:10]
                fecha_max = row[1].strftime('%Y-%m-%d') if hasattr(row[1], 'strftime') else str(row[1])[:10]
    except Exception:
        logger.exception('Error no controlado')
    
    return jsonify({
        'patrocinadores': [{'id': p['id_patrocinador'], 'nombre': p['nombre_empresa']} for p in patrocinadores],
        'tipos': [{'value': k, 'label': v} for k, v in TIPO_CONTRATO_MAP.items()],
        'estatus': ['Borrador', 'Vigente', 'Vencido'],
        'monto_min': kpi_ranges['monto_min'],
        'monto_max': kpi_ranges['monto_max'],
        'fecha_min': fecha_min or '',
        'fecha_max': fecha_max or '',
    })


def _filtros_guiones(params):
    ESTADOS = ['borrador', 'publicado', 'en_vivo', 'finalizado']
    encargados = []
    try:
        from app.model.guion_model import GuionModel
        db = GuionModel()._get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT encargado FROM elementos_guion "
                "WHERE encargado IS NOT NULL AND encargado != '' ORDER BY encargado"
            )
            encargados = [r['encargado'] for r in cur.fetchall()]
    except Exception:
        logger.exception('Error cargando encargados para filtros de guiones')
    return jsonify({
        'estados': [{'value': s, 'label': s.capitalize()} for s in ESTADOS],
        'encargados': encargados,
    })


def _filtros_inventario(params):
    from app.model.inventario_model import InventarioModel
    try:
        model = InventarioModel()
        db = model._get_db()
        tipo_filter = params.get('tipo_nombre', '')
        with db.cursor() as cur:
            if tipo_filter:
                cur.execute("SELECT id FROM tipo_recurso WHERE nombre = %s", (tipo_filter,))
                row = cur.fetchone()
                tipo_id = row['id'] if row else None
            else:
                tipo_id = None
            cur.execute("""
                SELECT DISTINCT t.id, t.nombre
                FROM tipo_recurso t
                JOIN recursos r ON r.tipo_id = t.id
                WHERE r.eliminado = 0
                ORDER BY t.nombre
            """)
            tipos = [r['nombre'] for r in cur.fetchall()]
            if tipo_id:
                cur.execute("""
                    SELECT DISTINCT e.id, e.nombre
                    FROM estado_recurso e
                    JOIN recursos r ON r.estado_id = e.id
                    WHERE r.eliminado = 0 AND r.tipo_id = %s
                    ORDER BY e.nombre
                """, (tipo_id,))
            else:
                cur.execute("""
                    SELECT DISTINCT e.id, e.nombre
                    FROM estado_recurso e
                    JOIN recursos r ON r.estado_id = e.id
                    WHERE r.eliminado = 0
                    ORDER BY e.nombre
                """)
            estados = [r['nombre'] for r in cur.fetchall()]
            cur.execute("SELECT MIN(costo), MAX(costo) FROM recursos WHERE eliminado = 0")
            row = cur.fetchone()
            costo_min = float(row[0]) if row and row[0] is not None else 0
            costo_max = float(row[1]) if row and row[1] is not None else 999999
        return jsonify({'tipos': tipos, 'estados': estados, 'costo_min': costo_min, 'costo_max': costo_max})
    except Exception as e:
        logger.exception('Error cargando filtros de inventario')
        return jsonify({'tipos': [], 'estados': [], 'costo_min': 0, 'costo_max': 999999})


def _filtros_premios(params):
    from app.model.patrocinador_model import PatrocinadorModel
    from app.model.premio_model import PremioModel
    patrocinadores = PatrocinadorModel().consultar()

    # progresividad estado -> patrocinador: solo patrocinadores con premios en ese estado
    estado = params.get('estado')
    if estado in ('pendiente', 'entregado'):
        try:
            db = PremioModel()._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT id_patrocinador FROM premios "
                    "WHERE estado = %s AND id_patrocinador IS NOT NULL",
                    (estado,)
                )
                ids_con_estado = {r['id_patrocinador'] for r in cur.fetchall()}
            patrocinadores = [p for p in patrocinadores if p['id_patrocinador'] in ids_con_estado]
        except Exception:
            logger.exception('Error filtrando patrocinadores por estado de premio')

    rangos = {'cantidad_min': 0, 'cantidad_max': 999999,
              'cantidad_entregada_min': 0, 'cantidad_entregada_max': 999999}
    try:
        db = PremioModel()._get_db()
        with db.cursor() as cur:
            cur.execute(
                "SELECT MIN(cantidad), MAX(cantidad), MIN(cantidad_entregada), "
                "MAX(cantidad_entregada) FROM premios WHERE estatus = FALSE"
            )
            row = cur.fetchone()
            if row and row[0] is not None:
                rangos = {'cantidad_min': int(row[0]), 'cantidad_max': int(row[1]),
                          'cantidad_entregada_min': int(row[2] or 0),
                          'cantidad_entregada_max': int(row[3] or 0)}
    except Exception:
        logger.exception('Error cargando rangos de cantidades de premios')

    return jsonify({
        'patrocinadores': [{'id': p['id_patrocinador'], 'nombre': p['nombre_empresa']} for p in patrocinadores],
        'cantidad_min': rangos['cantidad_min'],
        'cantidad_max': rangos['cantidad_max'],
        'cantidad_entregada_min': rangos['cantidad_entregada_min'],
        'cantidad_entregada_max': rangos['cantidad_entregada_max'],
    })


def _filtros_balance(params):
    from app.model.balance_model import BalanceModel
    from app.model.patrocinador_model import PatrocinadorModel
    try:
        db = BalanceModel()._get_db()
        tipos = []
        with db.cursor() as cur:
            # ponytail: antes consultaba 'pagos_contratos' (tabla inexistente) y el filtro cargaba vacío
            cur.execute("SELECT DISTINCT tipo_pago FROM pagos WHERE tipo_pago IS NOT NULL ORDER BY tipo_pago")
            tipos = [r['tipo_pago'] for r in cur.fetchall()]
        rangos = {'monto_min': 0, 'monto_max': 99999999}
        with db.cursor() as cur:
            cur.execute("SELECT MIN(monto), MAX(monto) FROM pagos")
            row = cur.fetchone()
            if row and row[0]:
                rangos = {'monto_min': float(row[0]), 'monto_max': float(row[1])}
        patrocinadores = PatrocinadorModel().consultar()
        return jsonify({
            'tipos_pago': tipos,
            'patrocinadores': [{'id': p['id_patrocinador'], 'nombre': p['nombre_empresa']} for p in patrocinadores],
            'monto_min': rangos['monto_min'],
            'monto_max': rangos['monto_max'],
        })
    except Exception:
        logger.exception('Error cargando filtros de balance')
        return jsonify({'tipos_pago': [], 'patrocinadores': [], 'monto_min': 0, 'monto_max': 99999999})


def _filtros_tareas(params):
    from app.model.auth_model import UsuarioModel
    ESTADOS = ['Pendiente', 'En Progreso', 'Completada']
    usuarios = [{'id': u.id, 'nombre': u.nombre} for u in UsuarioModel().consultar() if hasattr(u, 'id')]

    # progresividad estado -> usuario asignado: solo usuarios con tareas en ese estado
    estado = params.get('estado')
    if estado in ESTADOS:
        try:
            from app.model.tarea_model import TareasAsignadasModel
            db = TareasAsignadasModel()._get_db()
            with db.cursor() as cur:
                cur.execute(
                    "SELECT DISTINCT u.id, u.nombre FROM tareas_asignadas ta "
                    "JOIN seguridad.usuarios u ON u.id = ta.id_usuario "
                    "WHERE ta.Estado = %s AND ta.Estatus = 1 ORDER BY u.nombre",
                    (estado,)
                )
                usuarios = [{'id': r['id'], 'nombre': r['nombre']} for r in cur.fetchall()]
        except Exception:
            logger.exception('Error filtrando usuarios por estado de tarea')

    return jsonify({
        'usuarios': usuarios,
        'estados': ESTADOS,
    })


def _filtros_patrocinadores(params):
    return jsonify({
        'tipos_contrato': [{'value': '1', 'label': 'Vigente'}, {'value': '2', 'label': 'Vencido'}],
    })


def _filtros_usuarios(params):
    from app.model.auth_model import UsuarioModel
    try:
        db = UsuarioModel()._get_db()
        roles = []
        deptos = []
        with db.cursor() as cur:
            # progresividad departamento -> rol: roles dentro del departamento elegido
            departamento = params.get('departamento')
            if departamento:
                cur.execute(
                    "SELECT DISTINCT rol FROM usuarios WHERE rol IS NOT NULL "
                    "AND departamento = %s ORDER BY rol",
                    (departamento,)
                )
            else:
                cur.execute("SELECT DISTINCT rol FROM usuarios WHERE rol IS NOT NULL ORDER BY rol")
            roles = [r['rol'] for r in cur.fetchall()]
            cur.execute("SELECT DISTINCT departamento FROM usuarios WHERE departamento IS NOT NULL ORDER BY departamento")
            deptos = [r['departamento'] for r in cur.fetchall()]
        return jsonify({'roles': roles, 'departamentos': deptos})
    except Exception:
        logger.exception('Error cargando filtros de usuarios')
        return jsonify({'roles': [], 'departamentos': []})


def _filtros_mantenimiento(params):
    from app.model.mantenimiento_model import RecursoModel, MantenimientoModel
    try:
        db = MantenimientoModel()._get_db()
        recursos = RecursoModel().consultar() if hasattr(RecursoModel(), 'consultar') else []
        estados = []
        with db.cursor() as cur:
            cur.execute("SELECT DISTINCT estado FROM mantenimientos WHERE estado IS NOT NULL ORDER BY estado")
            estados = [r['estado'] for r in cur.fetchall()]

        # progresividad estado -> recurso: solo recursos con mantenimientos en ese estado
        estado = params.get('estado')
        if estado:
            with db.cursor() as cur:
                cur.execute("SELECT DISTINCT recurso_id FROM mantenimientos WHERE estado = %s", (estado,))
                ids_con_estado = {r['recurso_id'] for r in cur.fetchall()}
            recursos = [r for r in recursos if r.get('id') in ids_con_estado]

        # pistas para el rango de días en taller
        dias_min, dias_max = 0, 365
        with db.cursor() as cur:
            cur.execute(
                "SELECT MIN(DATEDIFF(COALESCE(fecha_salida, CURDATE()), fecha_ingreso)), "
                "MAX(DATEDIFF(COALESCE(fecha_salida, CURDATE()), fecha_ingreso)) FROM mantenimientos"
            )
            row = cur.fetchone()
            if row and row[0] is not None:
                dias_min = max(int(row[0]), 0)
                dias_max = max(int(row[1]), dias_min)
        return jsonify({
            'estados': estados,
            'recursos': [{'id': r.get('id', r.get('id_recurso', '')), 'nombre': r.get('nombre', '')} for r in recursos] if recursos else [],
            'dias_min': dias_min,
            'dias_max': dias_max,
        })
    except Exception:
        logger.exception('Error cargando filtros de mantenimiento')
        return jsonify({'estados': [], 'recursos': [], 'dias_min': 0, 'dias_max': 365})


def _filtros_reels(params):
    from app.model.patrocinador_model import PatrocinadorModel
    from app.model.reels_model import ReelModel
    patrocinadores = PatrocinadorModel().consultar()

    # pistas del rango de duración en segundos (duracion_total se guarda en minutos)
    duracion_min, duracion_max = 0, 3600
    try:
        db = ReelModel()._get_db()
        with db.cursor() as cur:
            cur.execute("SELECT MIN(duracion_total), MAX(duracion_total) FROM reels")
            row = cur.fetchone()
            if row and row[0] is not None:
                duracion_min = int(float(row[0]) * 60)
                duracion_max = max(int(float(row[1]) * 60), duracion_min)
    except Exception:
        logger.exception('Error cargando rangos de duración de reels')

    return jsonify({
        'patrocinadores': [{'id': p['id_patrocinador'], 'nombre': p['nombre_empresa']} for p in patrocinadores],
        'duracion_min': duracion_min,
        'duracion_max': duracion_max,
    })


def _filtros_bitacora(params):
    from app.model.bitacora_model import ActividadModel
    model = ActividadModel()
    return jsonify({
        'usuarios': model.obtener_usuarios_distintos(),
        'acciones': model.obtener_acciones_distintas(),
        'modulos': model.obtener_modulos_distintos(),
    })


FILTROS_HANDLERS = {
    'guiones': _filtros_guiones,
    'inventario': _filtros_inventario,
    'premios': _filtros_premios,
    'contratos': _filtros_contratos,
    'balance': _filtros_balance,
    'tareas': _filtros_tareas,
    'patrocinadores': _filtros_patrocinadores,
    'usuarios': _filtros_usuarios,
    'mantenimiento': _filtros_mantenimiento,
    'reels': _filtros_reels,
    'bitacora': _filtros_bitacora,
}



from app.helpers.reportes_data import TIPO_CONTRATO_MAP
from app.helpers.reportes_utils import _ordenar_datos, _parsear_fecha

logger = logging.getLogger(__name__)


def _obtener_datos(modulo, filtros):
    """Despacha por módulo; la lógica vive en app/helpers/reportes_data.py."""
    from app.helpers.reportes_data import OBTENEDORES, rango_fechas_defecto
    ob = OBTENEDORES.get(modulo)
    if not ob:
        return [], {}
    fi, ff = rango_fechas_defecto(modulo, filtros)
    return ob(filtros, fi, ff)

COLUMNAS_PREVIEW = {
    'guiones': [
        {'key': 'nombre', 'label': 'Nombre'},
        {'key': 'game', 'label': 'Game'},
        {'key': 'pregame', 'label': 'Pre-Game'},
        {'key': 'fecha_ejecucion', 'label': 'Ejecución'},
        {'key': 'estado', 'label': 'Estado'},
        {'key': 'tiempo_total', 'label': 'Tiempo'},
    ],
    'inventario': [
        {'key': 'id', 'label': 'ID'},
        {'key': 'nombre', 'label': 'Nombre'},
        {'key': 'tipo_nombre', 'label': 'Tipo'},
        {'key': 'estado_nombre', 'label': 'Estado'},
        {'key': 'costo', 'label': 'Costo'},
        {'key': 'fecha_compra', 'label': 'Fecha Compra'},
    ],
    'patrocinadores': [
        {'key': 'nombre_empresa', 'label': 'Empresa'},
        {'key': 'rif', 'label': 'RIF'},
        {'key': 'telefono', 'label': 'Teléfono'},
        {'key': 'tipo_contrato', 'label': 'Contrato'},
        {'key': 'estado', 'label': 'Activo'},
    ],
    'contratos': [
        {'key': 'nombre_empresa', 'label': 'Patrocinador'},
        {'key': 'tipo', 'label': 'Tipo'},
        {'key': 'estatus', 'label': 'Estatus'},
        {'key': 'monto_total', 'label': 'Monto'},
        {'key': 'fecha_inicio', 'label': 'Inicio'},
        {'key': 'fecha_fin', 'label': 'Fin'},
        {'key': 'dias_restantes', 'label': 'Días Restantes'},
    ],
    'balance': [
        {'key': 'nombre_patrocinador', 'label': 'Patrocinador'},
        {'key': 'tipo_pago', 'label': 'Tipo Pago'},
        {'key': 'monto', 'label': 'Monto'},
        {'key': 'referencia', 'label': 'Referencia'},
        {'key': 'fecha_pago', 'label': 'Fecha Pago'},
    ],
    'premios': [
        {'key': 'nombre', 'label': 'Nombre'},
        {'key': 'patrocinador_nombre', 'label': 'Patrocinador'},
        {'key': 'estado', 'label': 'Estado'},
        {'key': 'cantidad', 'label': 'Total'},
        {'key': 'cantidad_entregada', 'label': 'Entregados'},
        {'key': 'fecha_creacion', 'label': 'Creación'},
    ],
    'tareas': [
        {'key': 'nombre_tarea', 'label': 'Tarea'},
        {'key': 'estado', 'label': 'Estado'},
        {'key': 'asignado_a', 'label': 'Asignado a'},
        {'key': 'fecha_asignacion_tarea', 'label': 'Fecha'},
    ],
    'usuarios': [
        {'key': 'nombre', 'label': 'Nombre'},
        {'key': 'email', 'label': 'Email'},
        {'key': 'rol', 'label': 'Rol'},
        {'key': 'departamento', 'label': 'Depto'},
        {'key': 'activo', 'label': 'Estado'},
    ],
    'mantenimiento': [
        {'key': 'recurso_nombre', 'label': 'Recurso'},
        {'key': 'estado', 'label': 'Estado'},
        {'key': 'fecha_ingreso', 'label': 'Ingreso'},
        {'key': 'dias_en_taller', 'label': 'Días'},
        {'key': 'diagnostico', 'label': 'Diagnóstico'},
    ],
    'reels': [
        {'key': 'nombre', 'label': 'Nombre'},
        {'key': 'patrocinado', 'label': 'Patrocinador'},
        {'key': 'videos_count', 'label': 'Videos'},
        {'key': 'duracion', 'label': 'Duración'},
        {'key': 'creado_en', 'label': 'Creado'},
    ],
    'bitacora': [
        {'key': 'usuario_nombre', 'label': 'Usuario'},
        {'key': 'tipo_accion', 'label': 'Acción'},
        {'key': 'modulo', 'label': 'Módulo'},
        {'key': 'detalle', 'label': 'Detalle'},
        {'key': 'created_at', 'label': 'Fecha'},
    ],
    'resumen': [
        {'key': 'modulo', 'label': 'Módulo'},
        {'key': 'total', 'label': 'Total'},
        {'key': 'activos', 'label': 'Activos'},
        {'key': 'inactivos', 'label': 'Inactivos'},
    ],
}


def _serializar_datos(datos):
    """Convierte datos planos a JSON-safe. Ya vienen sanitizados."""
    from decimal import Decimal
    resultado = []
    for d in datos:
        fila = {}
        for k, v in d.items():
            if isinstance(v, datetime):
                fila[k] = v.strftime('%d/%m/%Y %H:%M' if hasattr(v, 'hour') else '%d/%m/%Y')
            elif isinstance(v, Decimal):
                fila[k] = float(v)
            elif isinstance(v, (int, float, str, bool, type(None))):
                fila[k] = v
        resultado.append(fila)
    return resultado


@bp.route('/filtros/<modulo>', methods=['GET'])
def filtros_modulo(modulo):
    handler = FILTROS_HANDLERS.get(modulo)
    if handler:
        return handler(request.args)
    return jsonify({'error': 'Módulo no soportado'}), 400


@bp.route('/', methods=['GET'])
def dashboard():
    reportes = ReporteModel().listar(limite=50)
    return render_template('reportes/dashboard.html',
                           modulos=MODULOS_DISPONIBLES,
                           reportes=reportes,
                           columnas_preview=COLUMNAS_PREVIEW)


@bp.route('/filtros-bitacora', methods=['GET'])
def filtros_bitacora():
    from app.model.bitacora_model import ActividadModel
    model = ActividadModel()
    return jsonify({
        'usuarios': model.obtener_usuarios_distintos(),
        'acciones': model.obtener_acciones_distintas(),
        'modulos': model.obtener_modulos_distintos(),
    })


@bp.route('/preview', methods=['POST'])
def preview():
    modulo = request.form.get('modulo', '')
    if modulo not in MODULOS_DISPONIBLES:
        return jsonify({'error': 'Módulo no válido'}), 400
    try:
        filtros = _filtros_del_request(modulo, excluir=('modulo', 'csrf_token', 'sort_by', 'sort_dir'))

        sort_by = request.form.get('sort_by', '')
        sort_dir = request.form.get('sort_dir', 'asc')

        datos, kpis = _obtener_datos(modulo, filtros)
        datos = _ordenar_datos(datos, sort_by, sort_dir)
        cols = COLUMNAS_PREVIEW.get(modulo)
        if cols:
            col_keys = [c['key'] for c in cols]
            datos = [{k: d.get(k) for k in col_keys} for d in datos]
        datos_serializados = _serializar_datos(datos)

        kpis_display = {}
        for k, v in kpis.items():
            if isinstance(v, (dict, list)):
                continue
            kpis_display[k] = v

        resp = {
            'datos': datos_serializados[:100],
            'total': len(datos),
            'kpis': kpis_display,
            'modulo': MODULOS_DISPONIBLES[modulo]['nombre'],
        }
        if cols:
            resp['columnas'] = cols
        return jsonify(resp)
    except Exception as e:
        logger.exception('Error no controlado')
        return jsonify({'error': f'Error al cargar datos: {str(e)}'}), 500


@bp.route('/generar', methods=['POST'])
def generar():
    modulo = request.form.get('modulo', '')
    if modulo not in MODULOS_DISPONIBLES:
        return jsonify({'error': 'Módulo no válido'}), 400
    try:
        OPCIONES_FORM = ('resumen', 'comparar', 'top_n')
        filtros = _filtros_del_request(
            modulo, excluir=('modulo', 'csrf_token', 'sort_by', 'sort_dir', *OPCIONES_FORM))

        # análisis opcional del PDF (whitelist server-side)
        opciones = {
            'resumen': request.form.get('resumen') == '1',
            'comparar': request.form.get('comparar') == '1',
        }
        try:
            top_n = int(request.form.get('top_n') or 0)
        except ValueError:
            top_n = 0
        if 1 <= top_n <= 20:
            opciones['top_n'] = top_n

        sort_by = request.form.get('sort_by', '')
        sort_dir = request.form.get('sort_dir', 'asc')

        datos, kpis = _obtener_datos(modulo, filtros)
        if not datos:
            return jsonify({'error': 'No hay datos para los filtros seleccionados'}), 400

        # comparativa: misma consulta con el rango desplazado hacia atrás
        if opciones['comparar']:
            fi = _parsear_fecha(filtros.get('fecha_inicio', ''))
            ff = _parsear_fecha(filtros.get('fecha_fin', ''))
            if fi and ff and ff > fi:
                delta = ff - fi
                filtros_previos = dict(filtros)
                filtros_previos['fecha_inicio'] = (fi - delta).strftime('%Y-%m-%d')
                filtros_previos['fecha_fin'] = (fi - timedelta(days=1)).strftime('%Y-%m-%d')
                try:
                    _, kpis_previos = _obtener_datos(modulo, filtros_previos)
                    opciones['kpis_previos'] = kpis_previos
                except Exception:
                    logger.exception('Error calculando período anterior para comparativa')

        datos = _ordenar_datos(datos, sort_by, sort_dir)
        if sort_by:
            label = sort_by
            cols = COLUMNAS_PREVIEW.get(modulo, [])
            for c in cols:
                if c['key'] == sort_by:
                    label = c['label']
                    break
            dir_label = 'Descendente' if sort_dir == 'desc' else 'Ascendente'
            filtros['orden'] = f"{label} ({dir_label})"

        generadores = {
            'guiones': lambda: __import__('app.helpers.generators.guiones_report', fromlist=['GuionesReport']).GuionesReport(current_user),
            'inventario': lambda: __import__('app.helpers.generators.inventario_report', fromlist=['InventarioReport']).InventarioReport(current_user),
            'premios': lambda: __import__('app.helpers.generators.premios_report', fromlist=['PremiosReport']).PremiosReport(current_user),
            'contratos': lambda: __import__('app.helpers.generators.contratos_report', fromlist=['ContratosReport']).ContratosReport(current_user),
            'balance': lambda: __import__('app.helpers.generators.balance_report', fromlist=['BalanceReport']).BalanceReport(current_user),
            'tareas': lambda: __import__('app.helpers.generators.tareas_report', fromlist=['TareasReport']).TareasReport(current_user),
            'patrocinadores': lambda: __import__('app.helpers.generators.patrocinadores_report', fromlist=['PatrocinadoresReport']).PatrocinadoresReport(current_user),
            'usuarios': lambda: __import__('app.helpers.generators.usuarios_report', fromlist=['UsuariosReport']).UsuariosReport(current_user),
            'mantenimiento': lambda: __import__('app.helpers.generators.mantenimiento_report', fromlist=['MantenimientoReport']).MantenimientoReport(current_user),
            'reels': lambda: __import__('app.helpers.generators.reels_report', fromlist=['ReelsReport']).ReelsReport(current_user),
            'bitacora': lambda: __import__('app.helpers.generators.bitacora_report', fromlist=['BitacoraReport']).BitacoraReport(current_user),
            'resumen': lambda: __import__('app.helpers.generators.resumen_report', fromlist=['ResumenReport']).ResumenReport(current_user),
        }

        if modulo not in generadores:
            return jsonify({'error': 'Generador no disponible'}), 400

        generador = generadores[modulo]()
        pdf_bytes = generador.generate(datos, filtros=filtros, kpis=kpis, opciones=opciones)
        ruta, nombre = generador.save(pdf_bytes, current_user.id, filtros)

        return jsonify({
            'mensaje': 'Reporte generado exitosamente',
            'descargar': f'/reportes/descargar/{nombre}',
        })
    except Exception as e:
        logger.exception('Error no controlado')
        return jsonify({'error': f'Error al generar reporte: {str(e)}'}), 500


@bp.route('/descargar/<nombre>', methods=['GET'])
def descargar(nombre):
    reportes = ReporteModel().listar()
    reporte = next((r for r in reportes if r['archivo_ruta'].endswith(nombre)), None)
    if not reporte:
        return jsonify({'error': 'Reporte no encontrado'}), 404

    base_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'reportes')
    filepath = os.path.join(base_dir, reporte['archivo_ruta'])
    if not os.path.exists(filepath):
        return jsonify({'error': 'Archivo no encontrado'}), 404

    return send_file(filepath, as_attachment=True, download_name=reporte['archivo_nombre'])


@bp.route('/eliminar/<int:id>', methods=['POST'])
def eliminar(id):
    ok = ReporteModel().eliminar(id)
    if ok:
        return jsonify({'mensaje': 'Reporte eliminado exitosamente'})
    return jsonify({'error': 'Error al eliminar reporte'}), 400


# ──────────────────────────────────────────────
# CONSTRUCTOR DE REPORTES (arquitectura: docs/ARQUITECTURA_CONSTRUCTOR_REPORTES.md)
# ──────────────────────────────────────────────
@bp.route('/catalogo/<modulo>', methods=['GET'])
def catalogo_modulo(modulo):
    from app.helpers.reportes_catalogo import catalogo_publico
    publico = catalogo_publico(modulo)
    if not publico:
        return jsonify({'error': 'Módulo no disponible en el constructor'}), 400
    return jsonify(publico)


@bp.route('/construir', methods=['POST'])
def construir():
    from app.helpers.reportes_constructor import ConstructorError, ejecutar
    peticion = request.get_json(silent=True) or {}
    modulo = peticion.get('modulo', '')
    if modulo not in MODULOS_DISPONIBLES:
        return jsonify({'error': 'Módulo no válido'}), 400
    try:
        dataset = ejecutar(modulo, peticion)
    except ConstructorError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        logger.exception('Error no controlado')
        return jsonify({'error': 'Error al construir el reporte'}), 500
    return jsonify(dataset)


@bp.route('/construir/exportar', methods=['POST'])
def construir_exportar():
    """PDF (ConstructorReport) o CSV desde la misma petición del preview."""
    import csv
    import io
    import json as jsonlib

    from app.helpers.generators.constructor_report import ConstructorReport
    from app.helpers.reportes_constructor import ConstructorError, ejecutar

    peticion = request.get_json(silent=True) or {}
    formato = peticion.get('formato', 'pdf')
    if formato not in ('pdf', 'csv'):
        return jsonify({'error': 'Formato no soportado'}), 400
    modulo = peticion.get('modulo', '')
    if modulo not in MODULOS_DISPONIBLES:
        return jsonify({'error': 'Módulo no válido'}), 400

    try:
        dataset = ejecutar(modulo, peticion)
    except ConstructorError as e:
        return jsonify({'error': str(e)}), 400
    except Exception:
        logger.exception('Error no controlado')
        return jsonify({'error': 'Error al construir el reporte'}), 500

    sello = datetime.now().strftime('%Y%m%d_%H%M%S')

    if formato == 'csv':
        buffer = io.StringIO()
        writer = csv.writer(buffer)
        writer.writerow([c['label'] for c in dataset['columnas']])
        for fila in dataset['filas']:
            writer.writerow([fila.get(c['key'], '') for c in dataset['columnas']])
        buffer.seek(0)
        return Response(
            '\ufeff' + buffer.getvalue(),
            mimetype='text/csv; charset=utf-8',
            headers={'Content-Disposition':
                     f'attachment; filename=constructor_{modulo}_{sello}.csv'})

    generador = ConstructorReport(current_user)
    generador.MODULO = f'{modulo}_personalizado'
    pdf_bytes = generador.generar(dataset)
    ruta, nombre = generador.save(pdf_bytes, current_user.id,
                                  dataset.get('meta', {}).get('filtros_aplicados'))
    return jsonify({'mensaje': 'Reporte generado exitosamente',
                    'descargar': f'/reportes/descargar/{nombre}'})
