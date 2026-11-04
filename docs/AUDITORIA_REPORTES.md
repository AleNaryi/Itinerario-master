# AUDITORÍA TÉCNICA — Módulo de Reportes (pre-evolución "constructor")

**Fecha:** 2026-08-25 · **Naturaleza:** auditoría de solo lectura. **Cero cambios de código.**
**Objetivo:** base factual para evolucionar el módulo hacia un sistema profesional de construcción de reportes (navegación progresiva tipo Profit Plus: módulo → categoría → subcategoría → filtros → agrupación → métricas → visualización → comparación → resultado) **sin eliminar la funcionalidad actual**.

**Fuentes leídas íntegras:** `AGENTS.md`, `.opencode/reportes-context.md`, `reportes_controller.py` (682 l.), `reportes_data.py` (749 l.), `reportes_utils.py` (110 l.), `GestionReportes.js` (803 l.), `reportes/dashboard.html` (258 l.), `base_report.py` (394 l.), los 13 `*_report.py` (1.053 l.), `test_reportes_filtros/pdf/smoke.py`, skills `reportes-pdf` + `reportes-detallados`, `requirements.txt`, modelos involucrados, `estadio_db.sql`, `seguridad.sql`. Referencias como `archivo:línea` son verificables.

---

## PARTE 1 — Las 16 respuestas

### 1. Qué funciona actualmente

- Flujo completo y probado: módulo → filtros contextuales AJAX (`/reportes/filtros/<modulo>`) → preview (tabla + KPIs, truncado a 100 con aviso) → PDF (KPIs + análisis opcional resumen/Top-N/comparativa + tabla completa) → guardado en `static/reportes/YYYY/MM/` + registro en `seguridad.reportes_generados` → descarga/eliminación.
- Filtros progresivos reales en 6 módulos: contratos (tipo→patrocinador), inventario (tipo→estado), premios (estado→patrocinador), tareas (estado→usuario), usuarios (departamento→rol), mantenimiento (estado→recurso); bitácora tiene triple select AJAX.
- Hints de rango calculados en SQL real: MIN/MAX de monto/costo/cantidad/días/duración por módulo (`_filtros_*`, controller L34-356).
- Ordenamiento server-side con etiqueta legible en el PDF ("Ordenado por: …", controller L620-629).
- Whitelist server-side de opciones PDF (`resumen/comparar/top_n`, controller L578-596).
- Comparativa de períodos por desplazamiento de ventana (controller L606-618 + `base_report.py:228`).
- Suite de tests: filtros por módulo (151 l.), PDF (56 l.), smoke (41 l.) — red de seguridad para refactorizar.
- Permisos: blueprint completo bajo `verificar_acceso({'reportes.dashboard': 'dashboard.view'})`.
- Soft-delete de reportes generados + listado en dashboard (últimos 50).

### 2. Qué debe mantenerse intacto (contratos)

| Contrato | Por qué |
|---|---|
| Firma `(filtros, fi, ff) -> (datos, kpis)` del dict `OBTENEDORES` | Es el punto de acoplamiento backend; todo lo demás puede envolverla |
| Rutas HTTP y payloads de `/filtros/<modulo>`, `/preview`, `/generar`, `/descargar`, `/eliminar` | El frontend y los tests dependen de ellas |
| Firma `generate(datos, filtros=None, kpis=None, opciones=None)` + `save()` de `BaseReportGenerator` | Punto único de extensión del PDF (skill reportes-pdf) |
| Forma de `MODULE_CONFIG.<modulo>` (`filters/columns/kpiCards`) y convenciones `progressive`/`dependsOn`/primer option "Todos..." | Contrato frontend documentado |
| Whitelist de opciones en `generar()` y CSRF | Seguridad |
| Registro en `ReporteModel` y ruta física de archivos | Trazabilidad ya usada por la UI |
| Tests existentes (smoke congelan respuesta observable) | Red de migración |

### 3. Qué debe refactorizarse

