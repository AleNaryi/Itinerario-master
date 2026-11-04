# INVENTARIO DEL SISTEMA — Itinerario

Fecha de auditoría: 2026-09-01

---

## 1. Arquitectura general

| Capa | Tecnología | Estado |
|------|-----------|--------|
| Backend | Python 3 + Flask 3 (app factory) | Estable |
| ORM | PyMySQL crudo (sin ORM) | Intencional |
| Auth | Flask-Login + werkzeug hash | Funcional |
| CSRF | Flask-WTF CSRFProtect | Activo |
| Tiempo real | Flask-SocketIO + eventlet | Activo |
| Frontend | HTML + Bootstrap 5.3 + jQuery + DataTables + SweetAlert2 | Funcional |
| BD | MySQL (2 esquemas: estadio_db + seguridad) | Activo |
| PDFs | ReportLab | Activo |
| Tests | pytest (63 tests) | Funcional |

### Estructura de directorios

```
app/
  __init__.py          # create_app(), 18 blueprints, SocketIO handlers
  config.py            # DATABASE_CONFIG, MAIL_CONFIG
  database.py          # Database.get_connection(), transaction()
  controller/          # 18 blueprints (1 por módulo)
  model/               # 18 modelos + validaciones + interfaces
  helpers/             # 13 helpers + 12 generadores PDF
  view/                # 55 templates HTML
  static/              # 28 JS + 6 CSS + assets
tests/                 # 11 archivos, 63 tests
docs/                  # 13 archivos de documentación
.opencode/             # 17 skills locales + 2 externas
```

---

## 2. Dependencias (requirements.txt)

| Paquete | Versión | Uso |
|---------|---------|-----|
| Flask | 3.1.3 | Framework web |
| Werkzeug | 3.1.8 | Utilities, password hashing |
| Flask-Login | 0.6.3 | Sesiones de usuario |
| Flask-WTF | 1.3.0 | CSRF protection |
| Flask-SocketIO | 5.6.1 | WebSocket real-time |
| PyMySQL | 1.2.0 | Driver MySQL |
| reportlab | -- | Generación PDF |
| gunicorn | -- | WSGI server (producción) |
| eventlet | -- | Async para SocketIO |
| python-dotenv | -- | Variables de entorno |
| Pillow | -- | Optimización imágenes (implícito) |

---

## 3. Blueprints (18)

| Blueprint | URL | Permiso | Rutas | Descripción |
|-----------|-----|---------|-------|-------------|
| auth | /auth | Público | 7 | Login, logout, CAPTCHA, forgot/reset password, validate-login |
| dashboard | / | dashboard.view | 1 | Panel principal con métricas |
| guion | /guiones | guion.view | 10 | CRUD guiones, elementos, previsualizar, publicar, replicar |
| en_vivo | /en-vivo | envivo.view | 8 | Iniciar/finalizar, sincronizar, SocketIO, log, API estado |
| inventario | /inventario | inventario.view | 8 | CRUD recursos, tipos, asignaciones |
| contrato | /contratos | contrato.view | 4 | CRUD contratos, API obtener |
| balance | /balance | balance.view | 5 | Pagos, estado de cuenta, PDF |
| premio | /premio | premio.view | 5 | CRUD premios, entrega parcial |
| mantenimiento | /mantenimiento | mantenimiento.view | 6 | Ciclo de mantenimiento, historial |
| gestion_tarea | /gestion-tarea | gestion_tarea.supervisar | 6 | CRUD tareas, multi-asignación, seguimiento |
| patrocinador | /patrocinador | patrocinador.view | 4 | CRUD patrocinadores |
| rol | /roles | rol.view | 4 | CRUD roles, permisos por rol/usuario |
| usuario | /usuarios | usuario.view | 5 | CRUD usuarios, perfil, cambiar contraseña |
| bitacora | /bitacora | rol.view | 3 | Dashboard auditoría, reporte por usuario |
| reportes | /reportes | dashboard.view | 15+ | Dashboard, filtros progresivos, constructor, PDF, CSV |
| chat | /asistente | Login | 2 | Chatbot Aurora (reglas) |
| notificaciones | /notificaciones | Login | 3 | API listar, marcar leída/todas |
| reels | /reels | reels.view | 6 | CRUD reels + videos |

---

## 4. Modelos (18)

