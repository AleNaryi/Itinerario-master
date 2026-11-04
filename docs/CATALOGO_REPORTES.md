# CATÁLOGO FUNCIONAL DE REPORTES — 12 módulos

**Fecha:** 2026-08-25 · **Base:** exclusivamente columnas y relaciones verificadas en `estadio_db.sql` / `seguridad.sql` y el código real (auditoría `docs/AUDITORIA_REPORTES.md`, arquitectura `docs/ARQUITECTURA_CONSTRUCTOR_REPORTES.md`). **Documento de diseño: no implementado salvo lo marcado ✓ (piloto).**

---

## 0. Convenciones globales

**Validez de visualizaciones** (regla dura, aplica a todos los módulos):

| Visualización | Cuándo es válida |
|---|---|
| `tabla` | Siempre |
| `kpi_cards` | Solo agrupación "todos" (una fila total) |
| `torta` | Distribución categórica de ≤8 valores, métrica aditiva positiva |
| `barras_h` | Ranking de dimensión categórica, 1-2 métricas |
| `barras_v` | ≤6 categorías comparables |
| `linea` | SOLO dimensión temporal (evolución) |
| `ranking` | Tabla ordenada descendente con posición |

**Reglas de métricas:** monetarias → SUM/AVG/MIN/MAX (nunca COUNT sobre montos); porcentajes → solo derivados de ratios; duraciones → SUM/AVG sobre segundos/días; conteos → COUNT/DISTINCT.

**Leyenda:** ✓ ya implementado en el piloto · ⚠️ limitación real de datos · 🔒 requiere resolver deuda previa.

---

## 1. GUIONES

**Fuentes reales:** `guiones g` (+ `elementos_guion eg ON eg.guion_id=g.id`, `guion_fechas gf`) · soft-delete `g.status=1`.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Producción por encargado · Evolución de creación · Ejecución programada |
| 2 | Dimensiones | estado(g.estado) · encargado(eg.encargado) · tipo elemento(eg.tipo: pregame/game) · inning(eg.inning, solo game) · mes_creacion(DATE_FORMAT g.creado_en) |
| 3 | Filtros | estado · encargado (AJAX existente) · elementos_min/max (HAVING COUNT eg) · fecha_inicio/fin sobre creado_en |
| 4 | Agrupaciones | estado · encargado · mes · año · todos |
| 5 | Métricas | COUNT guiones · COUNT elementos (eg) · SUM eg.duracion_estimada (seg) · AVG duración por elemento · AVG elementos/guion · pregame/game ratio |
| 6 | KPIs | total · borradores · publicados · en_vivo · finalizados · tiempo_total · promedio_seg *(ya existen)* |
| 7 | Rankings | Top encargados por nº de elementos · Top guiones por duración total |
| 8 | Visualizaciones | tabla ✓ · torta estados (4 valores) ✓ · barras_h encargados ✓ · línea creación/mes ✓ · kpi_cards ✓ · ranking ✓ |
| 9 | Comparaciones | período anterior (creación) · A-vs-B estados (borrador vs publicado) |
| 10 | Columnas tabla | nombre · game · pregame · fecha_ejecucion · estado · tiempo_total *(actuales)* |
| 11 | Ordenamientos | nombre · nº elementos · duración · creado_en |
| 12 | Top N | encargados más cargados (5-20) · guiones más largos |
| 13 | Temporal | creación por semana/mes (creado_en) |
| 14 | Exportaciones | pdf · csv |

⚠️ `fecha_ejecucion` proviene de `guion_fechas` (N+1 actual): la categoría "Ejecución programada" requiere la consulta en bloque previa (deuda D-guiones).

---

## 2. INVENTARIO