1. **Boilerplate duplicado en generadores:** ~9 de 13 `*_report.py` copian íntegro el cuerpo de `generate()` (buffer/doc/story/header/kpis/análisis/tabla/pie — p.ej. `balance_report.py:20-39`). Solo guiones/contratos/reels añaden distribuciones propias. Refactor: hook `_secciones_extra(kpis)` llamado desde `BaseReportGenerator.generate()`; los generadores vuelven a ser declarativos.
2. **Columnas de preview definidas en DOS sitios:** `COLUMNAS_PREVIEW` en el controller (L390-478) Y `columns` en cada `MODULE_CONFIG` del JS. Deben unificarse (una fuente, la otra la recibe).
3. **`cargarOpcionesAjax`:** cadena de 12 `if/else` por clave de respuesta (JS L492-557). Refactor: contrato genérico — el backend devuelve `{opciones: [{value,label}], placeholder}` y el JS pinta sin conocer el módulo.
4. **`_datos_*` monolíticos:** cada función repite cargar→filtrar→fechas→enriquecer→agregar→sanitizar con try/except idénticos por filtro numérico. Refactor: pipeline pequeño (`aplicar_rango(datos, campo, filtros, 'costo')`, etc.) o generación SQL.
5. **Validación de filtros inexistente en preview/generar:** se acepta CUALQUIER clave del form (solo se excluyen 5, controller L534/L580). Los desconocidos no filtran pero SÍ se imprimen en el header del PDF como "Filtros aplicados" (base_report L80-89) → texto inyectable al PDF y ruido. Necesita whitelist de filtros por módulo.
6. **Doble contabilidad de fechas:** `CAMPOS_FECHA` en utils (L66) vs `rango_fechas_defecto` en data (L133) vs hints `fecha_min/fecha_max` solo en contratos. Unificar catálogo de campos fecha/métrica por módulo.

### 4. Qué puede reutilizarse tal cual

- `OBTENEDORES` + firma de funciones (el constructor puede seguir llamándolos como "vista por defecto" de cada módulo).
- `_filtrar_por_fecha`, `_parsear_fecha`, `_ordenar_datos`, `_formatear_tiempo`, `_fmt_video_dur` (utils, testeados).
- Patrón de hints MIN/MAX SQL de los `_filtros_*` (es la semilla del futuro catálogo de métricas).
- `_seccion_kpis/_seccion_distribucion/_top_destacados/_comparativa_periodos` del PDF (los gráficos nuevos consumirán esos mismos dicts).
- El patrón progresivo AJAX completo (frontend + handlers) como bloque de la nueva navegación.
- Tests existentes como especificación ejecutable del comportamiento que no debe cambiar.

### 5. Qué está limitado por el diseño actual

- **Vista única por módulo:** no hay categorías/subcategorías (p. ej. "Pagos → por patrocinador → detalle").
- **Columnas/KPIs fijos:** decididos en Python+JS hardcode; el usuario no elige qué ver ni qué métricas calcular.
- **Sin agrupación dinámica:** las distribuciones están pre-elegidas (por tipo, por estado…); no hay "agrupar por X".
- **Sin series temporales:** toda agregación es global del rango filtrado; no hay "por mes/semana/día" (bloquea comparaciones y tendencias reales).
- **Sin gráficos:** solo tablas de distribución; el contrato para charts ya está diseñado en la skill `reportes-pdf` (reportlab nativo, sin deps nuevas) pero **no implementado**.
- **PDF fijo:** vertical letter, columnas completas siempre; el contrato `opciones` de la skill (orientacion/titulo/periodo/columnas/incluir/agrupar_por/logo) está pendiente de implementación — hoy solo existen `resumen/comparar/top_n`.
- **Sin export CSV/Excel**, sin plantillas/favoritos, sin programación/envío.
- **Comparativa débil:** solo escalares globales lado a lado; requiere que el usuario haya puesto ambas fechas (si no, salta silenciosamente, controller L609); no compara series ni categorías.

### 6. Problemas de rendimiento

1. **Recalculo total en cada paso:** preview ejecuta la carga completa; "Generar PDF" la vuelve a ejecutar desde cero (controller L601 tras L543 del preview); con `comparar=1` son 3 ejecuciones. Sin cache del último resultado.
2. **Carga completa en memoria + filtrado/agregación Python** en 11 de 12 módulos (ver §9).
3. **Ordenamiento Python sobre strings:** `_ordenar_datos` hace `str(d.get(campo)).lower()` (utils L104) → orden lexicográfico INCORRECTO en columnas numéricas ('100' < '20'). Bug real de UX en previews con montos/costos.
4. **Preview sin paginación server-side:** serializa hasta 100 filas pero KPIs y datos completos se procesan igual.
5. **`_serializar_datos` descarta silenciosamente valores no primitivos** (objetos anidados, controller L481-495) — riesgo de columnas vacías sin aviso si un enriquecimiento devuelve objetos.

