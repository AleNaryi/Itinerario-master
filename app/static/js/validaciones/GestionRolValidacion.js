import { validarNombre, validarTextoLargo } from '../validacion.js';

export function validarFormularioRol() {
    const nombre = document.getElementById('nombre');
    const descripcion = document.getElementById('descripcion');
    let valido = validarNombre(nombre);
    if (descripcion.value.trim()) {
        valido = validarTextoLargo(descripcion) && valido;
    }
    return valido;
}

document.addEventListener('DOMContentLoaded', () => {
    const form = document.querySelector('form[novalidate]');
    if (form) {
        form.addEventListener('submit', (e) => {
            if (!validarFormularioRol()) {
                e.preventDefault();
            }
        });
    }
});
