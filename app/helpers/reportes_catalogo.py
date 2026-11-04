"""Catálogo declarativo del Constructor de Reportes — CAPA DE CONFIGURACIÓN.

Única fuente de verdad de identificadores: todo campo/alias que llega al motor
SQL (reportes_constructor.py) DEBE existir aquí o se rechaza con 400.
Arquitectura: docs/ARQUITECTURA_CONSTRUCTOR_REPORTES.md
Matriz funcional: docs/CATALOGO_REPORTES.md

Extender un análisis = añadir entradas a estos dicts. Motor y wizard no cambian.
'resumen' NO tiene constructor: su flujo legado tiene un bug latente conocido
(objeto Usuario vs dict) y no es alcanzable desde rutas — ver auditoría §12.
"""

# ── Esqueletos FROM/JOIN — SOLO FKs reales verificadas en estadio_db.sql ──
FUENTES_SQL = {
    'contratos': (
        "FROM contrato c "
        "JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador"
    ),
    'pagos': (
        "FROM pagos pg "
        "JOIN contrato c ON pg.id_contrato = c.id_contrato "
        "JOIN patrocinadores p ON c.id_patrocinador = p.id_patrocinador"
    ),
    'bitacora_actividad': (
        "FROM actividad_usuario au "
        "JOIN seguridad.usuarios u ON au.usuario_id = u.id"
    ),
    'guiones': "FROM guiones g",
    'elementos_guion': (
        "FROM elementos_guion eg "
        "JOIN guiones g ON eg.guion_id = g.id"
    ),
    'recursos': (
        "FROM recursos r "
        "LEFT JOIN tipo_recurso t ON r.tipo_id = t.id "
        "LEFT JOIN estado_recurso e ON r.estado_id = e.id"
    ),
    'asignaciones': (
        "FROM asignaciones_recursos a "
        "JOIN seguridad.usuarios u ON a.usuario_id = u.id"
    ),
    'premios': (
        "FROM premios p2 "
        "LEFT JOIN patrocinadores pat ON p2.id_patrocinador = pat.id_patrocinador"
    ),
    'tareas_carga': (
        "FROM tareas_asignadas ta "
        "JOIN tareas t ON ta.id_tarea = t.id_tarea "
        "JOIN seguridad.usuarios u ON u.id = ta.id_usuario"
    ),
    'patrocinadores': (
        "FROM patrocinadores pa "
        "LEFT JOIN seguridad.usuarios ue ON ue.id = pa.encargado_id"
    ),
    'usuarios_sistema': "FROM usuarios us",
    'mantenimientos': (
        "FROM mantenimientos m "
        "JOIN recursos r ON m.recurso_id = r.id"
    ),
    'reels': (
        "FROM reels re "
        "LEFT JOIN patrocinadores rp ON re.id_patrocinador = rp.id_patrocinador"
    ),
    'reels_videos': (
        "FROM videos v "
        "JOIN reels re ON v.reel_id = re.id "
        "LEFT JOIN patrocinadores rp ON re.id_patrocinador = rp.id_patrocinador"
    ),
}

# Conexión que usa cada fuente (dos esquemas: negocio y seguridad)
FUENTE_SCHEMA = {
    'bitacora_actividad': 'seguridad',
    'usuarios_sistema': 'seguridad',
}
DEFAULT_SCHEMA = 'estadio_db'

# Soft-delete / vigencia por fuente (flags heterogéneos documentados en el esquema)
SOFT_DELETE = {
    'contratos': 'c.estado = 1',
    'pagos': 'pg.estado = 0',
    'bitacora_actividad': None,
    'guiones': 'g.status = 1',
    'elementos_guion': 'g.status = 1',
    'recursos': 'r.eliminado = 0',
    'asignaciones': None,
    'premios': 'p2.estatus = FALSE',
    'tareas_carga': 'ta.Estatus = 1 AND t.Estatus = 1',
    'patrocinadores': None,
    'usuarios_sistema': None,
    'mantenimientos': None,
    'reels': None,
    'reels_videos': None,
}

# Aliases válidos por fuente (documentación ejecutable; el test de consistencia
# verifica que toda dimensión/métrica use uno de estos prefijos)
FUENTE_ALIASES = {
    'contratos': {'c', 'p'},
    'pagos': {'pg', 'c', 'p'},
    'bitacora_actividad': {'au', 'u'},
    'guiones': {'g'},
    'elementos_guion': {'eg', 'g'},
    'recursos': {'r', 't', 'e'},
    'asignaciones': {'a', 'u'},
    'premios': {'p2', 'pat'},
    'tareas_carga': {'ta', 't', 'u'},
    'patrocinadores': {'pa', 'ue'},
    'usuarios_sistema': {'us'},
    'mantenimientos': {'m', 'r'},
    'reels': {'re', 'rp'},
    'reels_videos': {'v', 're', 'rp'},
}

GRANOS_TEMPORALES = {
    'dia': '%Y-%m-%d',
    'semana': '%x-W%v',
    'mes': '%Y-%m',
    'ano': '%Y',
}

LIMITE_FILAS = 500  # salvaguarda por consulta; meta.limit_alcanzado lo reporta

