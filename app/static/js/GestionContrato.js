import { validarFormularioContrato } from './validaciones/GestionContratoValidacion.js';
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

let tablaContratos = null;

function actualizarPreviewPlan() {
    const sel = document.getElementById('tipo');
    const preview = document.getElementById('planPreview');
    const opt = sel.options[sel.selectedIndex];
    if (!sel.value) { preview.style.display = 'none'; return; }
    const precio = opt.dataset.precio;
    const features = JSON.parse(opt.dataset.features || '[]');
    const iconMap = { '1': 'fa-medal text-warning', '2': 'fa-award text-secondary', '3': 'fa-trophy text-warning' };
    preview.innerHTML = '<div class="d-flex justify-content-between align-items-center mb-2">'
        + '<span class="fw-bold"><i class="fas ' + (iconMap[sel.value] || 'fa-tag') + ' me-1"></i>' + escHtml(opt.text) + '</span>'
        + '<span class="badge bg-primary bg-opacity-10 text-primary">' + escHtml(precio) + '</span>'
        + '</div>'
        + '<ul class="mb-0 small text-muted">' + features.map(function(f) { return '<li><i class="fas fa-check text-success me-1"></i> ' + escHtml(f); }).join('') + '</ul>';
    preview.style.display = 'block';
}

function initTablaContratos() {
    if (!document.getElementById('tablaContratos')) return;
    if ($.fn.DataTable.isDataTable('#tablaContratos')) {
        $('#tablaContratos').DataTable().destroy();
    }
    tablaContratos = $('#tablaContratos').DataTable({
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
            { orderable: false, targets: 7 }
        ],
        ajax: {
            url: '/contratos/',
            type: 'POST',
            data: function(d) {
                d.consultar = true;
                d.csrf_token = getCSRF();
            },
            headers: { 'X-CSRFToken': getCSRF() },
            dataSrc: ''
        },
        columns: [
            { data: 'id_contrato' },
            { data: 'nombre_empresa' },
            { data: 'fecha_inicio' },
            { data: 'fecha_fin' },
            {
                data: 'tipo',
                render: function(data) {
                    const map = { '1': 'Bronce', '2': 'Plata', '3': 'Oro' };
                    return map[data] || data;
                }
            },
            {
                data: 'monto_total',
                render: function(data) {
                    if (data === null || data === undefined) return '<span class="text-muted small"><em>No definido</em></span>';
                    return '<span class="fw-bold text-success">$' + Number(data).toLocaleString('en', { minimumFractionDigits: 2 }) + '</span>';
                }
            },
            {
                data: 'estatus',
                render: function(data) {
                    const map = { 'Vigente': 'success', 'Vencido': 'danger', 'Borrador': 'warning text-dark' };
                    const cls = map[data] || 'secondary';
                    return '<span class="badge bg-' + cls + ' rounded-pill px-3 py-1">' + escHtml(data) + '</span>';
                }
            },
            {
                data: null,
                defaultContent: '',
                render: function(data) {
                    return '<div class="action-group">'
                        + '<button class="btn btn-action btn-action-edit btn-editar-contrato" data-id="' + data.id_contrato + '" title="Editar"><i class="fas fa-pen"></i></button>'
                        + '<button class="btn btn-action btn-action-danger btn-eliminar-contrato" data-id="' + data.id_contrato + '" title="Eliminar"><i class="fas fa-trash"></i></button>'
                        + '</div>';
                }
            }
        ]
    });
}

function recargarTabla() {
    if (tablaContratos) tablaContratos.ajax.reload();
}

function resetFormContrato() {
    document.getElementById('idContrato').value = '';
    const form = document.getElementById('formContrato');
    form.reset();
    form.querySelectorAll('.is-invalid, .is-valid').forEach(function(el) {
        el.classList.remove('is-invalid', 'is-valid');
    });
    document.getElementById('planPreview').style.display = 'none';
    document.getElementById('modalLabel').innerHTML = '<i class="fas fa-plus-circle me-2"></i>Registrar Contrato';
    document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Guardar';
}