**Fuentes:** `recursos r LEFT JOIN tipo_recurso t LEFT JOIN estado_recurso e` (+ `asignaciones_recursos a JOIN seguridad.usuarios u`) · `r.eliminado=0`.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Valorización · Asignaciones (cruce real a.u→u.id) · Antigüedad |
| 2 | Dimensiones | tipo(t.nombre) · estado(e.nombre) · mes_compra(r.fecha_compra) · año_compra · usuario_asignado(u.nombre, solo cat. Asignaciones) |
| 3 | Filtros | tipo_nombre · estado_nombre (AJAX progresivos existentes) · costo_min/max · fechas compra · asignaciones: usuario · devuelto sí/no (`a.fecha_devolucion_real IS NULL`) |
| 4 | Agrupaciones | tipo · estado · mes compra · año compra · usuario (Asignaciones) · todos |
| 5 | Métricas | COUNT recursos · SUM/AVG/MIN/MAX r.costo · antigüedad media `DATEDIFF(CURDATE(), r.fecha_compra)` · COUNT asignaciones activas |
| 6 | KPIs | total · costo_total · costo_promedio · tipos(dict) · estados(dict) *(existentes)* |
| 7 | Rankings | tipos por valor acumulado · usuarios con más activos asignados |
| 8 | Visualizaciones | tabla ✓ · torta tipos/estados ✓ · barras_h valor por tipo ✓ · línea compras/mes ✓ · ranking ✓ · kpi_cards ✓ |
| 9 | Comparaciones | período anterior (compras) |
| 10 | Columnas tabla | id · nombre · tipo · estado · costo · fecha_compra / Asignaciones: recurso · usuario · fecha_asignacion · devolucion_esperada · devuelto |
| 11 | Ordenamientos | nombre · costo (numérico) · fecha_compra · nº asignaciones |
| 12 | Top N | tipos más valiosos · recursos más asignados |
| 13 | Temporal | compras por mes/año (fecha_compra) |
| 14 | Exportaciones | pdf · csv |

---

## 3. PREMIOS

**Fuentes:** `premios p LEFT JOIN patrocinadores pat` · `p.estatus=FALSE`.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Entregas · Stock pendiente · Por patrocinador |
| 2 | Dimensiones | estado(p.estado) · patrocinador(pat.nombre_empresa) · mes_creacion(p.fecha_creacion) · mes_entrega(p.fecha_entrega) |
| 3 | Filtros | estado · patrocinador_id (progresivo existente) · cantidad_min/max · cantidad_entregada_min/max · fechas creacion/entrega |
| 4 | Agrupaciones | estado · patrocinador · mes entrega · todos |
| 5 | Métricas | COUNT premios · SUM p.cantidad · SUM p.cantidad_entregada · pendientes `SUM(cantidad-cantidad_entregada)` · tasa entrega % |
| 6 | KPIs | total · pendientes · entregados · tasa_entrega% · por_patrocinador(dict) *(existentes)* |
| 7 | Rankings | top patrocinadores por premios aportados · por unidades entregadas |
| 8 | Visualizaciones | tabla ✓ · torta estado (2 valores) ✓ · barras_h patrocinadores ✓ · línea entregas/mes ✓ · ranking ✓ |
| 9 | Comparaciones | período anterior (entregas) |
| 10 | Columnas tabla | nombre · patrocinador · estado · cantidad · cantidad_entregada · fecha_creacion *(actuales)* + pendiente calculada |
| 11 | Ordenamientos | nombre · cantidad · entregada · tasa % · fecha |
| 12 | Top N | patrocinadores más generosos (unidades/premios) |
| 13 | Temporal | entregas por mes (fecha_entrega) · altas por mes (fecha_creacion) |
| 14 | Exportaciones | pdf · csv |

---

## 4. CONTRATOS ✓ (categorías Cartera e Ingresos ya implementadas)

**Fuentes:** `contrato c JOIN patrocinadores p`; Ingresos → `pagos pg JOIN contrato c JOIN patrocinadores p` · `c.estado=1` · `pg.estado=0`.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen ✓ · Cartera ✓ · Ingresos ✓ · Vencimientos · Distribución |
| 2 | Dimensiones | nivel(p.tipo mapa Bronce/Plata/Oro) ✓ · estatus ✓ · patrocinador ✓ · mes_inicio ✓ · mes_pago(pg.fecha_pago, Ingresos) ✓ · tipo_pago(pg) ✓ |
| 3 | Filtros | tipo · estatus · patrocinador_id · monto_min/max ✓ · pg_fecha/pg_tipo/pg_monto ✓ · c_fecha ✓ |
| 4 | Agrupaciones | nivel · estatus · patrocinador · mes inicio · mes pago · todos ✓ |
| 5 | Métricas | COUNT ✓ · SUM/AVG/MIN/MAX c.monto_total ✓ · SUM/AVG pg.monto ✓ · **duración media de contrato** `AVG DATEDIFF(c.fecha_fin,c.fecha_inicio)` · % vigente · % vencido |
| 6 | KPIs | los 13 existentes (montos formateados $, niveles, top_patrocinadores) |
| 7 | Rankings | patrocinadores por monto ✓ (top_patrocinadores) · por nº contratos · próximos a vencer (dias_restantes ASC) |
| 8 | Visualizaciones | tabla ✓ · torta nivel/estatus ✓ · barras_h monto por patrocinador ✓ · línea ingresos/mes ✓ · kpi_cards ✓ · ranking ✓ |
| 9 | Comparaciones | período anterior ✓ (pagos y contratos) · A-vs-B niveles (Bronce vs Oro) |
| 10 | Columnas tabla | patrocinador · tipo · estatus · monto · inicio · fin · dias_restantes *(actuales)* |
| 11 | Ordenamientos | monto (numérico ✓) · fecha_inicio · dias_restantes · patrocinador |
| 12 | Top N | patrocinadores por monto ✓ · mayores contratos vigentes |
| 13 | Temporal | contratos por mes inicio ✓ · cobranza por mes pago ✓ |
| 14 | Exportaciones | pdf · csv ✓ |

