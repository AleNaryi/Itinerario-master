# MÓDULO REPORTES — Brief técnico completo

> **Documento de contexto para asistentes IA** (ChatGPT u otros). Describe TODO lo que el sistema de reportes usa y recibe: archivos, rutas HTTP, fuentes de datos reales (modelo → tablas SQL), filtros, KPIs, esquema de las tablas y las reglas para extender cualquier reporte. Verificado contra el código línea a línea (referencias `archivo:línea`). Última actualización: 2026-08-25.

---

## 1. Qué es

Sistema de reportes del Estadio Antonio Herrera Gutiérrez (Flask 3 + PyMySQL crudo **sin ORM** + reportlab para PDF). Dashboard progresivo tipo "efecto bitácora":

```
Usuario elige MÓDULO
   → GET /reportes/filtros/<modulo>      (backend devuelve filtros contextuales JSON)
   → panel pinta filtros (selects AJAX progresivos, rangos min/max, fechas)
   → POST /reportes/preview              (tabla + tarjetas KPI + distribución)
   → POST /reportes/generar              (PDF: KPIs + distribuciones + tabla + análisis opcional)
```

12 módulos reportables: `guiones`, `inventario`, `premios`, `contratos`, `balance`, `tareas`, `patrocinadores`, `usuarios`, `mantenimiento`, `reels`, `bitacora`, `resumen`.

---

## 2. Mapa de archivos

| Archivo | Líneas | Rol |
|---|---|---|
| `app/controller/reportes_controller.py` | 682 | Rutas `/reportes/*`; funciones `_filtros_<modulo>(params)` (opciones de filtros); `_obtener_datos(modulo, filtros)` orquestador; whitelist de opciones PDF en `generar()` |
| `app/helpers/reportes_data.py` | 749 | Las 12 funciones `_datos_<modulo>(filtros, fi, ff)` → devuelven `(datos, kpis)`; dict global `OBTENEDORES` (L734); `_filtrar_por_fecha()`, `_sanitizar_para_reporte()` |
| `app/helpers/reportes_utils.py` | 110 | Utilidades compartidas (parseo de fechas, ordenamiento) |
| `app/static/js/GestionReportes.js` | 802 | Frontend completo: `MODULE_CONFIG.<modulo>` (filtros/columnas/kpiCards), `cargarOpcionesAjax`, render de preview |
| `app/view/reportes/dashboard.html` | 257 | Grid de módulos + panel dinámico de filtros + tabla preview |
| `app/helpers/generators/base_report.py` | ~400 | Clase base PDF (ver §7) |
| `app/helpers/generators/<modulo>_report.py` | ×13 | Un generador por módulo + `resumen_report.py` |
| `tests/test_reportes_filtros.py` · `_pdf.py` · `_smoke.py` | | Suite: filtros por módulo, análisis PDF, estabilidad preview (`venv/bin/pytest -q`) |

Contexto interno complementario: `.opencode/reportes-context.md` (estado histórico y bugs corregidos).

---

## 3. Contratos HTTP (definidos en `reportes_controller.py`)

| Ruta | Método | Entrada | Salida |
|---|---|---|---|
| `/reportes/filtros/<modulo>` | GET | query params (ej. `tipo=1` para filtro progresivo) | JSON: `{ selects: {campo: [options]}, hints: {campo_min: 0, campo_max: …} }` vía `_filtros_<modulo>` |
| `/reportes/filtros-bitacora` | GET | — | JSON triple progresiva (usuarios, acciones, módulos) |
| `/reportes/preview` | POST | form: `modulo` + valores de filtros + `fecha_inicio`/`fecha_fin` | JSON `{ datos: [...], kpis: {...}, columnas }` — datos pasan por `_serializar_datos()` (fechas/datetime → string) |
| `/reportes/generar` | POST | igual que preview + opciones `resumen=1`, `top_n=N` (1-20), `comparar=1` | PDF binario (guardado en `static/reportes/YYYY/MM/` + registro en `seguridad.reportes_generados`) |

Permisos: todas las rutas bajo `@verificar_acceso(REPORTES)` (blueprint). CSRF activo en POSTs (Flask-WTF).

