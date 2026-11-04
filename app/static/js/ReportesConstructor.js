// CONSTRUCTOR VISUAL DE REPORTES — asistente progresivo por pasos.
// Arquitectura: docs/ARQUITECTURA_CONSTRUCTOR_REPORTES.md · Catálogo: reportes_catalogo.py
// Convive con GestionReportes.js (flujo clásico intacto). Sin dependencias externas:
// barras = CSS, torta = conic-gradient, línea = SVG inline.
/* eslint-disable */

const PALETA = ['#2563eb', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6',
    '#06b6d4', '#ec4899', '#64748b'];

const VIZ_META = {
    tabla:    { label: 'Tabla',  icono: 'fa-table' },
    barras_h: { label: 'Barras', icono: 'fa-chart-simple' },
    torta:    { label: 'Torta',  icono: 'fa-chart-pie' },
    linea:    { label: 'Línea',  icono: 'fa-chart-line' },
};

const GRANOS = [
    ['dia', 'Día'], ['semana', 'Semana'], ['mes', 'Mes'], ['ano', 'Año'],
];

const PASOS = [
    { id: 'categoria',  label: 'Análisis' },
    { id: 'dimension',  label: 'Dimensión' },
    { id: 'filtros',    label: 'Filtros' },
    { id: 'metricas',   label: 'Métricas' },
    { id: 'visual',     label: 'Visualización' },
];

const ESTADO = {
    activo: false, modulo: null, nombreModulo: '', catalogo: null,
    paso: 0, categoria: null, dimension: null, grano: 'mes',
    filtros: {}, metricas: [], visualizacion: 'tabla', comparacion: 'ninguna',
};

const $ = (id) => document.getElementById(id);
const getCSRF = () => document.querySelector('input[name="csrf_token"]')?.value || '';
const fmtValor = (v, tipo) => {
    if (v === null || v === undefined || v === '') return '—';
    if (tipo === 'moneda') return '$' + Number(v).toLocaleString('es-VE');
    if (tipo === 'decimal_1') return Number(v).toLocaleString('es-VE',
        { maximumFractionDigits: 1 });
    if (tipo === 'entero') return Number(v).toLocaleString('es-VE');
    if (tipo === 'pct') return Number(v).toLocaleString('es-VE') + '%';
    return String(v);
};
const esc = (s) => String(s ?? '').replace(/[&<>"']/g,
    c => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]));

// ── entrada ────────────────────────────────────────────────────────────
document.addEventListener('DOMContentLoaded', () => {
    $('btnConstructor')?.addEventListener('click', function () {
        this.classList.toggle('active');
        const activo = this.classList.contains('active');
        this.innerHTML = activo
            ? '<i class="fas fa-xmark me-1"></i>Salir del constructor'
            : '<i class="fas fa-wand-magic-sparkles me-1"></i>Constructor avanzado';
        if (!activo) cerrarWizard();
    });

    $('moduloGrid')?.addEventListener('click', (e) => {
        if (!$('btnConstructor')?.classList.contains('active')) return;
        e.stopImmediatePropagation();          // intercepta antes del flujo clásico
        const card = e.target.closest('.modulo-card');
        if (!card) return;
        iniciar(card.dataset.modulo, card.dataset.nombre);
    }, true);

    $('btnWizCerrar')?.addEventListener('click', cerrarWizard);
    $('btnWizAtras')?.addEventListener('click', () => irAPaso(Math.max(ESTADO.paso - 1, 0)));
    $('btnWizNext')?.addEventListener('click', siguientePaso);
});