"Vencimientos": dimensión bucket de dias_restantes (≤30 / 31-90 / >90 días) — métrica derivada ya existente en filas.

---

## 5. BALANCE / PAGOS

**Fuentes:** `pagos pg JOIN contrato c JOIN patrocinadores p` · `pg.estado=0`. *Requiere el fix SQL ya aplicado en F0 (LIMIT→WHERE).*

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Cobranza · Por tipo de pago · Por patrocinador · Por nivel |
| 2 | Dimensiones | tipo_pago(pg) ✓ · patrocinador(p.nombre_empresa) · nivel(c.tipo mapa) · mes_pago(pg.fecha_pago) ✓ · dia_pago |
| 3 | Filtros | tipo_pago · patrocinador_id (exacto vía JOIN, ya corregido) · monto_min/max · fechas pago ✓ |
| 4 | Agrupaciones | tipo_pago · patrocinador · nivel · mes · día · todos |
| 5 | Métricas | COUNT pagos · SUM/AVG/MIN/MAX pg.monto · ticket promedio (=AVG) · pagos por mes COUNT |
| 6 | KPIs | total_pagos · monto_total · promedio · monto_min/max · tipos_pago(dict) *(existentes)* |
| 7 | Rankings | patrocinadores que más pagan · meses de mayor cobranza |
| 8 | Visualizaciones | tabla ✓ · torta tipos_pago ✓ · barras_h patrocinador/nivel ✓ · **línea cobranza mensual ★** ✓ · ranking ✓ |
| 9 | Comparaciones | período anterior (cobranza) |
| 10 | Columnas tabla | patrocinador · tipo_pago · monto · referencia · fecha_pago *(actuales)* |
| 11 | Ordenamientos | monto numérico · fecha_pago · tipo_pago |
| 12 | Top N | meses de mayor cobranza · pagos individuales mayores |
| 13 | Temporal | ★ cobranza por día/semana/mes (fecha_pago + hora_pago para detalle) |
| 14 | Exportaciones | pdf · csv |

---

## 6. TAREAS

**Fuentes:** `tareas t LEFT JOIN tareas_asignadas ta ON ta.id_tarea=t.id_tarea LEFT JOIN seguridad.usuarios u ON u.id=ta.id_usuario` · `t.Estatus=1 AND ta.Estatus=1`. ⚠️ **No existe fecha de cierre** → prohibido cualquier métrica de duración/tiempo de resolución.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Carga por usuario · Estados |
| 2 | Dimensiones | estado(ta.Estado: Pendiente/En Progreso/Completada) · usuario asignado(u.nombre) · mes_asignacion(ta.fecha_asignacion_tarea) |
| 3 | Filtros | estado · asignado_a (AJAX existente, ya funcional tras F0) · fechas asignación |
| 4 | Agrupaciones | estado · usuario · mes asignación · todos |
| 5 | Métricas | COUNT tareas · COUNT asignaciones · usuarios distintos `COUNT(DISTINCT ta.id_usuario)` · % completadas · tareas sin asignar `COUNT(ta.id_usuario IS NULL)` |
| 6 | KPIs | total · pendientes · en_progreso · completadas · completadas_pct *(existentes)* |
| 7 | Rankings | usuarios con más tareas asignadas · usuarios con más completadas |
| 8 | Visualizaciones | tabla ✓ · torta estados (3 valores) ✓ · barras_h carga por usuario ✓ · ranking ✓ · ✗ línea (sin serie de cierre; asignaciones/mes es débil pero válida como volumen) |
| 9 | Comparaciones | período anterior (volumen asignado) |
| 10 | Columnas tabla | tarea · estado · asignado_a · fecha_asignacion *(actuales)* |
| 11 | Ordenamientos | tarea · estado · usuario · fecha asignación |
| 12 | Top N | usuarios más cargados · tareas con más asignatarios |
| 13 | Temporal | ⚠️ solo volumen de asignaciones por mes (sin evolución de cierre) |
| 14 | Exportaciones | pdf · csv |

