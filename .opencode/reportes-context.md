# Contexto: Sistema de Reportes (Itinerario)

## Arquitectura general

El sistema de reportes es un dashboard progresivo tipo "Profit Plus":
- Seleccionas un módulo → aparecen filtros contextuales (algunos vía AJAX)
- Seleccionas filtros → preview en tabla + KPIs + distribución
- Botón "Generar PDF" produce un PDF con KPIs + distribuciones + tabla de datos

### Archivos clave

| Archivo | Rol |
|---------|-----|
| `app/controller/reportes_controller.py` | Rutas Flask (`/reportes/*`), funciones de filtros (`_filtros_*`), obtención de datos (`_obtener_datos`), configuración de módulos |
| `app/static/js/GestionReportes.js` | Frontend: `MODULE_CONFIG` por módulo, `cargarOpcionesAjax`, render de filtros/tabla/KPIs |
| `app/view/reportes/dashboard.html` | Template: card grid + panel de filtros dinámico + tabla preview |
| `app/helpers/generators/base_report.py` | Clase base: `_seccion_kpis()`, `_seccion_distribucion()`, `_header()`, `_tabla()`, `_build_rows()` |
| `app/helpers/generators/*_report.py` | 12 generadores PDF (uno por módulo + resumen) |

## Estados de implementación

### ✅ Completos (patrón "efecto bitácora" aplicado a TODOS los módulos)

- **contratos**: tipo→patrocinador progresivo, estatus, monto min/max, fechas
- **bitácora**: usuario/acción/módulo AJAX con triple progresividad, fechas
- **inventario**: tipo→estado AJAX progresivo, costo min/max, fechas
- **guiones**: estado + encargado AJAX (desde `elementos_guion.encargado`) + `elementos_min/max` + fechas
- **premios**: estado→patrocinador progresivo + `cantidad_min/max` y `cantidad_entregada_min/max` + fechas
- **tareas**: claves unificadas lowercase (`nombre_tarea`, `estado`) + estado→usuario_asignado progresivo (filtro por `id_usuario`, nombre resuelto en SQL) + fechas
- **patrocinadores**: tipo_contrato + `estado_pat` (activo/inactivo; antes `estado_filter`) + fechas
- **usuarios**: departamento→rol progresivo + `activo` sí/no + fechas
- **mantenimiento**: estado→recurso progresivo + rango `dias_en_taller` (`dias_min/max`, calculado de fecha_ingreso→fecha_salida o hoy) + KPI `promedio_dias` + fechas
- **reels**: patrocinador AHORA FUNCIONAL (`ReelModel.consultar` trae `id_patrocinador AS patrocinado`) + `duracion_min/max` en segundos + fechas

### Bugs corregidos durante Fase 4 (eran silenciosos)
- `_filtros_balance` consultaba tabla inexistente `pagos_contratos` → ahora `pagos` (el select tipo_pago cargaba siempre vacío)
- `_datos_premios`: `fetchall()` (tupla) + lista no se concatenaban → TypeError 500 en preview de premios
- `_datos_tareas`: `usuario_nombre` nunca existía en el SELECT → asignado_a salía siempre '—'
- Filtro de reels por patrocinador era no-op (el modelo no devolvía el id)

### Análisis opcional del PDF (todos los módulos)
Opciones enviadas desde el panel de filtros (`Análisis del PDF`) a `/reportes/generar`,
parseadas con whitelist server-side en `generar()`:

| Opción form | Efecto |
|---|---|
| `resumen=1` | Párrafo factual generado SOLO desde los KPIs (`BaseReportGenerator._resumen_ejecutivo`) |
| `top_n=N` (1-20) | Tabla Top N reutilizando la primera distribución dict de los kpis (`_top_destacados`) |
| `comparar=1` | Misma consulta con ventana desplazada hacia atrás → tabla Actual/Anterior/Variación (`_comparativa_periodos`; "sin datos comparables" si no hay) |

