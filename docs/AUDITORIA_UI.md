# Auditoría UI/UX — Sistema Itinerario

**Fecha:** 23/08/2026 · **Método:** barrido de solo lectura sobre todas las vistas y CSS global, con criterios de craft visual (jerarquía, densidad, consistencia, estados, feedback, móvil, accesibilidad).
**Alcance excluido:** `app/view/en_vivo/vivo.html` (intocable por regla del proyecto).

## Resumen

| Severidad | Cantidad |
|---|---|
| Crítico | 5 |
| Alto | 22 |
| Medio | 24 |
| Bajo | 8 |

**Ya resuelto en esta sesión (no aparece como pendiente):** bug de notificaciones que no se marcaban leídas (POST cancelado por navegación inmediata), panel desalineado por Popper y rediseño completo de campana/menú (`notificaciones.js`, `head.html`, bloque NOTIFICACIONES de `estilo.css`).

---

## Hallazgos sistémicos (arreglan varios módulos a la vez)

Estos se repiten en casi todos los módulos; atacarlos una vez vale por diez parches:

### S1 · [CRÍTICO] Selector global de botones y guerra de `!important`
`app/static/css/estilo.css:416` — `button:not(.sidebar-toggle):not(.btn-close):not(.btn)` pinta TODOS los botones sin clase Bootstrap de azul con `padding:10px 20px`. Es la raíz de los ~15 bloques `!important` defensivos en `.aurora-*`, `.captcha-refresh` y `.action-dropdown`.
→ Eliminar el selector global y estilizar clases explícitas.

### S2 · [ALTO] Botones de acción de tabla con ~26px de alto
`estilo.css:439-465` (`.btn-action`) — padding `5px 10px` ≈ 26-28px de alto. Aparece en tareas, seguimiento, usuarios, roles, inventario, mantenimiento, contratos, patrocinadores, premios, guion, balance, reportes. Uso móvil frecuente, muy debajo del objetivo táctil de 44px.
→ `min-width/min-height: 40px` (+44px en `@media (pointer: coarse)`).

### S3 · [ALTO] Errores de red silenciosos
Sin `.catch` con feedback: `GestionTarea.js` (crear/editar/asignar/eliminar), `GestionPremio.js` (todos los fetch), `refreshCaptchaTile()` (`captcha_baseball.html:42`). Si la red falla, la UI queda muda o el botón "muere".
→ Patrón único: `.catch(() => Swal.fire('Error', 'Error de conexión', 'error'))` (ya existe en `GestionUsuario.js:310-313`).

### S4 · [ALTO] Doble envío sin bloqueo
Submits AJAX sin deshabilitar el botón durante el fetch: `GestionInventario.js` (4 submits), guion (crear/editar/replicar/elemento vía Swal→submit nativo), "Completar" tarea (`tareas_usuario_vista.html:38`). Un doble tap en móvil duplica registros.
→ `btn.disabled = true` antes del fetch, restaurar en `finally`.

### S5 · [ALTO] Sin foco visible para teclado
Solo la campana define `:focus-visible`. `.btn-login`, `.btn-action`, `.captcha-refresh`, FAB/send/suggestions de Aurora y links del sidebar son invisibles para teclado; `.aurora-chat-input:focus { outline:none }` (`estilo.css:887`) empeora.
→ Regla global `:focus-visible { outline: 2px solid #2563eb; outline-offset: 2px }`.

### S6 · [ALTO] Sidebar no marca la sección actual
`components/menu.html` — ningún ítem recibe clase activa; el usuario pierde orientación.
→ Marcar ruta actual comparando `request.endpoint` (Jinja) o `location.pathname` (JS), reutilizando el estilo de hover (`border-left` blanco).

### S7 · [MEDIO] Confirmaciones dobles para eliminar
Inventario (página GET + Swal encadenada), contratos y patrocinadores (modal Bootstrap + Swal); premio elimina con una sola. Editar premio pide confirmación previa antes de abrir el modal; reels también ("¿Editar reel?").
→ Una sola confirmación Swal con el nombre del registro, unificado en los 3 módulos.

### S8 · [MEDIO] `location.reload()` tras acciones destruye estado
`GestionTarea.js:19,151` y `GestionReportes.js:739`: pierde búsqueda/página/scroll del DataTable y filtros cargados del reporte.
→ `tabla.ajax.reload(null,false)` / refrescar solo la sección afectada.

### S9 · [MEDIO] Tablas AJAX sin estados de carga
`GestionTarea.js`, `GestionRol.js`, `GestionTareaSeguimiento.js`, `GestionContrato.js`, `GestionPatrocinador.js` sin `processing: true` ni lenguaje propio: mientras carga parece "no hay datos" y si el endpoint falla queda en blanco en silencio.
→ Copiar el bloque `language` + `processing` que ya tiene `GestionUsuario.js`.

