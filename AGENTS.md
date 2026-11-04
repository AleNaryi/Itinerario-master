# AGENTS.md — Guía del proyecto Itinerario

Guía de orientación para agentes IA. Léela antes de tocar código. Si algo de aquí contradice el código real, manda el código: verifica y actualiza esta guía.

## Módulo EN VIVO — reglas permanentes

Para cualquier trabajo sobre `app/view/en_vivo/` existen 9 skills dedicadas
(`envivo-audit`, `envivo-ux`, `envivo-ui`, `envivo-socketio`, `envivo-mobile`,
`envivo-offline`, `envivo-performance`, `envivo-testing`, `envivo-review`) y un
brief técnico en `docs/MODULO_EN_VIVO_BRIEF.md`.

Reglas que NO se negocian:

- **NO modificar** backend, API, modelos, DB ni SocketIO server para mejoras de vista/UX. La vista principal es `app/view/en_vivo/vivo.html`.
- Secuencia estricta de elementos: `pendiente → en_curso → completado` (sin saltos). Retroceso = "lo marqué mal y aún lo debo ejecutar": completado→en_curso; en_curso→pendiente reactivando el anterior pendiente.
- Solo UN guion puede estar `en_vivo`. Operar requiere permiso `envivo.control`; espectadores (`envivo.view`) solo leen. El backend es autoridad; el frontend solo mejora la experiencia.
- Interacciones intocables: doble toque/doble clic para avanzar; botón ↩ para retroceder. Mantener SocketIO (sin polling), dark/light persistente y mobile-first (~30 usuarios).
- Sin PWA ni modo TV. Sin dependencias/build nuevos sin justificación fuerte.
- Excepciones al "no tocar backend" ya AUTORIZADAS por el usuario (hechas): fix del campo `accion` en `sincronizar` y migración de relojes server-side (`guiones.inicio_show`, `elementos_guion.inicio_curso` — columnas en BD real y en `estadio_db.sql`). Cualquier NUEVA excepción requiere autorización explícita.

## Qué es

Sistema web de gestión operativa del **Estadio Antonio Herrera Gutiérrez** (béisbol): guiones de shows en vivo, estado on-air, inventario, contratos/patrocinadores, premios, balance, tareas, mantenimiento, reels, usuarios/roles/permisos, bitácora, reportes PDF y un asistente chat basado en reglas (sin LLM). Migración de PHP a Flask.

## Stack y cómo correr

- Python 3 + Flask 3 (app factory), PyMySQL crudo (**sin ORM**), Flask-Login, Flask-WTF (CSRF), Flask-SocketIO + eventlet, reportlab (PDFs).
- BD MySQL: dos esquemas — `estadio_db` (negocio) y `seguridad` (usuarios/roles/sesiones). Esquema completo en `estadio_db.sql` y `seguridad.sql` de la raíz.
- Config por `.env` (ver `.env.example`): SECRET_KEY, DB_*, MAIL_*.
- Dev: `venv/bin/python run.py` → http://localhost:5001. Prod: `gunicorn -k eventlet -w 1 wsgi:app`.
- Instalar deps: `venv/bin/pip install -r requirements.txt`.

## Mapa de directorios