### 7. N+1 existentes

| Dónde | Coste | Detalle |
|---|---|---|
| `MantenimientoModel.consultar()` (mantenimiento_model.py:162) | **×4 por fila** | recurso + usuario + historial + usuario-por-nota-de-historial |
| `ReelModel.consultar()` → `_obtener_videos` (reels_model.py:40) | ×1 por reel | `videos LEFT JOIN patrocinadores` por reel |
| `GuionModel.obtener_fechas` por guion en `_datos_guiones` (data L209) | ×1 por guion | `guion_fechas` |
| `BalanceModel.obtener_historial_pagos` construye un objeto Pago por fila | lineal OK | no es N+1 pero materializa objetos innecesarios |

### 8. LIMIT 500 / límites

- `balance`: `obtener_historial_pagos(limit=500)` — el reporte trunca silenciosamente a partir de 500 pagos.
- `bitacora`: `limite=500` en `_datos_bitacora` (data L655).
- Preview `datos[:100]` (controller L558): correcto como display (hay aviso UI), NO es deuda — mantener.
- Acción recomendada: mover fechas/tipo al WHERE SQL y eliminar los 500; paginar solo el preview.

### 9. Consultas que deben pasar de Python a SQL

Prioridad por volumen potencial:

1. **balance** — WHERE `fecha_pago BETWEEN` + `tipo_pago` + JOIN real a patrocinador (hoy matchea `id_contrato.startswith(patrocinador_id)`, data L428 — incorrecto si ids multi-dígito coinciden por prefijo).
2. **mantenimiento** — reescribir como 3 consultas planas con JOIN (`mantenimientos LEFT JOIN recursos`, `seguridad.usuarios`, `historial_mantenimiento` en bloque) + `DATEDIFF` ya demostrado viable (controller L305 usa DATEDIFF para hints).
3. **tareas** — un solo `tareas LEFT JOIN tareas_asignadas LEFT JOIN seguridad.usuarios` en vez de T×A anidado en Python (data L467-485).
4. **reels** — videos en bloque `WHERE reel_id IN (...)` agrupado en Python (patrón ya usado en guiones-elementos, data L180).
5. **guiones** — conteo de elementos y suma de duración vía `GROUP BY guion_id`; fechas en bloque.
6. **Todos los rangos numéricos y fechas** (costo/monto/cantidad/días/duración + fecha_inicio/fin) → WHERE/HAVING.
7. **Agregación de KPIs/distribuciones** → `GROUP BY` + `COUNT/SUM/AVG/MIN/MAX` cuando el módulo crezca (contratos e inventario son los primeros candidatos por volumen monetario).

### 10. Filtros ya existentes (inventario completo)

| Módulo | Selects | Rangos | Fechas | Progresivo |
|---|---|---|---|---|
| guiones | estado (estático), encargado (AJAX BD) | elementos_min/max | creado_en | — |
| inventario | tipo_nombre, estado_nombre (AJAX BD) | costo_min/max | fecha_compra | tipo→estado |
| premios | estado (estático), patrocinador_id (AJAX) | cantidad_min/max, cantidad_entregada_min/max | fecha_creacion | estado→patrocinador |
| contratos | tipo (estático), estatus (estático), patrocinador_id (AJAX) | monto_min/max (+hints MIN/MAX SQL y fecha_min/max) | fecha_inicio | tipo→patrocinador |
| balance | tipo_pago (AJAX), patrocinador_id (AJAX) | monto_min/max | fecha_pago | — |
| tareas | estado (estático), asignado_a (AJAX→usuario_id) | — | fecha_asignacion_tarea | estado→usuario |
| patrocinadores | tipo_contrato (estático), estado_pat (estático) | — | ⚠️ sin columna fecha real en tabla | — |
| usuarios | departamento, rol (AJAX), activo (estático) | — | fecha_registro | depto→rol |
| mantenimiento | estado (estático), recurso_id (AJAX) | dias_min/max (+hint DATEDIFF SQL) | fecha_ingreso | estado→recurso |
| reels | patrocinador_id (AJAX) | duracion_min/max (segundos) | creado_en | — |
| bitacora | usuario_id, tipo_accion, modulo_filter (triple AJAX BD) | — | created_at | — |

