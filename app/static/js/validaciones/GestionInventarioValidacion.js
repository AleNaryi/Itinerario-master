import { validarNombre, validarDescripcion, validarFechaOpcional, validarSelect } from '../validacion.js';

export function validarFormularioActivo() {
    const tipo = document.getElementById('id_tipo_activo');
    const nombre = document.getElementById('Nombre');
    const descripcion = document.getElementById('Descripcion');
    const fecha = document.getElementById('Fecha_adquisicion');

    return (
        validarSelect(tipo) &&
        validarNombre(nombre) &&
        validarDescripcion(descripcion) &&
        validarFechaOpcional(fecha)
    );
}

export function validarFormularioTipoActivo() {
    const nombre = document.getElementById('nombre_tipo_activo');
    const descripcion = document.getElementById('descripcion_tipo_activo');

    return (
        validarNombre(nombre) &&
        validarDescripcion(descripcion)
    );
}