**Reglas server-side:** las opciones del PDF se parsean con **whitelist** en `generar()` (nunca se confía en el form); los valores de filtros se usan como strings comparados en Python o parametrizados en SQL — nunca interpolados.

---

## 4. Motor de datos — patrón general (`reportes_data.py`)

```python
# L734: dispatch
OBTENEDORES = {'guiones': _datos_guiones, 'inventario': _datos_inventario, ...}

def _datos_<modulo>(filtros: dict, fi, ff) -> tuple[list[dict], dict]:
    # 1. Carga inicial desde el MODELO (no SQL directo): model.consultar()
    # 2. Filtra EN PYTHON por cada filtro del request
    # 3. _filtrar_por_fecha(datos, 'campo_fecha', fi, ff)
    # 4. Calcula KPIs (contadores, sumas, promedios, distribuciones dict)
    # 5. _sanitizar_para_reporte(modulo, datos)  ← whitelist de claves por módulo
    return datos, kpis
```

**Patrón dominante: carga completa en memoria + filtrado/agregación en Python.** Solo 2 excepciones filtran en SQL: `bitacora` (el modelo acepta `usuario_id/tipo_accion/modulo/limite`) y la consulta de asignaciones de tareas (JOIN directo `tareas_asignadas JOIN seguridad.usuarios`, L462).

`fi`/`ff`: fechas por defecto según módulo (`rango_fechas_defecto`, L133). Fechas llegan como `YYYY-MM-DD` string.

---

## 5. Los 12 módulos — negocio, filtros, fuente de datos y escalabilidad

### Resumen rápido (módulo → modelo → tablas)

| Reporte | Modelo usado | Tablas SQL tocadas |
|---|---|---|
| guiones | `GuionModel` + `ElementoGuionModel` | `guiones`, `elementos_guion`, `guion_fechas` (N+1) |
| inventario | `InventarioModel` | `recursos` LEFT JOIN `tipo_recurso`, `estado_recurso` |
| premios | `PremioModel` | `premios` LEFT JOIN `patrocinadores` (×2 métodos) |
| contratos | `ContratoModel` | `contrato` LEFT JOIN `patrocinadores` |
| balance | `BalanceModel (=Pago)` | `pagos` LEFT JOIN `contrato`, `patrocinadores` (**LIMIT 500**) |
| tareas | `TareaModel` + `TareasAsignadasModel` | `tareas`, `tareas_asignadas` JOIN `seguridad.usuarios` |
| patrocinadores | `PatrocinadorModel` | `patrocinadores` |
| usuarios | `UsuarioModel` (usuario_model, esquema seguridad) | `seguridad.usuarios` |
| mantenimiento | `MantenimientoModel.consultar()` | `mantenimientos` + **N+1**: `recursos`, `seguridad.usuarios`, `historial_mantenimiento` (+usuario por fila) |
| reels | `ReelModel` | `reels` + **N+1**: `videos` (LEFT JOIN `patrocinadores` por video) |
| bitacora | `ActividadModel` | `actividad_usuario` (**LIMIT 500**, filtros en SQL) |
| resumen | los 10 modelos anteriores | todas (⚠️ bug latente conocido, ver §8) |

---

### 5.1 GUIONES
- **Negocio:** guiones de shows en vivo del estadio (entretenimiento durante el juego de béisbol). Cada guion tiene elementos pregame (por hora) y game (por inning); estados: borrador → publicado → en_vivo → finalizado. Fechas de ejecución en `guion_fechas`.
- **Filtros:** `estado` (select), `encargado` (select AJAX desde `elementos_guion.encargado`), `elementos_min`/`elementos_max` (rango de nº de elementos), `fecha_inicio`/`fecha_fin` (sobre `creado_en`).
- **Enriquecimiento por fila:** `pregame`/`game` (conteo por tipo), `tiempo_segundos` (suma `duracion_estimada`), `tiempo_total` (formateado), `fecha_ejecucion` (primera fecha de `guion_fechas` — consulta por guion).
- **KPIs:** `total`, `borradores`, `publicados`, `en_vivo`, `finalizados`, `tiempo_total`, `promedio_seg`.
- **Fuente:** `GuionModel.consultar()` = `SELECT * FROM guiones WHERE status = 1`; `ElementoGuionModel().consultar()` = 1 consulta total agrupada en dict (buena práctica ya aplicada, L180).
- **Escalabilidad:** media-alta. 2 consultas grandes; techo real = `obtener_fechas()` por guion (N+1) y agregaciones en Python. Ruta de escala: traer fechas en bloque (`WHERE guion_id IN (...)`) y mover conteo de elementos a `GROUP BY guion_id`.