# ── Dimensiones: sql SIEMPRE calificado con alias de su(s) fuente(s) ──
DIMENSIONES = {
    # contratos / pagos
    'patrocinador': {'tipo': 'entidad', 'sql': 'p.nombre_empresa', 'label': 'Patrocinador'},
    'nivel': {'tipo': 'mapa', 'sql': 'c.tipo',
              'mapa': {'1': 'Bronce', '2': 'Plata', '3': 'Oro'}, 'label': 'Nivel'},
    'estatus': {'tipo': 'entidad', 'sql': 'c.estatus', 'label': 'Estatus'},
    'mes_contrato': {'tipo': 'temporal', 'sql': 'c.fecha_inicio', 'label': 'Por mes'},
    'tipo_pago': {'tipo': 'entidad', 'sql': 'pg.tipo_pago', 'label': 'Tipo de pago'},
    'mes_pago': {'tipo': 'temporal', 'sql': 'pg.fecha_pago', 'label': 'Por mes'},
    'dia_pago': {'tipo': 'temporal', 'sql': 'pg.fecha_pago', 'label': 'Por día'},
    # bitácora
    'usuario_bitacora': {'tipo': 'entidad', 'sql': 'u.nombre', 'label': 'Usuario'},
    'accion': {'tipo': 'mapa', 'sql': 'au.tipo_accion',
               'mapa': {'create': 'Creación', 'update': 'Edición',
                        'delete': 'Eliminación', 'login': 'Login', 'logout': 'Logout'},
               'label': 'Acción'},
    'modulo_bitacora': {'tipo': 'entidad', 'sql': 'au.modulo', 'label': 'Módulo'},
    'dia_bitacora': {'tipo': 'temporal', 'sql': 'au.created_at', 'label': 'Por día'},
    # guiones / elementos
    'g_estado': {'tipo': 'entidad', 'sql': 'g.estado', 'label': 'Estado del guion'},
    'mes_creacion_guion': {'tipo': 'temporal', 'sql': 'g.creado_en', 'label': 'Por mes'},
    'encargado_elemento': {'tipo': 'entidad', 'sql': 'eg.encargado', 'label': 'Encargado'},
    'tipo_elemento': {'tipo': 'mapa', 'sql': 'eg.tipo',
                      'mapa': {'pregame': 'Pre-Game', 'game': 'Game'},
                      'label': 'Tipo de elemento'},
    'inning': {'tipo': 'entidad', 'sql': 'eg.inning', 'label': 'Inning'},
    'mes_elemento': {'tipo': 'temporal', 'sql': 'eg.creado_en', 'label': 'Por mes'},
    # inventario
    'inv_tipo': {'tipo': 'entidad', 'sql': 't.nombre', 'label': 'Tipo'},
    'inv_estado': {'tipo': 'entidad', 'sql': 'e.nombre', 'label': 'Estado'},
    'mes_compra': {'tipo': 'temporal', 'sql': 'r.fecha_compra', 'label': 'Por mes'},
    'asg_usuario': {'tipo': 'entidad', 'sql': 'u.nombre', 'label': 'Usuario asignado'},
    'asg_estado': {'tipo': 'entidad',
                   'sql': ("CASE WHEN a.fecha_devolucion_real IS NULL "
                           "THEN 'Activa' ELSE 'Devuelta' END"),
                   'label': 'Estado de asignación'},
    # premios
    'pr_estado': {'tipo': 'entidad', 'sql': 'p2.estado', 'label': 'Estado'},
    'pr_patrocinador': {'tipo': 'entidad', 'sql': 'pat.nombre_empresa',
                        'label': 'Patrocinador'},
    'pr_mes_creacion': {'tipo': 'temporal', 'sql': 'p2.fecha_creacion', 'label': 'Por mes'},
    'pr_mes_entrega': {'tipo': 'temporal', 'sql': 'p2.fecha_entrega', 'label': 'Por mes'},
    # tareas
    'tar_estado': {'tipo': 'entidad', 'sql': 'ta.Estado', 'label': 'Estado'},
    'tar_usuario': {'tipo': 'entidad', 'sql': 'u.nombre', 'label': 'Usuario asignado'},
    'tar_mes': {'tipo': 'temporal', 'sql': 'ta.fecha_asignacion_tarea', 'label': 'Por mes'},
    # patrocinadores
    'pat_estado': {'tipo': 'mapa', 'sql': 'pa.estado',
                   'mapa': {'1': 'Activo', '0': 'Inactivo'}, 'label': 'Estado'},
    'pat_tipo': {'tipo': 'mapa', 'sql': 'pa.tipo_contrato',
                 'mapa': {'1': 'Vigente', '2': 'Vencido'}, 'label': 'Tipo de contrato'},
    'pat_encargado': {'tipo': 'entidad', 'sql': 'ue.nombre', 'label': 'Encargado interno'},
    # usuarios
    'us_rol': {'tipo': 'entidad', 'sql': 'us.rol', 'label': 'Rol'},
    'us_departamento': {'tipo': 'entidad', 'sql': 'us.departamento', 'label': 'Departamento'},
    'us_activo': {'tipo': 'mapa', 'sql': 'us.activo',
                  'mapa': {'1': 'Activo', '0': 'Inactivo'}, 'label': 'Estado'},
    'us_mes_registro': {'tipo': 'temporal', 'sql': 'us.fecha_registro', 'label': 'Por mes'},
    # mantenimiento
    'man_estado': {'tipo': 'entidad', 'sql': 'm.estado', 'label': 'Estado'},
    'man_recurso': {'tipo': 'entidad', 'sql': 'r.nombre', 'label': 'Recurso'},
    'man_mes_ingreso': {'tipo': 'temporal', 'sql': 'm.fecha_ingreso', 'label': 'Por mes'},
    # reels
    'reel_patrocinador': {'tipo': 'entidad', 'sql': 'rp.nombre_empresa',
                          'label': 'Patrocinador'},
    'reel_mes': {'tipo': 'temporal', 'sql': 're.creado_en', 'label': 'Por mes'},
}