```
run.py / wsgi.py        # arranque dev / prod
app/__init__.py          # create_app(): registra 18 blueprints, CSRF, SocketIO
                         # autenticado (handshake rechaza anónimos), salas privadas
                         # user_<id>, presencia global (usuarios_conectados),
                         # sesión única, emitir_notificacion()
app/config.py            # DATABASE_CONFIG (lee .env)
app/database.py          # Database.get_connection('estadio_db'|'seguridad'),
                         # transaction() contextmanager, DictCursor, autocommit ON
app/controller/          # Rutas Flask, UN blueprint por módulo (bp);
                         # notificaciones_controller.py = API propia del usuario
app/model/               # Clases con setters validadores (ValidacionesMixin) + SQL;
                         # notificacion_model.py, tarea_model.asignar_a_usuarios()
                         # (transacción única asignaciones+notificaciones cruzando esquemas)
app/helpers/             # decorators.py (permiso_requerido, verificar_acceso),
                         # permission_map.py, email_service.py, bitacora_helper.py,
                         # generators/ (12 generadores PDF + base_report.py),
                         # chat_knowledge.py (reglas del asistente),
                         # reportes_utils.py + reportes_data.py (motor de reportes)
app/view/                # Templates HTML (un subdirectorio por módulo);
                         # components/head.html aloja la campana global de notificaciones
app/static/js|css        # JS/CSS por módulo (Gestion*.js); notificaciones.js es global
                         # (se carga en components/footer.html); validaciones JS en
                         # static/js/validaciones/ (solo UX, NO reemplazan server-side)
docs/                    # ARQUITECTURA_INVENTARIO.md, GUIA_DEFENSA.md,
                         # GUION_Y_ENVIVO_GUIA.md, MODULO_EN_VIVO_BRIEF.md,
                         # PRUEBAS_ENVIVO.md, PROMPT_MAESTRO_envivo.md
.opencode/skills/        # Locales: seguridad, db-transacciones, refactor-controladores,
                         # tests-pytest, reportes-pdf, reportes-detallados,
                         # envivo-{audit,ux,ui,socketio,mobile,offline,performance,
                         # testing,review}. Externas instaladas: emil-design-eng
                         # (filosofía UI/animaciones Emil Kowalski), interface-design
                         # (craft para dashboards/paneles)
.opencode/reportes-context.md  # Estado detallado del sistema de reportes
CHECKLIST.md             # Tracker completo por fases (fuente de verdad del progreso)
```

## Arquitectura en una mirada

1. **Flujo MVC:** ruta en `controller/<modulo>_controller.py` → modelo en `model/<modulo>_model.py` (setters validan) → template en `view/<modulo>/`. Sin capa servicios.
2. **BD:** conexión por request en `flask.g`, teardown cierra sola. Autocommit activo: escrituras multi-statement DEBEN usar `with transaction():`. Escrituras cruzadas de esquema (ej. tareas→seguridad.notificaciones) se hacen desde UNA conexión calificando el esquema con `DATABASE_CONFIG[...]['database']` (nunca el nombre duro, para respetar los clones *_test).
3. **Auth:** Flask-Login + hash werkzeug; CAPTCHA propio en login; sesión única forzada en `before_request` (`verificar_sesion_unica`) contra `SesionModel`.
4. **Permisos:** cada ruta usa `@permiso_requerido('<codigo>')` o `verificar_acceso(PERMISSION_MAP)` como before_request del blueprint. Excepción: `/notificaciones/*` solo exige login (data propia del usuario). Códigos en `permission_map.py`; seed en `RolModel.seed_permisos_iniciales()`.
5. **Bitácora:** registrar vía `app/helpers/bitacora_helper.registrar_bitacora(modulo, tipo, accion, detalle)` — ya NO duplicar en el controlador.
6. **Tiempo real:** SocketIO para presencia, estados en_vivo y notificaciones en vivo (`emitir_notificacion(user_ids, payload)` emite a salas privadas `user_<id>` que se unen en `registrar_usuario`; identidad SIEMPRE de la sesión). `usuarios_conectados` es dict global en memoria (solo válido con `-w 1`).
7. **Reportes PDF:** dashboard progresivo (`view/reportes/dashboard.html` + `static/js/GestionReportes.js`) → `reportes_controller.generar()` → generador por módulo en `helpers/generators/` heredando `BaseReportGenerator`. PDFs se guardan en `static/reportes/YYYY/MM/` y se registran en `ReporteModel`.
8. **Notificaciones:** tabla `seguridad.notificaciones` (usuario_id, tipo, titulo, mensaje, url, leida). Tipos actuales: `tarea_asignada`, `tarea_completada`. La campana vive en `components/head.html`, la lógica en `static/js/notificaciones.js` (pull inicial + push por socket; sin polling).

## Reglas anti-alucinación (obligatorias)

- **Nunca inventes tablas, columnas ni campos.** Antes de escribir SQL o modelos, confirma nombres reales en `app/model/*.py`, en los `.sql` de la raíz o leyendo la tabla real.
- No asumas que existe una librería: revisa `requirements.txt` primero. Nada nuevo sin justificarlo.
- UI, mensajes, comentarios y commits **en español** (así está todo el proyecto).
- Las validaciones JS no cuentan: toda escritura valida también en servidor.
- Los tests corren contra BDs de test (`*_test`), nunca contra las reales. Suite base en `tests/` (conftest clona los `.sql` a `estadio_db_test`/`seguridad_test`); correr con `venv/bin/pytest -q` y ver `CHECKLIST.md`.
- No toques `venv/`, `__pycache__/`, `.DS_Store`, `run.py.bak`.

