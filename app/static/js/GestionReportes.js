const COLUMNAS_PREVIEW = window.COLUMNAS_PREVIEW || {};

const MODULE_CONFIG = {
    guiones: {
        filters: [
            { id: 'estado', label: 'Estado', type: 'select',
                options: [
                    { value: '', label: 'Todos' },
                    { value: 'borrador', label: 'Borrador' },
                    { value: 'publicado', label: 'Publicado' },
                    { value: 'en_vivo', label: 'En Vivo' },
                    { value: 'finalizado', label: 'Finalizado' },
                ], colClass: 'col-md-3' },
            { id: 'encargado', label: 'Encargado', type: 'select', loadVia: 'ajax', colClass: 'col-md-3' },
            { id: 'elementos_min', label: 'Elementos Mín', type: 'number', placeholder: '0', colClass: 'col-md-2' },
            { id: 'elementos_max', label: 'Elementos Máx', type: 'number', placeholder: '100', colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'nombre', label: 'Nombre' }, { key: 'game', label: 'Game' },
            { key: 'pregame', label: 'Pre-Game' }, { key: 'fecha_ejecucion', label: 'Ejecución' },
            { key: 'estado', label: 'Estado' }, { key: 'tiempo_total', label: 'Tiempo' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'borradores', label: 'Borradores', color: '#f59e0b' },
            { key: 'publicados', label: 'Publicados', color: '#10b981' },
            { key: 'en_vivo', label: 'En Vivo', color: '#06b6d4' },
            { key: 'finalizados', label: 'Finalizados', color: '#64748b' },
            { key: 'tiempo_total', label: 'Tiempo Total', color: '#8b5cf6' },
        ],
    },
    inventario: {
        filters: [
            { id: 'tipo_nombre', label: 'Tipo', type: 'select', loadVia: 'ajax', colClass: 'col-md-3', progressive: ['estado_nombre'] },
            { id: 'estado_nombre', label: 'Estado', type: 'select', loadVia: 'ajax', dependsOn: ['tipo_nombre'], colClass: 'col-md-3' },
            { id: 'costo_min', label: 'Costo Mín', type: 'number', placeholder: '0', colClass: 'col-md-2' },
            { id: 'costo_max', label: 'Costo Máx', type: 'number', placeholder: '999999', colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'id', label: 'ID' }, { key: 'nombre', label: 'Nombre' },
            { key: 'tipo_nombre', label: 'Tipo' }, { key: 'estado_nombre', label: 'Estado' },
            { key: 'costo', label: 'Costo' }, { key: 'fecha_compra', label: 'Compra' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'costo_total', label: 'Costo Total', color: '#8b5cf6' },
            { key: 'costo_promedio', label: 'Costo Promedio', color: '#06b6d4' },
        ],
    },
    premios: {
        filters: [
            { id: 'estado', label: 'Estado', type: 'select',
                options: [
                    { value: '', label: 'Todos' },
                    { value: 'pendiente', label: 'Pendientes' },
                    { value: 'entregado', label: 'Entregados' },
                ], colClass: 'col-md-3',
                progressive: ['patrocinador_id'] },
            { id: 'patrocinador_id', label: 'Patrocinador', type: 'select', loadVia: 'ajax', dependsOn: ['estado'], colClass: 'col-md-3' },
            { id: 'cantidad_min', label: 'Cantidad Mín', type: 'number', placeholder: '0', colClass: 'col-md-2' },
            { id: 'cantidad_max', label: 'Cantidad Máx', type: 'number', placeholder: '999', colClass: 'col-md-2' },
            { id: 'cantidad_entregada_min', label: 'Entregados Mín', type: 'number', placeholder: '0', colClass: 'col-md-2' },
            { id: 'cantidad_entregada_max', label: 'Entregados Máx', type: 'number', placeholder: '999', colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'nombre', label: 'Nombre' }, { key: 'patrocinador_nombre', label: 'Patrocinador' },
            { key: 'estado', label: 'Estado' }, { key: 'cantidad', label: 'Total' },
            { key: 'cantidad_entregada', label: 'Entregados' }, { key: 'fecha_creacion', label: 'Creación' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'pendientes', label: 'Pendientes', color: '#f59e0b' },
            { key: 'entregados', label: 'Entregados', color: '#10b981' },
            { key: 'tasa_entrega', label: '% Entregado', color: '#06b6d4' },
        ],
    },
    contratos: {
        filters: [
            {
                id: 'tipo', label: 'Tipo', type: 'select',
                options: [
                    { value: '', label: 'Todos los tipos' },
                    { value: '1', label: 'Bronce' },
                    { value: '2', label: 'Plata' },
                    { value: '3', label: 'Oro' },
                ],
                colClass: 'col-md-3',
                progressive: ['patrocinador_id'],
            },
            {
                id: 'estatus', label: 'Estatus', type: 'select',
                options: [
                    { value: '', label: 'Todos los estados' },
                    { value: 'Vigente', label: 'Vigentes' },
                    { value: 'Vencido', label: 'Vencidos' },
                    { value: 'Borrador', label: 'Borradores' },
                ],
                colClass: 'col-md-3',
            },
            {
                id: 'patrocinador_id', label: 'Patrocinador', type: 'select',
                loadVia: 'ajax',
                dependsOn: ['tipo'],
                colClass: 'col-md-3',
            },
            {
                id: 'monto_min', label: 'Monto Mín', type: 'number',
                placeholder: '0',
                colClass: 'col-md-2',
            },
            {
                id: 'monto_max', label: 'Monto Máx', type: 'number',
                placeholder: '999999',
                colClass: 'col-md-2',
            },
            {
                id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date',
                colClass: 'col-md-3',
            },
            {
                id: 'fecha_fin', label: 'Fecha Fin', type: 'date',
                colClass: 'col-md-3',
            },
        ],
        columns: [
            { key: 'nombre_empresa', label: 'Patrocinador' },
            { key: 'tipo', label: 'Tipo' },
            { key: 'estatus', label: 'Estatus' },
            { key: 'monto_total', label: 'Monto' },
            { key: 'fecha_inicio', label: 'Inicio' },
            { key: 'fecha_fin', label: 'Fin' },
            { key: 'dias_restantes', label: 'Días' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'vigentes', label: 'Vigentes', color: '#10b981' },
            { key: 'vencidos', label: 'Vencidos', color: '#ef4444' },
            { key: 'borradores', label: 'Borradores', color: '#f59e0b' },
            { key: 'bronce', label: 'Bronce', color: '#cd7f32' },
            { key: 'plata', label: 'Plata', color: '#94a3b8' },
            { key: 'oro', label: 'Oro', color: '#f59e0b' },
            { key: 'monto_total', label: 'Monto Total', color: '#2563eb' },
            { key: 'monto_promedio', label: 'Promedio', color: '#06b6d4' },
            { key: 'monto_min', label: 'Monto Mín', color: '#64748b' },
            { key: 'monto_max', label: 'Monto Máx', color: '#64748b' },
            { key: 'vigentes_porcentaje', label: '% Vigentes', color: '#10b981' },
        ],
    },
    balance: {
        filters: [
            { id: 'tipo_pago', label: 'Tipo Pago', type: 'select', loadVia: 'ajax', colClass: 'col-md-3' },
            { id: 'patrocinador_id', label: 'Patrocinador', type: 'select', loadVia: 'ajax', colClass: 'col-md-3' },
            { id: 'monto_min', label: 'Monto Mín', type: 'number', placeholder: '0', colClass: 'col-md-2' },
            { id: 'monto_max', label: 'Monto Máx', type: 'number', placeholder: '999999', colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'nombre_patrocinador', label: 'Patrocinador' },
            { key: 'tipo_pago', label: 'Tipo Pago' },
            { key: 'monto', label: 'Monto' },
            { key: 'referencia', label: 'Referencia' },
            { key: 'fecha_pago', label: 'Fecha Pago' },
        ],
        kpiCards: [
            { key: 'total_pagos', label: 'Total Pagos', color: '#2563eb' },
            { key: 'monto_total', label: 'Monto Total', color: '#10b981' },
            { key: 'promedio', label: 'Promedio', color: '#06b6d4' },
            { key: 'monto_min', label: 'Monto Mín', color: '#64748b' },
            { key: 'monto_max', label: 'Monto Máx', color: '#ef4444' },
        ],
    },
    tareas: {
        filters: [
            { id: 'estado', label: 'Estado', type: 'select',
                options: [
                    { value: '', label: 'Todos' },
                    { value: 'Pendiente', label: 'Pendientes' },
                    { value: 'En Progreso', label: 'En Progreso' },
                    { value: 'Completada', label: 'Completadas' },
                ], colClass: 'col-md-3',
                progressive: ['asignado_a'] },
            { id: 'asignado_a', label: 'Usuario Asignado', type: 'select', loadVia: 'ajax', dependsOn: ['estado'], colClass: 'col-md-3' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'nombre_tarea', label: 'Tarea' },
            { key: 'estado', label: 'Estado' },
            { key: 'asignado_a', label: 'Asignado a' },
            { key: 'fecha_asignacion_tarea', label: 'Fecha' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'pendientes', label: 'Pendientes', color: '#f59e0b' },
            { key: 'en_progreso', label: 'En Progreso', color: '#06b6d4' },
            { key: 'completadas', label: 'Completadas', color: '#10b981' },
            { key: 'completadas_pct', label: '% Compl.', color: '#10b981' },
        ],
    },
    patrocinadores: {
        filters: [
            { id: 'tipo_contrato', label: 'Tipo Contrato', type: 'select',
                options: [
                    { value: '', label: 'Todos' },
                    { value: 'Vigente', label: 'Vigentes' },
                    { value: 'Vencido', label: 'Vencidos' },
                ], colClass: 'col-md-3' },
            { id: 'estado_pat', label: 'Estado', type: 'select',
                options: [
                    { value: '', label: 'Todos' },
                    { value: '1', label: 'Activos' },
                    { value: '0', label: 'Inactivos' },
                ], colClass: 'col-md-3' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'nombre_empresa', label: 'Empresa' },
            { key: 'rif', label: 'RIF' },
            { key: 'telefono', label: 'Teléfono' },
            { key: 'tipo_contrato', label: 'Contrato' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'activos', label: 'Activos', color: '#10b981' },
            { key: 'inactivos', label: 'Inactivos', color: '#ef4444' },
        ],
    },
    usuarios: {
        filters: [
            { id: 'departamento', label: 'Departamento', type: 'select', loadVia: 'ajax', colClass: 'col-md-3',
                progressive: ['rol'] },
            { id: 'rol', label: 'Rol', type: 'select', loadVia: 'ajax', dependsOn: ['departamento'], colClass: 'col-md-3' },
            { id: 'activo', label: 'Estado', type: 'select',
                options: [
                    { value: '', label: 'Todos' },
                    { value: '1', label: 'Activos' },
                    { value: '0', label: 'Inactivos' },
                ], colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'nombre', label: 'Nombre' }, { key: 'email', label: 'Email' },
            { key: 'rol', label: 'Rol' }, { key: 'departamento', label: 'Depto' },
            { key: 'activo', label: 'Estado' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'activos', label: 'Activos', color: '#10b981' },
            { key: 'inactivos', label: 'Inactivos', color: '#ef4444' },
        ],
    },
    mantenimiento: {
        filters: [
            { id: 'estado', label: 'Estado', type: 'select',
                options: [
                    { value: '', label: 'Todos' },
                    { value: 'en_espera', label: 'En Espera' },
                    { value: 'en_reparacion', label: 'En Reparación' },
                    { value: 'reparado', label: 'Reparado' },
                    { value: 'baja', label: 'Dado de Baja' },
                ], colClass: 'col-md-3',
                progressive: ['recurso_id'] },
            { id: 'recurso_id', label: 'Recurso', type: 'select', loadVia: 'ajax', dependsOn: ['estado'], colClass: 'col-md-3' },
            { id: 'dias_min', label: 'Días Mín', type: 'number', placeholder: '0', colClass: 'col-md-2' },
            { id: 'dias_max', label: 'Días Máx', type: 'number', placeholder: '365', colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'recurso_nombre', label: 'Recurso' }, { key: 'estado', label: 'Estado' },
            { key: 'fecha_ingreso', label: 'Ingreso' }, { key: 'dias_en_taller', label: 'Días' },
            { key: 'diagnostico', label: 'Diagnóstico' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'en_espera', label: 'En Espera', color: '#f59e0b' },
            { key: 'en_reparacion', label: 'En Reparación', color: '#06b6d4' },
            { key: 'reparados', label: 'Reparados', color: '#10b981' },
            { key: 'dados_baja', label: 'Dados Baja', color: '#ef4444' },
            { key: 'promedio_dias', label: 'Días Prom.', color: '#8b5cf6' },
        ],
    },
    reels: {
        filters: [
            { id: 'patrocinador_id', label: 'Patrocinador', type: 'select', loadVia: 'ajax', colClass: 'col-md-3' },
            { id: 'duracion_min', label: 'Duración Mín (seg)', type: 'number', placeholder: '0', colClass: 'col-md-2' },
            { id: 'duracion_max', label: 'Duración Máx (seg)', type: 'number', placeholder: '3600', colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-3' },
        ],
        columns: [
            { key: 'nombre', label: 'Nombre' }, { key: 'patrocinado', label: 'Patrocinador' },
            { key: 'videos_count', label: 'Videos' }, { key: 'duracion', label: 'Duración' },
            { key: 'creado_en', label: 'Creado' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total Reels', color: '#2563eb' },
            { key: 'total_videos', label: 'Total Videos', color: '#06b6d4' },
            { key: 'duracion_total', label: 'Duración Total', color: '#8b5cf6' },
            { key: 'duracion_promedio', label: 'Duración Prom.', color: '#64748b' },
        ],
    },
    bitacora: {
        filters: [
            { id: 'usuario_id', label: 'Usuario', type: 'select', loadVia: 'ajax', colClass: 'col-md-3' },
            { id: 'tipo_accion', label: 'Acción', type: 'select', loadVia: 'ajax', colClass: 'col-md-2' },
            { id: 'modulo_filter', label: 'Módulo', type: 'select', loadVia: 'ajax', colClass: 'col-md-2' },
            { id: 'fecha_inicio', label: 'Fecha Inicio', type: 'date', colClass: 'col-md-3' },
            { id: 'fecha_fin', label: 'Fecha Fin', type: 'date', colClass: 'col-md-2' },
        ],
        columns: [
            { key: 'usuario_nombre', label: 'Usuario' }, { key: 'tipo_accion', label: 'Acción' },
            { key: 'modulo', label: 'Módulo' }, { key: 'detalle', label: 'Detalle' },
            { key: 'created_at', label: 'Fecha' },
        ],
        kpiCards: [
            { key: 'total', label: 'Total', color: '#2563eb' },
            { key: 'creaciones', label: 'Creaciones', color: '#10b981' },
            { key: 'ediciones', label: 'Ediciones', color: '#06b6d4' },
            { key: 'eliminaciones', label: 'Eliminaciones', color: '#ef4444' },
        ],
    },
};

const MONEY_KEYS = ['monto', 'monto_total', 'capital', 'saldo', 'precio', 'monto_vigentes', 'monto_promedio', 'monto_min', 'monto_max'];

let moduloActual = null;
let datosPreview = null;

function getCSRF() {
    const el = document.querySelector('input[name="csrf_token"]');
    return el ? el.value : '';
}

function moneyStr(val) {
    if (typeof val === 'string' && val.startsWith('$')) return val;
    const n = parseFloat(val);
    if (isNaN(n)) return val;
    return '$' + n.toLocaleString('es-VE', { minimumFractionDigits: 0, maximumFractionDigits: 0 });
}

document.addEventListener('DOMContentLoaded', function () {
    const moduloGrid = document.getElementById('moduloGrid');
    const filterPanel = document.getElementById('filterPanel');
    const filterPanelBody = document.getElementById('filterPanelBody');
    const filterModuloNombre = document.getElementById('filterModuloNombre');
    const btnPreview = document.getElementById('btnPreview');
    const btnCerrarPanel = document.getElementById('btnCerrarPanel');
    const btnLimpiarFiltros = document.getElementById('btnLimpiarFiltros');
    const btnDescargarPDF = document.getElementById('btnDescargarPDF');
    const btnCerrarPreview = document.getElementById('btnCerrarPreview');
    const kpiPreviewCard = document.getElementById('kpiPreviewCard');
    const kpiGrid = document.getElementById('kpiGrid');
    const previewHead = document.getElementById('previewHead');
    const previewBody = document.getElementById('previewBody');
    const previewNote = document.getElementById('previewNote');
    const kpiModuloNombre = document.getElementById('kpiModuloNombre');
    const kpiTotalRegistros = document.getElementById('kpiTotalRegistros');

    moduloGrid.addEventListener('click', function (e) {
        const card = e.target.closest('.modulo-card');
        if (!card) return;
        const modulo = card.dataset.modulo;
        abrirModulo(modulo, card);
    });

    function abrirModulo(modulo, card) {
        moduloGrid.querySelectorAll('.modulo-card').forEach(c => c.classList.remove('active'));
        if (card) card.classList.add('active');
        if (kpiPreviewCard) kpiPreviewCard.style.display = 'none';

        moduloActual = modulo;
        filterModuloNombre.textContent = card ? card.dataset.nombre : modulo;
        btnPreview.disabled = true;

        const config = MODULE_CONFIG[modulo];
        if (!config) {
            filterPanelBody.innerHTML = '<div class="text-center text-muted py-3"><i class="fas fa-cog fa-spin me-2"></i>Configuración no disponible</div>';
            filterPanel.classList.add('open');
            return;
        }

        filterPanelBody.innerHTML = '<div class="text-center text-muted py-4"><span class="filter-spinner"></span> Preparando filtros...</div>';
        filterPanel.classList.add('open');

        setTimeout(() => renderFiltros(modulo, config), 100);
    }

    function renderFiltros(modulo, config) {
        const html = ['<div class="row g-3">'];
        config.filters.forEach((f, i) => {
            const col = f.colClass || 'col-md-3';
            html.push(`<div class="${col} filter-group">`);
            html.push(`<label class="form-label fw-bold small mb-1">${f.label}</label>`);

            if (f.type === 'select') {
                html.push(`<select id="filtro_${f.id}" class="form-select form-select-sm" data-modulo="${modulo}" data-filter="${f.id}" data-loadvia="${f.loadVia || ''}" data-progressive="${(f.progressive || []).join(',')}" data-depends="${(f.dependsOn || []).join(',')}">`);
                if (f.loadVia === 'ajax') {
                    html.push('<option value="" disabled selected>Cargando...</option>');
                } else if (f.options) {
                    f.options.forEach(o => {
                        html.push(`<option value="${o.value}">${o.label}</option>`);
                    });
                }
                html.push('</select>');
            } else if (f.type === 'number') {
                html.push(`<input type="number" id="filtro_${f.id}" class="form-control form-control-sm" placeholder="${f.placeholder || ''}" min="0" data-modulo="${modulo}" data-filter="${f.id}">`);
            } else if (f.type === 'date') {
                html.push(`<input type="date" id="filtro_${f.id}" class="form-control form-control-sm" data-modulo="${modulo}" data-filter="${f.id}">`);
            }

            html.push('</div>');
        });
        html.push('</div>');

        // Análisis opcional del PDF (disponible para todos los módulos)
        html.push('<div class="row g-2 mt-2 pt-2 border-top">');
        html.push('<div class="col-12"><label class="form-label fw-bold small mb-1 text-muted"><i class="fas fa-chart-line me-1"></i>Análisis del PDF</label></div>');
        html.push('<div class="col-md-4 form-check form-switch ps-4">'
            + '<input class="form-check-input" type="checkbox" id="opcion_resumen" checked>'
            + '<label class="form-check-label small" for="opcion_resumen">Resumen ejecutivo</label></div>');
        html.push('<div class="col-md-4 form-check form-switch ps-4">'
            + '<input class="form-check-input" type="checkbox" id="opcion_comparar">'
            + '<label class="form-check-label small" for="opcion_comparar">Comparar período anterior</label></div>');
        html.push('<div class="col-md-4">'
            + '<input type="number" class="form-control form-control-sm" id="opcion_top_n" placeholder="Top N destacados (ej. 5)" min="1" max="20"></div>');
        html.push('</div>');
        filterPanelBody.innerHTML = html.join('');

        config.filters.forEach(f => {
            const el = document.getElementById(`filtro_${f.id}`);
            if (el && f.loadVia === 'ajax') {
                cargarOpcionesAjax(modulo, f.id, config, {});
            }
            if (el && el.tagName === 'SELECT') {
                el.addEventListener('change', function () {
                    const progressive = (this.dataset.progressive || '').split(',').filter(Boolean);
                    if (progressive.length > 0) {
                        const params = obtenerValoresFiltros(modulo);
                        progressive.forEach(targetId => {
                            mostrarSpinnerEn(targetId);
                            cargarOpcionesAjax(modulo, targetId, config, params);
                        });
                    }
                    validarFiltros(modulo, config);
                });
            }
            if (el && (el.tagName === 'INPUT' && (el.type === 'number' || el.type === 'date'))) {
                el.addEventListener('input', () => validarFiltros(modulo, config));
                el.addEventListener('change', () => validarFiltros(modulo, config));
            }
        });

        btnPreview.disabled = false;
    }

    function mostrarSpinnerEn(filterId) {
        const el = document.getElementById(`filtro_${filterId}`);
        if (!el) return;
        if (el.tagName === 'SELECT') {
            el.innerHTML = '<option value="" disabled selected><span class="filter-spinner"></span> Cargando...</option>';
        }
    }

    async function cargarOpcionesAjax(modulo, filterId, config, params) {
        const el = document.getElementById(`filtro_${filterId}`);
        if (!el) return;

        try {
            const qs = new URLSearchParams();
            const f = config.filters.find(x => x.id === filterId);
            if (f && f.dependsOn) {
                f.dependsOn.forEach(depId => {
                    if (params[depId] !== undefined && params[depId] !== '') {
                        qs.set(depId, params[depId]);
                    }
                });
            }

            const res = await fetch(`/reportes/filtros/${modulo}?${qs.toString()}`);
            const data = await res.json();

            if (data.patrocinadores) {
                el.innerHTML = '<option value="">Todos los patrocinadores</option>';
                data.patrocinadores.forEach(p => {
                    el.innerHTML += `<option value="${p.id}">${p.nombre}</option>`;
                });
            } else if (data.usuarios && filterId === 'usuario_id') {
                el.innerHTML = '<option value="">Todos los usuarios</option>';
                data.usuarios.forEach(u => {
                    el.innerHTML += `<option value="${u.id}">${u.nombre}</option>`;
                });
            } else if (data.usuarios && filterId === 'asignado_a') {
                el.innerHTML = '<option value="">Cualquier usuario</option>';
                data.usuarios.forEach(u => {
                    el.innerHTML += `<option value="${u.id}">${u.nombre}</option>`;
                });
            } else if (data.encargados && filterId === 'encargado') {
                el.innerHTML = '<option value="">Todos los encargados</option>';
                data.encargados.forEach(x => {
                    el.innerHTML += `<option value="${x}">${x}</option>`;
                });
            } else if (data.acciones && filterId === 'tipo_accion') {
                el.innerHTML = '<option value="">Todas</option>';
                data.acciones.forEach(a => {
                    el.innerHTML += `<option value="${a}">${a.charAt(0).toUpperCase() + a.slice(1)}</option>`;
                });
            } else if (data.modulos && filterId === 'modulo_filter') {
                el.innerHTML = '<option value="">Todos</option>';
                data.modulos.forEach(m => {
                    el.innerHTML += `<option value="${m}">${m}</option>`;
                });
            } else if (data.tipos && filterId === 'tipo') {
                el.innerHTML = '<option value="">Todos los tipos</option>';
                data.tipos.forEach(t => {
                    el.innerHTML += `<option value="${t.value}">${t.label}</option>`;
                });
            } else if (data.tipos && filterId === 'tipo_nombre') {
                el.innerHTML = '<option value="">Todos los tipos</option>';
                data.tipos.forEach(t => {
                    el.innerHTML += `<option value="${t}">${t}</option>`;
                });
            } else if (data.estados && filterId === 'estado_nombre') {
                el.innerHTML = '<option value="">Todos los estados</option>';
                data.estados.forEach(e => {
                    el.innerHTML += `<option value="${e}">${e}</option>`;
                });
            } else if (data.tipos_pago) {
                el.innerHTML = '<option value="">Todos</option>';
                data.tipos_pago.forEach(t => {
                    el.innerHTML += `<option value="${t}">${t}</option>`;
                });
            } else if (data.roles) {
                el.innerHTML = '<option value="">Todos los roles</option>';
                data.roles.forEach(r => {
                    el.innerHTML += `<option value="${r}">${r}</option>`;
                });
            } else if (data.departamentos) {
                el.innerHTML = '<option value="">Todos los departamentos</option>';
                data.departamentos.forEach(d => {
                    el.innerHTML += `<option value="${d}">${d}</option>`;
                });
            } else if (data.recursos) {
                el.innerHTML = '<option value="">Todos los recursos</option>';
                data.recursos.forEach(r => {
                    el.innerHTML += `<option value="${r.id || r.value}">${r.nombre || r.label}</option>`;
                });
            }

            // pistas de rangos numéricos: cualquier par <campo>_min/<campo>_max del backend
            Object.keys(data).forEach(k => {
                const m = k.match(/^(.+)_min$/);
                if (!m || data[`${m[1]}_max`] === undefined) return;
                const campo = m[1];
                const minEl = document.getElementById(`filtro_${campo}_min`);
                const maxEl = document.getElementById(`filtro_${campo}_max`);
                if (minEl && !minEl.value) minEl.placeholder = `Mín: ${data[k]}`;
                if (maxEl && !maxEl.value) maxEl.placeholder = `Máx: ${data[`${campo}_max`]}`;
            });
            if (data.fecha_min) {
                const fi = document.getElementById('filtro_fecha_inicio');
                const ff = document.getElementById('filtro_fecha_fin');
                if (fi && !fi.value) fi.min = data.fecha_min;
                if (ff && !ff.value) ff.max = data.fecha_max || '';
            }
        } catch (err) {
            el.innerHTML = '<option value="">Error al cargar</option>';
        }
    }

    function obtenerValoresFiltros(modulo) {
        const config = MODULE_CONFIG[modulo];
        if (!config) return {};
        const vals = {};
        config.filters.forEach(f => {
            const el = document.getElementById(`filtro_${f.id}`);
            if (el) vals[f.id] = el.value;
        });
        return vals;
    }

    function validarFiltros(modulo, config) {
        btnPreview.disabled = false;
    }

    btnPreview.addEventListener('click', async function () {
        if (!moduloActual) return;
        const config = MODULE_CONFIG[moduloActual];
        if (!config) return;

        this.disabled = true;
        this.innerHTML = '<span class="filter-spinner"></span> Cargando...';

        const fd = new FormData();
        fd.append('modulo', moduloActual);
        fd.append('csrf_token', getCSRF());

        const vals = obtenerValoresFiltros(moduloActual);
        Object.entries(vals).forEach(([k, v]) => {
            if (v) fd.append(k, v);
        });

        try {
            const res = await fetch('/reportes/preview', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRF() },
                body: fd,
            });
            const data = await res.json();
            if (data.error) {
                Swal.fire('Error', data.error, 'error');
                return;
            }
            datosPreview = data;
            mostrarPreview(data, config);
        } catch (err) {
            Swal.fire('Error', 'Error de conexión', 'error');
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-eye me-1"></i>Vista Previa';
        }
    });

    function mostrarPreview(data, config) {
        kpiModuloNombre.textContent = data.modulo;
        kpiTotalRegistros.textContent = `${data.total} registros`;

        if (data.kpis) {
            const cards = (config.kpiCards || []).filter(c => data.kpis[c.key] !== undefined && !(data.kpis[c.key] && typeof data.kpis[c.key] === 'object'));
            kpiGrid.innerHTML = cards.map(c => {
                let val = data.kpis[c.key];
                if (val === undefined || val === null) val = '—';
                if (typeof val === 'string' && val.startsWith('$')) {
                    const n = parseFloat(val.replace(/[$,]/g, ''));
                    if (!isNaN(n)) val = '$' + n.toLocaleString('es-VE', { minimumFractionDigits: 0 });
                }
                return `<div class="kpi-card-sm">
                    <div class="kpi-value" style="color:${c.color}">${val}</div>
                    <div class="kpi-label">${c.label}</div>
                </div>`;
            }).join('');
        } else {
            kpiGrid.innerHTML = '';
        }

        previewHead.innerHTML = '';
        previewBody.innerHTML = '';

        if (data.datos && data.datos.length > 0) {
            let columns;
            if (data.columnas) {
                columns = data.columnas;
            } else if (config.columns) {
                columns = config.columns;
            } else {
                columns = Object.keys(data.datos[0]).map(k => ({key: k, label: k}));
            }

            previewHead.innerHTML = columns.map(c => `<th class="text-nowrap small">${c.label}</th>`).join('');

            previewBody.innerHTML = data.datos.map(row =>
                '<tr>' + columns.map(c => {
                    let val = row[c.key];
                    if (val === null || val === undefined || val === '') val = '—';
                    if (MONEY_KEYS.includes(c.key) && typeof val === 'number') val = moneyStr(val);
                    return `<td class="small">${val}</td>`;
                }).join('') + '</tr>'
            ).join('');
            previewNote.textContent = data.total > 100 ? `Mostrando primeros 100 de ${data.total} registros` : '';

            const verMasBtn = document.createElement('button');
            verMasBtn.type = 'button';
            verMasBtn.className = 'btn btn-sm btn-outline-primary mt-1';
            verMasBtn.innerHTML = '<i class="fas fa-expand me-1"></i>Ver todos en PDF';
            verMasBtn.onclick = () => document.getElementById('btnDescargarPDF').click();
            const note = document.getElementById('previewNote');
            if (data.total > 100) {
                note.innerHTML = `Mostrando primeros 100 de ${data.total} registros. `;
                note.appendChild(verMasBtn);
            }
        } else {
            previewHead.innerHTML = '<th>Sin datos</th>';
            previewBody.innerHTML = '<tr><td class="text-center text-muted py-3">No se encontraron registros</td></tr>';
            previewNote.textContent = '';
        }

        kpiPreviewCard.style.display = 'block';
        kpiPreviewCard.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    btnDescargarPDF.addEventListener('click', async function () {
        if (!moduloActual || !datosPreview) return;

        this.disabled = true;
        this.innerHTML = '<span class="filter-spinner"></span> Generando...';

        const fd = new FormData();
        fd.append('modulo', moduloActual);
        fd.append('csrf_token', getCSRF());

        const vals = obtenerValoresFiltros(moduloActual);
        Object.entries(vals).forEach(([k, v]) => {
            if (v) fd.append(k, v);
        });

        // opciones de análisis del PDF
        const opResumen = document.getElementById('opcion_resumen');
        const opComparar = document.getElementById('opcion_comparar');
        const opTopN = document.getElementById('opcion_top_n');
        if (opResumen && opResumen.checked) fd.append('resumen', '1');
        if (opComparar && opComparar.checked) fd.append('comparar', '1');
        if (opTopN && parseInt(opTopN.value, 10) > 0) fd.append('top_n', opTopN.value);

        try {
            const res = await fetch('/reportes/generar', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRF() },
                body: fd,
            });
            const data = await res.json();
            if (data.error) {
                Swal.fire('Error', data.error, 'error');
                return;
            }
            Swal.fire({
                icon: 'success', title: 'Reporte generado', text: data.mensaje,
                timer: 1500, showConfirmButton: false,
            });
            if (data.descargar) window.open(data.descargar, '_blank');
            setTimeout(() => location.reload(), 1800);
        } catch (err) {
            Swal.fire('Error', 'Error de conexión', 'error');
        } finally {
            this.disabled = false;
            this.innerHTML = '<i class="fas fa-file-pdf me-1"></i>Descargar PDF';
        }
    });

    btnCerrarPanel.addEventListener('click', function () {
        filterPanel.classList.remove('open');
        moduloGrid.querySelectorAll('.modulo-card').forEach(c => c.classList.remove('active'));
        moduloActual = null;
    });

    btnLimpiarFiltros.addEventListener('click', function () {
        if (!moduloActual) return;
        const config = MODULE_CONFIG[moduloActual];
        if (!config) return;
        config.filters.forEach(f => {
            const el = document.getElementById(`filtro_${f.id}`);
            if (el) el.value = '';
        });
        config.filters.filter(f => f.loadVia === 'ajax').forEach(f => {
            cargarOpcionesAjax(moduloActual, f.id, config, {});
        });
        if (kpiPreviewCard) kpiPreviewCard.style.display = 'none';
    });

    btnCerrarPreview.addEventListener('click', function () {
        kpiPreviewCard.style.display = 'none';
    });

    document.addEventListener('click', function (e) {
        const btn = e.target.closest('.btn-eliminar-reporte');
        if (btn) {
            const id = btn.dataset.id;
            Swal.fire({
                title: '¿Eliminar reporte?',
                text: 'Esta acción no se puede deshacer.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonColor: '#dc3545',
                confirmButtonText: 'Eliminar',
                cancelButtonText: 'Cancelar',
            }).then(result => {
                if (result.isConfirmed) {
                    const params = new URLSearchParams();
                    params.append('csrf_token', getCSRF());
                    fetch(`/reportes/eliminar/${id}`, {
                        method: 'POST',
                        headers: { 'X-CSRFToken': getCSRF() },
                        body: params,
                    })
                    .then(r => r.json())
                    .then(data => {
                        if (data.error) { Swal.fire('Error', data.error, 'error'); return; }
                        Swal.fire({ icon: 'success', title: 'Eliminado', text: data.mensaje, timer: 1500, showConfirmButton: false });
                        setTimeout(() => location.reload(), 1800);
                    });
                }
            });
        }
    });
});