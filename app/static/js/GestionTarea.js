import { validarTexto, validarTextoLargo } from './validacion.js';

function getCSRF() {
    var el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

function sendFetch(form, confirmMsg) {
    var params = new URLSearchParams(new FormData(form));
    params.append('csrf_token', getCSRF());
    fetch('/gestion-tarea/', { method: 'POST', body: params })
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.error) {
                Swal.fire({ title: 'Error', text: data.error, icon: 'error', confirmButtonColor: '#3085d6' });
                return;
            }
            Swal.fire({ title: 'Operación exitosa', icon: 'success', timer: 1500, showConfirmButton: false })
                .then(function() { location.reload(); });
        })
        .catch(function(err) { console.error('Error:', err); });
}

document.addEventListener('DOMContentLoaded', function() {
    function getCSRFStatic() { return getCSRF(); }

    var tabla = document.getElementById('tablaTareas');
    if (tabla && typeof jQuery !== 'undefined' && jQuery.fn.DataTable) {
        if (jQuery.fn.DataTable.isDataTable('#tablaTareas')) {
            jQuery('#tablaTareas').DataTable().destroy();
        }
        jQuery('#tablaTareas').DataTable({
            ajax: {
                url: '/gestion-tarea/',
                type: 'POST',
                data: function(d) { d.consultar = true; d.csrf_token = getCSRFStatic(); },
                dataSrc: ''
            },
            columns: [
                { data: 'id_tarea' },
                { data: 'Nombre_Tarea' },
                { data: 'Instruccion', render: function(d) { return '<span class="text-truncate d-inline-block" style="max-width:300px;">' + (d || '') + '</span>'; } },
                {
                    data: 'Estatus',
                    render: function(d) { return d ? '<span class="badge bg-success-subtle text-success rounded-pill px-3">Activa</span>' : '<span class="badge bg-secondary-subtle text-secondary rounded-pill px-3">Inactiva</span>'; }
                },
                {
                    data: null,
                    orderable: false,
                    render: function(row) {
                        var id = row.id_tarea;
                        var nombre = (row.Nombre_Tarea || '').replace(/'/g, "\\'");
                        var instr = (row.Instruccion || '').replace(/'/g, "\\'");
                        return '<div class="action-group">'
                            + '<button class="btn btn-action btn-action-edit" onclick="editarTarea(\'' + id + '\', \'' + nombre + '\', \'' + instr + '\')" title="Editar"><i class="fas fa-pen"></i></button>'
                            + '<button class="btn btn-action btn-action-danger" onclick="confirmarEliminar(\'' + id + '\', \'' + nombre + '\')" title="Eliminar"><i class="fas fa-trash"></i></button>'
                            + '</div>';
                    }
                }
            ],
            language: { url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json' },
            pageLength: 25,
            order: [[0, 'desc']]
        });
    }

    var formCrear = document.getElementById('formCrearTarea');
    if (formCrear) {
        var nombre = formCrear.querySelector('[name="Nombre_Tarea"]');
        var instruccion = formCrear.querySelector('[name="Instruccion"]');
        if (nombre) { nombre.addEventListener('input', function() { validarTexto(this); }); nombre.addEventListener('blur', function() { validarTexto(this); }); }
        if (instruccion) { instruccion.addEventListener('input', function() { validarTextoLargo(this); }); instruccion.addEventListener('blur', function() { validarTextoLargo(this); }); }
        formCrear.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validarTexto(nombre) || !validarTextoLargo(instruccion)) {
                Swal.fire({ title: 'Error de validación', text: 'Corrige los campos marcados en rojo.', icon: 'error' });
                return;
            }
            Swal.fire({
                title: '¿Crear tarea?', icon: 'question', showCancelButton: true,
                confirmButtonColor: '#198754', cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, crear', cancelButtonText: 'Cancelar'
            }).then(function(r) { if (r.isConfirmed) sendFetch(formCrear); });
        });
    }

    var formEditar = document.getElementById('formEditarTarea');
    if (formEditar) {
        var editNombre = document.getElementById('edit_Nombre_Tarea');
        var editInst = document.getElementById('edit_Instruccion');
        if (editNombre) { editNombre.addEventListener('input', function() { validarTexto(this); }); editNombre.addEventListener('blur', function() { validarTexto(this); }); }
        if (editInst) { editInst.addEventListener('input', function() { validarTextoLargo(this); }); editInst.addEventListener('blur', function() { validarTextoLargo(this); }); }
        formEditar.addEventListener('submit', function(e) {
            e.preventDefault();
            if (!validarTexto(editNombre) || !validarTextoLargo(editInst)) {
                Swal.fire({ title: 'Error de validación', text: 'Corrige los campos marcados en rojo.', icon: 'error' });
                return;
            }
            Swal.fire({
                title: '¿Guardar cambios?', icon: 'question', showCancelButton: true,
                confirmButtonColor: '#198754', cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, guardar', cancelButtonText: 'Cancelar'
            }).then(function(r) { if (r.isConfirmed) sendFetch(formEditar); });
        });
    }

    var formAsignar = document.getElementById('formAsignarTarea');
    if (formAsignar) {
        formAsignar.addEventListener('submit', function(e) {
            e.preventDefault();
            var selUsuarios = document.getElementById('asig_usuarios');
            var selDepto = document.getElementById('asig_departamento');
            if (!selUsuarios || !selDepto) return;
            if (!selUsuarios.selectedOptions.length && !selDepto.value) {
                Swal.fire({ title: 'Falta el destinatario', text: 'Marca al menos un empleado o elige un departamento completo.', icon: 'warning' });
                return;
            }
            Swal.fire({
                title: '¿Asignar tarea?', icon: 'question', showCancelButton: true,
                confirmButtonColor: '#198754', cancelButtonColor: '#6c757d',
                confirmButtonText: 'Sí, asignar', cancelButtonText: 'Cancelar'
            }).then(function(r) { if (r.isConfirmed) sendFetch(formAsignar); });
        });
    }
});

window.editarTarea = function(id, nombre, instruccion) {
    document.getElementById('edit_Nombre_Tarea').value = nombre;
    document.getElementById('edit_Instruccion').value = instruccion;
    document.getElementById('edit_id_tarea').value = id;
    new bootstrap.Modal(document.getElementById('modalEditarTarea')).show();
};

window.confirmarEliminar = function(id, nombre) {
    Swal.fire({
        title: '¿Eliminar tarea?', text: 'Se eliminará: "' + nombre + '"',
        icon: 'warning', showCancelButton: true,
        confirmButtonColor: '#dc3545', cancelButtonText: 'Cancelar',
        confirmButtonText: 'Sí, eliminar'
    }).then(function(result) {
        if (!result.isConfirmed) return;
        var params = new URLSearchParams();
        params.append('eliminar', 'true');
        params.append('id_tarea', id);
        params.append('csrf_token', document.querySelector('input[name="csrf_token"]').value);
        fetch('/gestion-tarea/', { method: 'POST', body: params })
            .then(function(r) { return r.json(); })
            .then(function(data) {
                if (data.error) { Swal.fire({ title: 'Error', text: data.error, icon: 'error' }); return; }
                Swal.fire({ title: 'Tarea eliminada', icon: 'success', timer: 1500, showConfirmButton: false })
                    .then(function() { location.reload(); });
            });
    });
};