---

## 7. PATROCINADORES

**Fuentes:** `patrocinadores p LEFT JOIN seguridad.usuarios ue ON ue.id=p.encargado_id`; cruce cartera → `contrato c`/`pagos pg` (FKs reales). ⚠️ sin columna de fecha propia.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Cartera cruzada (contratos+pagos por empresa) · Por encargado interno |
| 2 | Dimensiones | estado(p.estado activo/inactivo) · tipo_contrato(map Vigente/Vencido) · encargado_interno(ue.nombre) · nivel del contrato(c.tipo, en cruce) |
| 3 | Filtros | tipo_contrato · estado_pat (existentes) · encargado_id (nuevo, AJAX desde seguridad.usuarios) |
| 4 | Agrupaciones | estado · tipo_contrato · encargado · todos |
| 5 | Métricas | COUNT patrocinadores · SUM c.monto_total contratado (cruce) · SUM pg.monto cobrado (cruce) · % con contrato vigente · cartera promedio |
| 6 | KPIs | total · activos · inactivos · por_tipo(dict) *(existentes)* |
| 7 | Rankings | empresas por cartera · por cobranza histórica |
| 8 | Visualizaciones | tabla ✓ · torta estado ✓ · barras_h cartera por empresa ✓ · kpi_cards ✓ · ✗ línea propia (sin fecha alta/baja) |
| 9 | Comparaciones | período anterior SOLO vía pagos/cartera (no de la entidad misma) |
| 10 | Columnas tabla | empresa · rif · teléfono · contrato · encargado interno · monto contratado · cobrado *(nuevas via cruce)* |
| 11 | Ordenamientos | empresa · cartera · cobrado · estado |
| 12 | Top N | principales empresas por cartera/cobranza |
| 13 | Temporal | ✗ directo; ✓ indirecto vía sus pagos (ver Balance/Contratos) |
| 14 | Exportaciones | pdf · csv |

---

## 8. USUARIOS

**Fuentes:** `seguridad.usuarios u`; cruce actividad → `actividad_usuario au ON au.usuario_id=u.id`. ⚠️ nunca exponer password_hash (ya excluido por COLUMNAS_TECNICAS).

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Planta · Actividad en sistema (cruce) · Cuentas dormidas |
| 2 | Dimensiones | rol(u.rol) · departamento(u.departamento) · activo(u.activo) · mes_registro(DATE_FORMAT u.fecha_registro) |
| 3 | Filtros | departamento → rol (AJAX progresivo existente) · activo · fechas registro · dormidas: sin actividad desde X días `MAX(au.created_at)` |
| 4 | Agrupaciones | rol · departamento · mes registro · todos |
| 5 | Métricas | COUNT usuarios · % activos · actividades totales (au) · última actividad `MAX(au.created_at)` · días sin actividad |
| 6 | KPIs | total · activos · inactivos · roles(dict) · departamentos(dict) *(existentes)* |
| 7 | Rankings | usuarios más activos (au COUNT) · departamentos por headcount |
| 8 | Visualizaciones | tabla ✓ · torta roles/deptos ✓ · barras_h actividad ✓ · línea altas/mes ✓ · ranking ✓ |
| 9 | Comparaciones | período anterior (altas, actividad) |
| 10 | Columnas tabla | nombre · email · rol · depto · estado *(actuales)* + última_actividad |
| 11 | Ordenamientos | nombre · rol · depto · fecha_registro · actividad |
| 12 | Top N | usuarios más activos · cuentas más antiguas |
| 13 | Temporal | altas por mes (fecha_registro) · actividad por mes (au.created_at) |
| 14 | Exportaciones | pdf · csv |

---

## 9. MANTENIMIENTO 🔒

