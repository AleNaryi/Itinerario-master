import { validarFormularioActivo, validarFormularioTipoActivo } from './validaciones/GestionInventarioValidacion.js';
import * as v from './validacion.js';

const $ = window.jQuery;

// ── CSRF ──
function getCSRF() {
    const el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

function escHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// ── DATA TABLE ACTIVOS ──
let activoTable = null;

function initActivoTable() {
    if (!document.getElementById('activoTable')) return;
    if ($.fn.DataTable.isDataTable('#activoTable')) {
        $('#activoTable').DataTable().destroy();
    }
    activoTable = $('#activoTable').DataTable({
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
            { orderable: false, targets: 6 }
        ],
        ajax: {
            url: '/inventario/',
            type: 'POST',
            data: function(d) {
                d.consultar = true;
                d.csrf_token = getCSRF();
            },
            headers: { 'X-CSRFToken': getCSRF() },
            dataSrc: ''
        },
        columns: [
            { data: 'id_activo' },
            { data: 'tipo' },
            { data: 'Nombre_Activo' },
            { data: 'Descripcion_Activo' },
            {
                data: 'Estado_Activo',
                render: function (data, type, row) {
                    var map = { 1: 'success', 2: 'primary', 3: 'warning', 4: 'danger', 5: 'secondary' };
                    var cls = map[row.estado_id] || 'secondary';
                    return '<span class="badge bg-' + cls + ' rounded-pill px-3 py-1">' + escHtml(data) + '</span>';
                }
            },
            { data: 'Fecha_adquisicion' },
            {
                data: null,
                defaultContent: '',
                render: function (data) {
                    var botones = '';
                    if (data.estado_id == 1) {
                        botones += '<a class="btn btn-action btn-action-success" href="/inventario/asignar/' + data.id_activo + '" title="Asignar"><i class="fas fa-handshake"></i></a>';
                    }
                    botones += '<button class="btn btn-action btn-action-edit btn-editar-activo" data-id="' + data.id_activo + '" title="Editar"><i class="fas fa-pen"></i></button>'
                             + '<button class="btn btn-action btn-action-danger btn-eliminar-activo" data-id="' + data.id_activo + '" data-nombre="' + escHtml(data.Nombre_Activo) + '" title="Eliminar"><i class="fas fa-trash"></i></button>';
                    return '<div class="action-group">' + botones + '</div>';
                }
            }
        ]
    });
}

function cargarActivoTable() {
    if (activoTable) {
        activoTable.ajax.reload();
    }
}

// ── ACTIVO CRUD ──
function resetFormActivo() {
    document.getElementById('idActivo').value = '';
    const form = document.getElementById('formulario_activo_form');
    form.reset();
    form.querySelectorAll('.is-invalid, .is-valid').forEach(function (el) {
        el.classList.remove('is-invalid', 'is-valid');
    });
    document.getElementById('tituloFormularioActivo').innerHTML = '<i class="fas fa-plus-circle me-2"></i>Registrar Activo';
    document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Guardar';
    document.getElementById('mensajeActivo').style.display = 'none';
}

async function editarActivo(id) {
    try {
        const res = await fetch('/inventario/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRF()
            },
            body: new URLSearchParams({ buscar: 'true', idActivo: id, csrf_token: getCSRF() })
        });
        const data = await res.json();
        if (data.error) {
            Swal.fire({ icon: 'error', title: 'Error', text: data.error });
            return;
        }
        if (!data.status || !data.datos) {
            Swal.fire('Error', 'No se pudieron cargar los datos del activo.', 'error');
            return;
        }
        const d = data.datos;
        document.getElementById('idActivo').value = d.id_activo;
        document.getElementById('id_tipo_activo').value = d.id_tipo_activo;
        document.getElementById('Nombre').value = d.Nombre_Activo;
        document.getElementById('Descripcion').value = d.Descripcion_Activo || '';
        document.getElementById('Fecha_adquisicion').value = d.Fecha_adquisicion || '';
        document.getElementById('tituloFormularioActivo').innerHTML = '<i class="fas fa-edit me-2"></i>Editar Activo';
        document.getElementById('btnAccion').innerHTML = '<i class="fas fa-save me-1"></i> Actualizar';
        document.getElementById('mensajeActivo').style.display = 'none';
        const modal = new bootstrap.Modal(document.getElementById('formulario_activo'));
        modal.show();
    } catch (err) {
        console.error('Error al cargar activo:', err);
        Swal.fire('Error', 'No se pudieron cargar los datos.', 'error');
    }
}