### 11. KPIs ya existentes

- **guiones:** total, borradores, publicados, en_vivo, finalizados, tiempo_total, promedio_seg
- **inventario:** total, costo_total, costo_promedio (+dicts tipos, estados)
- **premios:** total, pendientes, entregados, tasa_entrega% (+dict por_patrocinador)
- **contratos:** total, vigentes/vencidos/borradores, bronce/plata/oro, monto_total/promedio/min/max/vigentes (formato $), vigentes_porcentaje%, top_patrocinadores(dict)
- **balance:** total_pagos, monto_total, promedio, monto_min/max (+dict tipos_pago)
- **tareas:** total, pendientes, en_progreso, completadas, completadas_pct%
- **patrocinadores:** total, activos, inactivos (+dict por_tipo)
- **usuarios:** total, activos, inactivos (+dicts roles, departamentos)
- **mantenimiento:** total, en_espera, en_reparacion, reparados, dados_baja, promedio_dias (+dict top_recursos)
- **reels:** total, total_videos, duracion_total, duracion_promedio
- **bitácora:** total, creaciones, ediciones, eliminaciones (+dicts modulos, top_usuarios)

### 12. Distribuciones ya existentes

En `kpis` como dicts (listas para gráficos): inventario tipos+estados · premios por_patrocinador · contratos top_patrocinadores · balance tipos_pago · patrocinadores por_tipo · usuarios roles+departamentos · mantenimiento top_recursos · bitácora modulos+top_usuarios.

Construidas ad-hoc EN el generador (no en kpis): guiones distribución por estado (desde escalares, guiones_report L31), contratos por tipo y estatus (contratos_report L51-54). → Deuda menor: homogeneizar (todas como dicts en kpis).

Sin ninguna distribución: tareas (% only), reels.

### 13. Capacidades faltantes para un constructor dinámico

1. **Catálogo metadata por módulo** (campos disponibles, tipo, si es métrica/dimensión/fecha) — hoy ese conocimiento vive implícito en código disperso.
2. **Selección dinámica de columnas** (subconjunto + orden) — el contrato `opciones['columnas']` de la skill ya lo anticipa.
3. **Agregaciones configurables** (sum/avg/count/min/max sobre campo elegido).
4. **GROUP BY dinámico** (agrupar por dimensión elegida) + subtotales.
5. **Series temporales** (día/semana/mes) — prerrequisito de tendencias y comparativas reales.
6. **Visualizaciones** (pie/barras/línea con reportlab.graphics — cero deps nuevas, ya previsto en skill).
7. **Comparación configurable** (período anterior ya existe; falta A-vs-B por categoría).
8. **Plantillas guardadas** (nombre + módulo + filtros + layout) — `reportes_generados.filtros` ya guarda JSON, es la semilla natural.
9. **Export CSV/Excel** (barato con stdlib csv; Excel requeriría lib nueva — evaluar).
10. **Paginación server-side** del preview.
11. **Whitelist/catálogo de filtros por módulo** (cierra el hueco de §3.5).
12. **Drill-down navegacional** (módulo → categoría → subcategoría → filas): hoy solo existe el drill-down de FILTROS (progresivos), no de RESULTADOS.

### 14. Columnas y relaciones reales por módulo

Esquema verificado (`estadio_db.sql` L29-388 + ALTER TABLE con FK reales L862-930; `seguridad.sql`). Relaciones con FOREIGN KEY declaradas:

```
contrato.id_patrocinador        → patrocinadores(id_patrocinador)
pagos.id_contrato               → contrato(id_contrato)
premios.id_patrocinador         → patrocinadores(id_patrocinador)
elementos_guion.guion_id        → guiones(id)
elementos_guion.fecha_id        → guion_fechas(id)
guion_fechas.guion_id           → guiones(id)
recursos.tipo_id                → tipo_recurso(id)
recursos.estado_id              → estado_recurso(id)
asignaciones_recursos.recurso_id→ recursos(id) · estado_asignacion_id → estado_asignacion(id)
historial_mantenimiento.mantenimiento_id → mantenimientos(id) ON DELETE CASCADE
```

