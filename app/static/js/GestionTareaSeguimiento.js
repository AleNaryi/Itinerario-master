function getCSRF() {
    var el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

function escHtml(str) {
    if (!str) return '';
    return String(str).replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/'/g, '&#39;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

document.addEventListener('DOMContentLoaded', function() {
    var tabla = document.getElementById('tablaSeguimiento');
    if (!tabla || typeof jQuery === 'undefined' || !jQuery.fn.DataTable) return;

    if (jQuery.fn.DataTable.isDataTable('#tablaSeguimiento')) {
        jQuery('#tablaSeguimiento').DataTable().destroy();
    }

    jQuery('#tablaSeguimiento').DataTable({
        ajax: {
            url: '/gestion-tarea/consultar-asignaciones',
            type: 'POST',
            data: function(d) { d.csrf_token = getCSRF(); },
            dataSrc: function(json) {
                if (json.error) {
                    Swal.fire({ icon: 'error', title: 'Error', text: json.error });
                    return [];
                }
                return json;
            }
        },
        columns: [
            { data: 'usuario_nombre', className: 'text-center',
                render: function(d, type, row) { return escHtml(d) + ' <small class="text-muted">(' + escHtml(row.usuario_cedula) + ')</small>'; } },
            { data: 'Nombre_Tarea', className: 'text-center' },
            { data: 'Instruccion', className: 'text-center',
                render: function(d) { return '<span class="text-truncate d-inline-block" style="max-width:250px;">' + escHtml(d) + '</span>'; } },
            {
                data: 'Estado', className: 'text-center',
                render: function(d) {
                    if (d === 'Completada') return '<span class="badge bg-success rounded-pill px-3">Completada</span>';
                    if (d === 'En Progreso') return '<span class="badge bg-info rounded-pill px-3">En Progreso</span>';
                    return '<span class="badge bg-warning text-dark rounded-pill px-3">Pendiente</span>';
                }
            },
            { data: 'fecha_asignacion_tarea', className: 'text-center' },
            {
                data: null,
                orderable: false,
                className: 'text-center',
                render: function(row) {
                    if (row.Estado === 'Completada') {
                        return '<span class="text-success small fw-bold"><i class="fas fa-check-circle me-1"></i>Finalizada</span>';
                    }
                    return '<button class="btn btn-action btn-action-success btn-completar-seguimiento" data-id="' + row.id_asignacion + '" title="Marcar como completada"><i class="fas fa-check"></i></button>';
                }
            }
        ],
        language: { url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json' },
        pageLength: 25,
        order: [[4, 'desc']],
        columnDefs: [{ orderable: false, targets: 'no-order' }]
    });

    document.getElementById('tablaSeguimiento').addEventListener('click', function(e) {
        var btn = e.target.closest('.btn-completar-seguimiento');
        if (!btn) return;
        var id = btn.getAttribute('data-id');
        Swal.fire({
            title: '¿Completar tarea?',
            text: 'Esta tarea se marcará como completada.',
            icon: 'question',
            showCancelButton: true,
            confirmButtonColor: '#198754',
            confirmButtonText: 'Sí, completar',
            cancelButtonText: 'Cancelar'
        }).then(function(result) {
            if (!result.isConfirmed) return;
            var params = new URLSearchParams();
            params.append('id_asignacion', id);
            params.append('csrf_token', getCSRF());
            fetch('/gestion-tarea/completar', {
                method: 'POST',
                headers: { 'Accept': 'application/json' },
                body: params
            })
                .then(function(r) { return r.json(); })
                .then(function(data) {
                    if (data.error) { Swal.fire({ icon: 'error', title: 'Error', text: data.error }); return; }
                    Swal.fire({ icon: 'success', title: 'Completada', text: 'Tarea marcada como completada', timer: 1500, showConfirmButton: false });
                    jQuery('#tablaSeguimiento').DataTable().ajax.reload();
                })
                .catch(function(err) { console.error('Error:', err); });
        });
    });
});