| Modelo | Tablas | Patrones especiales |
|--------|--------|-------------------|
| auth_model | usuarios, password_reset_tokens | Flask-Login UserMixin, hash scrypt |
| guion_model | guiones, guion_fechas, elementos_guion | Soft-delete (status), fechas |
| en_vivo_model | guiones, elementos_guion, sincronizaciones | Server clocks (inicio_show, inicio_curso) |
| inventario_model | recursos, tipo_recurso, asignaciones_recursos | Soft-delete (eliminado), estados |
| contrato_model | contrato | FK patrocinadores |
| balance_model | pagos | Hereda Database (error de diseño) |
| premio_model | premios | Entrega parcial, fotos |
| mantenimiento_model | mantenimientos, historial_mantenimiento | Ciclo de estados, N+1 en relaciones |
| tarea_model | tareas, tareas_asignadas | Transacción cruzada de esquema |
| patrocinador_model | patrocinadores | RIF validation |
| rol_model | roles, permisos, rol_permiso, usuario_permiso | seed_permisos_iniciales(), bug DDL |
| usuario_model | usuarios | SELECT * expone password_hash |
| bitacora_model | actividad_usuario, sesiones_usuario, cambios_por_modulo | N+1 en _cargar_nombres_usuario |
| notificacion_model | notificaciones | Anti-IDOR |
| reportes_model | reportes_generados | Limpieza filesystem |
| chat_model | historial_chat | JSON context |
| reels_model | reels, videos | N+1 en consultar(), DELETE sin transacción |
| validacionesMixin | -- | Setters: obligatory, length, date, email, RIF |

---

## 5. Helpers (13 + 12 generadores)

