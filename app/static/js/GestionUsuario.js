import { validarFormularioUsuario } from './validaciones/GestionUsuarioValidacion.js';
import * as v from './validacion.js';

const $ = window.jQuery;

function getCSRF() {
    const el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

function escHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

let tablaUsuarios = null;

function initTablaUsuarios() {
    if (!document.getElementById('tablaUsuarios')) return;
    if ($.fn.DataTable.isDataTable('#tablaUsuarios')) {
        $('#tablaUsuarios').DataTable().destroy();
    }
    tablaUsuarios = $('#tablaUsuarios').DataTable({
        language: {
            processing: 'Procesando...',
            search: 'Buscar:',
            lengthMenu: 'Mostrar _MENU_ registros',
            info: 'Mostrando _START_ a _END_ de _TOTAL_ registros',
            infoEmpty: 'Mostrando 0 a 0 de 0 registros',
            infoFiltered: '(filtrado de _MAX_ registros totales)',
            loadingRecords: 'Cargando...',
            zeroRecords: 'No se encontraron registros',
            emptyTable: 'No hay datos disponibles en la tabla',
            paginate: { first: 'Primero', previous: 'Anterior', next: 'Siguiente', last: 'Último' },
            aria: { sortAscending: ': activar para orden ascendente', sortDescending: ': activar para orden descendente' }
        },
        pageLength: 25,
        lengthMenu: [10, 25, 50, 100],
        order: [[0, 'desc']],
        columnDefs: [
            { orderable: false, targets: 9 }
        ],
        ajax: {
            url: '/usuarios/',
            type: 'POST',
            data: function(d) {
                d.consultar = true;
                d.csrf_token = getCSRF();
            },
            headers: { 'X-CSRFToken': getCSRF() },
            dataSrc: ''
        },
        columns: [
            { data: 'id' },
            { data: 'cedula' },
            { data: 'nombre' },
            { data: 'email' },
            {
                data: 'rol',
                render: function(data) {
                    const map = { 'Superadmin': 'dark', 'Administrador': 'danger' };
                    const cls = map[data] || 'primary';
                    return '<span class="badge bg-' + cls + ' rounded-pill">' + escHtml(data) + '</span>';
                }
            },
            { data: 'departamento' },
            { data: 'telefono' },
            {
                data: 'activo',
                render: function(data) {
                    return data
                        ? '<span class="badge bg-success rounded-pill px-2">Activo</span>'
                        : '<span class="badge bg-secondary rounded-pill px-2">Inactivo</span>';
                }
            },
            { data: 'fecha_registro' },
            {
                data: null,
                defaultContent: '',
                render: function(data) {
                    return '<div class="action-group">'
                        + '<button class="btn btn-action btn-action-edit btn-editar-usuario" data-id="' + data.id + '" title="Editar"><i class="fas fa-pen"></i></button>'
                        + '<button class="btn btn-action btn-action-danger btn-eliminar-usuario" data-id="' + data.id + '" data-nombre="' + escHtml(data.nombre) + '" title="Eliminar"><i class="fas fa-trash"></i></button>'
                        + '</div>';
                }
            }
        ]
    });
}

function recargarTabla() {
    if (tablaUsuarios) tablaUsuarios.ajax.reload();
}

function resetFormUsuario() {
    document.getElementById('idUsuario').value = '';
    const form = document.getElementById('usuarioForm');
    form.reset();
    form.querySelectorAll('.is-invalid, .is-valid').forEach(function(el) {
        el.classList.remove('is-invalid', 'is-valid');
    });
    document.getElementById('activo').checked = true;
    document.getElementById('password').required = true;
    document.getElementById('password').disabled = false;
    document.getElementById('confirm_password').required = true;
    document.getElementById('confirm_password').disabled = false;
    document.getElementById('modalTitle').innerHTML = '<i class="fas fa-user me-2"></i>Crear Nuevo Usuario';
    document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Guardar';
}

async function editarUsuario(id) {
    try {
        const res = await fetch('/usuarios/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRF()
            },
            body: new URLSearchParams({ buscar: 'true', id: id, csrf_token: getCSRF() })
        });
        const data = await res.json();
        if (data.error) {
            Swal.fire({ icon: 'error', title: 'Error', text: data.error });
            return;
        }
        if (!data.status || !data.datos) {
            Swal.fire('Error', 'No se pudieron cargar los datos del usuario.', 'error');
            return;
        }
        const d = data.datos;
        document.getElementById('idUsuario').value = d.id;
        document.getElementById('nombre').value = d.nombre;
        document.getElementById('cedula').value = d.cedula;
        document.getElementById('email').value = d.email;
        document.getElementById('rol').value = d.rol;
        document.getElementById('departamento').value = d.departamento;
        var tel = d.telefono || '';
        var prefixes = ['+507', '+593', '+591', '+52', '+54', '+56', '+57', '+58', '+1', '+34', '+53', '+51', '+1'];
        var pf = '+58', num = tel;
        for (var i = 0; i < prefixes.length; i++) {
            if (tel.indexOf(prefixes[i]) === 0) { pf = prefixes[i]; num = tel.slice(pf.length); break; }
        }
        document.getElementById('telefono_prefix').value = pf;
        document.getElementById('telefono').value = num;
        document.getElementById('activo').checked = d.activo;
        document.getElementById('password').value = '';
        document.getElementById('confirm_password').value = '';
        document.getElementById('modalTitle').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Usuario';
        document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Actualizar';
        const modal = new bootstrap.Modal(document.getElementById('usuarioModal'));
        modal.show();
    } catch (err) {
        console.error('Error al cargar usuario:', err);
        Swal.fire('Error', 'No se pudieron cargar los datos.', 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initTablaUsuarios();

    document.getElementById('btnNuevoUsuario').addEventListener('click', resetFormUsuario);

    document.getElementById('usuarioModal').addEventListener('hidden.bs.modal', function() {
        if (!document.getElementById('idUsuario').value) resetFormUsuario();
    });

    document.getElementById('email').addEventListener('blur', async function() {
        const email = this.value.trim();
        if (document.getElementById('idUsuario').value) return;
        if (!v.validarEmail(this)) return;
        try {
            const res = await fetch('/usuarios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRF()
                },
                body: new URLSearchParams({ verificar_email: email, csrf_token: getCSRF() })
            });
            const data = await res.json();
            if (data.error) return;
            const feedback = this.parentElement.querySelector('.invalid-feedback');
            if (data.existe) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (feedback) feedback.textContent = 'Este email ya está registrado';
            } else if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (feedback) feedback.textContent = '';
            }
        } catch (err) {
            console.error('Error al verificar email:', err);
        }
    });

    document.getElementById('cedula').addEventListener('blur', async function() {
        const cedula = this.value.trim();
        if (document.getElementById('idUsuario').value) return;
        if (!v.validarCedula(this)) return;
        try {
            const res = await fetch('/usuarios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRF()
                },
                body: new URLSearchParams({ verificar_cedula: cedula, csrf_token: getCSRF() })
            });
            const data = await res.json();
            if (data.error) return;
            const feedback = this.parentElement.querySelector('.invalid-feedback');
            if (data.existe) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (feedback) feedback.textContent = 'Esta cédula ya está registrada';
            } else if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (feedback) feedback.textContent = '';
            }
        } catch (err) {
            console.error('Error al verificar cedula:', err);
        }
    });

    // ponytail: validación en vivo (input + blur)
    document.getElementById('nombre')?.addEventListener('input', function() { v.validarNombre(this); });
    document.getElementById('nombre')?.addEventListener('blur', function() { v.validarNombre(this); });
    document.getElementById('email')?.addEventListener('input', function() { v.validarEmail(this); });
    document.getElementById('cedula')?.addEventListener('input', function() { v.validarCedula(this); });
    document.getElementById('telefono')?.addEventListener('input', function() { v.validarTelefono(this); });
    document.getElementById('telefono')?.addEventListener('blur', function() { v.validarTelefono(this); });
    document.getElementById('rol')?.addEventListener('change', function() { v.validarSelect(this); });
    document.getElementById('departamento')?.addEventListener('change', function() { v.validarSelect(this); });
    document.getElementById('password')?.addEventListener('input', function() { v.validarPassword(this); });
    document.getElementById('password')?.addEventListener('blur', function() { v.validarPassword(this); });
    document.getElementById('confirm_password')?.addEventListener('input', function() {
        const pwd = document.getElementById('password');
        if (pwd) v.validarConfirmPassword(pwd, this);
    });
    document.getElementById('confirm_password')?.addEventListener('blur', function() {
        const pwd = document.getElementById('password');
        if (pwd) v.validarConfirmPassword(pwd, this);
    });

    document.getElementById('usuarioForm').addEventListener('submit', async function(e) {
        e.preventDefault();
        if (!validarFormularioUsuario()) {
            const primero = document.querySelector('.is-invalid');
            if (primero) primero.focus();
            return;
        }

        const id = document.getElementById('idUsuario').value;
        const esCreacion = !id;
        const confirm = await Swal.fire({
            title: esCreacion ? '¿Crear usuario?' : '¿Guardar cambios?',
            text: esCreacion ? 'Se creará un nuevo usuario.' : 'Se actualizarán los datos del usuario.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: esCreacion ? '#198754' : '#ffc107',
            confirmButtonText: esCreacion ? 'Crear' : 'Actualizar',
            cancelButtonText: 'Cancelar'
        });
        if (!confirm.isConfirmed) return;

        const params = new URLSearchParams();
        params.append('csrf_token', getCSRF());
        if (esCreacion) {
            params.append('registrar', 'true');
        } else {
            params.append('editar', id);
        }
        params.append('nombre', document.getElementById('nombre').value.trim());
        params.append('email', document.getElementById('email').value.trim());
        params.append('cedula', document.getElementById('cedula').value.trim());
        params.append('rol', document.getElementById('rol').value);
        params.append('departamento', document.getElementById('departamento').value);
        params.append('telefono', document.getElementById('telefono_prefix').value + document.getElementById('telefono').value.trim());
        params.append('activo', document.getElementById('activo').checked ? 'true' : 'false');
        if (!esCreacion) {
            const pwd = document.getElementById('password').value;
            if (pwd) params.append('password', pwd);
        } else {
            params.append('password', document.getElementById('password').value);
        }

        try {
            const res = await fetch('/usuarios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRF()
                },
                body: params
            });
            const data = await res.json();
            if (data.error) {
                Swal.fire({ icon: 'error', title: 'Error', text: data.error });
                return;
            }
            if (data.mensaje && !data.mensaje.startsWith('Error')) {
                await Swal.fire({ icon: 'success', title: esCreacion ? 'Usuario creado' : 'Usuario actualizado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                bootstrap.Modal.getInstance(document.getElementById('usuarioModal')).hide();
                recargarTabla();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al guardar el usuario' });
            }
        } catch (err) {
            console.error('Error al guardar usuario:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al guardar el usuario' });
        }
    });

    document.addEventListener('click', function(e) {
        const btnEditar = e.target.closest('.btn-editar-usuario');
        if (btnEditar) {
            editarUsuario(btnEditar.dataset.id);
        }
    });

    document.addEventListener('click', function(e) {
        const btnEliminar = e.target.closest('.btn-eliminar-usuario');
        if (btnEliminar) {
            document.getElementById('idUsuarioEliminar').value = btnEliminar.dataset.id;
            new bootstrap.Modal(document.getElementById('modalEliminar')).show();
        }
    });

    document.getElementById('btnEliminar').addEventListener('click', async function() {
        const id = document.getElementById('idUsuarioEliminar').value;
        if (!id) return;

        const confirm = await Swal.fire({
            title: '¿Eliminar usuario?',
            text: 'Esta acción eliminará el usuario permanentemente.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'Eliminar',
            cancelButtonText: 'Cancelar'
        });
        if (!confirm.isConfirmed) return;

        try {
            const res = await fetch('/usuarios/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRF()
                },
                body: new URLSearchParams({ eliminar: id, csrf_token: getCSRF() })
            });
            const data = await res.json();
            if (data.error) {
                Swal.fire({ icon: 'error', title: 'Error', text: data.error });
                return;
            }
            if (data.mensaje && !data.mensaje.startsWith('Error')) {
                await Swal.fire({ icon: 'success', title: 'Eliminado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                bootstrap.Modal.getInstance(document.getElementById('modalEliminar')).hide();
                recargarTabla();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al eliminar' });
            }
        } catch (err) {
            console.error('Error al eliminar usuario:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al eliminar' });
        }
    });
});
