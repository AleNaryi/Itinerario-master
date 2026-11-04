$(document).ready(function() {
    if (!$.fn.DataTable) return;
    $.extend($.fn.DataTable.defaults, {
        language: {
            processing: "Procesando...",
            search: "Buscar:",
            lengthMenu: "Mostrar _MENU_ registros",
            info: "Mostrando _START_ a _END_ de _TOTAL_ registros",
            infoEmpty: "Mostrando 0 a 0 de 0 registros",
            infoFiltered: "(filtrado de _MAX_ registros totales)",
            infoPostFix: "",
            loadingRecords: "Cargando...",
            zeroRecords: "No se encontraron registros",
            emptyTable: "No hay datos disponibles en la tabla",
            paginate: {
                first: "Primero",
                previous: "Anterior",
                next: "Siguiente",
                last: "Último"
            },
            aria: {
                sortAscending: ": activar para ordenar ascendente",
                sortDescending: ": activar para ordenar descendente"
            }
        },
        pageLength: 25,
        lengthMenu: [10, 25, 50, 100],
        order: [],
        columnDefs: [
            { orderable: false, targets: 'no-order' }
        ]
    });
    $('table.datatable').DataTable();
});
