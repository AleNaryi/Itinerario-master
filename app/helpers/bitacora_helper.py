"""Registro de bitácora centralizado (antes duplicado en ~12 controladores)."""
import json
import logging

from flask import request
from flask_login import current_user

from app.model.bitacora_model import ActividadModel

logger = logging.getLogger(__name__)


def registrar_bitacora(modulo, tipo, accion, detalle=None):
    """Registra una actividad; un fallo de bitácora nunca rompe la operación principal."""
    try:
        ActividadModel().registrar({
            'usuario_id': current_user.id,
            'tipo_accion': tipo,
            'modulo': modulo,
            'accion': accion,
            'detalle': json.dumps({'detalle': detalle}),
            'pagina': request.path,
            'ip_address': request.remote_addr,
        })
    except Exception:
        logger.exception('No se pudo registrar actividad de bitácora (%s/%s)', modulo, accion)