Los generadores que sobreescriben `generate()` aceptan `opciones=None` e insertan
`story.extend(self._secciones_analisis(kpis, opciones))` tras sus KPIs.

Tests: `tests/test_reportes_filtros.py` (filtros por módulo), `tests/test_reportes_pdf.py`
(análisis PDF), `tests/test_reportes_smoke.py` (estabilidad preview).

## Patrón para implementar un módulo (receta)

### 1. Backend: `_filtros_<modulo>(params)`
- Devolver en JSON: arrays para selects + `{campo}_min`/`{campo}_max` para rangos
- Si hay progresividad: filtrar datos según `params.get('campo_dependencia')`
- Usar `try/except` con log del error real (no silencioso)

### 2. Backend: `_obtener_datos` sección del módulo
- Agregar filtros faltantes (rango numérico)
- Agregar KPIs: total + contadores + promedios/totales
- Mantener distribuciones (`tipos`, `estados`, `por_*`)

### 3. Frontend: `MODULE_CONFIG.<modulo>`
```javascript
filters: [
    { id: 'select_con_progresividad', label: '...', type: 'select', loadVia: 'ajax',
      colClass: 'col-md-3', progressive: ['select_dependiente'] },
    { id: 'select_dependiente', label: '...', type: 'select', loadVia: 'ajax',
      dependsOn: ['select_con_progresividad'], colClass: 'col-md-3' },
    { id: 'campo_min', label: '... Mín', type: 'number', placeholder: '0', colClass: 'col-md-2' },
    { id: 'campo_max', label: '... Máx', type: 'number', placeholder: '999999', colClass: 'col-md-2' },
    { id: 'fecha_inicio', ..., 'fecha_fin', ... },
],
columns: [...],
kpiCards: [
    { key: 'total', label: 'Total', color: '#2563eb' },
    { key: '...', label: '...', color: '...' },
],
```

### 4. Frontend: `cargarOpcionesAjax`
Si devuelves un nuevo campo tipo `{campo}_min`/`{campo}_max`, agregar bloque similar al de `monto_min`/`monto_max`.

### 5. PDF: `<modulo>_report.py`
Agregar `_seccion_distribucion` con los datos de distribución (tipos, estados, etc.) disponibles en `kpis`.

## Convenciones
- `progressive` en el FILTRO ORIGEN (el que al cambiar recarga al destino)
- `dependsOn` en el FILTRO DESTINO (el que se recarga cuando cambia el origen)
- <select> options: primer option siempre `value=""` con label "Todos..." (o el equivalente)
- Rangos numéricos: enviar `{campo}_min`/`{campo}_max` desde backend como hint (placeholders en frontend)
- Fechas: `fecha_inicio`/`fecha_fin` siempre presentes
- columnas preview: deben coincidir con lo que devuelve `_obtener_datos`
- kpiCards keys: deben coincidir con las claves del dict `kpis`

## Fase 5 — Constructor de Reportes (2026-08-25, EN CURSO)

Arquitectura aprobada: `docs/ARQUITECTURA_CONSTRUCTOR_REPORTES.md`. Auditoría previa: `docs/AUDITORIA_REPORTES.md`.

### ✅ F0 blindaje (hecho)
- Whitelists de filtros por módulo en preview/generar (`FILTROS_PERMITIDOS` + `_filtros_del_request`, reportes_controller.py) — claves desconocidas se descartan y ya no llegan al header del PDF.
- `_ordenar_datos` numérico (antes '100'<'20' string-wise) + tests.
- balance: fechas/tipo_pago en SQL (`obtener_historial_pagos(limit, fecha_inicio, fecha_fin, tipo_pago)`), tope 2000, match patrocinador EXACTO vía `c.id_patrocinador` (muere el startswith); `Pago.id_patrocinador` nuevo property.
- bitácora: fechas en SQL (fecha_desde/hasta), cap 5000 (antes 500 silencioso).
- FIX no-op: filtro tareas `asignado_a` nunca filtraba (backend leía `usuario_id`) — ahora ambas claves.