### 5.2 INVENTARIO
- **Negocio:** recursos físicos del estadio (sonido, mobiliario, herramientas) con tipo, estado (Disponible/Asignado/Mantenimiento/Baja), costo y fecha de compra. Asignaciones a empleados gestionadas fuera de este reporte.
- **Filtros:** `tipo_nombre` → `estado_nombre` (selects AJAX progresivos, nombres ya resueltos por JOIN), `costo_min`/`costo_max`, fechas (sobre `fecha_compra`).
- **KPIs:** `total`, `costo_total`, `costo_promedio`, distribuciones `tipos` y `estados` (dict nombre→cantidad).
- **Fuente:** única consulta con JOINs ya resueltos en SQL (`recursos r LEFT JOIN tipo_recurso t LEFT JOIN estado_recurso e`).
- **Escalabilidad:** alta — la mejor construida. Siguiente paso natural si crece: pasar rangos de costo y fechas al WHERE SQL.

### 5.3 PREMIOS
- **Negocio:** premios/promocionales donados por patrocinadores; ciclo pendiente→entregado con cantidades parciales (`cantidad` vs `cantidad_entregada`), foto, quién entregó y cuándo.
- **Filtros:** `estado` (pendiente|entregado), `patrocinador_id` (AJAX), `cantidad_min/max`, `cantidad_entregada_min/max`, fechas (`fecha_creacion`).
- **KPIs:** `total`, `pendientes`, `entregados`, `tasa_entrega` (%), distribución `por_patrocinador`.
- **Fuente:** 2 consultas (`obtener_premios_pendientes` + `obtener_premios_entregados`), ambas con `LEFT JOIN patrocinadores` para `patrocinador_nombre`. ⚠️ `fetchall()` devuelve tuplas: siempre `list(a) + list(b)` (bug histórico ya parcheado, L276).
- **Escalabilidad:** alta (JOINs en SQL, volúmenes bajos).

### 5.4 CONTRATOS
- **Negocio:** contratos de patrocinio con niveles Bronce/Plata/Oro (`tipo` 1/2/3), estatus Borrador/Vigente/Vencido y monto_total. El dinero del patrocinio del estadio.
- **Filtros:** `tipo` → `patrocinador_id` (progresivo: al elegir tipo, recarga patrocinadores que tengan ese tipo), `estatus`, `monto_min/max`, fechas (`fecha_inicio`).
- **Enriquecimiento:** `tipo` mapeado a texto, `dias_restantes` calculado contra `date.today()`.
- **KPIs (los más ricos del sistema):** `total`, `vigentes/vencidos/borradores`, `bronce/plata/oro`, `monto_total/monto_promedio/monto_vigentes/monto_min/monto_max` (formateados `$`), `vigentes_porcentaje`, `top_patrocinadores` (top 5 por monto — alimenta `top_n` del PDF).
- **Fuente:** `contrato LEFT JOIN patrocinadores`.
- **Escalabilidad:** alta. Candidato natural a métricas nuevas: proyección mensualizada, vencimientos próximos, % cartera por nivel.