### S10 · [MEDIO] Contraste WCAG fallido en KPIs/badges
`text-warning`/`text-info` sobre blanco (~1.6–1.9:1): balance, bitácora, premio, guion (`bg-info` texto blanco), en_vivo index. También blanco sobre `bg-warning`/`#ffc107`.
→ Tonos oscuros (`text-dark` junto a warning/info, o fondos `*-subtle` con texto oscuro).

### S11 · [BAJO] Labels sin `for` / iconos sin `aria-label`
Labels sin asociar: reels (agregar/editar + grupos dinámicos), balance (6 modales), premio (modal), login/forgot captcha, guion agregar_elementos. Botones solo-icono con solo `title` (que además no se inicializa como tooltip ni existe en táctil): inventario, mantenimiento, contratos, patrocinadores, premio.
→ Emparejar `for`/`id`; añadir `aria-label="Editar/Eliminar…"` a cada botón de fila.

---

## Por módulo

### Autenticación y layout base
- **[ALTO]** `reset_password.html:100-104` — validación en `click` con `alert()` nativo: enviar con Enter la salta por completo. → validar en `submit` con Swal.
- **[ALTO]** `login.css:262` + `estilo.css:987` — ojo de contraseña (~13px) y captcha-refresh (30px) sin área táctil. → padding transparente hasta 44px.
- **[MEDIO]** `components/menu.html:38-42` — Bitácora y Reportes anidados dentro del `if rol.view`: quien tiene `bitacora.view`/`reportes.view` pero no `rol.view` pierde esos módulos del menú.
- **[MEDIO]** `dashboard/index.html` — 10 bloques de estilos inline conviviendo con `dashboard.css`; KPI "Mis Tareas" es `<a>` clicable entre 3 `<div>` idénticos (affordance ambigua).
- **[MEDIO]** `components/chatbot.html:25` — mensaje inicial muestra literalmente `**Aurora**` (no hay parser markdown).
- **[MEDIO]** `error/error.html:95` — "Reintentar" lleva siempre a login (expulsa sesión activa en un 500); código de error casi ilegible (opacidad .15 sobre navy).
- **[BAJO]** ternario no-op `category if category != 'warning' else 'warning'` copiado en 4 plantillas; toggle móvil nunca actualiza `aria-expanded`.

### Guion + EN VIVO (index/log)
- **[CRÍTICO]** `guion/agregar_elementos.html:119` — tabla de 6 columnas sin `.table-responsive`: desborda el card en móvil. → envolver.
- **[ALTO]** `agregar_elementos.html:77` y `editar_elemento.html:89` — `oninput` borra la coma pero la ayuda exige "min,seg" (ej: 2,30): imposible teclear lo documentado. Mismo bug en reels (`agregar_reel.html:20`, `editar_reel.html:20`) — ahí es **[CRÍTICO]** porque deja sin segundos. → filtro `/[^0-9,]/g` como ya usa `crear.html:25`.
- **[ALTO]** `en_vivo/index.html:93` — "Finalizar" destructivo como enlace GET con `confirm()` nativo, fuera del patrón SweetAlert2/CSRF del sistema.
- **[ALTO]** `en_vivo/index.html:98-101` — botón "Iniciar" deshabilitado cuya explicación solo se ve en desktop (`d-none d-sm-inline`): en móvil no hay razón visible del bloqueo.
- **[ALTO]** `GestionGuion.js:94-96,347` — submit tras Swal sin deshabilitar botones (ver S4).
- **[MEDIO]** `guion/editar.html`, `publicar.html` — segunda generación de UI (bordes default, headers plenos `bg-warning`/`bg-success`, emojis) frente al patrón border-0/shadow-sm/header blanco; `editar.html` sin contenedor estándar.
- **[MEDIO]** `guion/replicar.html` — calendario de días `<div>` inoperables por teclado; flechas `</>` sin `aria-label`.
- **[BAJO]** copy "al menos 2 caracteres" vs `minlength="3"` real (`GestionGuion.js:66`).
- **[BAJO]** `en_vivo/log.html` + `en_vivo_controller.py:169` — bitácora del show sin paginación ni LIMIT (una fila por avance = tabla infinita en móvil).

### Tareas + Usuarios + Roles
- **[CRÍTICO]** `GestionTarea.js:21,146-152` — fallos de red silenciosos (ver S3).
- **[ALTO]** `GestionTarea.js:42,50-57` — columna Instrucción inyectada cruda sin escapar + `onclick` inline frágil (inyección + filas rotas con `"` en el nombre). → `escHtml` + delegación como `GestionUsuario.js:80-86`.
- **[ALTO]** `gestion_tarea/dashboard.html:4` — header sin `flex-column flex-md-row`: 4 botones desbordan a 375px (usuario/dashboard sí usa el patrón correcto).
- **[ALTO]** `gestion_tarea/dashboard.html:167` — asignar empleados con `<select multiple>` + hint "mantén Ctrl/Cmd": casi inoperable en móvil para una acción core. → checkboxes agrupados por departamento o chips.
- **[MEDIO]** semáforo de estados contradictorio entre "Mis Tareas" y "Seguimiento" (En Progreso amarillo vs azul; Pendiente gris vs amarillo) + warning sobre warning-subtle ilegible.
- **[MEDIO]** ojo de contraseña `<i onclick>` no enfocable, sin aria (`usuario/dashboard.html:126,134`, `cambiar_password.html`).
- **[BAJO]** dos botones primarios verdes idénticos compitiendo ("Nueva Tarea"/"Asignar Tarea"); radio inline puntual y escala h5/h6 inconsistente en modales.

