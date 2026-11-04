# Checklist de mejoras — Itinerario

Plan priorizado para atacar las deudas del proyecto. Marcar `[x]` al completar.
Referencias verificadas en código; si algo cambió, actualizar esta lista.

## ✅ Fase 1 · Seguridad (COMPLETA)
- [x] SECRET_KEY sin fallback — falla al arrancar si falta (`app/__init__.py`)
- [x] CORS de sockets same-origin + `SOCKET_ALLOWED_ORIGINS` opcional
- [x] Handshake SocketIO autenticado contra sesión Flask-Login
- [x] Validación anti open-redirect de `next` en login (`auth_controller.py`)

## 🧪 Fase 2 · Tests (red de seguridad)
- [x] Setup: `pytest` instalado + `tests/conftest.py` (BDs `*_test` clonadas desde los `.sql`, CSRF off, email parcheado)
- [x] Tests validaciones puras (`ValidacionesMixin`) — `tests/test_validaciones.py`
- [x] Helpers reportes (`_parsear_fecha`, `_ordenar_datos`, `_filtrar_por_fecha`, `_formatear_tiempo`) — `tests/test_reportes_helpers.py`
- [x] Tests auth: login ok/fallido, CAPTCHA, sesión única, reset password, validación de `next` — `tests/test_auth.py`
- [x] Tests permisos: anon → login, sin permiso → rechazo, Superadmin → 200 — `tests/test_permisos.py`
- [ ] Tests transacciones compuestas (contrato+pagos): fallo a mitad → nada escrito
- [ ] Tests PDFs: bytes empiezan con `%PDF-` por módulo
- Correr con: `venv/bin/pytest -q` (24 tests verdes al cerrar esta fase). NUNCA contra BDs reales.

## 🔧 Fase 3 · Refactor (COMPLETA — verificado contra línea base de previews)
- [x] `_registrar_bitacora` → `app/helpers/bitacora_helper.py` (12 copias eliminadas; wrapper de 1 línea por controlador)
- [x] `reportes_controller.py` dividido (1.213 → 533 líneas):
  - helpers puros → `app/helpers/reportes_utils.py`
  - datos/KPIs por módulo + `_sanitizar_para_reporte` → `app/helpers/reportes_data.py` (dict `OBTENEDORES`)
  - el controlador conserva rutas, `_filtros_*` y constantes de UI
- [x] Errores silenciosos con log real: ~205 `except Exception` ahora usan `logger.exception(...)` (194 automáticos + prints de balance_model/inventario/filtros). Excluidos donde el silencio es legítimo (teardown, guards por-fila).
- Verificación: previews de los 11 módulos byte-a-byte idénticos antes/después (incluye preservar bugs latentes), 28 tests verdes.
- (Bugs latentes movidos a la sección 🐛 más abajo)

## 📊 Fase 4 · Módulo Reportes (COMPLETA — patrón "efecto bitácora" en los 11 módulos)
Verificado con 22 tests nuevos (`test_reportes_filtros.py`, `test_reportes_pdf.py`).

- [x] **guiones**: encargado AJAX (desde `elementos_guion`) + rango `elementos_min/max`
- [x] **premios**: progresividad estado→patrocinador + rangos `cantidad_min/max`, `cantidad_entregada_min/max`
- [x] **balance**: fix — `_filtros_balance` consultaba tabla inexistente `pagos_contratos`; ahora `pagos`
- [x] **tareas**: claves lowercase (`nombre_tarea`, `estado`) + estado→usuario progresivo por id (bug: asignado_a salía siempre '—')
- [x] **patrocinadores**: filtro activo/inactivo (`estado_pat`)
- [x] **usuarios**: progresividad departamento→rol + filtro activo sí/no
- [x] **mantenimiento**: rango `dias_en_taller` + KPI promedio_dias + estado→recurso progresivo
- [x] **reels**: rangos `duracion_min/max` (seg) + fix filtro patrocinador que era no-op
- [x] PDF análisis nuevo: resumen ejecutivo + Top-N + comparativa período anterior (opciones whitelist server-side, UI en panel de filtros)
- [x] `.opencode/reportes-context.md` actualizado (incluye bugs corregidos)
- Bugs extra corregidos al pasar: preview de premios daba 500 (tupla+lista), asignado_a de tareas siempre vacío

## 🔔 Notificaciones de tareas + multi-asignación (COMPLETO)
- [x] Tabla `seguridad.notificaciones` (migración ejecutada por el usuario; `seguridad.sql` parcheado para clones de test; `migracion_notificaciones.sql` documentado)
- [x] Multi-asignación: modal acepta varios empleados (optgroups por departamento) y/o "departamento completo"; dedupe de activos; transacción única asignaciones+notificaciones (`TareasAsignadasModel.asignar_a_usuarios`, escritura cruzada con esquema desde config para soportar *_test)
- [x] Campana global estilo red social (`components/head.html` + `static/js/notificaciones.js`): badge no leídas, dropdown con últimas 15, marcar leída/todas, toast en vivo por SocketIO (`join_room user_<id>` desde sesión, nunca del cliente)
- [x] API propia del usuario: `GET /notificaciones/api`, `POST /leer` (anti-IDOR), `POST /leer-todas` — solo login requerido
- [x] Al completar una tarea, su creador recibe notificación `tarea_completada` (+socket); sin auto-notificación
- [x] Tests: `tests/test_notificaciones.py` (4 casos). Hallazgo del harness: el `_contexto` autouse mantiene un app context y flask_login cachea el usuario en `g._login_user` → al probar con 2 usuarios hay que hacer `g.pop('_login_user', None)` al cambiar de actor
- Fix menor: helper `_iniciar` de tests ahora devuelve True (suite completa 63/63)

## 🐛 Bugs latentes descubiertos (pendientes de decisión — tocar backend está prohibido en este módulo)
- [x] **EN VIVO** (autorizado por el usuario): endpoint `sincronizar` descartaba `accion` → el log de sincronizaciones ya registra los marcajes del operador. Fix de 1 línea + test con aserción del log.
- [ ] branch `resumen` de reportes revienta (`Usuario` no es dict); inalcanzable vía rutas
- [ ] `rol_model._asegurar_schema` intenta ADD PRIMARY KEY duplicado en cada arranque (visible en logs desde Fase 3)

## 🎬 Rediseño EN VIVO (COMPLETO — según docs/PROMPT_MAESTRO_envivo.md)
- [x] 9 skills `.opencode/skills/envivo-*` + reglas permanentes en AGENTS.md
- [x] `vivo.html` reescrito (solo esa vista): header 3 filas móvil, tarjeta hero del elemento en curso con cronómetro+sobretiempo, barra progreso n/m %, chip de conexión CONECTADO/RECONECTANDO/SIN CONEXIÓN, cola offline con CAMBIOS PENDIENTES:n y reconciliación, toasts propios (SweetAlert solo finalizar/errores), aviso "otro operador actualizó", filtro visual por encargado, atajos teclado (Espacio/R solo con `envivo.control`), dark/light con contraste AA, logo existente, prefers-reduced-motion
- [x] Tests de integración de la vista: `tests/test_envivo_vista.py` (contrato frontend + permisos + sincronización)
- Backend/API/DB/SocketIO server modificados para el rediseño: NO

## ☁️ Fase 5 · Escalabilidad (opcional, solo si cambia el despliegue)
- [ ] Presencia SocketIO del dict global a Redis/BD si hay >1 worker