Relaciones lógicas SIN FK declarada (usadas por el motor igualmente): `asignaciones_recursos.usuario_id → seguridad.usuarios.id`, `mantenimientos.recurso_id/usuario_id`, `tareas_asignadas.id_tarea/id_usuario`, `videos.reel_id/id_patrocinador`, `reels.id_patrocinador`, `actividad_usuario.usuario_id`, `pagos.registrado_por`, `premios.entregado_por`, `tareas.id_usuario_creador`.

Campos por tabla: ver §6 del documento hermano `docs/MODULO_REPORTES_BRIEF.md` (volcado literal de CREATE TABLEs — sigue vigente, mismo esquema).

### 15. Datos convertibles realemente en métricas (campos numéricos/fecha)

| Módulo | Métricas posibles con datos actuales |
|---|---|
| contratos | monto_total (SUM/AVG/MIN/MAX), duración contrato (fecha_fin−inicio), días restantes, conteo por tipo/estatus |
| pagos | monto (SUM/AVG/MIN/MAX), conteo por tipo_pago, serie mensual por fecha_pago, % pagado vs monto contratado (JOIN contrato) |
| inventario | costo (SUM/AVG), conteo por tipo/estado, antigüedad (fecha_compra→hoy) |
| premios | cantidad, cantidad_entregada, tasa entrega, pendiente= cantidad−entregada |
| guiones | COUNT elementos, SUM duracion_estimada, promedio por guion, pregame/game ratio |
| mantenimientos | dias_en_taller (DATEDIFF ya validado), promedio/moda, frecuencia por recurso, costo implícito si se agrega campo |
| tareas | conteos por estado, tiempo implícito (fecha_asignacion→sin campo de cierre ⚠️), carga por usuario |
| reels | SUM duracion (min→seg), COUNT videos, promedio clips/reel |
| bitácora | conteos por tipo_acción/módulo/usuario/día (serie temporal natural) |
| usuarios | conteos por rol/depto/activo, antigüedad (fecha_registro) |
| patrocinadores | conteos (⚠️ sin fecha ni montos propios; su valor sale de JOIN con contrato/pagos) |

⚠️ Huecos de datos que limitan métricas nuevas: tareas no registra fecha de completado; pagos no registran moneda; patrocinadores carecen de fecha alta/baja.

### 16. Gráficos válidos por módulo (con datos YA disponibles)

| Módulo | Torta/Barras (distribución) | Línea (serie temporal) | Barras comparativas |
|---|---|---|---|
| contratos | tipo, estatus | monto por mes (fecha_inicio/pagos) | período actual vs anterior (monto_total) |
| balance | tipos_pago | monto por mes/semana (fecha_pago) ★ | período anterior |
| inventario | tipos, estados | — | costo por tipo |
| premios | por_patrocinador, estado | entregas por mes (fecha_entrega) | período anterior |
| guiones | estados | elementos/duración por mes (creado_en) | período anterior |
| mantenimiento | estados, top_recursos | ingresos por mes (fecha_ingreso) | promedio_dias vs anterior |
| tareas | estados | — (falta fecha de cierre) | período anterior |
| usuarios | roles, departamentos | altas por mes (fecha_registro) | — |
| reels | — | reels creados por mes | duración media vs anterior |
| bitácora | modulos, acciones | actividad por día ★ (created_at) | período anterior |

★ = casos donde una serie temporal aporta más valor inmediato.

---

## PARTE 2 — Secciones finales

### A. Arquitectura actual

```
[dashboard.html] --grid módulos--> click
[GestionReportes.js MODULE_CONFIG] --GET /reportes/filtros/<modulo>--> [_filtros_<modulo>] --> JSON selects+hints
      │  (progresivos: change → refetch con dependsOn)
      ▼ POST /preview {modulo + filtros}
[_obtener_datos] --> OBTENEDORES[modulo](filtros, fi, ff) --> (datos[], kpis{})
      │            modelo.consultar() → memoria → filtrar/agregar EN PYTHON
      ▼ JSON {datos[:100], total, kpis escalares}
[render preview: kpiCards + tabla COLUMNAS_PREVIEW]
      ▼ POST /generar (+resumen/comparar/top_n whitelist)
[_obtener_datos OTRA VEZ (+3ª vez si comparar)]
      ▼ <Modulo>Report(current_user).generate(...) --> reportlab story --> save() --> static/reportes + reportes_generados
```

Características estructurales: MVC sin capa servicios; el "cerebro" de cada reporte vive en 2 mitades (Python: qué datos/KPIs; JS: cómo se piden y pintan); el PDF hereda de una base con punto único de extensión.

