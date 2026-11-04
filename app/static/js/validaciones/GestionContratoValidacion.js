import { validarSelect, validarFecha, validarFechaFin, validarCosto } from '../validacion.js';

export function validarFormularioContrato() {
    const patrocinador = document.getElementById('id_patrocinador');
    const tipo = document.getElementById('tipo');
    const fechaInicio = document.getElementById('fecha_inicio');
    const fechaFin = document.getElementById('fecha_fin');
    const monto = document.getElementById('monto_total');
    const estatus = document.getElementById('estatus');

    return (
        validarSelect(patrocinador) &&
        validarSelect(tipo) &&
        validarFecha(fechaInicio) &&
        validarFechaFin(fechaFin, fechaInicio) &&
        validarCosto(monto) &&
        validarSelect(estatus)
    );
}