async function iniciar(modulo, nombre) {
    try {
        const res = await fetch(`/reportes/catalogo/${modulo}`);
        if (!res.ok) throw new Error();
        ESTADO.catalogo = await res.json();
    } catch (err) {
        Swal.fire('Aviso', 'Este módulo aún no tiene análisis del constructor', 'info');
        return;
    }
    Object.assign(ESTADO, {
        activo: true, modulo, nombreModulo: nombre, catalogo: ESTADO.catalogo,
        paso: 0, categoria: null, dimension: null, grano: 'mes',
        filtros: {}, metricas: [], visualizacion: 'tabla', comparacion: 'ninguna',
    });
    $('wizModuloNombre').textContent = nombre;
    $('wizardCard').classList.remove('d-none');
    $('filterPanel').classList.add('d-none');
    $('kpiPreviewCard').classList.add('d-none');
    renderPaso();
}

function cerrarWizard() {
    ESTADO.activo = false;
    $('wizardCard')?.classList.add('d-none');
    $('filterPanel')?.classList.remove('d-none');
}

// ── máquina de pasos ───────────────────────────────────────────────────
function irAPaso(n) {
    ESTADO.paso = n;
    renderPaso();
}

function siguientePaso() {
    const paso = PASOS[ESTADO.paso].id;
    if (paso === 'categoria' && !validarCategoria()) return;
    if (paso === 'dimension' && !ESTADO.dimension) return;
    if (paso === 'filtros') recolectarFiltros();
    if (paso === 'metricas') {
        ESTADO.metricas = [...$('wizBody').querySelectorAll('input[type=checkbox]:checked')]
            .map(i => i.value);
        if (!ESTADO.metricas.length) {
            Swal.fire('Aviso', 'Selecciona al menos una métrica', 'warning');
            return;
        }
    }
    if (ESTADO.paso === PASOS.length - 1) { ejecutar(); return; }
    irAPaso(ESTADO.paso + 1);
}

function pintarPasos() {
    $('wizSteps').innerHTML = PASOS.map((p, i) => {
        const clase = i < ESTADO.paso ? 'done'
            : i === ESTADO.paso ? 'active' : '';
        const num = i < ESTADO.paso ? '<i class="fas fa-check"></i>' : (i + 1);
        return `<span class="wiz-chip ${clase}"><span class="wiz-num">${num}</span>${p.label}</span>`;
    }).join('');
    $('btnWizAtras').disabled = ESTADO.paso === 0;
    const ultimo = ESTADO.paso === PASOS.length - 1;
    $('btnWizNext').innerHTML = ultimo
        ? '<i class="fas fa-play me-1"></i>Generar reporte'
        : 'Siguiente<i class="fas fa-arrow-right ms-1">';
    $('btnWizNext').disabled = false;
}

function renderPaso() {
    pintarPasos();
    const paso = PASOS[ESTADO.paso].id;
    ({ categoria: pCategoria, dimension: pDimension, filtros: pFiltros,
        metricas: pMetricas, visual: pVisual }[paso])();
}

function pregunta(texto) {
    return `<div class="wiz-pregunta">${texto}</div>`;
}

// ── paso 1: categoría ──────────────────────────────────────────────────
function validarCategoria() {
    if (!ESTADO.categoria) {
        Swal.fire('Aviso', 'Elige qué quieres analizar', 'warning');
        return false;
    }
    return true;
}

function pCategoria() {
    const cats = Object.entries(ESTADO.catalogo.categorias);
    $('wizBody').innerHTML = pregunta('¿Qué quieres analizar?')
        + `<div class="wiz-opciones">${cats.map(([id, c]) => `
            <div class="wiz-card ${ESTADO.categoria === id ? 'sel' : ''}" data-cat="${id}"
                 role="button" tabindex="0">
                <div class="wiz-icono"><i class="fas ${c.icono || 'fa-layer-group'}"></i></div>
                <div class="wiz-titulo">${esc(c.nombre)}</div>
                <div class="wiz-detalle">${id === 'resumen'
                    ? 'reporte clásico' : esc(c.descripcion || '').slice(0, 60)}</div>
            </div>`).join('')}</div>`;

    $('wizBody').querySelectorAll('[data-cat]').forEach(card => {
        card.addEventListener('click', () => {
            ESTADO.categoria = card.dataset.cat;
            ESTADO.dimension = null;
            ESTADO.metricas = [];
            if (ESTADO.categoria === 'resumen') {
                // delega al flujo clásico, intacto
                cerrarWizard();
                document.querySelector(`.modulo-card[data-modulo="${ESTADO.modulo}"]`)?.click();
                return;
            }
            ESTADO.visualizacion = 'tabla';
            ESTADO.comparacion = 'ninguna';
            irAPaso(1);
        });
    });
}