async function editarContrato(id) {
    try {
        const res = await fetch('/contratos/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRF()
            },
            body: new URLSearchParams({ buscar: 'true', id_contrato: id, csrf_token: getCSRF() })
        });
        const data = await res.json();
        if (data.error) {
            Swal.fire({ icon: 'error', title: 'Error', text: data.error });
            return;
        }
        if (!data.status || !data.datos) {
            Swal.fire('Error', 'No se pudieron cargar los datos del contrato.', 'error');
            return;
        }
        const d = data.datos;
        document.getElementById('idContrato').value = d.id_contrato;
        document.getElementById('id_patrocinador').value = d.id_patrocinador;
        document.getElementById('fecha_inicio').value = d.fecha_inicio;
        document.getElementById('fecha_fin').value = d.fecha_fin;
        document.getElementById('tipo').value = d.tipo;
        actualizarPreviewPlan();
        document.getElementById('monto_total').value = d.monto_total;
        document.getElementById('estatus').value = d.estatus;
        document.getElementById('modalLabel').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Contrato';
        document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Actualizar';
        const modal = new bootstrap.Modal(document.getElementById('modalContrato'));
        modal.show();
    } catch (err) {
        console.error('Error al cargar contrato:', err);
        Swal.fire('Error', 'No se pudieron cargar los datos.', 'error');
    }
}

document.addEventListener('DOMContentLoaded', function() {
    initTablaContratos();

    document.getElementById('btnNuevoContrato').addEventListener('click', resetFormContrato);

    document.getElementById('modalContrato').addEventListener('hidden.bs.modal', function() {
        if (!document.getElementById('idContrato').value) resetFormContrato();
    });

    // ponytail: validación en vivo (input + blur + change)
    document.getElementById('id_patrocinador')?.addEventListener('change', function() { v.validarSelect(this); });

    document.getElementById('tipo')?.addEventListener('change', function() {
        v.validarSelect(this);
        actualizarPreviewPlan();
    });
    document.getElementById('estatus')?.addEventListener('change', function() { v.validarSelect(this); });
    document.getElementById('fecha_inicio')?.addEventListener('input', function() { v.validarFecha(this); });
    document.getElementById('fecha_inicio')?.addEventListener('blur', function() { v.validarFecha(this); });
    document.getElementById('monto_total')?.addEventListener('input', function() { v.validarCosto(this); });
    document.getElementById('monto_total')?.addEventListener('blur', function() { v.validarCosto(this); });
    document.getElementById('fecha_fin')?.addEventListener('input', function() {
        const inicio = document.getElementById('fecha_inicio');
        v.validarFechaFin(this, inicio);
    });
    document.getElementById('fecha_fin')?.addEventListener('blur', function() {
        const inicio = document.getElementById('fecha_inicio');
        v.validarFechaFin(this, inicio);
    });

    document.getElementById('formContrato').addEventListener('submit', async function(e) {
        e.preventDefault();
        if (!validarFormularioContrato()) {
            const primero = document.querySelector('.is-invalid');
            if (primero) primero.focus();
            return;
        }

        const id = document.getElementById('idContrato').value;
        const esCreacion = !id;
        const confirm = await Swal.fire({
            title: esCreacion ? '¿Registrar contrato?' : '¿Guardar cambios?',
            text: esCreacion ? 'Se registrará un nuevo contrato.' : 'Se actualizarán los datos del contrato.',
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
        params.append('id_patrocinador', document.getElementById('id_patrocinador').value);
        params.append('fecha_inicio', document.getElementById('fecha_inicio').value);
        params.append('fecha_fin', document.getElementById('fecha_fin').value);
        params.append('tipo', document.getElementById('tipo').value);
        params.append('monto_total', document.getElementById('monto_total').value);
        params.append('estatus', document.getElementById('estatus').value);

        try {
            const res = await fetch('/contratos/', {
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
                await Swal.fire({ icon: 'success', title: esCreacion ? 'Contrato registrado' : 'Contrato actualizado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                bootstrap.Modal.getInstance(document.getElementById('modalContrato')).hide();
                recargarTabla();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al guardar el contrato' });
            }
        } catch (err) {
            console.error('Error al guardar contrato:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al guardar el contrato' });
        }
    });

    document.addEventListener('click', function(e) {
        const btnEditar = e.target.closest('.btn-editar-contrato');
        if (btnEditar) {
            editarContrato(btnEditar.dataset.id);
        }
    });

    document.addEventListener('click', function(e) {
        const btnEliminar = e.target.closest('.btn-eliminar-contrato');
        if (btnEliminar) {
            document.getElementById('idContratoEliminar').value = btnEliminar.dataset.id;
            new bootstrap.Modal(document.getElementById('modalEliminar')).show();
        }
    });

    document.getElementById('btnEliminar').addEventListener('click', async function() {
        const id = document.getElementById('idContratoEliminar').value;
        if (!id) return;

        const confirm = await Swal.fire({
            title: '¿Eliminar contrato?',
            text: 'Esta acción marcará el contrato como eliminado.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'Eliminar',
            cancelButtonText: 'Cancelar'
        });
        if (!confirm.isConfirmed) return;

        try {
            const res = await fetch('/contratos/', {
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
            console.error('Error al eliminar contrato:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al eliminar' });
        }
    });
});