### 5.5 BALANCE (pagos)
- **Negocio:** pagos recibidos contra contratos (flujo de caja del patrocinio). Cada pago tiene tipo_pago, referencia, fecha+hora, y pertenece a un contrato→patrocinador.
- **Filtros:** `tipo_pago` (AJAX desde tabla `pagos`), `patrocinador_id` (⚠️ matchea por `id_contrato.startswith(patrocinador_id)` — aproximación frágil, L428), `monto_min/max`, fechas (`fecha_pago`).
- **KPIs:** `total_pagos`, `monto_total`, `promedio`, `monto_min/max`, distribución `tipos_pago`.
- **Fuente:** `Pago.obtener_historial_pagos(limit=500)` — `pagos LEFT JOIN contrato LEFT JOIN patrocinadores`, devuelve objetos `Pago`.
- **Escalabilidad:** ⚠️ **techo duro: LIMIT 500** — con más de 500 pagos el reporte trunca silenciosamente. Ruta: mover `fecha_inicio/fin` y `tipo_pago` al WHERE SQL y eliminar el límite. También corregir el match patrocinador (JOIN real contrato.id_patrocinador).

### 5.6 TAREAS
- **Negocio:** catálogo de tareas operativas (`tareas`) y sus asignaciones a empleados (`tareas_asignadas`, estado Pendiente/En Progreso/Completada). Multi-asignación: una tarea puede tener varias filas de asignación.
- **Filtros:** `estado`, `asignado_a` (select AJAX de usuarios → envía `usuario_id`), fechas (sobre `fecha_asignacion_tarea`).
- **Composición de filas:** cada tarea toma SU PRIMERA asignación activa (break al primer match, L479-484) → `asignado_a` (nombre resuelto en SQL), `asignado_id`, `fecha_asignacion_tarea`.
- **KPIs:** `total`, `pendientes`, `en_progreso`, `completadas`, `completadas_pct`.
- **Fuente:** `tareas` (TareaModel) + consulta directa `SELECT ta.*, u.nombre FROM tareas_asignadas ta JOIN seguridad.usuarios u ...` (único JOIN cruzado de esquemas del motor, L459-465).
- **Escalabilidad:** media. Bucle anidado T×A en Python; con volumen conviene un solo `LEFT JOIN` en SQL. Nota de diseño: el "1 asignación por tarea" oculta multi-asignaciones — un reporte más detallado podría listar TODOS los asignados o agregar por persona.

### 5.7 PATROCINADORES
- **Negocio:** empresas patrocinadoras (RIF, contacto, teléfono/email, encargado interno, estado activo/inactivo).
- **Filtros:** `tipo_contrato` (Vigente/Vencido — map de int 1/2), `estado_pat` (activo/inactivo), fechas (⚠️ la tabla NO tiene columna de fecha: el filtro existe en UI pero opera sin campo propio).
- **KPIs:** `total`, `activos`, `inactivos`, `por_tipo`.
- **Fuente:** `SELECT * FROM patrocinadores` (+WHERE estado opcional).
- **Escalabilidad:** trivial (tabla maestra pequeña). Mejora posible: cruzar contratos/pagos activos por patrocinador (valor de cartera).

### 5.8 USUARIOS
- **Negocio:** empleados del estadio con acceso al sistema (rol, departamento, activo/inactivo, último acceso).
- **Filtros:** `departamento` → `rol` (progresivo), `activo` (sí/no), fechas (`fecha_registro`).
- **KPIs:** `total`, `activos`, `inactivos`, distribuciones `roles` y `departamentos`.
- **Fuente:** `UsuarioModel.consultar()` = `SELECT * FROM usuarios ORDER BY nombre` (esquema `seguridad`).
- **Escalabilidad:** trivial. Cruce valioso futuro: actividad real (JOIN `actividad_usuario`) para detectar cuentas dormidas.

### 5.9 MANTENIMIENTO
- **Negocio:** reparaciones de recursos: ingreso→diagnóstico→(notas de historial)→reparado/baja. Estados: en_espera/en_reparacion/reparado/baja. Métrica clave: días en taller.
- **Filtros:** `estado` → `recurso_id` (progresivo AJAX), `dias_min/max` (rango calculado), fechas (`fecha_ingreso`).
- **Enriquecimiento:** `dias_en_taller` = `fecha_salida − fecha_ingreso` (o hoy si sigue en proceso).
- **KPIs:** `total`, `en_espera`, `en_reparacion`, `reparados`, `dados_baja`, `promedio_dias`, `top_recursos` (top 5 frecuencia).
- **Fuente:** ⚠️ **peor N+1 del sistema** (`MantenimientoModel.consultar`, mantenimiento_model.py:162): por cada mantenimiento ejecuta 3-4 consultas extra (recurso, usuario, historial, usuario-de-cada-nota). 
- **Escalabilidad:** baja tal cual — con cientos de mantenimientos e historiales largos, el reporte dispara miles de queries. Ruta concreta: 3 consultas planas (`mantenimientos LEFT JOIN recursos`, `usuarios`, `historial_mantenimiento` en bloque) y agrupar en Python por `mantenimiento_id`. Es el primer candidato a refactor si el reporte se vuelve lento.