// ── paso 2: dimensión (+ granularidad si es temporal) ──────────────────
function pDimension() {
    const cat = ESTADO.catalogo.categorias[ESTADO.categoria];
    const dims = cat.dimensiones.map(id =>
        ({ id, ...ESTADO.catalogo.dimensiones[id] }));
    $('wizBody').innerHTML = pregunta('¿Por qué agrupar los datos?')
        + `<div class="wiz-opciones">${dims.map(d => `
            <div class="wiz-card ${ESTADO.dimension === d.id ? 'sel' : ''}"
                 data-dim="${d.id}" role="button" tabindex="0">
                <div class="wiz-icono"><i class="fas fa-${d.tipo === 'temporal'
                    ? 'calendar' : 'fa-shapes'}"></i></div>
                <div class="wiz-titulo">${esc(d.label)}</div>
            </div>`).join('')}</div>
        <div class="wiz-fila-grano d-none" id="granoBox">
            <label class="form-label fw-bold small mb-1">Agrupar el tiempo por</label>
            <div class="wiz-segmentos" id="granoSeg">
                ${GRANOS.map(([k, l]) =>
                    `<button type="button" data-grano="${k}"
                        class="${ESTADO.grano === k ? 'on' : ''}">${l}</button>`).join('')}
            </div>
        </div>`;

    $('wizBody').querySelectorAll('[data-dim]').forEach(card => {
        card.addEventListener('click', () => {
            ESTADO.dimension = card.dataset.dim;
            const dimInfo = ESTADO.catalogo.dimensiones[ESTADO.dimension];
            $('wizBody').querySelectorAll('[data-dim]')
                .forEach(c => c.classList.toggle('sel', c === card));
            $('granoBox').classList.toggle('d-none', dimInfo.tipo !== 'temporal');
        });
    });
    $('wizBody').querySelectorAll('#granoSeg button').forEach(b => {
        b.addEventListener('click', () => {
            ESTADO.grano = b.dataset.grano;
            $('wizBody').querySelectorAll('#granoSeg button')
                .forEach(x => x.classList.toggle('on', x === b));
        });
    });
}

// ── paso 3: filtros ────────────────────────────────────────────────────
function pFiltros() {
    const cat = ESTADO.catalogo.categorias[ESTADO.categoria];
    const filtros = cat.filtros.map(id => ESTADO.catalogo.filtros[id]).filter(Boolean);
    let html = pregunta('¿Quieres acotar el análisis? <span class="text-muted fw-normal">(opcional)</span>')
        + '<div class="row g-3">';
    filtros.forEach(f => {
        if (f.coercion === 'rango_fecha') {
            html += `
                <div class="col-12 col-md-6">
                    <label class="form-label fw-bold small mb-1">${esc(f.label)}</label>
                    <div class="d-flex gap-2">
                        <input type="date" class="form-control form-control-sm"
                               data-filtro="${f.id}_ini" title="Desde">
                        <input type="date" class="form-control form-control-sm"
                               data-filtro="${f.id}_fin" title="Hasta">
                    </div>
                </div>`;
            return;
        }
        if (f.opciones || f.ajax) {
            html += `
                <div class="col-12 col-md-6">
                    <label class="form-label fw-bold small mb-1">${esc(f.label)}</label>
                    <select class="form-select form-select-sm" data-filtro="${f.id}"
                            data-ajax='${esc(JSON.stringify(f.ajax || null))}'>
                        <option value="">Todos</option>
                        ${(f.opciones || []).map(o =>
                            `<option value="${esc(o.value)}">${esc(o.label)}</option>`).join('')}
                    </select>
                </div>`;
            return;
        }
        const numerico = f.coercion.includes('float') || f.coercion === 'entero';
        html += `
            <div class="col-12 col-md-6">
                <label class="form-label fw-bold small mb-1">${esc(f.label)}</label>
                <input type="${numerico ? 'number' : 'text'}"
                       class="form-control form-control-sm" data-filtro="${f.id}">
            </div>`;
    });
    html += '</div>';
    $('wizBody').innerHTML = html;

    $('wizBody').querySelectorAll('select[data-filtro]').forEach(sel => {
        const ajax = sel.dataset.ajax && sel.dataset.ajax !== 'null'
            ? JSON.parse(sel.dataset.ajax) : null;
        if (ajax) cargarOpciones(sel, ajax);
        sel.addEventListener('change', () => {
            $('wizBody').querySelectorAll('select[data-filtro]').forEach(otro => {
                const oAjax = otro.dataset.ajax && otro.dataset.ajax !== 'null'
                    ? JSON.parse(otro.dataset.ajax) : null;
                if (!oAjax || oAjax.depende_de !== sel.dataset.filtro) return;
                oAjax._valorDep = sel.value;
                cargarOpciones(otro, oAjax);
            });
        });
    });
}