### Inventario + Mantenimiento
- **[ALTO]** tooltips nunca inicializados para acciones solo-icono + sin `aria-label` (`GestionInventario.js:75-78`, `mantenimiento/dashboard.html:106-115`).
- **[ALTO]** `inventario/eliminar.html:46` — entidad HTML `&oacute;` dentro del texto plano de Swal: el usuario ve literalmente "acci&oacute;n" (también `ver.html:102`, `gestion_asignaciones.html:138`).
- **[MEDIO]** doble UX de borrado para la misma entidad (ver S7).
- **[MEDIO]** paleta de diálogos incoherente (verdes #198754 vs #28a745, rojos translúcidos, azul #3085d6 ajeno al navy).
- **[MEDIO]** `mantenimiento/dashboard.html:21-47` — grid KPI roto (`col-sm-3+4+3` suma 10/12); botón `btn-outline-warning` ilegible (1.9:1).
- **[MEDIO]** timeline de detalle con emojis 📥📝🔧⛔🏁 en un módulo FontAwesome; contenedores inconsistentes (`detalle.html:5`, `ingresar.html:3`).
- **[BAJO]** labels de formularios con estilo distinto a los de modales; modales sin `aria-labelledby`; "Devolver" duplicado con datos/estilos distintos en dos vistas.

### Contratos + Patrocinadores + Premios
- **[ALTO]** `premio/dashboard.html:112` — estado vacío `d-none` fijo: sin premios pendientes el área queda totalmente en blanco.
- **[ALTO]** `GestionPremio.js` — ningún fetch tiene `.catch` (ver S3).
- **[MEDIO]** tarjeta de premio con `cursor:pointer` y hover lift sin handler de clic (affordance falsa, peor en móvil sin hover).
- **[MEDIO]** tablas de 7-8 columnas en scroll horizontal móvil con las acciones fuera del viewport → extensión Responsive de DataTables u ocultar secundarias en `d-none d-md-table-cell`.
- **[MEDIO]** buscador de catálogo con placeholder como única etiqueta y grid vacío sin mensaje "sin resultados".

### Balance + Reels + Reportes + Bitácora
- **[ALTO]** `balance/dashboard.html:94-96` — chips "Todos/Pendientes/Pagados" marcan `active` pero **no existe** `.filter-chip.active` en el CSS: el filtro aplicado es invisible; grid puede quedar vacío sin mensaje.
- **[ALTO]** `GestionReportes.js:739` — al generar PDF hace `location.reload()`: destruye módulo seleccionado y filtros AJAX (ver S8).
- **[ALTO]** `reportes/dashboard.html:48-59` — `.filter-panel` con `max-height:600px` fijo: en móvil los módulos con muchos filtros quedan recortados e inaccesibles. → `max-height:none` cuando `.open`.
- **[MEDIO]** `reportes/dashboard.html:136-143` — `modulo-card` clickeables sin `tabindex`/`role`/Enter: inutilizables por teclado.
- **[MEDIO]** reels: formato de duración inconsistente ("2.50 min" en listado vs "2m 30s" en fichas); confirmación previa absurda para abrir edición.
- **[MEDIO]** `balance/dashboard.html:3-4` — Bootstrap Icons por CDN solo en esta página (dos lenguajes de íconos conviviendo con FontAwesome).
- **[BAJO]** atributo inválido `...` dentro de un input de balance (`dashboard.html:279`); headers de modal mezclando `bg-dark`/`bg-warning`; grupo de video de reels con columnas fijas que se aplastan a ~60px en móvil.

---

## Orden de ataque sugerido

1. **S1** (selector global de botones): desbloquea limpiar toda la guerra de `!important`.
2. **S2** (`.btn-action` táctil) + **S5** (focus visible global): dos reglas CSS, impacto en TODO el sistema.
3. **Coma en min,seg** (guion/reels): bug funcional que impide capturar datos documentados.
4. **S3+S4** (catch + bloqueo de doble envío): patrón único aplicado a los 4 JS afectados.
5. **S6** (sidebar activo): orientación instantánea, cambio pequeño en `menu.html`.
6. Resto por módulo según prioridad operativa (tareas y EN VIVO index son los de uso diario).

*Informe generado solo lectura; nada fue modificado fuera de las notificaciones.*