### B. Arquitectura propuesta (evolución compatible)

Principio: **añadir capas, no reemplazar las existentes.** Lo actual se convierte en la "vista rápida" de cada módulo dentro de la nueva navegación.

```
NIVEL 1 · Módulo          = MODULOS_DISPONIBLES (igual)
NIVEL 2 · Categoría       = plantilla de análisis: "Resumen general" (≈ hoy),
                            "Por dimensión", "Serie temporal", "Detalle"
NIVEL 3 · Subcategoría    = dimensión elegible (catálogo por módulo)
NIVEL 4 · Filtros         = mismos _filtros_* + whitelist/catálogo (§3.5)
NIVEL 5 · Agrupación      = GROUP BY dinámico + subtotales (SQL)
NIVEL 6 · Métricas        = catálogo sum/avg/count/min/max por campo (§15)
NIVEL 7 · Visualización   = tablas (hoy) + pie/bar/line (reportlab nativo)
NIVEL 8 · Comparación     = períodos (existe) + A-vs-B por dimensión (nuevo)
NIVEL 9 · Resultado       = PDF configurable (contrato opciones de la skill)
                            + export CSV + plantilla guardable
```

Piezas nuevas necesarias (backend):
1. **`reportes_catalogo.py`** (nuevo): metadata por módulo — dimensiones agrupables, métricas agregables, campos fecha, distribuciones ya calculadas, gráficos válidos (§15/§16 son su primer borrador).
2. **Endpoint `/reportes/construir`** (POST): recibe `{modulo, categoria, dimension, metricas[], filtros{}, grupo_tiempo?, comparar?}` → genera dataset genérico `{columnas, filas, series, totales}` ejecutando SQL con GROUP BY real.
3. **Motor SQL parametrizado** con whitelists DOBLES: nombres de campo/métrica validados contra el catálogo (nunca interpolados crudos).
4. **Generador `ConstructorReport`** único que consume el dataset genérico + `opciones` completas de la skill (orientación/columnas/gráficos/agrupación).

Frontend: wizard de pasos dentro del panel actual (stepper), reutilizando el render de filtros; `MODULE_CONFIG` gana `dimensiones/metricas/series` por módulo generadas desde el catálogo (un fetch, no hardcoded).

Los 12 flujos actuales quedan intactos como categoría "Resumen general".

### C. Riesgos

| # | Riesgo | Severidad | Mitigación |
|---|---|---|---|
| R1 | SQL dinámico mal saneado en el constructor (nombres de campos/métricas) | ALTA | Catálogo-whitelist estricto: solo identificadores que existan en `reportes_catalogo`; tests de inyección |
| R2 | Regresión en los 12 flujos vivos durante la migración | ALTA | Tests smoke+filtros congelan comportamiento; migrar por módulo detrás de flag |
| R3 | Consultas GROUP BY pesadas sin índices de fecha | MEDIA | Índices `(fecha_campo)` por tabla antes de habilitar series; LIMIT de salvaguarda inicial |
| R4 | Doble sistema (viejo/nuevo) divergiendo en KPIs | MEDIA | El nuevo REUTILIZA OBTENEDORES como vista por defecto; números deben coincidir en tests |
| R5 | Inyección de texto al header del PDF vía filtros desconocidos (hoy, §3.5) | BAJA-MEDIA | Cerrar con whitelists antes del constructor |
| R6 | Complejidad UI supera al usuario (~30 operadores, no analistas) | MEDIA | Wizard guiado por defectos sensatos; avanzado opcional |
| R7 | `eventlet -w 1` single-worker: consultas largas bloquean al resto del sitio | MEDIA | Timeout/LIMIT duros por consulta del constructor |

### D. Deuda técnica (inventariada, priorizada)

1. N+1 de mantenimiento (×4) — impacto directo en reportes.
2. LIMIT 500 en balance y bitácora (truncado silencioso).
3. Orden numérico roto en preview (`_ordenar_datos` string-wise).
4. Filtros sin whitelist → texto inyectable a header PDF.
5. Boilerplate generate() duplicado en ~9 generadores.
6. Columnas duplicadas controller/JS.
7. `cargarOpcionesAjax` con cadena if/else por clave.
8. Distribuciones de guiones/contratos construidas en el generador en vez de kpis.
9. Match patrocinador en balance por `startswith` (incorrecto con prefijos).
10. Bug latente de `resumen` (objeto Usuario vs dict) — inalcanzable hoy, pero el constructor no debe copiarlo.
11. `validarFiltros()` del JS es no-op (L591: siempre habilita).
12. CAMPOS_FECHA/rango_fechas_defecto duplicados entre utils y data.