async function cargarOpciones(selectEl, ajax) {
    try {
        const qs = new URLSearchParams();
        if (ajax.param && ajax._valorDep) qs.set(ajax.param, ajax._valorDep);
        const res = await fetch(`${ajax.url}?${qs.toString()}`);
        const data = await res.json();
        selectEl.innerHTML = '<option value="">Todos</option>' + (data[ajax.clave] || [])
            .map(x => {
                const valor = typeof x === 'object' ? (x.id ?? x.value) : x;
                const label = typeof x === 'object' ? (x.nombre ?? x.label ?? valor) : x;
                return `<option value="${esc(valor)}">${esc(label)}</option>`;
            }).join('');
    } catch (err) {
        selectEl.innerHTML = '<option value="">Error al cargar</option>';
    }
}

function recolectarFiltros() {
    ESTADO.filtros = {};
    $('wizBody').querySelectorAll('[data-filtro]').forEach(inp => {
        if (inp.value) ESTADO.filtros[inp.dataset.filtro] = inp.value;
    });
}

// ── paso 4: métricas ───────────────────────────────────────────────────
function pMetricas() {
    const cat = ESTADO.catalogo.categorias[ESTADO.categoria];
    const defaults = cat.metricas_default || cat.metricas.slice(0, 1);
    $('wizBody').innerHTML = pregunta('¿Qué quieres medir?')
        + '<div class="row g-2">'
        + cat.metricas.map(id => {
            const m = ESTADO.catalogo.metricas[id];
            return `<div class="col-12 col-md-6">
                <div class="form-check wiz-metrica-check ps-4 m-0 py-2 px-3"
                     style="border:1px solid #eef2f7;border-radius:10px;">
                    <input class="form-check-input mt-1" type="checkbox" value="${id}"
                           id="met_${id}" ${defaults.includes(id) ? 'checked' : ''}>
                    <label class="form-check-label small fw-semibold" for="met_${id}">
                        ${esc(m.label)}
                        <span class="d-block text-muted" style="font-size:.68rem;">
                            ${m.formato}</span>
                    </label>
                </div></div>`;
        }).join('') + '</div>';
}