### 5.10 REELS
- **Negocio:** videos resumen (reels) para redes sociales; cada reel agrupa clips con orden, duración por clip y patrocinador asociado. `duracion_total` se guarda en MINUTOS float.
- **Filtros:** `patrocinador_id` (AJAX), `duracion_min/max` (**en segundos**; el código multiplica minutos×60, L619), fechas (`creado_en`).
- **Enriquecimiento:** `videos_count`, `duracion` formateada ("3m 30s"), `videos_detalle` (texto multilínea "1. nombre (dur)").
- **KPIs:** `total`, `total_videos`, `duracion_total` (min), `duracion_promedio`.
- **Fuente:** `ReelModel.consultar()` trae `reels` (con `id_patrocinador AS patrocinado`) y hace **N+1**: `_obtener_videos(reel_id)` por cada reel (`videos LEFT JOIN patrocinadores`).
- **Escalabilidad:** media. Ruta: una sola consulta `SELECT * FROM videos WHERE reel_id IN (...)` y agrupar en Python (patrón ya aplicado en guiones-elementos, copiar esa idea).

### 5.11 BITÁCORA
- **Negocio:** registro de auditoría de todo el sistema (quién hizo qué en qué módulo, cuándo, desde qué IP). Tipos: create/update/delete/login/logout.
- **Filtros:** triple progresiva AJAX `usuario_id` → `tipo_accion` → `modulo_filter` + fechas (`created_at`). **Único módulo que filtra en SQL** (el modelo recibe los filtros).
- **KPIs:** `total`, `creaciones`, `ediciones`, `eliminaciones`, `modulos` (dict), `top_usuarios` (top 5).
- **Fuente:** `actividad_usuario` con `limite=500` + filtros en WHERE.
- **Escalabilidad:** buena por diseño SQL; techo = LIMIT 500 y ausencia de índices compuestos `(usuario_id, created_at)` si crece. Candidato a histogramas por día/semana (GROUP BY DATE).

### 5.12 RESUMEN (transversal)
- **Negocio:** vista ejecutiva: totales/activos/inactivos de los 9 módulos principales en una tabla.
- **Fuente:** llama a los 10 `consultar()` de golpe (10 consultas). ⚠️ **Bug latente conocido** (`ponytail:` en L746): `auth_model.UsuarioModel` devuelve objetos (no dicts) → revienta con AttributeError; NO es alcanzable desde las rutas actuales. No usar como base sin arreglar antes.

---

## 6. Esquema SQL de las tablas involucradas

Esquema negocio `estadio_db` (fuente: `estadio_db.sql`; claves foráneas/índices omitidos por brevedad):

