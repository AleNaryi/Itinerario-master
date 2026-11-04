# app/helpers/permission_map.py
# Mapa centralizado de permisos por módulo
# Uso: from app.helpers.permission_map import GUION

GUION = {
    'guion.dashboard': 'guion.view',
    'guion.crear': 'guion.create',
    'guion.agregar_elementos': 'guion.edit',
    'guion.editar_elemento': 'guion.edit',
    'guion.eliminar_elemento': 'guion.edit',
    'guion.editar': 'guion.edit',
    'guion.previsualizar': 'guion.preview',
    'guion.publicar': 'guion.publish',
    'guion.eliminar': 'guion.delete',
    'guion.replicar': 'guion.create',
    'guion.verificar_nombre': 'guion.view',
}

EN_VIVO = {
    'en_vivo.index': 'envivo.view',
    'en_vivo.ver': 'envivo.view',
    'en_vivo.iniciar': 'envivo.control',
    'en_vivo.finalizar': 'envivo.control',
    'en_vivo.sincronizar': 'envivo.control',
    'en_vivo.ver_log': 'envivo.view',
    'en_vivo.guiones_por_fecha': 'envivo.view',
    'en_vivo.estado_actual': 'envivo.view',
}

MANTENIMIENTO = {
    'mantenimiento.dashboard': 'mantenimiento.view',
    'mantenimiento.ver': 'mantenimiento.view',
    'mantenimiento.ingresar': 'mantenimiento.edit',
    'mantenimiento.agregar_nota': 'mantenimiento.edit',
    'mantenimiento.reparar': 'mantenimiento.edit',
    'mantenimiento.dar_baja': 'mantenimiento.delete',
    'mantenimiento.finalizar': 'mantenimiento.edit',
}

PREMIO = {
    'premio.dashboard': 'premio.view',
}

CONTRATO = {
    'contrato.dashboard': 'contrato.view',
    'contrato.api_obtener': 'contrato.view',
}

BALANCE = {
    'balance.dashboard': 'balance.view',
}

TAREA = {
    'gestion_tarea.dashboard': 'gestion_tarea.supervisar',
    'gestion_tarea.tareas_usuario': 'gestion_tarea.view',
    'gestion_tarea.completar': 'gestion_tarea.complete',
    'gestion_tarea.seguimiento': 'gestion_tarea.supervisar',
}

PATROCINADOR = {
    'patrocinador.dashboard': 'patrocinador.view',
    'patrocinador.api_obtener': 'patrocinador.view',
}

USUARIO = {
    'usuario.dashboard': 'usuario.view',
    'usuario.ver': 'usuario.view',
    'usuario.perfil': 'usuario.perfil',
    'usuario.cambiar_contrasena': 'usuario.perfil',
}

INVENTARIO = {
    'inventario.dashboard': 'inventario.view',
    'inventario.ver': 'inventario.view',
    'inventario.crear': 'inventario.create',
    'inventario.editar': 'inventario.edit',
    'inventario.eliminar': 'inventario.delete',
    'inventario.gestion_asignaciones': 'inventario.assign',
    'inventario.asignar': 'inventario.assign',
    'inventario.asignar_desde_gestion': 'inventario.assign',
    'inventario.devolver_recurso': 'inventario.assign',
}

REELS = {
    'reels.dashboard': 'reels.view',
    'reels.crear': 'reels.create',
    'reels.ver': 'reels.view',
    'reels.editar': 'reels.edit',
    'reels.eliminar': 'reels.delete',
    'reels.agregar_video': 'reels.edit',
    'reels.eliminar_video': 'reels.edit',
}

ROL = {
    'rol.dashboard': 'rol.view',
    'rol.editar': 'rol.edit',
    'rol.editar_rol': 'rol.edit',
    'rol.crear': 'rol.edit',
}

BITACORA = {
    'bitacora.dashboard': 'rol.view',
    'bitacora.reporte_usuario': 'rol.view',
}

REPORTES = {
    'reportes.dashboard': 'dashboard.view',
    'reportes.filtros_bitacora': 'reportes.view',
}