// ── paso 5: visualización + comparación ───────────────────────────────
function pVisual() {
    const cat = ESTADO.catalogo.categorias[ESTADO.categoria];
    const dimTemporal = ESTADO.catalogo.dimensiones[ESTADO.dimension]?.tipo === 'temporal';
    const validas = (cat.visualizaciones_validas || [])
        .filter(v => VIZ_META[v])
        .filter(v => v !== 'linea' || dimTemporal)     // línea SOLO con dimensión temporal
        .filter(v => v !== 'torta' || true);
    const comps = (cat.comparaciones_validas || []).filter(
        c => c === 'ninguna' || c === 'periodo_anterior');

    $('wizBody').innerHTML = pregunta('¿Cómo lo quieres ver?')
        + `<div class="wiz-opciones mb-3">${validas.map(v => `
            <div class="wiz-card ${ESTADO.visualizacion === v ? 'sel' : ''}"
                 data-viz="${v}" role="button" tabindex="0">
                <div class="wiz-icono"><i class="fas ${VIZ_META[v].icono}"></i></div>
                <div class="wiz-titulo">${VIZ_META[v].label}</div>
            </div>`).join('')}</div>`
        + (comps.length > 1
            ? `<label class="form-label fw-bold small mb-1">Comparación</label>
               <div class="wiz-segmentos">
                   ${comps.map(c => `<button type="button" data-comp="${c}"
                        class="${ESTADO.comparacion === c ? 'on' : ''}">${
                        c === 'ninguna' ? 'Sin comparación' : 'vs período anterior'
                    }</button>`).join('')}
               </div>` : '');

    $('wizBody').querySelectorAll('[data-viz]').forEach(card => {
        card.addEventListener('click', () => {
            ESTADO.visualizacion = card.dataset.viz;
            $('wizBody').querySelectorAll('[data-viz]')
                .forEach(c => c.classList.toggle('sel', c === card));
        });
    });
    $('wizBody').querySelectorAll('[data-comp]').forEach(b => {
        b.addEventListener('click', () => {
            ESTADO.comparacion = b.dataset.comp;
            $('wizBody').querySelectorAll('[data-comp]')
                .forEach(x => x.classList.toggle('on', x === b));
        });
    });
}

// ── ejecución y resultado ──────────────────────────────────────────────
async function ejecutar() {
    const btn = $('btnWizNext');
    btn.disabled = true;
    btn.innerHTML = '<span class="filter-spinner"></span>Generando…';
    try {
        const res = await fetch('/reportes/construir', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF() },
            body: JSON.stringify({
                modulo: ESTADO.modulo, categoria: ESTADO.categoria,
                dimension: ESTADO.dimension, tiempo_grano: ESTADO.grano,
                metricas: ESTADO.metricas, filtros: ESTADO.filtros,
                comparacion: ESTADO.comparacion,
            }),
        });
        const data = await res.json();
        if (data.error) { Swal.fire('Error', data.error, 'error'); return; }
        renderResultado(data);
    } catch (err) {
        Swal.fire('Error', 'Error de conexión', 'error');
    } finally {
        btn.disabled = false;
        pintarPasos();
    }
}

function renderResultado(data) {
    pintarResultadoPasos();
    $('btnWizNext').classList.add('d-none');
    $('btnWizAtras').classList.remove('d-none');

    const cols = data.columnas;
    const primeraMetrica = cols[1];
    const ordenadas = [...data.filas];

    // KPIs de totales
    const kpis = cols.slice(1).map(c => `
        <div class="kpi-card-sm">
            <div class="kpi-value">${fmtValor(data.totales[c.key], c.tipo)}</div>
            <div class="kpi-label">${esc(c.label)}</div>
        </div>`).join('');

    const cuerpo = {
        tabla: vizTabla(data),
        barras_h: vizBarras(data, ordenadas),
        torta: vizTorta(data),
        linea: vizLinea(data),
    }[ESTADO.visualizacion] || '';

    $('wizBody').innerHTML = `
        ${data.meta.limit_alcanzado
            ? '<div class="alert alert-warning py-2 small">Resultado truncado por límite; acota los filtros.</div>' : ''}
        <div class="wiz-kpis">${kpis}</div>
        <h6 class="fw-bold small text-muted text-uppercase mb-2">
            ${esc(data.dimension.label)} · ${VIZ_META[ESTADO.visualizacion].label}</h6>
        ${cuerpo}
        ${compBloque(data.comparacion, cols)}
        <div class="d-flex gap-2 flex-wrap justify-content-end mt-3">
            <button class="btn btn-outline-secondary btn-sm" id="btnWizAjustar">
                <i class="fas fa-sliders me-1"></i>Ajustar</button>
            <button class="btn btn-outline-secondary btn-sm" id="btnWizCsv">
                <i class="fas fa-file-csv me-1"></i>CSV</button>
            <button class="btn btn-danger btn-sm" id="btnWizPdf">
                <i class="fas fa-file-pdf me-1"></i>PDF</button>
            <button class="btn btn-primary btn-sm" id="btnWizNuevo">
                <i class="fas fa-plus me-1"></i>Nuevo análisis</button>
        </div>`;

    $('btnWizAjustar').onclick = () => irAPaso(PASOS.length - 1);
    $('btnWizNuevo').onclick = () => irAPaso(0);
    $('btnWizCsv').onclick = () => exportar('csv');
    $('btnWizPdf').onclick = () => exportar('pdf');
}