# ── Métricas: AGG sobre columna calificada; formato gobierna presentación ──
METRICAS = {
    'registros_conteo': {'agg': 'COUNT', 'sql': '*', 'formato': 'entero',
                         'label': 'Registros'},
    'monto_total_suma': {'agg': 'SUM', 'sql': 'c.monto_total', 'formato': 'moneda',
                         'label': 'Monto total'},
    'monto_promedio': {'agg': 'AVG', 'sql': 'c.monto_total', 'formato': 'moneda',
                       'label': 'Monto promedio'},
    'pago_suma': {'agg': 'SUM', 'sql': 'pg.monto', 'formato': 'moneda',
                  'label': 'Monto cobrado'},
    'pago_promedio': {'agg': 'AVG', 'sql': 'pg.monto', 'formato': 'moneda',
                      'label': 'Pago promedio'},
    'actividades_conteo': {'agg': 'COUNT', 'sql': '*', 'formato': 'entero',
                           'label': 'Actividades'},
    # guiones
    'elementos_conteo': {'agg': 'COUNT', 'sql': 'eg.id', 'formato': 'entero',
                         'label': 'Elementos'},
    'duracion_suma': {'agg': 'SUM', 'sql': 'eg.duracion_estimada', 'formato': 'entero',
                      'label': 'Duración total (seg)'},
    'duracion_promedio': {'agg': 'AVG', 'sql': 'eg.duracion_estimada',
                          'formato': 'decimal_1', 'label': 'Duración promedio (seg)'},
    'guiones_conteo': {'agg': 'COUNT', 'sql': 'DISTINCT g.id', 'formato': 'entero',
                       'label': 'Guiones'},
    # inventario
    'costo_suma': {'agg': 'SUM', 'sql': 'r.costo', 'formato': 'moneda',
                   'label': 'Costo total'},
    'costo_promedio': {'agg': 'AVG', 'sql': 'r.costo', 'formato': 'moneda',
                       'label': 'Costo promedio'},
    'costo_maximo': {'agg': 'MAX', 'sql': 'r.costo', 'formato': 'moneda',
                     'label': 'Costo máximo'},
    'recursos_conteo': {'agg': 'COUNT', 'sql': 'r.id', 'formato': 'entero',
                        'label': 'Recursos'},
    'antiguedad_promedio': {'agg': 'AVG', 'sql': 'DATEDIFF(CURDATE(), r.fecha_compra)',
                            'formato': 'decimal_1', 'label': 'Antigüedad media (días)'},
    'asignaciones_conteo': {'agg': 'COUNT', 'sql': 'a.id', 'formato': 'entero',
                            'label': 'Asignaciones'},
    # premios
    'premios_conteo': {'agg': 'COUNT', 'sql': 'p2.id', 'formato': 'entero',
                       'label': 'Premios'},
    'unidades_suma': {'agg': 'SUM', 'sql': 'p2.cantidad', 'formato': 'entero',
                      'label': 'Unidades totales'},
    'entregadas_suma': {'agg': 'SUM', 'sql': 'p2.cantidad_entregada',
                        'formato': 'entero', 'label': 'Unidades entregadas'},
    'pendientes_suma': {'agg': 'SUM', 'sql': '(p2.cantidad - p2.cantidad_entregada)',
                        'formato': 'entero', 'label': 'Unidades pendientes'},
    # tareas
    'asignaciones_tarea_conteo': {'agg': 'COUNT', 'sql': 'ta.id_asignacion',
                                  'formato': 'entero', 'label': 'Asignaciones'},
    'usuarios_distintos': {'agg': 'COUNT', 'sql': 'DISTINCT ta.id_usuario',
                           'formato': 'entero', 'label': 'Usuarios distintos'},
    'completadas_pct': {
        'agg': '',
        'sql': ("ROUND(100 * SUM(CASE WHEN ta.Estado = 'Completada' THEN 1 ELSE 0 END) "
                "/ COUNT(*))"),
        'formato': 'pct', 'label': '% Completadas',
        'sin_agg': True,   # el sql ya trae la agregación completa
    },
    # patrocinadores
    'patrocinadores_conteo': {'agg': 'COUNT', 'sql': 'pa.id_patrocinador',
                              'formato': 'entero', 'label': 'Empresas'},
    'activos_conteo': {'agg': 'SUM', 'sql': '(pa.estado = 1)', 'formato': 'entero',
                       'label': 'Activos'},
    # usuarios
    'usuarios_conteo': {'agg': 'COUNT', 'sql': 'us.id', 'formato': 'entero',
                        'label': 'Usuarios'},
    'usuarios_activos_conteo': {'agg': 'SUM', 'sql': '(us.activo = 1)',
                                'formato': 'entero', 'label': 'Activos'},
    # mantenimiento
    'mantenimientos_conteo': {'agg': 'COUNT', 'sql': 'm.id', 'formato': 'entero',
                              'label': 'Mantenimientos'},
    'dias_promedio': {
        'agg': 'AVG',
        'sql': 'DATEDIFF(COALESCE(m.fecha_salida, CURDATE()), m.fecha_ingreso)',
        'formato': 'decimal_1', 'label': 'Días en taller (promedio)',
    },
    'dias_maximo': {
        'agg': 'MAX',
        'sql': 'DATEDIFF(COALESCE(m.fecha_salida, CURDATE()), m.fecha_ingreso)',
        'formato': 'entero', 'label': 'Días en taller (máximo)',
    },
    # reels
    'clips_conteo': {'agg': 'COUNT', 'sql': 'v.id', 'formato': 'entero',
                     'label': 'Clips'},
    'duracion_clip_suma': {'agg': 'SUM', 'sql': 'v.duracion_segundos',
                           'formato': 'entero', 'label': 'Duración total (seg)'},
}

