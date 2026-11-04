import { validarNombre, validarEmail, validarCedula, validarTelefono, validarPassword, validarConfirmPassword, validarSelect } from '../validacion.js';

export function validarFormularioUsuario() {
    const nombre = document.getElementById('nombre');
    const email = document.getElementById('email');
    const cedula = document.getElementById('cedula');
    const rol = document.getElementById('rol');
    const departamento = document.getElementById('departamento');
    const telefono = document.getElementById('telefono');
    const password = document.getElementById('password');
    const confirm = document.getElementById('confirm_password');
    const id = document.getElementById('idUsuario').value;
    const esCreacion = !id;

    const debeValidarPass = esCreacion || password.value.length > 0;

    return (
        validarNombre(nombre) &&
        validarEmail(email) &&
        validarCedula(cedula) &&
        validarSelect(rol) &&
        validarSelect(departamento) &&
        (telefono.value ? validarTelefono(telefono) : true) &&
        (!debeValidarPass || (validarPassword(password) && validarConfirmPassword(password, confirm)))
    );
}
