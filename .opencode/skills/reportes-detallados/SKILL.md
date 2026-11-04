---
name: reportes-detallados
description: Patrón "efecto bitácora" para reportes profundos y progresivos en Itinerario — filtros apilables cargados desde BD real (una entidad específica + categoría + rango + fechas), KPIs recalculados y PDF con resumen ejecutivo, Top-N y comparativa de períodos. Use when improving any module's report filters or PDF depth in the reportes dashboard, when the user says "reportes detallados", "más filtros", "comparativa", "top", "resumen ejecutivo", or asks to make a module's report like bitácora.
---

# Reportes detallados — patrón "efecto bitácora"

Bitácora es el estándar de oro: permite apilar filtros reales (1 usuario específico + 1 acción + 1 módulo + fechas), las opciones se cargan por AJAX **desde la BD**, los KPIs se recalculan con lo filtrado y el PDF refleja exactamente esa combinación. Objetivo: que TODOS los módulos crezcan así.

## Referencias del patrón (leer antes de replicar)

- Filtros AJAX: `_filtros_bitacora` en `app/controller/reportes_controller.py` (~línea 227) — devuelve `usuarios`, `acciones`, `modulos` desde `ActividadModel.obtener_*_distintos()`
- Config frontend: `MODULE_CONFIG.bitacora` en `app/static/js/GestionReportes.js` (~línea 282)
- Datos+KPIs: sección `elif modulo == 'bitacora'` en `_obtener_datos()` (~línea 870)
- Módulos ya completos (modelos de referencia): **bitácora, contratos, inventario**

## Las 4 reglas del patrón

1. **Opciones desde datos reales.** Todo select se llena con valores distintos existentes en BD (`obtener_*_distintos` o query equivalente), nunca hardcodeado cuando hay catálogo. Estático solo si es un enum cerrado (ej. estado Borrador/Vigente/Vencido).
2. **Filtros apilables por entidad específica.** Cada módulo debe poder filtrar por UNA entidad concreta (un patrocinador, un encargado, un usuario asignado, un recurso) además de categoría + rango numérico + fechas.
3. **Progresividad:** el filtro origen lleva `progressive: [...]` y el destino `dependsOn: [...]` (convención de `GestionReportes.js`). Ejemplo bitácora: módulo → acción; contratos: tipo → patrocinador.
4. **KPIs server-side con lo filtrado.** `_obtener_datos` calcula KPIs y distribuciones DESPUÉS de aplicar todos los filtros. El PDF imprime los filtros aplicados (el header de `base_report.py` ya lo hace).

## Receta por módulo (trabajo pendiente real)

| Módulo | Entidad específica (drill-down) | Rangos / fixes |
|---|---|---|
| guiones | encargado específico (AJAX desde guiones) | `elementos_min/max` |
| premios | patrocinador (ya existe) | progresividad estado→patrocinador; `cantidad_min/max`, `cantidad_entregada_min/max` |
| balance | tipo_pago→patrocinador (ya existe) | fix preview: columna `referencia` puede ser NULL |
| tareas | usuario asignado específico (AJAX) | fix key inconsistente `Estado`→`estado`; progresividad estado→usuario |
| patrocinadores | tipo_contrato (estático ok) | filtro activo/inactivo; renombrar `estado_filter` |
| usuarios | departamento→rol progresivo | filtro activo sí/no |
| mantenimiento | estado→recurso (ya existe) | rango costo o días |
| reels | patrocinador (ya existe) | `duracion_min/max` (segundos) |

Implementar de a UN módulo end-to-end (backend → JS → PDF → probar en navegador) antes del siguiente.

## Análisis nuevo dentro del PDF

Tres secciones opcionales para `BaseReportGenerator` (coordinar con el dict `opciones` de la skill `reportes-pdf`):

1. **Resumen ejecutivo** (`resumen=True`): párrafo generado desde los KPIs ya calculados — total filtrado, métrica principal del módulo (monto, duración, % completadas...), dato más notorio. Máx 4-5 líneas, sin inventar texto fuera de los números.
2. **Top-N destacados** (`top_n_analisis=N`): tabla corta con los N registros/entidades líderes por la métrica clave del módulo (ej. top 5 patrocinadores por monto). Reutiliza distribuciones que ya están en kpis cuando aplique.
3. **Comparativa período vs anterior** (`comparar=True`): ejecutar la misma consulta con el rango desplazado hacia atrás (misma longitud), mostrar KPIs lado a lado con % de variación. Solo si hay datos del período anterior; indicar "sin datos comparables" si no.

## Reglas duras

- Whitelist server-side de filtros y opciones: claves desconocidas se descartan; rangos con coerción segura (`int`/`float` con try).
- Solo PDF: cero dependencias nuevas (reportlab nativo para gráficos si se agregan).
- No romper el flujo `save()` + registro en `ReporteModel`.
- Coherencia con `.opencode/reportes-context.md` (actualizarlo al completar cada módulo).

## Checklist final por módulo

- [ ] ¿Los selects se llenan con datos reales de la BD?
- [ ] ¿Se puede filtrar por una entidad específica + categoría + rango + fechas?
- [ ] ¿La progresividad funciona (origen recarga destino)?
- [ ] ¿Los KPIs del preview Y del PDF reflejan TODOS los filtros aplicados?
- [ ] ¿El header del PDF lista los filtros usados?