**Fuentes:** `mantenimientos m JOIN recursos r` (+`seguridad.usuarios`); `historial_mantenimiento h`. 🔒 **Resolver N+1 ×4 antes de habilitar agregaciones** (auditoría C5/D1).

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Taller (días) · Frecuencia por recurso · Historial de notas |
| 2 | Dimensiones | estado(m.estado) · recurso(r.nombre) · mes_ingreso(m.fecha_ingreso) · usuario que ingresó |
| 3 | Filtros | estado → recurso (AJAX progresivo existente) · dias_min/max · fechas ingreso |
| 4 | Agrupaciones | estado · recurso · mes ingreso · todos |
| 5 | Métricas | COUNT mantenimientos · AVG/MAX dias_en_taller `DATEDIFF(COALESCE(fecha_salida,CURDATE()), fecha_ingreso)` · COUNT notas h · % dados de baja |
| 6 | KPIs | total · en_espera · en_reparacion · reparados · dados_baja · promedio_dias · top_recursos(dict) *(existentes)* |
| 7 | Rankings | recursos más intervenidos ✓ · estados más frecuentes |
| 8 | Visualizaciones | tabla ✓ · torta estados (4 valores) ✓ · barras_h recursos ✓ · línea ingresos/mes ✓ · ranking ✓ |
| 9 | Comparaciones | período anterior (ingresos, días promedio) |
| 10 | Columnas tabla | recurso · estado · ingreso · dias_en_taller · diagnostico *(actuales)* |
| 11 | Ordenamientos | dias_en_taller (numérico) · fecha_ingreso · recurso · estado |
| 12 | Top N | recursos más problemáticos · reparaciones más largas |
| 13 | Temporal | ingresos por mes/semana (fecha_ingreso) |
| 14 | Exportaciones | pdf · csv |

---

## 10. REELS

**Fuentes:** `reels re LEFT JOIN videos v ON v.reel_id=re.id LEFT JOIN patrocinadores p` · ⚠️ resolver N+1 videos (D-reels) para las agregaciones.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen · Contenido · Por patrocinador |
| 2 | Dimensiones | patrocinador(re.id_patrocinador→p.nombre_empresa) · mes_creacion(re.creado_en) |
| 3 | Filtros | patrocinador_id · duracion_min/max en SEGUNDOS (re.duracion_total×60, convención ya usada) · fechas creado_en |
| 4 | Agrupaciones | patrocinador · mes · año · todos |
| 5 | Métricas | COUNT reels · COUNT videos (v) · SUM duración seg `SUM(duracion_total)*60` · AVG clips/reel |
| 6 | KPIs | total reels · total_videos · duracion_total · duracion_promedio *(existentes)* |
| 7 | Rankings | patrocinadores por reels/videos · reels más largos |
| 8 | Visualizaciones | tabla ✓ · barras_h patrocinador ✓ · línea creados/mes ✓ · ranking ✓ · torta ✗ (patrocinador suele ser 1-dominante; permitir solo si ≤8 valores — regla general ya lo cubre) |
| 9 | Comparaciones | período anterior (producción) |
| 10 | Columnas tabla | nombre · patrocinador · videos_count · duracion · creado *(actuales)* |
| 11 | Ordenamientos | duración · nº videos · creado_en · nombre |
| 12 | Top N | reels más largos · con más clips |
| 13 | Temporal | producción por mes (creado_en) |
| 14 | Exportaciones | pdf · csv |

---

## 11. BITÁCORA ✓ (categoría Actividad ya implementada)

**Fuentes:** `actividad_usuario au JOIN seguridad.usuarios u` · filtros YA en SQL.

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Resumen ✓ · Actividad ✓ · Por módulo · Serie diaria |
| 2 | Dimensiones | usuario(u.nombre) ✓ · acción(au.tipo_accion mapa Creación/Edición/Eliminación/Login/Logout) ✓ · módulo(au.modulo) ✓ · día/semana/mes(au.created_at) ✓ |
| 3 | Filtros | triple AJAX (usuario_id, tipo_accion, modulo_filter) ✓ · fechas ✓ |
| 4 | Agrupaciones | usuario · acción · módulo · día · semana · mes · todos ✓ |
| 5 | Métricas | COUNT actividades ✓ · usuarios distintos `COUNT(DISTINCT au.usuario_id)` · módulos tocados DISTINCT |
| 6 | KPIs | total · creaciones · ediciones · eliminaciones · modulos(dict) · top_usuarios(dict) *(existentes)* |
| 7 | Rankings | usuarios más activos ✓ · módulos más movidos ✓ |
| 8 | Visualizaciones | tabla ✓ · **línea diaria ★** ✓ · barras_h módulos ✓ · torta acciones (5 valores) ✓ · ranking ✓ |
| 9 | Comparaciones | período anterior ✓ |
| 10 | Columnas tabla | usuario · acción · módulo · detalle · fecha *(actuales)* |
| 11 | Ordenamientos | fecha · usuario · módulo · conteo |
| 12 | Top N | usuarios más activos · módulos más movidos · días de mayor actividad |
| 13 | Temporal | ★ día/semana/mes — el mejor caso de serie temporal del sistema |
| 14 | Exportaciones | pdf · csv ✓ |