### E. Oportunidades

- El catálogo de métricas (§15) y de gráficos (§16) ya está esbozado por esta auditoría — arrancar desde ahí.
- `reportes_generados.filtros` ya guarda JSON → plantillas guardadas casi gratis.
- Skill `reportes-pdf` dejó el contrato `opciones` diseñado (orientación/columnas/agrupar_por/incluir/logo/charts reportlab) — implementarlo es la fase PDF del constructor.
- Gráficos con `reportlab.graphics.charts` (ya instalado): cero dependencias nuevas para visualizaciones.
- Export CSV con `csv` stdlib: cero deps. Excel requeriría openpyxl (evaluar necesidad real primero).
- La comparativa por desplazamiento de ventana ya funciona → extenderla a series es incremental.
- Bitácora ya filtra en SQL: es el patrón a generalizar, no el contrario.

### F. Módulos y capacidades (matriz resumen)

| Módulo | Filtros | Progresivo | KPIs | Distribuciones | Serie temporal posible | Escalabilidad actual |
|---|---|---|---|---|---|---|
| contratos | ●●● | ✓ | ●●● (montos) | 3 | ✓ mensual | Alta |
| inventario | ●●● | ✓ | ●● | 2 | ✗ (fecha_compra puntual) | Alta |
| premios | ●●● | ✓ | ●●● | 1 | ✓ entregas | Alta |
| guiones | ●●○ | — | ●●● | 1 (en PDF) | ✓ creado_en | Media (N+1 fechas) |
| balance | ●●○ | — | ●●● | 1 | ✓★ mensual | 🔴 LIMIT 500 |
| tareas | ●●○ | ✓ | ●● | ✗ | ⚠️ falta fecha cierre | Media (T×A) |
| patrocinadores | ●○○ | — | ●○○ | 1 | ✗ (sin fecha propia) | Trivial |
| usuarios | ●●○ | ✓ | ●●○ | 2 | ✓ altas | Trivial |
| mantenimiento | ●●● | ✓ | ●●● | 1 | ✓ ingresos | 🔴 N+1 ×4 |
| reels | ●○○ | — | ●●○ | ✗ | ✓ creado_en | Media (N+1 videos) |
| bitácora | ●●● | triple | ●●● | 2 | ✓★ diaria | Buena (SQL) |
| resumen | — | — | ●○○ | ✗ | ✗ | 🐛 bug latente |

### G. Plan de migración (fases, cada una deja el sistema verde)

- **F0 · Blindaje (previo, pequeño):** cerrar deuda crítica que el constructor heredaría — whitelists de filtros por módulo (R5/D4), orden numérico (D3), quitar LIMIT 500 moviendo filtros a SQL en balance/bitácora (D2), fix startswith de balance (D9).
- **F1 · Catálogo:** crear `reportes_catalogo.py` con metadata de los 12 módulos (dimensiones/métricas/fechas/gráficos de §15-16) + tests de consistencia (toda métrica del catálogo existe como columna real).
- **F2 · Motor de construcción:** endpoint `/reportes/construir` + SQL parametrizado con doble whitelist (GROUP BY, agregaciones, series). Empezar por 2 módulos piloto: **bitácora** (ya filtra en SQL) y **contratos** (mejor KPIs).
- **F3 · Visualizador:** stepper frontend (categorías→dimensión→métricas) + preview genérico reutilizando kpiCards/tabla + gráficos reportlab en el PDF vía `ConstructorReport`.
- **F4 · PDF configurable:** implementar el contrato `opciones` de la skill (orientación, columnas, incluir.*, agrupar_por) en `base_report.py`; refactor del boilerplate de generadores (D5) en la misma pasada.
- **F5 · Extensión por módulos:** replicar piloto al resto en orden de valor: balance → mantenimiento (tras matar su N+1) → premios → guiones → inventario → tareas → usuarios/patrocinadores/reels.
- **F6 · Extras:** plantillas guardadas (JSON ya existe), export CSV, comparación A-vs-B por dimensión.

