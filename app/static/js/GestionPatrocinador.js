import { validarFormularioPatrocinador } from './validaciones/GestionPatrocinadorValidacion.js';
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

let tablaPatrocinadores = null;

function initTablaPatrocinadores() {
    if (!document.getElementById('tablaPatrocinadores')) return;
    if ($.fn.DataTable.isDataTable('#tablaPatrocinadores')) {
        $('#tablaPatrocinadores').DataTable().destroy();
    }
    tablaPatrocinadores = $('#tablaPatrocinadores').DataTable({
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
            { orderable: false, targets: 8 }
        ],
        ajax: {
            url: '/patrocinador/',
            type: 'POST',
            data: function(d) {
                d.consultar = true;
                d.csrf_token = getCSRF();
            },
            headers: { 'X-CSRFToken': getCSRF() },
            dataSrc: ''
        },
        columns: [
            { data: 'id_patrocinador' },
            { data: 'nombre_empresa' },
            { data: 'rif' },
            {
                data: 'tipo_contrato',
                render: function(d) { return d == 1 ? 'Vigente' : 'Vencido'; }
            },
            { data: 'nombre_contacto' },
            { data: 'telefono' },
            { data: 'email' },
            { data: 'encargado_nombre', render: function(d) { return d || '—'; } },
            {
                data: null,
                defaultContent: '',
                render: function(data) {
                    return '<div class="action-group">'
                        + '<button class="btn btn-action btn-action-edit btn-editar-patrocinador" data-id="' + data.id_patrocinador + '" title="Editar"><i class="fas fa-pen"></i></button>'
                        + '<button class="btn btn-action btn-action-danger btn-eliminar-patrocinador" data-id="' + data.id_patrocinador + '" title="Eliminar"><i class="fas fa-trash"></i></button>'
                        + '</div>';
                }
            }
        ]
    });
}

function recargarTabla() {
    if (tablaPatrocinadores) tablaPatrocinadores.ajax.reload();
}

function resetFormPatrocinador() {
    document.getElementById('idPatrocinador').value = '';
    const form = document.getElementById('formPatrocinador');
    form.reset();
    document.getElementById('tipo_contrato').value = '1';
    form.querySelectorAll('.is-invalid, .is-valid').forEach(function(el) {
        el.classList.remove('is-invalid', 'is-valid');
    });
    document.getElementById('modalLabel').innerHTML = '<i class="fas fa-plus-circle me-2"></i>Registrar Patrocinador';
    document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Guardar';
    document.getElementById('mensajePatrocinador').style.display = 'none';
}