# ── Filtros del constructor: coerción + WHERE parametrizado (%s) ──
FILTROS_BUILDER = {
    'fecha_inicio': {'coercion': 'fecha'},
    'fecha_fin': {'coercion': 'fecha'},
    # helper para declarar UI de opciones estáticas
    # contratos / pagos
    'c_fecha': {'campo_sql': 'c.fecha_inicio', 'coercion': 'rango_fecha',
                'label': 'Fecha contrato'},
    'c_tipo': {'campo_sql': 'c.tipo', 'coercion': 'texto', 'label': 'Nivel',
               'opciones': [('1', 'Bronce'), ('2', 'Plata'), ('3', 'Oro')]},
    'c_estatus': {'campo_sql': 'c.estatus', 'coercion': 'texto', 'label': 'Estatus',
                  'opciones': [('Vigente', 'Vigente'), ('Vencido', 'Vencido'),
                               ('Borrador', 'Borrador')]},
    'c_patrocinador': {'campo_sql': 'c.id_patrocinador', 'coercion': 'entero',
                       'label': 'Patrocinador',
                       'ajax': {'url': '/reportes/filtros/contratos',
                                'clave': 'patrocinadores', 'param': 'tipo'}},
    'c_monto_min': {'campo_sql': 'c.monto_total', 'coercion': 'float_min',
                    'label': 'Monto mínimo'},
    'c_monto_max': {'campo_sql': 'c.monto_total', 'coercion': 'float_max',
                    'label': 'Monto máximo'},
    'pg_fecha': {'campo_sql': 'pg.fecha_pago', 'coercion': 'rango_fecha',
                 'label': 'Fecha de pago'},
    'pg_tipo': {'campo_sql': 'pg.tipo_pago', 'coercion': 'texto', 'label': 'Tipo de pago',
                'ajax': {'url': '/reportes/filtros/balance', 'clave': 'tipos_pago'}},
    'pg_nivel': {'campo_sql': 'c.tipo', 'coercion': 'texto', 'label': 'Nivel del contrato',
                 'opciones': [('1', 'Bronce'), ('2', 'Plata'), ('3', 'Oro')]},
    'pg_monto_min': {'campo_sql': 'pg.monto', 'coercion': 'float_min',
                     'label': 'Monto mínimo'},
    'pg_monto_max': {'campo_sql': 'pg.monto', 'coercion': 'float_max',
                     'label': 'Monto máximo'},
    # bitácora
    'b_usuario': {'campo_sql': 'au.usuario_id', 'coercion': 'entero', 'label': 'Usuario',
                  'ajax': {'url': '/reportes/filtros-bitacora', 'clave': 'usuarios'}},
    'b_accion': {'campo_sql': 'au.tipo_accion', 'coercion': 'texto', 'label': 'Acción',
                 'ajax': {'url': '/reportes/filtros-bitacora', 'clave': 'acciones'}},
    'b_modulo': {'campo_sql': 'au.modulo', 'coercion': 'texto', 'label': 'Módulo',
                 'ajax': {'url': '/reportes/filtros-bitacora', 'clave': 'modulos'}},
    'b_fecha': {'campo_sql': 'au.created_at', 'coercion': 'rango_fecha',
                'label': 'Fecha de actividad'},
    # guiones / elementos
    'g_estado_f': {'campo_sql': 'g.estado', 'coercion': 'texto', 'label': 'Estado',
                   'opciones': [('borrador', 'Borrador'), ('publicado', 'Publicado'),
                                ('en_vivo', 'En Vivo'), ('finalizado', 'Finalizado')]},
    'g_fecha': {'campo_sql': 'g.creado_en', 'coercion': 'rango_fecha',
                'label': 'Fecha de creación'},
    'eg_encargado': {'campo_sql': 'eg.encargado', 'coercion': 'texto',
                     'label': 'Encargado',
                     'ajax': {'url': '/reportes/filtros/guiones', 'clave': 'encargados'}},
    'eg_tipo': {'campo_sql': 'eg.tipo', 'coercion': 'texto', 'label': 'Tipo de elemento',
                'opciones': [('pregame', 'Pre-Game'), ('game', 'Game')]},
    'eg_fecha': {'campo_sql': 'eg.creado_en', 'coercion': 'rango_fecha',
                 'label': 'Fecha del elemento'},
    # inventario
    'i_tipo': {'campo_sql': 't.nombre', 'coercion': 'texto', 'label': 'Tipo',
               'ajax': {'url': '/reportes/filtros/inventario', 'clave': 'tipos'}},
    'i_estado': {'campo_sql': 'e.nombre', 'coercion': 'texto', 'label': 'Estado',
                 'ajax': {'url': '/reportes/filtros/inventario',
                          'clave': 'estados', 'param': 'tipo_nombre',
                          'depende_de': 'i_tipo'}},
    'i_costo_min': {'campo_sql': 'r.costo', 'coercion': 'float_min',
                    'label': 'Costo mínimo'},
    'i_costo_max': {'campo_sql': 'r.costo', 'coercion': 'float_max',
                    'label': 'Costo máximo'},
    'i_fecha': {'campo_sql': 'r.fecha_compra', 'coercion': 'rango_fecha',
                'label': 'Fecha de compra'},
    'a_usuario': {'campo_sql': 'a.usuario_id', 'coercion': 'entero', 'label': 'Usuario'},
    'a_fecha': {'campo_sql': 'a.fecha_asignacion', 'coercion': 'rango_fecha',
                'label': 'Fecha de asignación'},
    # premios
    'pr_estado_f': {'campo_sql': 'p2.estado', 'coercion': 'texto', 'label': 'Estado',
                    'opciones': [('pendiente', 'Pendiente'),
                                 ('entregado', 'Entregado')]},
    'pr_patrocinador': {'campo_sql': 'p2.id_patrocinador', 'coercion': 'entero',
                        'label': 'Patrocinador',
                        'ajax': {'url': '/reportes/filtros/premios',
                                 'clave': 'patrocinadores'}},
    'pr_cantidad_min': {'campo_sql': 'p2.cantidad', 'coercion': 'float_min',
                        'label': 'Cantidad mínima'},
    'pr_cantidad_max': {'campo_sql': 'p2.cantidad', 'coercion': 'float_max',
                        'label': 'Cantidad máxima'},
    'pr_entregadas_min': {'campo_sql': 'p2.cantidad_entregada', 'coercion': 'float_min',
                          'label': 'Entregadas mínimo'},
    'pr_entregadas_max': {'campo_sql': 'p2.cantidad_entregada', 'coercion': 'float_max',
                          'label': 'Entregadas máximo'},
    'pr_fecha': {'campo_sql': 'p2.fecha_creacion', 'coercion': 'rango_fecha',
                 'label': 'Fecha de creación'},
    'pr_fecha_entrega': {'campo_sql': 'p2.fecha_entrega', 'coercion': 'rango_fecha',
                         'label': 'Fecha de entrega'},
    # tareas
    'tar_estado_f': {'campo_sql': 'ta.Estado', 'coercion': 'texto', 'label': 'Estado',
                     'opciones': [('Pendiente', 'Pendiente'),
                                  ('En Progreso', 'En Progreso'),
                                  ('Completada', 'Completada')]},
    'tar_usuario_f': {'campo_sql': 'ta.id_usuario', 'coercion': 'entero',
                      'label': 'Usuario',
                      'ajax': {'url': '/reportes/filtros/tareas', 'clave': 'usuarios',
                               'param': 'estado', 'depende_de': 'tar_estado_f'}},
    'tar_fecha': {'campo_sql': 'ta.fecha_asignacion_tarea', 'coercion': 'rango_fecha',
                  'label': 'Fecha de asignación'},
    # patrocinadores
    'pa_tipo_f': {'campo_sql': 'pa.tipo_contrato', 'coercion': 'texto',
                  'label': 'Tipo de contrato',
                  'opciones': [('1', 'Vigente'), ('2', 'Vencido')]},
    'pa_estado_f': {'campo_sql': 'pa.estado', 'coercion': 'entero', 'label': 'Estado',
                    'opciones': [('1', 'Activo'), ('0', 'Inactivo')]},
    'pa_encargado_f': {'campo_sql': 'pa.encargado_id', 'coercion': 'entero',
                       'label': 'Encargado interno (id)'},
    # usuarios
    'us_rol_f': {'campo_sql': 'us.rol', 'coercion': 'texto', 'label': 'Rol',
                 'ajax': {'url': '/reportes/filtros/usuarios',
                          'clave': 'roles', 'param': 'departamento',
                          'depende_de': 'us_departamento_f'}},
    'us_departamento_f': {'campo_sql': 'us.departamento', 'coercion': 'texto',
                          'label': 'Departamento',
                          'ajax': {'url': '/reportes/filtros/usuarios',
                                   'clave': 'departamentos'}},
    'us_activo_f': {'campo_sql': 'us.activo', 'coercion': 'entero', 'label': 'Estado',
                    'opciones': [('1', 'Activos'), ('0', 'Inactivos')]},
    'us_fecha': {'campo_sql': 'us.fecha_registro', 'coercion': 'rango_fecha',
                 'label': 'Fecha de registro'},
    # mantenimiento
    'm_estado_f': {'campo_sql': 'm.estado', 'coercion': 'texto', 'label': 'Estado',
                   'opciones': [('en_espera', 'En Espera'),
                                ('en_reparacion', 'En Reparación'),
                                ('reparado', 'Reparado'), ('baja', 'Dado de Baja')]},
    'm_recurso_f': {'campo_sql': 'm.recurso_id', 'coercion': 'entero', 'label': 'Recurso',
                    'ajax': {'url': '/reportes/filtros/mantenimiento',
                             'clave': 'recursos', 'param': 'estado',
                             'depende_de': 'm_estado_f'}},
    'm_dias_min': {'campo_sql':
                   'DATEDIFF(COALESCE(m.fecha_salida, CURDATE()), m.fecha_ingreso)',
                   'coercion': 'float_min', 'label': 'Días mínimo'},
    'm_dias_max': {'campo_sql':
                   'DATEDIFF(COALESCE(m.fecha_salida, CURDATE()), m.fecha_ingreso)',
                   'coercion': 'float_max', 'label': 'Días máximo'},
    'm_fecha': {'campo_sql': 'm.fecha_ingreso', 'coercion': 'rango_fecha',
                'label': 'Fecha de ingreso'},
    # reels
    're_patroncinador_f': {'campo_sql': 're.id_patrocinador', 'coercion': 'entero',
                           'label': 'Patrocinador',
                           'ajax': {'url': '/reportes/filtros/reels',
                                    'clave': 'patrocinadores'}},
    're_duracion_min': {'campo_sql': '(re.duracion_total * 60)', 'coercion': 'float_min',
                        'label': 'Duración mínima (seg)'},
    're_duracion_max': {'campo_sql': '(re.duracion_total * 60)', 'coercion': 'float_max',
                        'label': 'Duración máxima (seg)'},
    're_fecha': {'campo_sql': 're.creado_en', 'coercion': 'rango_fecha',
                 'label': 'Fecha de creación'},
}