### H. Orden recomendado de implementación

1. F0 completo (sin él, cualquier medición nueva estará contaminada por bugs conocidos).
2. Catálogo + motor con bitácora y contratos (piloto vertical end-to-end).
3. Gráficos + PDF configurable.
4. Resto de módulos por orden de valor de negocio: balance (dinero) → mantenimiento (operación, previa limpieza N+1) → premios → guiones → resto.
5. Plantillas/export al final (son azúcar, no estructura).

Regla transversal: **un módulo end-to-end antes de abrir el siguiente** (misma disciplina que la skill reportes-detallados ya impuso en Fase 4).

### I. Archivos que deberían modificarse (en fases)

| Archivo | Cambio esperado |
|---|---|
| `app/helpers/reportes_catalogo.py` | NUEVO — catálogo metadata por módulo |
| `app/controller/reportes_controller.py` | +endpoint construir; whitelists de filtros; NO tocar rutas existentes |
| `app/helpers/reportes_data.py` | migración gradual de `_datos_*` a SQL (módulo a módulo); firma intacta |
| `app/static/js/GestionReportes.js` | stepper + render genérico de opciones; MODULE_CONFIG ampliado desde catálogo |
| `app/view/reportes/dashboard.html` | contenedor del wizard (panel actual reutilizado) |
| `app/helpers/generators/base_report.py` | contrato `opciones` completo + hook `_secciones_extra` + charts |
| `app/helpers/generators/*_report.py` | deglución del boilerplate (quedan declarativos) |
| `app/model/mantenimiento_model.py`, `reels_model.py`, `balance_model.py`, `guion_model.py` | eliminación de N+1 / LIMIT (consultas en bloque) |
| `tests/test_reportes_*.py` + `test_constructor.py` (nuevo) | ampliación por fase |
| `estadio_db.sql` | índices de fecha si las series lo exigen (migración real en BD + dump) |

### J. Archivos que NO deberían tocarse

- `AGENTS.md` reglas del proyecto; `.opencode/reportes-context.md` solo se ACTUALIZA al completar módulos (convención de la skill).
- Rutas y payloads HTTP existentes (`/filtros/<modulo>`, `/preview`, `/generar`, `/descargar`, `/eliminar`).
- Firma pública de `OBTENEDORES` y de `generate()/save()`.
- `reportes_utils.py` (helpers puros testeados; solo se les puede añadir, no cambiar semántica).
- Sistema de permisos (`PERMISSION_MAP`/`verificar_acceso`) y CSRF.
- `ReporteModel`/tabla `reportes_generados` (estructura estable; solo se consume).
- Todo lo ajeno al módulo: EN VIVO (`envivo-*` intocable por AGENTS.md), notificaciones, auth.
- `requirements.txt` salvo justificación fuerte (todo lo propuesto usa stdlib + reportlab ya presentes).

### K. Tests necesarios

1. **Congelamiento (ya existen, mantener verdes):** smoke + filtros + pdf actuales.
2. **Catálogo:** toda dimensión/métrica declarada existe como columna en su tabla (introspección contra `*_test`) — mata alucinaciones del catálogo.
3. **Motor constructor:** por módulo piloto — GROUP BY devuelve totales que cuadran con el flujo viejo (paridad de números); inyección: pedir `dimension=1; DROP` → 400; métrica fuera de catálogo → 400.
4. **Series temporales:** suma de buckets == total global del rango.
5. **Whitelists de filtros:** form con claves basura → no aparecen en header del PDF (regresión de R5).
6. **Orden numérico:** preview con montos 20/100 ordena 20<100 (regresión D3).
7. **LIMIT eliminado:** >500 filas sintéticas en `*_test` → total real en balance/bitácora.
8. **PDF configurable:** sin opciones byte-equivalente (checklist skill); orientación horizontal cambia mediabox; agrupar_por produce subtotales que suman el total.
9. **Paridad viejo/nuevo:** mismo módulo+filtros vía `/preview` y vía `/construir` (categoría resumen) → mismos KPIs.
10. **Rendimiento básico:** mantenimiento con N sintético no dispara queries O(N) (assert de contador de consultas con el driver en modo test).

---

*Fin de la auditoría. Ningún archivo de código fue modificado. Documento hermano de contexto: `docs/MODULO_REPORTES_BRIEF.md`.*