Columnas adicionales disponibles NO recomendadas como dimensiones (bajo valor analítico): `pagina`, `ip_address` — quedan fuera del catálogo a propósito.

---

## 12. RESUMEN 🐛

**Fuentes:** llamada transversal a los 10 `consultar()`. 🐛 Bug latente conocido (auth Usuario objeto vs dict) — **inhabilitado para el constructor hasta arreglarse** (no alcanzable desde rutas hoy).

| # | Capacidad | Definición |
|---|---|---|
| 1 | Categorías | Panorama (única; snapshot transversal) |
| 2 | Dimensiones | módulo (fija, no elegible) |
| 3 | Filtros | ninguno (snapshot global) |
| 4 | Agrupaciones | no aplica |
| 5 | Métricas | total registros · activos · inactivos por módulo (definición "activo" distinta por módulo, ya codificada) |
| 6 | KPIs | modulos · total_registros · total_activos · total_inactivos *(existentes, con bug latente)* |
| 7 | Rankings | módulos por volumen |
| 8 | Visualizaciones | tabla ✓ · kpi_cards ✓ · barras_v registros por módulo (≤12 categorías) |
| 9 | Comparaciones | período anterior (snapshot vs snapshot — requiere guardar snapshots; diferido) |
| 10 | Columnas tabla | módulo · total · activos · inactivos *(actuales)* |
| 11 | Ordenamientos | total · activos · módulo |
| 12 | Top N | módulos más grandes |
| 13 | Temporal | ✗ (snapshot puntual) |
| 14 | Exportaciones | pdf |

---

## MATRIZ RESUMEN DE CAPACIDADES

| Módulo | Categorías nuevas | Mejor dimensión | Métrica estrella | Serie temporal | Ranking natural | Estado |
|---|---|---|---|---|---|---|
| contratos | Cartera✓ · Ingresos✓ · Vencimientos · Distribución | patrocinador/nivel | monto_total SUMA | ✓ pagos | top patrocinadores | **Piloto vivo** |
| bitacora | Actividad✓ · Por módulo · Serie diaria | día/usuario/acción | actividades COUNT | ✓★ diaria | usuarios activos | **Piloto vivo** |
| balance | Cobranza · Por nivel | tipo_pago/patrocinador | monto SUMA | ✓★ mensual | patrocinadores | Listo (F0 hecho) |
| guiones | Producción · Evolución | encargado/estado | duración SUMA | ✓ creación | encargados | Pendiente N+1 fechas |
| inventario | Valorización · Asignaciones · Antigüedad | tipo/estado | costo SUMA | ✓ compras | tipos valiosos | Listo |
| premios | Entregas · Stock | patrocinador/estado | pendientes/tasa | ✓ entregas | patrocinadores | Listo |
| mantenimiento | Taller · Frecuencia · Historial | recurso/estado | dias_en_taller AVG | ✓ ingresos | recursos críticos | 🔒 N+1 primero |
| usuarios | Planta · Actividad · Dormidas | rol/depto | % activos | ✓ altas | más activos | Listo |
| reels | Contenido · Por patrocinador | patrocinador | duración SUMA | ✓ creación | más largos | Pendiente N+1 videos |
| tareas | Carga · Estados | usuario/estado | % completadas | ⚠️ solo asignaciones | carga por usuario | Listo |
| patrocinadores | Cartera cruzada · Encargado | estado/encargado | cartera (cruce) | ✗ directa | cartera | Listo |
| resumen | Panorama | módulo (fija) | totales | ✗ | módulos | 🐛 bug latente |

---

## EXCLUSIONES INTENCIONALES (y su motivo)

- **Torta/línea en tareas**: sin fecha de cierre no hay evolución real de estados; la torta de estados sí es válida.
- **Torta de patrocinadores por monto**: dominancia de 1-2 empresas haría gráfico ilegible → barras/ranking.
- **Promedios de montos formateados como texto ('$12,000')**: toda métrica monetaria se agrega sobre la columna DECIMAL cruda, jamás sobre strings.
- **Dimensiones pagina/ip_address en bitácora**: bajo valor analítico, alto riesgo de cardinalidad inútil.
- **Métricas de tiempo de resolución en tareas / fecha alta-baja en patrocinadores**: las columnas no existen en la BD — crearlas sería inventar esquema (prohibido).