## Cómo extender (recetas cortas)

- **Ruta nueva:** crear endpoint en el blueprint del módulo con su decorador de permiso; POST valida server-side y registra bitácora.
- **Módulo nuevo:** controller con `bp` + model + view + registro en `create_app()` + entrada en permisos.
- **Filtro de reporte:** seguir la receta de `.opencode/reportes-context.md` (backend `_filtros_<modulo>` + sección `_obtener_datos` + `MODULE_CONFIG.<modulo>` en JS). Convenciones: `progressive` en filtro origen, `dependsOn` en destino, primer option `value=""` = "Todos...".
- **Generador PDF nuevo:** clase en `helpers/generators/<modulo>_report.py` extendiendo `BaseReportGenerator` (MODULO, TITULO, COLUMNAS, `_build_rows`) + registro en el dict `generadores` de `generar()`.

## Estado del trabajo acumulado (contexto de sesiones previas)

Fuente de verdad detallada: `CHECKLIST.md`. Resumen:

1. **Fase 1 — Seguridad (hecha):** SECRET_KEY sin fallback, CORS de sockets same-origin (+`SOCKET_ALLOWED_ORIGINS`), handshake SocketIO autenticado contra sesión, anti open-redirect en `next`.
2. **Fase 2 — Tests (hecha):** conftest clona `*_test` desde los `.sql`; suites de validaciones, auth, permisos, reportes y EN VIVO. **Suite actual: 63 passed** (`venv/bin/pytest -q`).
3. **Fase 3 — Refactor (hecha):** bitácora centralizada en helper; `reportes_controller` dividido en `reportes_utils.py` + `reportes_data.py`; ~205 `except Exception` ahora loguean.
4. **Fase 4 — Reportes "efecto bitácora" (hecha):** filtros progresivos en los 11 módulos + PDFs con resumen ejecutivo/Top-N/comparativa. Detalle en `.opencode/reportes-context.md`.
5. **Rediseño EN VIVO (hecho):** `vivo.html` reescrito según `docs/PROMPT_MAESTRO_envivo.md`; relojes server-side (`inicio_show`/`inicio_curso`, epoch ms al frontend con offset de servidor); chip ⏱ SHOW en header.
6. **Tareas multi-asignación + notificaciones (hecho):** modal acepta varios empleados y/o departamento completo; tabla `seguridad.notificaciones` (migración ejecutada por el usuario, `seguridad.sql` parcheado para clones); campana global con pull+push; al completar, el creador recibe `tarea_completada`.

Pendientes OPCIONALES acordados pero diferidos por el usuario ("dejémoslo así por ahora"):
- Backfill defensivo SQL para filas `en_vivo/en_curso` heredadas sin reloj (blindaje de despliegues).
- Aviso discreto en EN VIVO cuando no hay ninguna actividad `en_curso` (evita confundir el gris legítimo con un apagón).

## Deudas conocidas (no reintroducirlas, atacarlas al tocar el archivo)

Presencia SocketIO no escala a múltiples workers (dict global en memoria; válido con `-w 1`). Bugs latentes pendientes: branch `resumen` de reportes revienta (`Usuario` no es dict, inalcanzable vía rutas) y `rol_model._asegurar_schema` lanza "Multiple primary key defined" en cada arranque (ruido en logs). Hallazgo del harness de tests: el fixture `_contexto` autouse mantiene un app context vivo y flask_login cachea el usuario en `g._login_user` — al probar con 2+ usuarios hacer `g.pop('_login_user', None)` al cambiar de actor (ver `tests/test_notificaciones.py`).

Resueltas históricas (NO reintroducir): SECRET_KEY sin fallback · CORS de sockets cerrado + handshake autenticado · open redirect en `next` · `except Exception` silenciosos (~205 ahora loguean) · bitácora duplicada → `app/helpers/bitacora_helper.py` · `reportes_controller.py` 1.213→533 líneas → `reportes_utils.py` + `reportes_data.py`. Detalle completo en `CHECKLIST.md`.