// ── TIPOS CRUD ──
async function cargarTiposActivo() {
    try {
        const res = await fetch('/inventario/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': getCSRF()
            },
            body: new URLSearchParams({ consultar_tipos: 'true', csrf_token: getCSRF() })
        });
        const tipos = await res.json();
        renderTiposActivo(tipos || []);
    } catch (e) {
        document.getElementById('tbodyTipoActivo').innerHTML =
            '<tr><td colspan="4" class="text-center text-danger py-3">Error al cargar tipos</td></tr>';
    }
}

function renderTiposActivo(tipos) {
    const tbody = document.getElementById('tbodyTipoActivo');
    if (!tipos.length) {
        tbody.innerHTML = '<tr><td colspan="4" class="text-center text-muted py-3">No hay tipos registrados</td></tr>';
        return;
    }
    tbody.innerHTML = tipos.map(function (t) {
        return '<tr>'
            + '<td>' + t.id_tipo_activo + '</td>'
            + '<td class="fw-semibold">' + escHtml(t.Nombre) + '</td>'
            + '<td class="text-muted">' + escHtml(t.Descripcion_tipo || '—') + '</td>'
            + '<td class="text-center">'
            + '<div class="action-group">'
            + '<button class="btn btn-action btn-action-edit btn-editar-tipo-activo" data-id="' + t.id_tipo_activo + '" data-nombre="' + escHtml(t.Nombre) + '" data-descripcion="' + escHtml(t.Descripcion_tipo || '') + '" title="Editar"><i class="fas fa-pen"></i></button>'
            + '<button class="btn btn-action btn-action-danger btn-eliminar-tipo-activo" data-id="' + t.id_tipo_activo + '" data-nombre="' + escHtml(t.Nombre) + '" title="Eliminar"><i class="fas fa-trash"></i></button>'
            + '</div>'
            + '</td>'
            + '</tr>';
    }).join('');
}

function resetFormTipoActivo() {
    document.getElementById('idTipo').value = '';
    document.getElementById('nombre_tipo_activo').value = '';
    document.getElementById('descripcion_tipo_activo').value = '';
    document.getElementById('nombre_tipo_activo').classList.remove('is-invalid');
    document.getElementById('tituloFormTipo').innerHTML = '<i class="fas fa-plus-circle me-1 text-primary"></i> Nuevo Tipo';
    document.getElementById('btnTipoActivo').innerHTML = '<i class="fas fa-save me-1"></i> Guardar';
    document.getElementById('btnResetTipoActivo').style.display = 'none';
    document.getElementById('mensajeTipo').style.display = 'none';
}

function editarTipoActivo(id, nombre, descripcion) {
    document.getElementById('idTipo').value = id;
    document.getElementById('nombre_tipo_activo').value = nombre;
    document.getElementById('descripcion_tipo_activo').value = descripcion;
    document.getElementById('nombre_tipo_activo').classList.remove('is-invalid');
    document.getElementById('tituloFormTipo').innerHTML = '<i class="fas fa-edit me-1 text-primary"></i> Editar Tipo';
    document.getElementById('btnTipoActivo').innerHTML = '<i class="fas fa-save me-1"></i> Actualizar';
    document.getElementById('btnResetTipoActivo').style.display = 'inline-block';
    document.getElementById('nombre_tipo_activo').focus();
}

