document.addEventListener('DOMContentLoaded', function () {
    const accionBtns = document.querySelectorAll('.btn-confirmar-accion');
    accionBtns.forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const mensaje = this.getAttribute('data-confirm') || '¿Estás seguro?';
            e.preventDefault();
            const form = this.closest('form');
            Swal.fire({
                title: '¿Confirmar acción?',
                text: mensaje,
                icon: 'question',
                showCancelButton: true,
                confirmButtonColor: '#3085d6',
                cancelButtonColor: 'rgba(232, 42, 42, 0.9)',
                confirmButtonText: 'Sí, continuar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed && form) {
                    HTMLFormElement.prototype.submit.call(form);
                }
            });
        });
    });

    var descripcionEl = document.getElementById('descripcion');
    if (descripcionEl) {
        descripcionEl.addEventListener('input', function() {
            if (this.value.trim().length < 3) this.classList.add('is-invalid');
            else this.classList.remove('is-invalid');
        });
        descripcionEl.addEventListener('blur', function() {
            if (this.value.trim().length < 3) this.classList.add('is-invalid');
            else this.classList.remove('is-invalid');
        });
    }

    const formNota = document.getElementById('formNota');
    if (formNota) {
        formNota.addEventListener('submit', function (e) {
            const descripcion = document.getElementById('descripcion');
            if (descripcion && descripcion.value.trim().length < 3) {
                e.preventDefault();
                descripcion.classList.add('is-invalid');
                Swal.fire({
                    title: '❌ Error de validación',
                    text: 'La nota debe tener al menos 3 caracteres.',
                    icon: 'error',
                    confirmButtonColor: '#3085d6'
                });
                return;
            }
        });
    }

    function mostrarError(campo, mensaje) {
        campo.classList.add('is-invalid');
        campo.classList.remove('is-valid');
        var fb = campo.parentElement.querySelector('.invalid-feedback');
        if (fb) fb.textContent = mensaje;
    }

    function mostrarValido(campo) {
        campo.classList.remove('is-invalid');
        campo.classList.add('is-valid');
    }

    var fechaIngreso = document.getElementById('fecha_ingreso');
    var diagnostico = document.getElementById('diagnostico');
    var formIngresar = document.getElementById('formIngresar');

    if (fechaIngreso) {
        fechaIngreso.addEventListener('input', function () {
            if (this.value) mostrarValido(this); else this.classList.remove('is-valid', 'is-invalid');
        });
        fechaIngreso.addEventListener('blur', function () {
            if (!this.value) mostrarError(this, 'La fecha de ingreso es obligatoria');
            else mostrarValido(this);
        });
    }

    if (diagnostico) {
        diagnostico.addEventListener('input', function () {
            var v = this.value.trim();
            if (!v) this.classList.remove('is-valid', 'is-invalid');
            else if (v.length >= 3) mostrarValido(this);
            else mostrarError(this, 'Mínimo 3 caracteres');
        });
        diagnostico.addEventListener('blur', function () {
            var v = this.value.trim();
            if (!v) mostrarError(this, 'El diagnóstico es obligatorio');
            else if (v.length < 3) mostrarError(this, 'Mínimo 3 caracteres');
            else mostrarValido(this);
        });
    }

    if (formIngresar) {
        formIngresar.addEventListener('submit', function (e) {
            var ok = true;
            if (!fechaIngreso.value) { mostrarError(fechaIngreso, 'La fecha de ingreso es obligatoria'); ok = false; } else mostrarValido(fechaIngreso);
            var diag = diagnostico.value.trim();
            if (!diag) { mostrarError(diagnostico, 'El diagnóstico es obligatorio'); ok = false; }
            else if (diag.length < 3) { mostrarError(diagnostico, 'Mínimo 3 caracteres'); ok = false; }
            else mostrarValido(diagnostico);
            if (!ok) {
                e.preventDefault();
                Swal.fire({ title: 'Campos requeridos', text: 'Completa los campos marcados en rojo.', icon: 'warning', confirmButtonColor: '#3085d6' });
            }
        });
    }

    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (el) {
        return new bootstrap.Tooltip(el);
    });
});