### ✅ F1 piloto (hecho): contratos + bitácora
- `app/helpers/reportes_catalogo.py`: MODULO_BUILDER declarativo, FUENTES_SQL (FKs reales), SOFT_DELETE, DIMENSIONES/METRICAS/FILTROS_BUILDER con SQL calificado, FUENTE_ALIASES, `catalogo_publico()` (sirve sin SQL interno).
- `app/helpers/reportes_constructor.py`: motor whitelistado → dataset genérico; buckets DATE_FORMAT; comparativa período anterior; LIMIT 500 visible vía meta.limit_alcanzado; ConstructorError→400.
- Endpoints: GET /reportes/catalogo/<modulo>, POST /reportes/construir, POST /reportes/construir/exportar (pdf/csv).
- `generators/constructor_report.py` (ConstructorReport) + wizard frontend `static/js/ReportesConstructor.js` (stepper; "Resumen general" delega al flujo clásico intacto).
- Tests: tests/test_reportes_constructor.py (11) — consistencia catálogo, anti-inyección, 400s, CSV/PDF.

### Pendiente (fases siguientes del plan)
- Extender MODULO_BUILDER al resto de módulos (balance→mantenimiento→premios→guiones→resto; antes matar N+1 mantenimiento/reels).
- Contrato `opciones` PDF completo (skill reportes-pdf) + refactor boilerplate generadores (D5).
- Plantillas guardadas (requiere decisión de migración BD) e índices de fecha.

### ✅ FASE 1 — Capa de configuración declarativa (2026-08-25, hecha)
- `reportes_catalogo.py` ampliado a 11 módulos con constructor (todos menos `resumen`, inhabilitado por bug latente): guiones(produccion/evolucion), inventario(valorizacion/asignaciones_cat), premios(entregas_stock), balance(cobranza), tareas(carga), patrocinadores(cartera_pat), usuarios(planta), mantenimiento(taller), reels(contenido).
- Nuevos registros: FUENTE_SCHEMA (conexión por fuente), FUENTE_ALIASES ampliados, SOFT_DELETE por fuente, filtros con UI declarativa (`opciones` estáticas o `ajax` {url,clave,param,depende_de} → reutilizan los endpoints legacy /filtros/*), métricas con `sin_agg` para agregaciones embebidas (% completadas) y expresiones DATEDIFF/CASE.
- Motor: conexión por FUENTE_SCHEMA; límite configurable por categoría (`cat['limite']`).
- Wizard JS: pasoFiltros pinta selects desde catálogo y recarga destinos por `depende_de` (progresividad declarativa sin tocar handlers legacy).
- Tests: test_reportes_constructor.py ahora 23 (consistencia global de alias/esquema/soft-delete/resumen-legado + un caso de ejecución por módulo). Suite total: 101 passed.

### ✅ FASE 2 — Constructor visual (2026-08-25, hecha)
- `ReportesConstructor.js` reescrito como asistente por pasos: Análisis → Dimensión (+grano temporal) → Filtros → Métricas → Visualización/Comparación → Resultado. Chips de progreso (done/active), footer Atrás/Siguiente→Generar.
- Renderizadores SIN dependencias: tabla, barras CSS, torta conic-gradient con leyenda %, línea SVG (solo se ofrece si la dimensión es temporal; orden cronológico).
- KPI cards de totales + fila Total en tabla + aviso de truncado + exportar CSV/PDF + "Ajustar"/"Nuevo análisis".
- `dashboard.html`: tarjeta #wizardCard con estilos .wiz-* propios (tokens del sistema); el grid clásico y su panel quedan intactos — "Resumen general" delega al flujo de siempre.
- Data-driven desde reportes_catalogo.py: los 11 módulos con constructor funcionan sin JS por módulo.