// ── EVENT BINDING ──
document.addEventListener('DOMContentLoaded', function () {
    initActivoTable();

    // ── Reset activo form when opening modal for creation ──
    document.getElementById('btnNuevoActivo').addEventListener('click', resetFormActivo);

    document.getElementById('formulario_activo').addEventListener('hidden.bs.modal', function () {
        if (!document.getElementById('idActivo').value) resetFormActivo();
    });

    // ── Verificar nombre duplicado via AJAX ──
    document.getElementById('Nombre').addEventListener('blur', async function () {
        const nombre = this.value.trim();
        if (document.getElementById('idActivo').value) return;
        if (!nombre || !v.validarNombre(this)) return;

        try {
            const res = await fetch('/inventario/', {
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
                if (feedback) feedback.textContent = 'Este nombre ya existe en la base de datos';
            } else if (this.classList.contains('is-invalid')) {
                this.classList.remove('is-invalid');
                this.classList.add('is-valid');
                if (feedback) feedback.textContent = '';
            }
        } catch (err) {
            console.error('Error al verificar nombre:', err);
        }
    });

    // ponytail: validación en vivo (input + blur) — activo
    document.getElementById('Nombre')?.addEventListener('input', function () { v.validarNombre(this); });
    document.getElementById('id_tipo_activo')?.addEventListener('change', function () { v.validarSelect(this); });
    document.getElementById('id_ubicacion')?.addEventListener('change', function () { v.validarSelect(this); });
    document.getElementById('Descripcion')?.addEventListener('input', function () { v.validarDescripcion(this); });
    document.getElementById('Descripcion')?.addEventListener('blur', function () { v.validarDescripcion(this); });
    document.getElementById('Fecha_adquisicion')?.addEventListener('input', function () {
        if (this.value) v.validarFecha(this);
        else v.limpiarInvalido(this);
    });
    document.getElementById('Fecha_adquisicion')?.addEventListener('blur', function () {
        if (this.value) v.validarFecha(this);
        else v.limpiarInvalido(this);
    });

    // ponytail: validación en vivo (input + blur) — tipo activo
    document.getElementById('nombre_tipo_activo')?.addEventListener('input', function () { v.validarNombre(this); });
    document.getElementById('nombre_tipo_activo')?.addEventListener('blur', function () { v.validarNombre(this); });
    document.getElementById('descripcion_tipo_activo')?.addEventListener('input', function () { v.validarDescripcion(this); });
    document.getElementById('descripcion_tipo_activo')?.addEventListener('blur', function () { v.validarDescripcion(this); });

    // ── Submit activo form ──
    document.getElementById('formulario_activo_form').addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!validarFormularioActivo()) {
            const primero = document.querySelector('.is-invalid');
            if (primero) primero.focus();
            return;
        }

        const id = document.getElementById('idActivo').value;
        const esCreacion = !id;
        const confirm = await Swal.fire({
            title: esCreacion ? '¿Registrar activo?' : '¿Guardar cambios?',
            text: esCreacion ? 'Se registrará un nuevo activo.' : 'Se actualizarán los datos del activo.',
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
        params.append('id_tipo_activo', document.getElementById('id_tipo_activo').value);
        params.append('Nombre', document.getElementById('Nombre').value.trim());
        params.append('Descripcion', document.getElementById('Descripcion').value.trim());
        params.append('Fecha_adquisicion', document.getElementById('Fecha_adquisicion').value);

        try {
            const res = await fetch('/inventario/', {
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
                await Swal.fire({ icon: 'success', title: esCreacion ? 'Activo registrado' : 'Activo actualizado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                bootstrap.Modal.getInstance(document.getElementById('formulario_activo')).hide();
                cargarActivoTable();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al guardar el activo' });
            }
        } catch (err) {
            console.error('Error al guardar activo:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al guardar el activo' });
        }
    });

    // ── Acciones en tabla de activos (editar/eliminar) ──
    document.addEventListener('click', function (e) {
        const btnEditar = e.target.closest('.btn-editar-activo');
        if (btnEditar) {
            editarActivo(btnEditar.dataset.id);
        }
    });

    document.addEventListener('click', function (e) {
        const btnEliminar = e.target.closest('.btn-eliminar-activo');
        if (btnEliminar) {
            document.getElementById('idActivoEliminar').value = btnEliminar.dataset.id;
            new bootstrap.Modal(document.getElementById('eliminar')).show();
        }
    });

    // ── Confirmar eliminación ──
    document.getElementById('btnEliminar').addEventListener('click', async function () {
        const id = document.getElementById('idActivoEliminar').value;
        if (!id) return;

        const confirm = await Swal.fire({
            title: '¿Eliminar activo?',
            text: 'Esta acción marcará el activo como eliminado.',
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#dc3545',
            confirmButtonText: 'Eliminar',
            cancelButtonText: 'Cancelar'
        });
        if (!confirm.isConfirmed) return;

        try {
            const res = await fetch('/inventario/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRF()
                },
                body: new URLSearchParams({ eliminar: 'true', idActivo: id, csrf_token: getCSRF() })
            });
            const data = await res.json();
            if (data.error) {
                Swal.fire({ icon: 'error', title: 'Error', text: data.error });
                return;
            }
            if (data.mensaje && !data.mensaje.startsWith('Error')) {
                await Swal.fire({ icon: 'success', title: 'Eliminado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                bootstrap.Modal.getInstance(document.getElementById('eliminar')).hide();
                cargarActivoTable();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al eliminar' });
            }
        } catch (err) {
            console.error('Error al eliminar activo:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión al eliminar' });
        }
    });

    // ── Modal Tipos ──
    const modalTipos = document.getElementById('formulario_tipo_activo');
    modalTipos.addEventListener('show.bs.modal', cargarTiposActivo);
    modalTipos.addEventListener('hidden.bs.modal', resetFormTipoActivo);

    document.getElementById('btnNuevoTipoActivo').addEventListener('click', function () {
        resetFormTipoActivo();
        document.getElementById('tituloFormTipo').scrollIntoView({ behavior: 'smooth', block: 'center' });
    });
    document.getElementById('btnResetTipoActivo').addEventListener('click', resetFormTipoActivo);

    // ── Acciones en tabla de tipos ──
    document.getElementById('tbodyTipoActivo').addEventListener('click', async function (e) {
        const btn = e.target.closest('button');
        if (!btn) return;

        if (btn.classList.contains('btn-editar-tipo-activo')) {
            editarTipoActivo(btn.dataset.id, btn.dataset.nombre, btn.dataset.descripcion);
        }

        if (btn.classList.contains('btn-eliminar-tipo-activo')) {
            const result = await Swal.fire({
                title: '¿Eliminar tipo?',
                text: '¿Eliminar el tipo "' + btn.dataset.nombre + '"?',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'Eliminar',
                cancelButtonText: 'Cancelar'
            });
            if (!result.isConfirmed) return;

            try {
                const res = await fetch('/inventario/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                        'X-CSRFToken': getCSRF()
                    },
                    body: new URLSearchParams({ eliminar_tipo_activo: btn.dataset.id, csrf_token: getCSRF() })
                });
                const data = await res.json();
                if (data.error) {
                    Swal.fire({ icon: 'error', title: 'Error', text: data.error });
                    return;
                }
                if (data.mensaje && !data.mensaje.startsWith('Error')) {
                    await Swal.fire({ icon: 'success', title: 'Tipo eliminado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                    cargarTiposActivo();
                } else {
                    Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al eliminar tipo' });
                }
            } catch (err) {
                console.error('Error al eliminar tipo:', err);
                Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión' });
            }
        }
    });

    // ── Submit formulario tipo ──
    document.getElementById('formTipoActivo').addEventListener('submit', async function (e) {
        e.preventDefault();
        if (!validarFormularioTipoActivo()) {
            const primero = document.querySelector('.is-invalid');
            if (primero) primero.focus();
            return;
        }

        const id = document.getElementById('idTipo').value;
        const nombre = document.getElementById('nombre_tipo_activo').value.trim();
        const descripcion = document.getElementById('descripcion_tipo_activo').value.trim();
        const esCreacion = !id;

        const confirm = await Swal.fire({
            title: esCreacion ? '¿Crear tipo?' : '¿Guardar cambios?',
            text: esCreacion ? 'Crear tipo "' + nombre + '"' : 'Actualizar tipo "' + nombre + '"',
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
            params.append('agregar_tipo_activo', 'true');
        } else {
            params.append('editar_tipo_activo', id);
        }
        params.append('nombre_tipo_activo', nombre);
        params.append('descripcion_tipo_activo', descripcion);

        try {
            const res = await fetch('/inventario/', {
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
                await Swal.fire({ icon: 'success', title: esCreacion ? 'Tipo creado' : 'Tipo actualizado', text: data.mensaje, timer: 2000, showConfirmButton: false });
                resetFormTipoActivo();
                cargarTiposActivo();
            } else {
                Swal.fire({ icon: 'error', title: 'Error', text: data.mensaje || 'Error al guardar tipo' });
            }
        } catch (err) {
            console.error('Error al guardar tipo:', err);
            Swal.fire({ icon: 'error', title: 'Error', text: 'Error de conexión' });
        }
    });
});