function pintarResultadoPasos() {
    $('wizSteps').innerHTML = PASOS.map(p =>
        `<span class="wiz-chip done"><span class="wiz-num"><i class="fas fa-check"></i></span>${p.label}</span>`)
        .join('');
}

function compBloque(comp, cols) {
    if (!comp) return '';
    const detalles = Object.entries(comp.variaciones || {})
        .map(([k, v]) => `${esc(cols.find(c => c.key === k)?.label || k)}: <strong>${esc(v)}</strong>`)
        .join(' · ');
    return `<div class="small text-muted mt-2">
        <i class="fas fa-clock-rotate-left me-1"></i>Vs ${esc(comp.rango_previo[0])} →
        ${esc(comp.rango_previo[1])}: ${detalles}</div>`;
}

function vizTabla(data) {
    const filas = data.filas.slice(0, 100).map(f => '<tr>'
        + data.columnas.map(c =>
            `<td class="small${c.key === 'dimension' ? ' fw-semibold' : ''}">${
                esc(fmtValor(f[c.key], c.tipo))}</td>`).join('') + '</tr>').join('');
    const totales = '<tr class="table-light fw-bold">' + data.columnas.map((c, i) =>
        `<td>${i === 0 ? 'Total' : esc(fmtValor(data.totales[c.key], c.tipo))}</td>`).join('')
        + '</tr>';
    return `<div class="table-responsive" style="max-height:340px;">
        <table class="table table-sm table-hover table-striped align-middle mb-0">
            <thead class="table-light sticky-top">
                <tr>${data.columnas.map(c =>
                    `<th class="small text-nowrap">${esc(c.label)}</th>`).join('')}</tr>
            </thead><tbody>${filas}${totales}</tbody>
        </table></div>`;
}

function vizBarras(data) {
    const metrica = data.columnas[1];
    const top = data.filas.slice(0, 12);
    const maxVal = Math.max(...top.map(f => f[metrica.key] || 0), 1);
    return top.map((fila, i) => {
        const val = fila[metrica.key] || 0;
        const pct = Math.round((val / maxVal) * 100);
        return `<div class="mb-2">
            <div class="d-flex justify-content-between small fw-semibold">
                <span class="text-truncate me-2">${esc(fila.dimension)}</span>
                <span>${fmtValor(val, metrica.tipo)}</span></div>
            <div style="height:9px;border-radius:5px;background:#eef2f7;">
                <div style="height:100%;width:${pct}%;border-radius:5px;
                     background:${PALETA[i % PALETA.length]};"></div>
            </div></div>`;
    }).join('') || '<p class="text-muted small">Sin datos</p>';
}