def _cat(nombre, icono, descripcion, fuente, dimensiones, metricas, filtros,
         orden_default, visualizaciones=None, comparaciones=None,
         metricas_default=None, limite=None):
    return {
        'nombre': nombre, 'icono': icono, 'descripcion': descripcion,
        'fuente': fuente, 'dimensiones': dimensiones, 'metricas': metricas,
        'filtros': filtros, 'orden_default': orden_default,
        'visualizaciones_validas': visualizaciones or ['tabla', 'barras_h'],
        'comparaciones_validas': comparaciones or ['ninguna', 'periodo_anterior'],
        'metricas_default': metricas_default or metricas[:1],
        'limite': limite or LIMITE_FILAS,
    }


RESUMEN_LEGADO = {'nombre': 'Resumen general', 'icono': 'fa-table',
                  'descripcion': 'El reporte clásico del módulo (tabla + KPIs)',
                  'tipo': 'legado'}

MODULO_BUILDER = {
    'bitacora': {
        'nombre': 'Bitácora', 'icono': 'fa-history',
        'descripcion': 'Actividad de usuarios en el sistema',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'actividad': _cat(
                'Actividad', 'fa-chart-bar',
                'Agregación de actividades por usuario, acción, módulo o día',
                fuente='bitacora_actividad',
                dimensiones=['usuario_bitacora', 'accion', 'modulo_bitacora',
                             'dia_bitacora'],
                metricas=['actividades_conteo'],
                filtros=['b_usuario', 'b_accion', 'b_modulo', 'b_fecha'],
                orden_default='-actividades_conteo',
                visualizaciones=['tabla', 'barras_h', 'linea', 'torta'],
            ),
        },
    },
    'contratos': {
        'nombre': 'Contratos', 'icono': 'fa-file-contract',
        'descripcion': 'Contratos de patrocinio: montos, niveles, vigencias',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'cartera': _cat(
                'Cartera de contratos', 'fa-file-contract',
                'Montos y conteos agrupados por patrocinador, nivel, estatus o mes',
                fuente='contratos',
                dimensiones=['patrocinador', 'nivel', 'estatus', 'mes_contrato'],
                metricas=['monto_total_suma', 'monto_promedio', 'registros_conteo'],
                filtros=['c_fecha', 'c_tipo', 'c_estatus', 'c_patrocinador',
                         'c_monto_min', 'c_monto_max'],
                orden_default='-monto_total_suma',
                metricas_default=['monto_total_suma'],
                visualizaciones=['tabla', 'torta', 'barras_h', 'linea'],
            ),
            'ingresos': _cat(
                'Ingresos (pagos)', 'fa-money-bill',
                'Cobranza real recibida contra contratos',
                fuente='pagos',
                dimensiones=['patrocinador', 'tipo_pago', 'nivel', 'mes_pago', 'dia_pago'],
                metricas=['pago_suma', 'pago_promedio', 'registros_conteo'],
                filtros=['pg_fecha', 'pg_tipo', 'pg_nivel', 'c_patrocinador',
                         'pg_monto_min', 'pg_monto_max'],
                orden_default='-pago_suma',
                metricas_default=['pago_suma'],
                visualizaciones=['tabla', 'barras_h', 'linea', 'torta'],
            ),
        },
    },
    'balance': {
        'nombre': 'Balance / Pagos', 'icono': 'fa-balance-scale',
        'descripcion': 'Cobranza recibida contra contratos de patrocinio',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'cobranza': _cat(
                'Cobranza', 'fa-money-bill-transfer',
                'Pagos agrupados por tipo, nivel, patrocinador o mes',
                fuente='pagos',
                dimensiones=['tipo_pago', 'nivel', 'patrocinador', 'mes_pago',
                             'dia_pago'],
                metricas=['pago_suma', 'pago_promedio', 'registros_conteo'],
                filtros=['pg_fecha', 'pg_tipo', 'pg_nivel', 'c_patrocinador',
                         'pg_monto_min', 'pg_monto_max'],
                orden_default='-pago_suma',
                metricas_default=['pago_suma'],
                visualizaciones=['tabla', 'linea', 'barras_h', 'torta'],
            ),
        },
    },
    'guiones': {
        'nombre': 'Guiones', 'icono': 'fa-scroll',
        'descripcion': 'Producción de guiones y carga por encargado',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'produccion': _cat(
                'Producción por elemento', 'fa-list-check',
                'Elementos de guion por encargado, tipo o inning',
                fuente='elementos_guion',
                dimensiones=['encargado_elemento', 'tipo_elemento', 'inning',
                             'mes_elemento'],
                metricas=['elementos_conteo', 'duracion_suma', 'duracion_promedio',
                          'guiones_conteo'],
                filtros=['eg_encargado', 'eg_tipo', 'eg_fecha'],
                orden_default='-elementos_conteo',
                metricas_default=['elementos_conteo'],
                visualizaciones=['tabla', 'barras_h', 'torta', 'linea'],
            ),
            'evolucion': _cat(
                'Evolución de creación', 'fa-chart-line',
                'Guiones creados por período y estado',
                fuente='guiones',
                dimensiones=['g_estado', 'mes_creacion_guion'],
                metricas=['guiones_conteo'],
                filtros=['g_estado_f', 'g_fecha'],
                orden_default='-guiones_conteo',
                metricas_default=['guiones_conteo'],
                visualizaciones=['tabla', 'linea', 'torta', 'barras_h'],
            ),
        },
    },
    'inventario': {
        'nombre': 'Inventario', 'icono': 'fa-boxes',
        'descripcion': 'Valorización de recursos y asignaciones',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'valorizacion': _cat(
                'Valorización', 'fa-sack-dollar',
                'Costos agrupados por tipo, estado o mes de compra',
                fuente='recursos',
                dimensiones=['inv_tipo', 'inv_estado', 'mes_compra'],
                metricas=['costo_suma', 'costo_promedio', 'costo_maximo',
                          'recursos_conteo', 'antiguedad_promedio'],
                filtros=['i_tipo', 'i_estado', 'i_costo_min', 'i_costo_max', 'i_fecha'],
                orden_default='-costo_suma',
                metricas_default=['costo_suma'],
                visualizaciones=['tabla', 'torta', 'barras_h', 'linea'],
            ),
            'asignaciones_cat': _cat(
                'Asignaciones', 'fa-people-arrows',
                'Asignaciones de recursos por usuario y estado',
                fuente='asignaciones',
                dimensiones=['asg_usuario', 'asg_estado'],
                metricas=['asignaciones_conteo'],
                filtros=['a_usuario', 'a_fecha'],
                orden_default='-asignaciones_conteo',
                metricas_default=['asignaciones_conteo'],
                visualizaciones=['tabla', 'barras_h', 'torta'],
            ),
        },
    },
    'premios': {
        'nombre': 'Premios', 'icono': 'fa-gift',
        'descripcion': 'Premios por patrocinador: entregas y stock pendiente',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'entregas_stock': _cat(
                'Entregas y stock', 'fa-boxes-stacked',
                'Unidades totales, entregadas y pendientes',
                fuente='premios',
                dimensiones=['pr_estado', 'pr_patrocinador', 'pr_mes_creacion',
                             'pr_mes_entrega'],
                metricas=['premios_conteo', 'unidades_suma', 'entregadas_suma',
                          'pendientes_suma'],
                filtros=['pr_estado_f', 'pr_patrocinador', 'pr_cantidad_min',
                         'pr_cantidad_max', 'pr_entregadas_min', 'pr_entregadas_max',
                         'pr_fecha', 'pr_fecha_entrega'],
                orden_default='-unidades_suma',
                metricas_default=['pendientes_suma'],
                visualizaciones=['tabla', 'torta', 'barras_h', 'linea'],
            ),
        },
    },
    'tareas': {
        'nombre': 'Tareas', 'icono': 'fa-tasks',
        'descripcion': 'Carga laboral por usuario y estados de asignación',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'carga': _cat(
                'Carga por usuario', 'fa-user-check',
                'Asignaciones por usuario, estado y mes',
                fuente='tareas_carga',
                dimensiones=['tar_usuario', 'tar_estado', 'tar_mes'],
                metricas=['asignaciones_tarea_conteo', 'usuarios_distintos',
                          'completadas_pct'],
                filtros=['tar_usuario_f', 'tar_estado_f', 'tar_fecha'],
                orden_default='-asignaciones_tarea_conteo',
                metricas_default=['asignaciones_tarea_conteo'],
                visualizaciones=['tabla', 'barras_h', 'torta'],
            ),
        },
    },
    'patrocinadores': {
        'nombre': 'Patrocinadores', 'icono': 'fa-handshake',
        'descripcion': 'Cartera de empresas por estado y encargado interno',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'cartera_pat': _cat(
                'Cartera de empresas', 'fa-building',
                'Empresas por estado, tipo de contrato y encargado',
                fuente='patrocinadores',
                dimensiones=['pat_estado', 'pat_tipo', 'pat_encargado'],
                metricas=['patrocinadores_conteo', 'activos_conteo'],
                filtros=['pa_tipo_f', 'pa_estado_f', 'pa_encargado_f'],
                orden_default='-patrocinadores_conteo',
                metricas_default=['patrocinadores_conteo'],
                visualizaciones=['tabla', 'torta', 'barras_v'],
            ),
        },
    },
    'usuarios': {
        'nombre': 'Usuarios', 'icono': 'fa-users',
        'descripcion': 'Planta laboral por rol, departamento y actividad',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'planta': _cat(
                'Planta', 'fa-users-line',
                'Usuarios por rol, departamento, estado o mes de registro',
                fuente='usuarios_sistema',
                dimensiones=['us_rol', 'us_departamento', 'us_activo',
                             'us_mes_registro'],
                metricas=['usuarios_conteo', 'usuarios_activos_conteo'],
                filtros=['us_rol_f', 'us_departamento_f', 'us_activo_f', 'us_fecha'],
                orden_default='-usuarios_conteo',
                metricas_default=['usuarios_conteo'],
                visualizaciones=['tabla', 'torta', 'barras_v', 'linea'],
            ),
        },
    },
    'mantenimiento': {
        'nombre': 'Mantenimiento', 'icono': 'fa-tools',
        'descripcion': 'Días en taller y frecuencia por recurso',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'taller': _cat(
                'Taller', 'fa-screwdriver-wrench',
                'Días en taller y conteos por recurso, estado o mes',
                fuente='mantenimientos',
                dimensiones=['man_estado', 'man_recurso', 'man_mes_ingreso'],
                metricas=['mantenimientos_conteo', 'dias_promedio', 'dias_maximo'],
                filtros=['m_estado_f', 'm_recurso_f', 'm_dias_min', 'm_dias_max',
                         'm_fecha'],
                orden_default='-mantenimientos_conteo',
                metricas_default=['dias_promedio'],
                visualizaciones=['tabla', 'barras_h', 'torta', 'linea'],
            ),
        },
    },
    'reels': {
        'nombre': 'Reels', 'icono': 'fa-video',
        'descripcion': 'Producción de clips por patrocinador y mes',
        'permiso': None,
        'exportaciones': ['pdf', 'csv'],
        'categorias': {
            'resumen': RESUMEN_LEGADO,
            'contenido': _cat(
                'Contenido', 'fa-clapperboard',
                'Clips y duración por patrocinador o mes de creación',
                fuente='reels_videos',
                dimensiones=['reel_patrocinador', 'reel_mes'],
                metricas=['clips_conteo', 'duracion_clip_suma', 'registros_conteo'],
                filtros=['re_patroncinador_f', 're_duracion_min', 're_duracion_max',
                         're_fecha'],
                orden_default='-duracion_clip_suma',
                metricas_default=['clips_conteo'],
                visualizaciones=['tabla', 'barras_h', 'linea'],
            ),
        },
    },
}


