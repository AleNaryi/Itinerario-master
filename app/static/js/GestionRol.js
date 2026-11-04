document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.select-all-module').forEach(function(btn) {
        btn.addEventListener('click', function() {
            var modulo = this.getAttribute('data-modulo');
            var checkboxes = document.querySelectorAll('.permiso-item[data-modulo="' + modulo + '"] .permiso-checkbox');
            var allChecked = true;
            checkboxes.forEach(function(cb) {
                if (!cb.checked) allChecked = false;
            });
            checkboxes.forEach(function(cb) {
                if (!cb.disabled) cb.checked = allChecked ? false : true;
            });
        });
    });

    function getCSRF() {
        var el = document.querySelector('input[name="csrf_token"]');
        return el ? el.value : '';
    }

    var tabla = document.getElementById('tablaUsuarios');
    if (tabla && typeof jQuery !== 'undefined' && jQuery.fn.DataTable) {
        if (jQuery.fn.DataTable.isDataTable('#tablaUsuarios')) {
            jQuery('#tablaUsuarios').DataTable().destroy();
        }
        jQuery('#tablaUsuarios').DataTable({
            ajax: {
                url: '/roles/',
                type: 'POST',
                data: function(d) { d.listar_usuarios = true; d.csrf_token = getCSRF(); },
                dataSrc: ''
            },
            columns: [
                { data: 'nombre' },
                { data: 'email' },
                { data: 'rol' },
                {
                    data: 'id',
                    orderable: false,
                    render: function(id, type, row) {
                        var editUrl = '/roles/editar/' + id;
                        return '<a href="' + editUrl + '" class="btn btn-action btn-action-primary"><i class="fas fa-pen"></i></a>';
                    }
                }
            ],
            language: { url: 'https://cdn.datatables.net/plug-ins/1.13.6/i18n/es-ES.json' },
            pageLength: 25,
            order: [[0, 'asc']]
        });
    }
});