| Helper | Función |
|--------|---------|
| decorators.py | @permiso_requerido, verificar_acceso |
| permission_map.py | Mapa de permisos por blueprint (14 módulos, 52 códigos) |
| bitacora_helper.py | registrar_bitacora() centralizado |
| email_service.py | enviar_email_recuperacion() SMTP |
| image_optimizer.py | optimizar_imagen() PIL |
| chat_knowledge.py | ChatKnowledge Aurora (427 líneas reglas) |
| reportes_utils.py | _parsear_fecha, _formatear_tiempo, _filtrar_por_fecha |
| reportes_data.py | 11 funciones _obtener_datos_* + _sanitizar_para_reporte |
| reportes_catalogo.py | Catálogo declarativo (770 líneas) |
| reportes_constructor.py | Motor SQL parametrizado |
| generators/base_report.py | BaseReportGenerator (394 líneas) |
| generators/*_report.py | 12 generadores por módulo |

---

## 6. Permisos (52 códigos)

```
dashboard.view
usuario.view, usuario.create, usuario.edit, usuario.delete, usuario.perfil
guion.view, guion.create, guion.edit, guion.delete, guion.publish, guion.preview
envivo.view, envivo.control
premio.view, premio.create, premio.edit, premio.delete, premio.entregar
mantenimiento.view, mantenimiento.create, mantenimiento.edit, mantenimiento.delete
rol.view, rol.edit
gestion_tarea.view, gestion_tarea.create, gestion_tarea.edit, gestion_tarea.delete,
  gestion_tarea.complete, gestion_tarea.supervisar
patrocinador.view, patrocinador.create, patrocinador.edit, patrocinador.delete
contrato.view, contrato.create, contrato.edit, contrato.delete
balance.view, balance.create, balance.edit, balance.delete
inventario.view, inventario.create, inventario.edit, inventario.delete, inventario.assign
reels.view, reels.create, reels.edit, reels.delete
reportes.view
```

---

## 7. Tablas BD (30+)

### estadio_db (20 tablas)

guiones, guion_fechas, elementos_guion, recursos, tipo_recurso, estado_recurso,
asignaciones_recursos, estado_asignacion, patrocinadores, contrato, pagos,
premios, tareas, tareas_asignadas, mantenimientos, historial_mantenimiento,
reels, videos, departamentos, historial_chat

### seguridad (14 tablas)

usuarios, roles, permisos, rol_permiso, usuario_permiso, sesiones_usuario,
actividad_usuario, cambios_por_modulo, errores_aplicacion, dashboard_visibilidad,
usuario_dashboard_vis, sincronizaciones, notificaciones, password_reset_tokens,
reportes_generados

---

## 8. SocketIO events

| Evento | Dirección | Handler |
|--------|-----------|---------|
| connect | Client→Server | Autenticación (rechaza anónimos) |
| registrar_usuario | Client→Server | join_room user_<id>, registra en memoria |
| cambio_pagina | Client→Server | Actualiza página del usuario |
| disconnect | Client→Server | Limpia de memoria |
| usuarios_actualizados | Server→All | Broadcast lista conectados |
| actualizar_estados | Server→All | Broadcast estados EN VIVO |
| notificacion_nueva | Server→User | Push notificación a sala privada |

---

## 9. Frontend

| Tipo | Archivos | Líneas totales |
|------|----------|---------------|
| HTML templates | 55 | ~5,000+ |
| JavaScript | 28 | ~5,917 |
| CSS | 6 | ~2,173 |
| JS validaciones | 5 | ~111 |

### Archivos JS más grandes

| Archivo | Líneas | Responsabilidad |
|---------|--------|----------------|
| GestionReportes.js | 802 | Dashboard reportes + constructor |
| ReportesConstructor.js | 586 | Wizard constructor |
| GestionBalance.js | 658 | Balance/pagos (60% código muerto) |
| GestionInventario.js | 507 | Inventario CRUD |
| GestionPremio.js | 470 | Premios |
| GestionGuion.js | 378 | Guiones |
| GestionUsuario.js | 372 | Usuarios |

### vivo.html

- ~53KB, 1100+ líneas
- 550 líneas CSS inline
- 550 líneas JS inline
- Toda la lógica EN VIVO en un solo archivo

---

## 10. Tests

| Archivo | Tests | Área |
|---------|-------|------|
| test_auth.py | 10 | Login, logout, CAPTCHA, sesión, reset |
| test_permisos.py | 3 | Permisos |
| test_validaciones.py | 18 | ValidacionesMixin |
| test_notificaciones.py | 4 | Notificaciones |
| test_envivo_vista.py | 12 | EN VIVO |
| test_reportes_smoke.py | 4 | Reportes smoke |
| test_reportes_pdf.py | 6 | PDFs |
| test_reportes_filtros.py | 13 | Filtros progresivos |
| test_reportes_helpers.py | 7 | Helpers reportes |
| test_reportes_constructor.py | 16 | Constructor SQL |
| conftest.py | -- | Fixtures (clonación BDs) |

---

## 11. Documentación existente

| Archivo | Líneas | Contenido |
|---------|--------|-----------|
| AGENTS.md | -- | Guía de reglas para agentes |
| CHECKLIST.md | 68 | Tracker de progreso por fases |
| SISTEMA_COMPLETO.md | 924 | Documentación técnica completa |
| GUION_Y_ENVIVO_GUIA.md | 2,168 | Ciclo vida guiones, EN VIVO |
| PROMPT_MAESTRO_envivo.md | 1,641 | Spec rediseño EN VIVO |
| ARQUITECTURA_INVENTARIO.md | 611 | Arquitectura inventario |
| GUIA_DEFENSA.md | 760 | Guía de seguridad |
| ARQUITECTURA_CONSTRUCTOR_REPORTES.md | 393 | Constructor reportes |
| CATALOGO_REPORTES.md | 334 | Matriz reportes |
| AUDITORIA_REPORTES.md | 375 | Auditoría reportes |
| MODULO_REPORTES_BRIEF.md | 315 | Brief reportes |
| MODULO_EN_VIVO_BRIEF.md | 130 | Brief EN VIVO |
| AUDITORIA_UI.md | 136 | Auditoría UI |
| PRUEBAS_ENVIVO.md | 97 | Pruebas EN VIVO |
| VALIDACIONES_REPORTE.md | 145 | Validaciones reportes |

---

## 12. Skills existentes (.opencode/skills/)

| Skill | Área | Utilidad |
|-------|------|---------|
| seguridad | Seguridad | Crítica |
| db-transacciones | Database | Alta |
| tests-pytest | Testing | Alta |
| refactor-controladores | Refactoring | Media-Alta |
| reportes-pdf | Reportes/PDF | Alta |
| reportes-detallados | Reportes/Data | Alta |
| envivo-audit | EN VIVO/Audit | Alta |
| envivo-ux | EN VIVO/UX | Alta |
| envivo-ui | EN VIVO/Visual | Media-Alta |
| envivo-mobile | EN VIVO/Mobile | Alta |
| envivo-socketio | EN VIVO/Real-time | Crítica |
| envivo-performance | EN VIVO/Performance | Alta |
| envivo-offline | EN VIVO/Offline | Media-Alta |
| envivo-testing | EN VIVO/Testing | Alta |
| envivo-review | EN VIVO/Review | Alta |
| emil-design-eng (ext) | UI/Animation | Media |
| interface-design (ext) | UI/Design system | Media |

---

## 13. Bugs conocidos

1. `rol_model._asegurar_schema` lanza "Multiple primary key defined" en cada arranque
2. branch `resumen` de reportes revienta (Usuario no es dict, inalcanzable vía rutas)

---

## 14. Deuda técnica conocida

- 60% de GestionBalance.js es código muerto (386 líneas comentadas)
- `getCSRF()` duplicado en 5+ archivos JS
- vivo.html: 1100+ líneas de CSS/JS inline
- N+1 en bitacora_model, mantenimiento_model, premio_model, reels_model
- SELECT * expone password_hash en usuario_model
- Falta transacción en reels_model._eliminar
- Falta transacción en dashboard_visibilidad save
- DDL en cada arranque (rol_model._asegurar_schema)
- Logout vía GET (CSRF-able)
- `Pago` hereda de `Database` (error de diseño)