```sql
-- GUIONES
guiones(id, nombre varchar200, estado varchar20, inicio_show datetime, creado_en,
        modificado_en, tiempo_inning int, grupo_id varchar36, status tinyint)
elementos_guion(id, guion_id, fecha_id, tipo varchar20, hora time, inning int,
        medio_inning varchar10, contenido text, duracion_estimada int /*segundos*/,
        encargado varchar100, orden int, creado_en, estado varchar20, inicio_curso datetime)
guion_fechas(id, guion_id, fecha date)

-- INVENTARIO
recursos(id, nombre varchar150, descripcion text, tipo_id, estado_id, fecha_compra date,
         costo decimal(10,2), eliminado tinyint, creado_en, modificado_en)
tipo_recurso(id, nombre varchar50, descripcion)
estado_recurso(id, nombre varchar30, descripcion)
estado_asignacion(id, nombre varchar30, descripcion)
asignaciones_recursos(id, recurso_id, usuario_id, fecha_asignacion datetime,
         fecha_devolucion_esperada date, fecha_devolucion_real datetime,
         estado_asignacion_id, notas text)

-- PATROCINIO Y DINERO
patrocinadores(id_patrocinador, nombre_empresa varchar100, rif varchar20,
         tipo_contrato int, nombre_contacto text, telefono varchar20,
         email varchar100, estado int, encargado_id)
contrato(id_contrato, id_patrocinador, fecha_inicio date, fecha_fin date,
         estado varchar100, estatus varchar100, tipo varchar50 /*'1'=Bronce,'2'=Plata,'3'=Oro*/,
         monto_total decimal(12,2))
pagos(id_pago, id_contrato, monto decimal(12,2), tipo_pago varchar20,
         referencia varchar100, fecha_pago date, hora_pago time,
         registrado_por int, Descripcion text, fecha_registro datetime,
         estado tinyint /*0=activo, 1=eliminado soft*/)

-- PREMIOS
premios(id, id_patrocinador, nombre varchar100, descripcion text,
         estado varchar20 /*pendiente|entregado*/, fecha_creacion date,
         fecha_entrega datetime, entregado_por int, hora_creacion time,
         foto varchar200, cantidad int, cantidad_entregada int,
         estatus tinyint /*0=activo, 1=eliminado soft*/)

-- TAREAS
tareas(id_tarea, Nombre_Tarea varchar255, Instruccion varchar255,
         id_usuario_creador, Estatus tinyint)
tareas_asignadas(id_asignacion, id_tarea, id_usuario, Estado varchar50
         /*Pendiente|En Progreso|Completada*/, fecha_asignacion_tarea datetime, Estatus tinyint)

-- MANTENIMIENTO
mantenimientos(id, recurso_id, usuario_id, estado varchar20
         /*en_espera|en_reparacion|reparado|baja*/, fecha_ingreso date,
         fecha_salida date, diagnostico text, observaciones text, creado_en datetime)
historial_mantenimiento(id, mantenimiento_id, usuario_id, accion varchar50,
         descripcion text, creado_en datetime)

-- REELS
reels(id, nombre varchar100, id_patrocinador, duracion_total float /*MINUTOS*/,
         creado_en, modificado_en)
videos(id, nombre varchar200, duracion_segundos int, orden int, reel_id, id_patrocinador)
```

Esquema `seguridad` (fuente: `seguridad.sql`):

```sql
usuarios(id, nombre varchar100, email varchar100, password_hash, cedula varchar20,
         rol varchar20 /*Superadmin|Administrador|Usuario*/, departamento varchar50,
         telefono, activo tinyint, fecha_registro datetime, ultimo_acceso datetime)

actividad_usuario(id, sesion_id, usuario_id, tipo_accion varchar30
         /*create|update|delete|login|logout*/, modulo varchar50, accion text,
         detalle longtext JSON, pagina varchar200, ip_address varchar45,
         created_at datetime)

reportes_generados(...)  -- registro de cada PDF emitido (save() escribe aquí)
```

**Convenciones de datos a respetar:** soft-delete con flags heterogéneos (`status=1` guiones, `eliminado=0` recursos, `estatus=0` premios, `estado=0` pagos) — toda consulta nueva debe filtrarlo. Claves con mayúsculas heredadas de PHP (`Nombre_Tarea`, `Estatus`, `Descripcion`) conviven con minúsculas.

---

## 7. Generación PDF — `BaseReportGenerator`

API disponible a todo generador (`helpers/generators/base_report.py`):