def catalogo_publico(modulo):
    """Versión segura para el frontend: sin SQL interno ni claves técnicas."""
    config = MODULO_BUILDER.get(modulo)
    if not config:
        return None
    publico = {
        'nombre': config['nombre'], 'icono': config['icono'],
        'descripcion': config['descripcion'], 'exportaciones': config['exportaciones'],
        'permiso': config['permiso'],
        'categorias': {}, 'dimensiones': {}, 'metricas': {}, 'filtros': {},
    }
    for cid, cat in config['categorias'].items():
        publico['categorias'][cid] = {
            'nombre': cat['nombre'], 'icono': cat.get('icono', ''),
            'descripcion': cat.get('descripcion', ''),
            'tipo': cat.get('tipo', 'constructor'),
            'dimensiones': cat.get('dimensiones', []),
            'metricas': cat.get('metricas', []),
            'metricas_default': cat.get('metricas_default', []),
            'filtros': cat.get('filtros', []),
            'visualizaciones_validas': cat.get('visualizaciones_validas', []),
            'comparaciones_validas': cat.get('comparaciones_validas', []),
            'orden_default': cat.get('orden_default', ''),
            'limite': cat.get('limite'),
        }
    ids_dim = {d for c in config['categorias'].values()
               for d in c.get('dimensiones', [])}
    for did in ids_dim:
        dim = DIMENSIONES[did]
        publico['dimensiones'][did] = {
            'label': dim['label'], 'tipo': dim['tipo'],
            'opciones': dim.get('mapa'),
        }
    ids_met = {m for c in config['categorias'].values() for m in c.get('metricas', [])}
    for mid in ids_met:
        met = METRICAS[mid]
        publico['metricas'][mid] = {'label': met['label'], 'formato': met['formato']}
    ids_fil = {f for c in config['categorias'].values() for f in c.get('filtros', [])}
    for fid in ids_fil:
        fil = FILTROS_BUILDER[fid]
        if 'campo_sql' not in fil:
            continue
        item = {'label': fil.get('label', fid), 'coercion': fil['coercion']}
        if fil.get('opciones'):
            item['opciones'] = [{'value': v, 'label': l} for v, l in fil['opciones']]
        if fil.get('ajax'):
            item['ajax'] = fil['ajax']
        publico['filtros'][fid] = item
    return publico