async function editarPatrocinador(id) {
    try {
        const res = await fetch('/patrocinador/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRF()
            },
            body: new URLSearchParams({ buscar: 'true', id_patrocinador: id, csrf_token: getCSRF() })
        });
        const data = await res.json();
        if (data.error) {
            Swal.fire({ icon: 'error', title: 'Error', text: data.error });
            return;
        }
        if (!data.status || !data.datos) {
            Swal.fire('Error', 'No se pudieron cargar los datos del patrocinador.', 'error');
            return;
        }
        const d = data.datos;
        document.getElementById('idPatrocinador').value = d.id_patrocinador;
        document.getElementById('nombre_empresa').value = d.nombre_empresa;
        document.getElementById('rif').value = d.rif;
        document.getElementById('tipo_contrato').value = d.tipo_contrato;
        document.getElementById('nombre_contacto').value = d.nombre_contacto || '';
        document.getElementById('telefono').value = d.telefono || '';
        document.getElementById('email').value = d.email || '';
        document.getElementById('encargado_id').value = d.encargado_id || '';
        document.getElementById('modalLabel').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Patrocinador';
        document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Actualizar';
        document.getElementById('mensajePatrocinador').style.display = 'none';
        const modal = new bootstrap.Modal(document.getElementById('modalPatrocinador'));
        modal.show();
    } catch (err) {
        console.error('Error al cargar patrocinador:', err);
        Swal.fire('Error', 'No se pudieron cargar los datos.', 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initTablaPatrocinadores();

    document.getElementById('btnNuevoPatrocinador').addEventListener('click', resetFormPatrocinador);

    document.getElementById('modalPatrocinador').addEventListener('hidden.bs.modal', function() {
        if (!document.getElementById('idPatrocinador').value) resetFormPatrocinador();
    });

    document.getElementById('nombre_empresa').addEventListener('blur', async function() {
        const nombre = this.value.trim();
        if (document.getElementById('idPatrocinador').value) return;
        if (!nombre || !v.validarRazonSocial(this)) return;
        try {
            const res = await fetch('/patrocinador/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRF()
                },
                body: new URLSearchParams({ verificar_nombre: nombre, csrf_token: getCSRF() })
            });
            const data = await res.json();
            if (data.error) return;
            const feedback = this.parentElement.querySelector('.invalid-feedback');
            if (data.existe) {
                this.classList.add('is-invalid');
                this.classList.remove('is-valid');
                if (feedback) feedback.textContent = 'Esta empresa ya existe en la base de datos';
            } else if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (feedback) feedback.textContent = '';
            }
        } catch (err) {
            console.error('Error al verificar nombre:', err);
        }
    });

    // ponytail: validación en vivo (input + blur)
    document.getElementById('nombre_empresa')?.addEventListener('input', function() { v.validarRazonSocial(this); });
    document.getElementById('rif')?.addEventListener('input', function() { v.validarRif(this); });
    document.getElementById('rif')?.addEventListener('blur', function() { v.validarRif(this); });
    document.getElementById('telefono')?.addEventListener('input', function() {
        if (this.value) v.validarTelefono(this);
        else v.limpiarInvalido(this);
    });
    document.getElementById('telefono')?.addEventListener('blur', function() {
        if (this.value) v.validarTelefono(this);
        else v.limpiarInvalido(this);
    });
    document.getElementById('email')?.addEventListener('input', function() {
        if (this.value) v.validarEmail(this);
        else v.limpiarInvalido(this);
    });
    document.getElementById('email')?.addEventListener('blur', function() {
        if (this.value) v.validarEmail(this);
        else v.limpiarInvalido(this);
    });
    document.getElementById('tipo_contrato')?.addEventListener('change', function() { v.validarSelect(this); });
    document.getElementById('encargado_id')?.addEventListener('change', function() { v.validarSelect(this); });

    document.getElementById('formPatrocinador').addEventListener('submit', async function(e) {
        e.preventDefault();
        if (!validarFormularioPatrocinador()) {
            const primero = document.querySelector('.is-invalid');
            if (primero) primero.focus();
            return;
        }

        const id = document.getElementById('idPatrocinador').value;
        const esCreacion = !id;
        const confirm = await Swal.fire({
            title: esCreacion ? '¿Registrar patrocinador?' : '¿Guardar cambios?',
            text: esCreacion ? 'Se registrará un nuevo patrocinador.' : 'Se actualizarán los datos del patrocinador.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: esCreacion ? '#198754' : '#ffc107',
            confirmButtonText: esCreacion ? 'Registrar' : 'Actualizar',
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
        params.append('nombre_empresa', document.getElementById('nombre_empresa').value.trim());
        params.append('rif', document.getElementById('rif').value.trim());
        params.append('tipo_contrato', document.getElementById('tipo_contrato').value);
        params.append('nombre_contacto', document.getElementById('nombre_contacto').value.trim());
        params.append('telefono', document.getElementById('telefono').value.trim());
        params.append('email', document.getElementById('email').value.trim());
        params.append('encargado_id', document.getElementById('encargado_id').value);

        try {
            const res = await fetch('/patrocinador/', {
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
                await Swal.fire({ icon: 'success', title: esCreacion ? 'Patrocinador registrado' : 'Patrocinador actualizado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                bootstrap.Modal.getInstance(document.getElementById('modalPatrocinador')).hide();
                recargarTabla();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al guardar el patrocinador' });
            }
        } catch (err) {
            console.error('Error al guardar patrocinador:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al guardar el patrocinador' });
        }
    });

    document.addEventListener('click', function(e) {
        const btnEditar = e.target.closest('.btn-editar-patrocinador');
        if (btnEditar) {
            editarPatrocinador(btnEditar.dataset.id);
        }
    });

    document.addEventListener('click', function(e) {
        const btnEliminar = e.target.closest('.btn-eliminar-patrocinador');
        if (btnEliminar) {
            document.getElementById('idPatrocinadorEliminar').value = btnEliminar.dataset.id;
            new bootstrap.Modal(document.getElementById('modalEliminar')).show();
        }
    });

    document.getElementById('btnEliminar').addEventListener('click', async function() {
        const id = document.getElementById('idPatrocinadorEliminar').value;
        if (!id) return;

        const confirm = await Swal.fire({
            title: '¿Eliminar patrocinador?',
            text: 'Esta acción marcará el patrocinador como eliminado.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'Eliminar',
            cancelButtonText: 'Cancelar'
        });
        if (!confirm.isConfirmed) return;

        try {
            const res = await fetch('/patrocinador/', {
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
            console.error('Error al eliminar patrocinador:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al eliminar' });
        }
    });
});
