function getCSRF() {
    var el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

document.addEventListener('DOMContentLoaded', function() {
    var tabla = document.getElementById('tablaReels');
    if (!tabla || typeof jQuery === 'undefined' || !jQuery.fn.DataTable) return;

    if (jQuery.fn.DataTable.isDataTable('#tablaReels')) {
        jQuery('#tablaReels').DataTable().destroy();
    }

    jQuery('#tablaReels').DataTable({
        ajax: {
            url: '/reels/',
            type: 'POST',
            data: function(d) { d.consultar = true; d.csrf_token = getCSRF(); },
            dataSrc: ''
        },
        columns: [
            { data: 'nombre', className: 'text-center' },
            { data: 'duracion_total', className: 'text-center', render: function(d) { return d ? Number(d).toFixed(2) + ' min' : '-'; } },
            {
                data: null,
                orderable: false,
                className: 'text-center',
                render: function(row) {
                    return '<div class="action-group">'
                        + '<a href="/reels/ver/' + row.id + '" class="btn btn-action btn-action-primary"><i class="fas fa-eye"></i></a>'
                        + '<a href="/reels/editar/' + row.id + '" class="btn btn-action btn-action-edit btn-editar-reel"><i class="fas fa-pen"></i></a>'
                        + '<button type="button" class="btn btn-action btn-action-danger btn-eliminar-reel" data-id="' + row.id + '" data-nombre="' + (row.nombre || '') + '"><i class="fas fa-trash"></i></button>'
                        + '</div>';
                }
            }
        ],
        language: { url: '//cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json' },
        pageLength: 25,
        order: [[0, 'desc']],
        columnDefs: [{ orderable: false, targets: 'no-order' }]
    });

    document.addEventListener('click', function(e) {
        var btnEditar = e.target.closest('.btn-editar-reel');
        if (btnEditar) {
            e.preventDefault();
            var href = btnEditar.getAttribute('href');
            Swal.fire({
                title: '¿Editar reel?',
                text: 'Se abrirá el formulario de edición.',
                icon: 'info',
                showCancelButton: true,
                confirmButtonColor: '#ffc107',
                confirmButtonText: 'Editar',
                cancelButtonText: 'Cancelar'
            }).then(function(result) {
                if (result.isConfirmed) window.location.href = href;
            });
        }
    });

    document.addEventListener('click', function(e) {
        var btnEliminar = e.target.closest('.btn-eliminar-reel');
        if (btnEliminar) {
            e.preventDefault();
            var id = btnEliminar.dataset.id;
            var nombre = btnEliminar.dataset.nombre;
            Swal.fire({
                title: '¿Eliminar reel?',
                text: 'Se eliminará el reel "' + nombre + '" y todos sus videos.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'Eliminar',
                cancelButtonText: 'Cancelar'
            }).then(function(result) {
                if (result.isConfirmed) {
                    var form = document.createElement('form');
                    form.method = 'POST';
                    form.action = '/reels/eliminar/' + id;
                    var inputCSRF = document.createElement('input');
                    inputCSRF.type = 'hidden';
                    inputCSRF.name = 'csrf_token';
                    inputCSRF.value = getCSRF();
                    form.appendChild(inputCSRF);
                    document.body.appendChild(form);
                    form.submit();
                }
            });
        }
    });
});
