import { validarRazonSocial, validarRif, validarSelect, validarTelefono, validarEmail } from '../validacion.js';

export function validarFormularioPatrocinador() {
    const nombre = document.getElementById('nombre_empresa');
    const rif = document.getElementById('rif');
    const tipoContrato = document.getElementById('tipo_contrato');
    const telefono = document.getElementById('telefono');
    const email = document.getElementById('email');
    const encargado = document.getElementById('encargado_id');

    return (
        validarRazonSocial(nombre) &&
        validarRif(rif) &&
        validarSelect(tipoContrato) &&
        (telefono.value ? validarTelefono(telefono) : true) &&
        (email.value ? validarEmail(email) : true) &&
        validarSelect(encargado)
    );
}