function vizTorta(data) {
    const metrica = data.columnas[1];
    const top = data.filas.slice(0, 8);
    const total = top.reduce((s, f) => s + (f[metrica.key] || 0), 0);
    if (!total) return '<p class="text-muted small">Sin datos</p>';
    let acumulado = 0;
    const stops = [];
    const leyenda = top.map((fila, i) => {
        const val = fila[metrica.key] || 0;
        const desde = (acumulado / total) * 100;
        acumulado += val;
        const hasta = (acumulado / total) * 100;
        stops.push(`${PALETA[i % PALETA.length]} ${desde}% ${hasta}%`);
        return `<div class="d-flex align-items-center gap-2 small mb-1">
            <span style="width:10px;height:10px;border-radius:3px;
                background:${PALETA[i % PALETA.length]};display:inline-block;"></span>
            <span class="flex-grow-1 text-truncate">${esc(fila.dimension)}</span>
            <span class="fw-semibold">${fmtValor(val, metrica.tipo)}</span>
            <span class="text-muted">${Math.round(hasta - desde)}%</span></div>`;
    }).join('');
    return `<div class="d-flex flex-column flex-sm-row align-items-center gap-4">
        <div style="width:170px;height:170px;border-radius:50%;
             background:conic-gradient(${stops.join(',')});position:relative;">
            <div style="position:absolute;inset:34px;background:#fff;border-radius:50%;"></div>
        </div>
        <div class="flex-grow-1 w-100">${leyenda}</div></div>`;
}

function vizLinea(data) {
    const metrica = data.columnas[1];
    const puntos = [...data.filas]
        .sort((a, b) => String(a.dimension).localeCompare(String(b.dimension)));
    if (puntos.length < 2) return '<p class="text-muted small">Se necesitan al menos 2 períodos para la línea.</p>';
    const vals = puntos.map(p => p[metrica.key] || 0);
    const maxV = Math.max(...vals), minV = Math.min(...vals);
    const rango = (maxV - minV) || 1;
    const W = 560, H = 160, PAD = 24;
    const px = i => PAD + (i * (W - 2 * PAD)) / (puntos.length - 1);
    const py = v => H - PAD - ((v - minV) / rango) * (H - 2 * PAD);
    const coords = vals.map((v, i) => `${px(i)},${py(v)}`).join(' ');
    const etiquetas = puntos.map((p, i) => (i % Math.ceil(puntos.length / 8) === 0
        ? `<text x="${px(i)}" y="${H - 6}" font-size="8" fill="#94a3b8"
             text-anchor="middle">${esc(p.dimension)}</text>` : '')).join('');
    const dots = vals.map((v, i) =>
        `<circle cx="${px(i)}" cy="${py(v)}" r="3" fill="#2563eb"/>`).join('');
    return `<svg viewBox="0 0 ${W} ${H}" style="width:100%;height:auto;">
        <polyline points="${coords}" fill="none" stroke="#2563eb"
             stroke-width="2.5" stroke-linejoin="round"/>
        ${dots}${etiquetas}</svg>
        <div class="small text-muted">Último punto: ${
            esc(puntos[puntos.length - 1].dimension)} = ${
            fmtValor(vals[vals.length - 1], metrica.tipo)}</div>`;
}

async function exportar(formato) {
    try {
        const res = await fetch('/reportes/construir/exportar', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCSRF() },
            body: JSON.stringify({
                modulo: ESTADO.modulo, categoria: ESTADO.categoria,
                dimension: ESTADO.dimension, tiempo_grano: ESTADO.grano,
                metricas: ESTADO.metricas, filtros: ESTADO.filtros,
                comparacion: ESTADO.comparacion, formato,
            }),
        });
        const tipo = res.headers.get('content-type') || '';
        if (tipo.includes('json')) {
            const out = await res.json();
            if (out.error) { Swal.fire('Error', out.error, 'error'); return; }
            window.open(out.descargar, '_blank');
            return;
        }
        const blob = await res.blob();
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `constructor_${ESTADO.modulo}.${formato}`;
        a.click();
        URL.revokeObjectURL(url);
    } catch (err) {
        Swal.fire('Error', 'No se pudo exportar', 'error');
    }
}