| Método | Uso |
|---|---|
| `MODULO / TITULO / COLUMNAS` | atributos de clase; COLUMNAS = `[(clave, título, ancho), ...]` |
| `generate(datos, filtros=None, kpis=None, opciones=None)` | ensambla el story completo; sobreescribible |
| `_build_rows(datos)` | filas de la tabla (override por módulo si hay formato) |
| `_seccion_kpis(kpis)` | grid de tarjetas KPI (auto: excluye dicts) |
| `_seccion_distribucion(titulo, items, color)` | barras horizontales desde un dict |
| `_secciones_analisis(kpis, opciones)` | inserta resumen/top/comparativa según opciones |
| `_resumen_ejecutivo(kpis)` | párrafo factual SOLO desde KPIs (sin inventar) |
| `_top_destacados(kpis, n)` | Top N desde la PRIMERA distribución dict de los kpis |
| `_comparativa_periodos(kpis, kpis_previos)` | Actual/Anterior/Variación% re-ejecutando la consulta con ventana desplazada |
| `save(pdf_bytes, usuario_id, filtros)` | guarda en `static/reportes/YYYY/MM/` + registra en `seguridad.reportes_generados` |

**Opciones del PDF** (checkboxes "Análisis del PDF" en la UI): `resumen=1`, `top_n=1..20`, `comparar=1`. Parseadas con whitelist en `generar()` (controller L571+).

Generadores vivos: `balance_report, bitacora_report, contratos_report, guiones_report, inventario_report, mantenimiento_report, patrocinadores_report, premios_report, reels_report, resumen_report, tareas_report, usuarios_report`.

---

## 8. Reglas inquebrantables para extender (leer ANTES de proponer código)

1. **Sin ORM.** Todo es PyMySQL crudo + DictCursor (filas = dicts). Queries parametrizadas `%s`, nunca f-strings con input de usuario.
2. **Filtros nuevos = 4 puntos sincronizados:** backend `_filtros_<modulo>` (hint/opciones) + backend `_datos_<modulo>` (aplicar el filtro) + frontend `MODULE_CONFIG.<modulo>.filters` + `cargarOpcionesAjax` si es AJAX. Si falta uno, el filtro aparece pero no filtra.
3. **Progresividad:** `progressive: ['destino']` va en el filtro ORIGEN; `dependsOn: ['origen']` en el DESTINO. Primer `<option>` siempre `value=""` label "Todos...".
4. **Claves que deben coincidir:** `kpis` del backend ↔ `kpiCards[].key` del frontend ↔ claves usadas por el generador PDF. Columnas del preview ↔ claves de las filas que devuelve `_datos_*`.
5. **Sanitización:** `_sanitizar_para_reporte(modulo, datos)` usa whitelist por módulo — si agregas una columna nueva a los datos, agrégalas ahí o desaparecerá del PDF.
6. **Tests:** correr contra BDs clonadas `*_test` (`venv/bin/pytest -q`, hoy 71 passed). Filtros nuevos merecen caso en `test_reportes_filtros.py`.
7. **UI y comentarios en español.**
8. **Escalabilidad primero:** si el dataset puede superar ~1-2k filas o vas a añadir N+1, empuja filtros/agregación a SQL (WHERE/GROUP BY) en vez de repetir el patrón en-memoria. Los techos actuales están documentados por módulo en §5.
9. **No tocar el bug latente de `resumen`** sin decidir su arreglo aparte (objeto vs dict de Usuario).

### Receta rápida (nuevo KPI en un reporte existente)
```text
1. reportes_data.py::_datos_X     → calcular kpi + incluirlo en el dict kpis
2. GestionReportes.js MODULE_CONFIG.X.kpiCards → { key, label, color }
3. <X>_report.py                  → _seccion_distribucion('...', kpis['mi_dict']) si aplica
4. test_reportes_filtros.py       → assert del kpi con fixture de datos
```

---

## 9. Stack y entorno

- Python 3 + Flask 3, PyMySQL crudo (DictCursor, autocommit ON), Flask-Login + permisos (`REPORTES` en `permission_map.py`), reportlab para PDF.
- Dos BD MySQL: `estadio_db` (negocio) y `seguridad` (usuarios/bitácora/reportes_generados). Consultas cruzadas calificando esquema (`seguridad.usuarios`).
- Dev: `venv/bin/python run.py` → :5001. Tests: `venv/bin/pytest -q` (clona esquemas a `*_test`).
- Docs hermanas: `docs/ARQUITECTURA_INVENTARIO.md`, `docs/GUION_Y_ENVIVO_GUIA.md`, `.opencode/reportes-context.md`.
