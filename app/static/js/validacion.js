import { regExp } from './RegExp.js';

export function agregarInvalido(campo, mensaje) {
    campo.classList.add('is-invalid');
    campo.classList.remove('is-valid');
    const feedback = campo.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.textContent = mensaje || '';
    }
}

export function limpiarInvalido(campo) {
    campo.classList.remove('is-invalid');
    campo.classList.remove('is-valid');
    const feedback = campo.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.textContent = '';
    }
}

export function quitarInvalido(campo) {
    campo.classList.remove('is-invalid');
    campo.classList.add('is-valid');
    const feedback = campo.parentElement.querySelector('.invalid-feedback');
    if (feedback) {
        feedback.textContent = '';
    }
}

function validarCampo(campo, condicion, mensaje) {
    if (condicion) {
        quitarInvalido(campo);
    } else {
        agregarInvalido(campo, mensaje);
    }
}

export function validarNombre(campo) {
    const valido = regExp.nombre.test(campo.value.trim());
    validarCampo(campo, valido, 'El nombre debe tener entre 2 y 50 caracteres');
    return valido;
}

export function validarEmail(campo) {
    const valido = regExp.email.test(campo.value.trim());
    validarCampo(campo, valido, 'Ingresa un correo electrónico válido');
    return valido;
}

export function validarPassword(campo) {
    const valido = regExp.password.test(campo.value);
    validarCampo(campo, valido, 'La contraseña debe tener entre 8 y 30 caracteres');
    return valido;
}

export function validarCedula(campo) {
    const valido = regExp.cedula.test(campo.value.trim());
    validarCampo(campo, valido, 'La cédula debe tener entre 6 y 10 numeros');
    return valido;
}

export function validarTelefono(campo) {
    const prefix = document.getElementById('telefono_prefix');
    const full = (prefix ? prefix.value : '+58') + (campo.value || '').trim();
    if (full === '+58') {
        limpiarInvalido(campo);
        return true;
    }
    const valido = regExp.telefono.test(full);
    const feedback = campo.closest('.col-md-6')?.querySelector('.invalid-feedback');
    if (valido) {
        campo.classList.remove('is-invalid');
        campo.classList.add('is-valid');
        if (feedback) feedback.textContent = '';
    } else {
        campo.classList.add('is-invalid');
        campo.classList.remove('is-valid');
        if (feedback) feedback.textContent = 'Ingresa un teléfono válido';
    }
    return valido;
}

export function validarFecha(campo) {
    const valido = campo.value && regExp.fecha.test(campo.value) && campo.value <= regExp.hoy;
    validarCampo(campo, valido, 'La fecha no puede ser posterior a hoy');
    return valido;
}

export function validarFechaFutura(campo) {
    const valido = campo.value && regExp.fecha.test(campo.value);
    validarCampo(campo, valido, 'Ingresa una fecha válida');
    return valido;
}

export function validarHora(campo) {
    const valido = campo.value && regExp.hora.test(campo.value);
    validarCampo(campo, valido, 'Ingresa una hora válida (HH:MM)');
    return valido;
}

export function validarSelect(campo) {
    const valido = regExp.select.test(campo.value);
    validarCampo(campo, valido, 'Selecciona una opción de la lista');
    return valido;
}

export function validarTexto(campo) {
    const valido = campo.value.trim().length >= 3;
    validarCampo(campo, valido, 'Debe tener al menos 3 caracteres');
    return valido;
}

export function validarTextoMax(campo, maximo) {
    const valido = campo.value.trim().length >= 3 && campo.value.trim().length <= maximo;
    validarCampo(campo, valido, 'Debe tener entre 3 y ' + maximo + ' caracteres');
    return valido;
}

export function validarTextoLargo(campo) {
    const valido = campo.value.trim().length >= 10;
    validarCampo(campo, valido, 'Debe tener al menos 10 caracteres');
    return valido;
}

export function validarDescripcion(campo) {
    const valido = regExp.descripcion.test(campo.value.trim());
    validarCampo(campo, valido, 'La descripción debe tener entre 5 y 500 caracteres');
    return valido;
}

export function validarRif(campo) {
    const valido = regExp.rif.test(campo.value.trim());
    validarCampo(campo, valido, 'Formato de RIF inválido (ej: J-12345678-9, j-12345678)');
    return valido;
}

export function validarCosto(campo) {
    const valido = campo.value && parseFloat(campo.value) > 0 && regExp.costo.test(campo.value);
    validarCampo(campo, valido, 'Ingresa un monto mayor a 0');
    return valido;
}

export function validarCantidad(campo) {
    const valido = regExp.cantidad.test(campo.value);
    validarCampo(campo, valido, 'Ingresa una cantidad válida (máx 9 dígitos)');
    return valido;
}

export function validarCodigo(campo) {
    const valido = regExp.codigo.test(campo.value.trim());
    validarCampo(campo, valido, 'El código solo puede contener letras, números y guiones');
    return valido;
}

export function validarTiempoInning(campo) {
    const val = campo.value.trim();
    if (val === '') {
        limpiarInvalido(campo);
        return true;
    }
    const valido = /^\d{1,2}(,\d{1,2})?$/.test(val);
    validarCampo(campo, valido, 'Formato: min,seg (ej: 3,30 o 5)');
    return valido;
}

export function validarRazonSocial(campo) {
    const valido = regExp.razonSocial.test(campo.value.trim());
    validarCampo(campo, valido, 'Ingresa una razón social válida');
    return valido;
}

export function validarFechaOpcional(campo) {
    if (!campo.value) return true;
    return validarFecha(campo);
}

export function validarFechaFin(fechaFin, fechaInicio) {
    if (!fechaFin.value || !regExp.fecha.test(fechaFin.value)) {
        validarCampo(fechaFin, false, 'Ingresa una fecha de fin válida');
        return false;
    }
    if (fechaInicio && fechaInicio.value && regExp.fecha.test(fechaInicio.value)) {
        if (fechaFin.value <= fechaInicio.value) {
            validarCampo(fechaFin, false, 'La fecha de fin debe ser posterior a la fecha de inicio');
            return false;
        }
    }
    validarCampo(fechaFin, true, '');
    return true;
}

export function validarTextoCaptcha(campo) {
    const valido = campo.value.trim().length === 4;
    validarCampo(campo, valido, 'Ingresa el codigo de la imagen');
    return valido;
}

export function validarConfirmPassword(password, confirm) {
    const valido = confirm.value === password.value && confirm.value.length >= 8;
    validarCampo(confirm, valido, 'Las contraseñas no coinciden');
    return valido;
}
