# SISTEMA COMPLETO — Itinerario

Guía definitiva para entender TODO el sistema en una sola lectura.
Para IA: lee esto antes de tocar cualquier archivo. Si algo contradice el código real, manda el código.

---

## 1. Qué es

Sistema web de gestión operativa del **Estadio Antonio Herrera Gutiérrez** (béisbol):
guiones de shows en vivo, estado on-air, inventario, contratos/patrocinadores,
premios, balance, tareas, mantenimiento, reels, usuarios/roles/permisos,
bitácora, reportes PDF, chatbot por reglas (sin LLM) y notificaciones en vivo.
Migración de PHP a Flask.

### Stack

- **Backend:** Python 3 + Flask 3 (app factory), PyMySQL crudo (sin ORM), Flask-Login, Flask-WTF (CSRF), Flask-SocketIO + eventlet
- **Frontend:** HTML + Bootstrap 5.3 + Font Awesome 6.4 + jQuery + DataTables + SweetAlert2
- **BD:** MySQL, 2 esquemas — `estadio_db` (negocio) + `seguridad` (auth/roles)
- **PDFs:** reportlab
- **Tests:** pytest

### Cómo correr

```bash
# Dev
venv/bin/pip install -r requirements.txt
venv/bin/python run.py          # → http://localhost:5001

# Prod
gunicorn -k eventlet -w 1 wsgi:app

# Tests (NUNCA contra BDs reales)
venv/bin/pytest -q               # 63 tests, corren contra *_test
```

### Variables de entorno (.env)

```
SECRET_KEY=...                   # OBLIGATORIA, falla al arrancar si falta
DB_HOST=localhost
DB_USER=root
DB_PASSWORD=
DB_NAME=estadio_db               # esquema de negocio
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=
MAIL_PASSWORD=
SOCKET_ALLOWED_ORIGINS=          # vacío = mismo origen (default seguro)
```

---

## 2. Esquema de BD completo

### 2.1 esquema `estadio_db` (negocio)

| Tabla | Descripción | Columnas clave |
|-------|-------------|----------------|
| `guiones` | Guiones de show | `id`, `nombre`, `estado` (borrador/publicado/en_vivo/finalizado), `inicio_show` (datetime, server clock), `tiempo_inning`, `grupo_id`, `status` (soft-delete), `creado_en`, `modificado_en` |
| `guion_fechas` | Fechas de presentación | `id`, `guion_id` FK→guiones, `fecha` |
| `elementos_guion` | Elementos del show (pregame/game) | `id`, `guion_id` FK→guiones, `fecha_id` FK→guion_fechas, `tipo` (pregame/game), `hora`, `inning`, `medio_inning` (alta/baja), `contenido`, `duracion_estimada` (seg), `encargado`, `orden`, `estado` (pendiente/en_curso/completado), `inicio_curso` (datetime, server clock) |
| `recursos` | Activos del estadio | `id`, `nombre`, `descripcion`, `tipo_id` FK→tipo_recurso, `estado_id` FK→estado_recurso, `fecha_compra`, `costo`, `eliminado` (soft-delete) |
| `tipo_recurso` | Tipos de recurso | `id`, `nombre`, `descripcion` (8 tipos seed) |
| `estado_recurso` | Estados de recurso | `id`, `nombre` (Disponible/Asignado/En Mantenimiento/Dañado/Baja) |
| `asignaciones_recursos` | Asignación de recursos a usuarios | `id`, `recurso_id` FK, `usuario_id`, `fecha_asignacion`, `fecha_devolucion_esperada`, `fecha_devolucion_real`, `estado_asignacion_id` FK, `notas` |
| `estado_asignacion` | Estados de asignación | Pendiente/Devuelto/Vencido |
| `patrocinadores` | Empresas patrocinadoras | `id_patrocinador`, `nombre_empresa`, `rif`, `tipo_contrato`, `nombre_contacto`, `telefono`, `email`, `estado`, `encargado_id` |
| `contrato` | Contratos de patrocinio | `id_contrato`, `id_patrocinador` FK, `fecha_inicio`, `fecha_fin`, `estado`, `estatus`, `tipo` (1=Bronce/2=Plata/3=Oro), `monto_total` |
| `pagos` | Pagos de contratos | `id_pago`, `id_contrato` FK, `monto`, `tipo_pago`, `referencia`, `fecha_pago`, `hora_pago`, `registrado_por`, `Descripcion`, `estado` (0=pendiente, 1=confirmado) |
| `premios` | Premios para fans | `id`, `id_patrocinador` FK, `nombre`, `descripcion`, `estado` (pendiente/entregado), `fecha_creacion`, `fecha_entrega`, `entregado_por`, `foto`, `cantidad`, `cantidad_entregada`, `estatus` (soft-delete) |
| `tareas` | Tareas del equipo | `id_tarea`, `Nombre_Tarea`, `Instruccion`, `id_usuario_creador`, `Estatus` (soft-delete) |
| `tareas_asignadas` | Asignaciones de tareas | `id_asignacion`, `id_tarea` FK, `id_usuario`, `Estado` (Pendiente/En Progreso/Completada), `fecha_asignacion_tarea`, `Estatus` |
| `mantenimientos` | Mantenimiento de recursos | `id`, `recurso_id` FK, `usuario_id`, `estado` (en_espera/en_reparacion/reparado/finalizado/baja), `fecha_ingreso`, `fecha_salida`, `diagnostico`, `observaciones` |
| `historial_mantenimiento` | Historial de acciones | `id`, `mantenimiento_id` FK, `usuario_id`, `accion`, `descripcion`, `creado_en` |
| `reels` | Reels de video | `id`, `nombre`, `id_patrocinador` FK, `duracion_total`, `creado_en` |
| `videos` | Videos dentro de reels | `id`, `nombre`, `duracion_segundos`, `orden`, `reel_id` FK, `id_patrocinador` |
| `departamentos` | Departamentos del estadio | `id`, `nombre`, `descripcion`, `color` (5 departamentos seed) |
| `historial_chat` | Chat con Aurora | `id`, `usuario_id`, `mensaje_usuario`, `respuesta_ia`, `contexto` (JSON), `created_at` |

### 2.2 esquema `seguridad` (auth/roles)

| Tabla | Descripción | Columnas clave |
|-------|-------------|----------------|
| `usuarios` | Usuarios del sistema | `id`, `nombre`, `email` (unique), `password_hash` (scrypt), `cedula` (unique), `rol` (string), `departamento`, `telefono`, `activo`, `fecha_registro`, `ultimo_acceso` |
| `roles` | Roles del sistema | `id`, `nombre` (unique), `descripcion` (3 roles seed: Superadmin/Administrador/Usuario) |
| `permisos` | 52 permisos del sistema | `id`, `nombre`, `codigo` (unique), `modulo`, `descripcion` |
| `rol_permiso` | Permisos por rol | `rol_id` FK, `permiso_id` FK (unique pair) |
| `usuario_permiso` | Permisos directos por usuario | `usuario_id` FK, `permiso_id` FK, `fecha_asignacion` |
| `sesiones_usuario` | Sesiones activas | `id`, `usuario_id`, `inicio_sesion`, `fin_sesion`, `ip_address`, `user_agent`, `duracion_segundos` |
| `actividad_usuario` | Bitácora de acciones | `id`, `sesion_id`, `usuario_id`, `tipo_accion`, `modulo`, `accion`, `detalle` (JSON), `pagina`, `ip_address` |
| `cambios_por_modulo` | Cambios detallados | `id`, `actividad_id` FK, `tabla_afectada`, `registro_id`, `campo`, `valor_anterior`, `valor_nuevo` |
| `errores_aplicacion` | Log de errores | `id`, `usuario_id`, `tipo_error`, `mensaje`, `traceback`, `pagina` |
| `dashboard_visibilidad` | Visibilidad de módulos por rol | `rol_id`, `modulo_key`, `visible` |
| `usuario_dashboard_vis` | Visibilidad de módulos por usuario | `usuario_id`, `modulo_key`, `visible` |
| `sincronizaciones` | Log de acciones EN VIVO | `id`, `guion_id`, `usuario_id`, `nombre`, `descripcion`, `fecha_sincronizacion`, `hora_sincronizacion`, `estado` |
| `notificaciones` | Notificaciones in-app | `id`, `usuario_id`, `tipo`, `titulo`, `mensaje`, `url`, `leida`, `fecha_creacion` |
| `password_reset_tokens` | Tokens de recuperación | `id`, `usuario_id` FK, `token` (unique), `expires_at`, `used` |
| `reportes_generados` | PDFs generados | `id`, `usuario_id`, `modulo`, `tipo_reporte`, `filtros` (JSON), `archivo_ruta`, `archivo_nombre`, `archivo_tamano` |

### 2.3 Relaciones importantes

```
guiones 1──* guion_fechas 1──* elementos_guion
patrocinadores 1──* contrato 1──* pagos
patrocinadores 1──* premios
patrocinadores 1──* reels 1──* videos
tareas 1──* tareas_asignadas (con seguridad.usuarios)
recursos 1──* asignaciones_recursos (con seguridad.usuarios)
recursos 1──* mantenimientos 1──* historial_mantenimiento
usuarios ──── sesiones_usuario
usuarios ──── actividad_usuario 1──* cambios_por_modulo
usuarios ──── notificaciones
usuarios ──── password_reset_tokens
roles ──── rol_permiso ──── permisos
usuarios ──── usuario_permiso ──── permisos
```

### 2.4 Migraciones ejecutadas

| Archivo | Qué hace |
|---------|----------|
| `migracion_envivo_tiempos.sql` | Agrega `guiones.inicio_show` + `elementos_guion.inicio_curso` (relojes server-side) |
| `migracion_notificaciones.sql` | Crea tabla `seguridad.notificaciones` |
| `migracion_reset_password.sql` | Crea tabla `seguridad.password_reset_tokens` |

---

## 3. Mapa de archivos

```
run.py / wsgi.py              # Arranque dev / prod
app/__init__.py                # create_app(): 18 blueprints, CSRF, SocketIO, handlers
app/config.py                  # DATABASE_CONFIG (lee .env)
app/database.py                # Database.get_connection(), transaction() contextmanager

app/controller/                # 18 blueprints (1 por módulo)
  auth_controller.py           # Login, logout, forgot/reset password
  dashboard_controller.py      # Panel principal
  guion_controller.py          # CRUD guiones + elementos
  en_vivo_controller.py        # Iniciar/finalizar/sincronizar EN VIVO
  inventario_controller.py     # CRUD recursos + asignaciones
  contrato_controller.py       # CRUD contratos
  balance_controller.py        # Pagos + estado de cuenta
  premio_controller.py         # CRUD premios + entrega
  mantenimiento_controller.py  # Ciclo de mantenimiento
  gestion_tarea_controller.py  # CRUD tareas + multi-asignación
  patrocinador_controller.py   # CRUD patrocinadores
  rol_controller.py            # CRUD roles + permisos
  usuario_controller.py        # CRUD usuarios + perfil
  bitacora_controller.py       # Auditoría + reportes por usuario
  reportes_controller.py       # Dashboard reportes + constructor + PDF
  chat_controller.py           # Chatbot Aurora
  notificaciones_controller.py # API notificaciones in-app
  reels_controller.py          # CRUD reels + videos

app/model/                     # 18 modelos (1 por módulo + utilidades)
  auth_model.py                # Usuario (Flask-Login), UsuarioModel, PasswordResetTokenModel
  guion_model.py               # GuionModel, ElementoGuionModel
  en_vivo_model.py             # EnVivoModel, SincronizacionModel
  inventario_model.py          # InventarioModel, TipoRecursoModel
  contrato_model.py            # ContratoModel
  balance_model.py             # BalanceModel, Pago
  premio_model.py              # PremioModel
  mantenimiento_model.py       # MantenimientoModel, HistorialMantenimientoModel
  tarea_model.py               # TareaModel, TareasAsignadasModel
  patrocinador_model.py        # PatrocinadorModel
  rol_model.py                 # RolModel, PermisoModel, seed_permisos_iniciales()
  usuario_model.py             # UsuarioModel
  bitacora_model.py            # ActividadModel, SesionModel, CambioModel
  notificacion_model.py        # NotificacionModel
  reportes_model.py            # ReporteModel
  chat_model.py                # ChatModel
  reels_model.py               # ReelModel, VideoModel
  validaciones_model.py        # ValidacionesMixin
  interfaces.py                # CrudInterface (ABC)

app/helpers/                   # Helpers centralizados
  decorators.py                # @permiso_requerido, verificar_acceso
  permission_map.py            # Mapa de permisos por blueprint (14 módulos)
  bitacora_helper.py           # registrar_bitacora() — centralizado
  email_service.py             # enviar_email_recuperacion() — SMTP
  image_optimizer.py           # optimizar_imagen() — PIL
  chat_knowledge.py            # ChatKnowledge — Aurora (427 líneas de reglas)
  reportes_utils.py            # Helpers puros: parsear_fecha, formatear_tiempo
  reportes_data.py             # 11 funciones _obtener_datos_* por módulo
  reportes_catalogo.py         # Catálogo declarativo: FUENTES_SQL, DIMENSIONES, METRICAS, FILTROS_BUILDER, MODULO_BUILDER
  reportes_constructor.py      # Motor SQL: arma y ejecuta consultas agregadas
  generators/                  # 12 generadores PDF + base
    base_report.py             # BaseReportGenerator (header, KPIs, tabla, resumen, Top-N, comparativa)
    guiones_report.py          # GuionesReport
    inventario_report.py       # InventarioReport
    premios_report.py          # PremiosReport
    contratos_report.py        # ContratosReport
    balance_report.py          # BalanceReport
    tareas_report.py           # TareasReport
    patrocinadores_report.py   # PatrocinadoresReport
    usuarios_report.py         # UsuariosReport
    mantenimiento_report.py    # MantenimientoReport
    reels_report.py            # ReelsReport
    bitacora_report.py         # BitacoraReport
    resumen_report.py          # ResumenReport
    constructor_report.py      # ConstructorReport (reportes custom)

app/view/                      # 55 templates HTML
  components/
    head.html                  # Global <head>: Bootstrap, Font Awesome, campana notificaciones
    footer.html                # SocketIO init, registrar_usuario, notificaciones.js
    menu.html                  # Sidebar navegación
    chatbot.html               # Aurora floating widget
  en_vivo/
    index.html                 # Lista de shows disponibles
    vivo.html                  # Pantalla principal EN VIVO (~53KB, toda la lógica)
    log.html                   # Log de sincronizaciones
  [otros módulos]              # 1 dashboard + views por módulo

app/static/
  js/                          # 28 archivos JS
    GestionReportes.js         # Dashboard reportes (802 líneas)
    ReportesConstructor.js     # Wizard constructor (586 líneas)
    GestionBalance.js          # Balance/pagos
    GestionInventario.js       # Inventario CRUD
    GestionPremio.js           # Premios
    GestionGuion.js            # Guiones
    GestionUsuario.js          # Usuarios
    GestionPatrocinador.js     # Patrocinadores
    GestionContrato.js         # Contratos
    GestionTarea.js            # Tareas
    GestionTareaSeguimiento.js # Supervisión tareas
    GestionReel.js             # Reels
    GestionMantenimiento.js    # Mantenimiento
    GestionRol.js              # Roles
    GestionAuth.js             # Login + CAPTCHA
    GestionChat.js             # Aurora
    notificaciones.js          # Campana global (pull + SocketIO push)
    GestionEnVivo.js           # EN VIVO client (mínimo, clock sync)
    validaciones/              # 5 archivos de validación JS
  css/
    estilo.css                 # Principal (sidebar, layout, tablas)
    dashboard.css              # Dashboard (métricas, charts)
    login.css                  # Login (CAPTCHA, dark/light)
    Mantenimiento.css          # Mantenimiento
    premios.css                # Premios

tests/                         # Suite de tests
  conftest.py                  # Fixtures: clonación BDs, app, client, crear_usuario, login, superadmin
  test_auth.py                 # Auth: login, logout, CAPTCHA, sesión única
  test_permisos.py             # Permisos: anon→login, sin permiso→rechazo
  test_validaciones.py         # ValidacionesMixin puras
  test_envivo_vista.py         # EN VIVO: iniciar/finalizar, sincronización, permisos
  test_notificaciones.py       # Notificaciones: crear, listar, marcar leída
  test_reportes_smoke.py       # Reportes: smoke test
  test_reportes_pdf.py         # Reportes: generación PDF
  test_reportes_filtros.py     # Reportes: filtros progresivos por módulo
  test_reportes_helpers.py     # Reportes: helpers puros
  test_reportes_constructor.py # Reportes: constructor SQL

docs/                          # Documentación
  GUION_Y_ENVIVO_GUIA.md       # Ciclo de vida guiones, mecánica EN VIVO, SocketIO
  PROMPT_MAESTRO_envivo.md     # Spec completa de rediseño EN VIVO
  ARQUITECTURA_INVENTARIO.md   # Arquitectura inventario (migración PHP)
  GUIA_DEFENSA.md              # Guía de seguridad
  ARQUITECTURA_CONSTRUCTOR_REPORTES.md  # Constructor de reportes
  CATALOGO_REPORTES.md         # Matriz funcional reportes
  AUDITORIA_REPORTES.md        # Auditoría sistema reportes
  MODULO_REPORTES_BRIEF.md     # Brief módulo reportes
  MODULO_EN_VIVO_BRIEF.md      # Brief módulo EN VIVO
  AUDITORIA_UI.md              # Auditoría UI
  PRUEBAS_ENVIVO.md            # Pruebas EN VIVO
  VALIDACIONES_REPORTE.md      # Validaciones reportes
  SISTEMA_COMPLETO.md          # ESTE ARCHIVO

.opencode/
  reportes-context.md          # Estado detallado sistema reportes
  skills/                      # 17 skills (seguridad, db, envivo-*, reportes-*, etc.)
```

---

## 4. App factory + SocketIO

### create_app() — `app/__init__.py`

```python
def create_app():
    # Flask + template/static paths
    # SECRET_KEY (obligatoria, falla si falta)
    # CSRFProtect.init_app()
    # SocketIO.init_app() con CORS same-origin por defecto
    # LoginManager.init_app()
    # Database.init_app(app)
    # user_loader → UsuarioModel.obtener_por_id()
    # seed_permisos_iniciales() (try/except para BD caída)
    # Registra 18 blueprints
    # before_request: verificar_sesion_unica()
    # SocketIO handlers: connect, registrar_usuario, cambio_pagina, disconnect
    # Error handlers: 404, 500, pymysql.err.OperationalError
```

### SocketIO events

| Evento | Dirección | Descripción |
|--------|-----------|-------------|
| `connect` | Server | Rechaza anónimos (identidad SIEMPRE de sesión) |
| `registrar_usuario` | Client→Server | `join_room('user_<id>')`, registra en `usuarios_conectados` |
| `cambio_pagina` | Client→Server | Actualiza página actual del usuario |
| `disconnect` | Client→Server | Limpia de `usuarios_conectados` |
| `usuarios_actualizados` | Server→All | Broadcast de lista de usuarios conectados |
| `actualizar_estados` | Server→All | Broadcast de estados EN VIVO (post-sincronizar) |
| `notificacion_nueva` | Server→User | Push de notificación a sala privada `user_<id>` |

### Variables globales en memoria

```python
usuarios_conectados = {}  # dict[socket_id] = {user_id, nombre, pagina, en_vivo_id}
# ponytail: con -w 1 (gunicorn) es válido; con múltiples workers NO escala
```

---

## 5. Los 18 blueprints

| Blueprint | URL prefix | Permiso base | Descripción |
|-----------|------------|-------------|-------------|
| `auth` | `/auth` | Ninguno (público) | Login (CAPTCHA), logout, forgot/reset password |
| `dashboard` | `/` | `dashboard.view` | Panel principal: métricas, widget EN VIVO, usuarios en línea |
| `guion` | `/guiones` | `guion.view` | CRUD guiones, agregar/editar/eliminar elementos, previsualizar, publicar, replicar |
| `en_vivo` | `/en-vivo` | `envivo.view` | Iniciar/finalizar, sincronizar estados, SocketIO broadcast, server clocks, log |
| `inventario` | `/inventario` | `inventario.view` | CRUD recursos, tipos, asignaciones (assign/return) |
| `contrato` | `/contratos` | `contrato.view` | CRUD contratos, API obtener |
| `balance` | `/balance` | `balance.view` | Dashboard pagos, registrar/editar/eliminar pagos, PDF estado-cuenta |
| `premio` | `/premio` | `premio.view` | CRUD premios, entrega parcial, fotos |
| `mantenimiento` | `/mantenimiento` | `mantenimiento.view` | Ciclo: ingresar→reparar→reparado/finalizado/baja, historial |
| `gestion_tarea` | `/gestion-tarea` | `gestion_tarea.supervisar` | CRUD tareas, multi-asignación (usuarios + departamento), seguimiento |
| `patrocinador` | `/patrocinador` | `patrocinador.view` | CRUD patrocinadores, RIF validation |
| `rol` | `/roles` | `rol.view` | CRUD roles, asignar permisos por rol y por usuario, visibilidad dashboard |
| `usuario` | `/usuarios` | `usuario.view` | CRUD usuarios, perfil, cambiar contraseña |
| `bitacora` | `/bitacora` | `rol.view` | Dashboard auditoría, reporte por usuario con filtros |
| `reportes` | `/reportes` | `dashboard.view` | Dashboard reportes (11 módulos), constructor wizard, PDF, CSV |
| `chat` | `/asistente` | Login | Chatbot Aurora (reglas, sin LLM) |
| `notificaciones` | `/notificaciones` | Login (sin permiso) | API propia: listar, marcar leída/todas |
| `reels` | `/reels` | `reels.view` | CRUD reels + videos, duración total |

---

## 6. Los 18 modelos

### Patrón general

```python
class Modelo:
    def _get_db(self):
        return Database.get_connection()  # conexión por request, DictCursor

    def consultar(self, **filtros): ...   # SELECT con filtros
    def obtener_por_id(self, id): ...     # SELECT por PK
    def crear(self, data): ...            # INSERT (setters validan)
    def modificar(self, id, data): ...    # UPDATE
    def eliminar(self, id): ...           # DELETE o soft-delete
```

### Modelos con lógica especial

| Modelo | Qué tiene de especial |
|--------|----------------------|
| `Usuario` (auth_model) | Hereda de `UserMixin` (Flask-Login). `UsuarioModel.registrar()` hashea password con werkzeug. |
| `EnVivoModel` | `iniciar()` pone estado=en_vivo + `inicio_show=datetime.now()`. `sincronizar_estados()` usa transacción. Server clocks: `inicio_show` en guiones, `inicio_curso` en elementos. |
| `TareasAsignadasModel` | `asignar_a_usuarios()` usa transacción ÚNICA cruzando esquemas (estadio_db.tareas_asignadas + seguridad.notificaciones). |
| `RolModel` | `seed_permisos_iniciales()` crea 48 permisos al arranque. `_asegurar_schema()` tiene bug latente (ADD PRIMARY KEY duplicado). |
| `NotificacionModel` | Anti-IDOR: `marcar_leida()` verifica `usuario_id`. Tipos: `tarea_asignada`, `tarea_completada`. |
| `ReporteModel` | Registra PDFs en BD + limpia archivos del filesystem. |
| `ValidacionesMixin` | Setters validadores: obligatory, length, date, email, RIF, text sanitization. |
| `SesionModel` | Sesión única: si `fin_sesion` existe → sesión cerrada desde otro dispositivo. |

### Patrón de transacciones

```python
from app.database import transaction

# Escrituras multi-statement DEBEN usar transaction()
with transaction():
    db.cursor().execute("INSERT INTO ...")
    db.cursor().execute("UPDATE ...")

# Escrituras cruzadas de esquema: UNA conexión calificando el esquema
db = Database.get_connection('estadio_db')
# Nunca hardcodear nombres de BD; usar DATABASE_CONFIG para soportar *_test
```

---

## 7. Helpers

### permission_map.py

Mapa centralizado de permisos por blueprint. 14 módulos:

```python
GUION = {
    'guion.dashboard': 'guion.view',
    'guion.crear': 'guion.create',
    'guion.agregar_elementos': 'guion.edit',
    # ... 11 rutas
}
EN_VIVO = { ... }  # envivo.view / envivo.control
MANTENIMIENTO = { ... }
PREMIO = { ... }
CONTRATO = { ... }
BALANCE = { ... }
TAREA = { ... }
PATROCINADOR = { ... }
USUARIO = { ... }
INVENTARIO = { ... }
REELS = { ... }
ROL = { ... }
BITACORA = { ... }
REPORTES = { ... }
```

### decorators.py

```python
def permiso_requerido(codigo):
    """Decorator: verifica que el usuario tenga el permiso dado."""
    ...

def verificar_acceso(permiso_map):
    """Before-request factory: mapea endpoint → permiso requerido."""
    ...
```

### bitacora_helper.py

```python
def registrar_bitacora(modulo, tipo, accion, detalle):
    """Registra en bitácora. Si falla, NO rompe la operación principal."""
    ...
```

### reportes_utils.py

```python
def _parsear_fecha(valor): ...
def _formatear_tiempo(segundos): ...
def _filtrar_por_fecha(datos, campo, fecha_inicio, fecha_fin): ...
def _ordenar_datos(datos, campo, descendente=True): ...
```

### reportes_data.py

11 funciones `_obtener_datos_*` que retornan `(datos, kpi)` para cada módulo:

```python
def _obtener_datos_guiones(filtros): ...
def _obtener_datos_inventario(filtros): ...
def _obtener_datos_premios(filtros): ...
def _obtener_datos_contratos(filtros): ...
def _obtener_datos_balance(filtros): ...
def _obtener_datos_tareas(filtros): ...
def _obtener_datos_patrocinadores(filtros): ...
def _obtener_datos_usuarios(filtros): ...
def _obtener_datos_mantenimiento(filtros): ...
def _obtener_datos_reels(filtros): ...
def _obtener_datos_bitacora(filtros): ...
```

### chat_knowledge.py

```python
class ChatKnowledge:
    NOMBRE = 'Aurora'
    GUIAS = {
        'guion': { 'crear': '...', 'editar': '...', 'publicar': '...', ... },
        'inventario': { ... },
        'contrato': { ... },
        'tarea': { ... },
        # 10+ módulos con guías paso a paso
    }

    def responder(self, mensaje, usuario_id=None): ...
    # Keyword matching, contexto de conversación, sin LLM
```

---

## 8. Sistema de reportes

### Arquitectura en capas

```
Frontend (GestionReportes.js + ReportesConstructor.js)
    ↓ AJAX
reportes_controller.py (rutas + filtros whitelist)
    ↓
reportes_data.py (obtener datos/kpis por módulo)  ← flujo LEGADO (resumen)
reportes_constructor.py (motor SQL agregado)       ← flujo CONSTRUCTOR
    ↓
reportes_catalogo.py (catálogo declarativo: FUENTES_SQL, DIMENSIONES, METRICAS, FILTROS_BUILDER)
    ↓
generators/base_report.py + 12 generadores → PDF
```

### Flujo LEGADO (Resumen general)

1. Usuario selecciona módulo + filtros → POST a `/reportes/generar`
2. `reportes_data._obtener_datos_<modulo>(filtros)` → `(datos, kpi)`
3. Generador PDF (`*_report.py`) → archivo en `static/reportes/YYYY/MM/`
4. `ReporteModel.registrar()` → tabla `seguridad.reportes_generados`

### Flujo CONSTRUCTOR (análisis profundo)

1. Frontend carga catálogo: `GET /reportes/catalogo/<modulo>` → `catalogo_publico()`
2. Usuario selecciona: categoría → dimensiones → métricas → filtros → visualización
3. POST a `/reportes/constructor` con `{fuente, dimensiones, metricas, filtros, orden, limite}`
4. `reportes_constructor.armar_consulta()` → valida contra catálogo → SQL parametrizado
5. Resultado → PDF con `ConstructorReport` o JSON para preview

### Filtros progresivos (AJAX)

Los filtros se cargan dinámicamente desde el backend. Patrón:

```javascript
// Cuando cambia el filtro padre, recarga el filtro hijo
$('#filtro_tipo').on('change', function() {
    fetch('/reportes/filtros/inventario', { tipo_nombre: this.value })
    .then(r => r.json())
    .then(data => populateSelect('#filtro_estado', data.estados));
});
```

### Catálogo declarativo (reportes_catalogo.py)

```python
FUENTES_SQL = {
    'contratos': "FROM contrato c JOIN patrocinadores p ON ...",
    'pagos': "FROM pagos pg JOIN contrato c ON ... JOIN patrocinadores p ON ...",
    'bitacora_actividad': "FROM actividad_usuario au JOIN seguridad.usuarios u ON ...",
    'guiones': "FROM guiones g",
    'elementos_guion': "FROM elementos_guion eg JOIN guiones g ON ...",
    'recursos': "FROM recursos r LEFT JOIN tipo_recurso t ON ... LEFT JOIN estado_recurso e ON ...",
    'asignaciones': "FROM asignaciones_recursos a JOIN seguridad.usuarios u ON ...",
    'premios': "FROM premios p2 LEFT JOIN patrocinadores pat ON ...",
    'tareas_carga': "FROM tareas_asignadas ta JOIN tareas t ON ... JOIN seguridad.usuarios u ON ...",
    'patrocinadores': "FROM patrocinadores pa LEFT JOIN seguridad.usuarios ue ON ...",
    'usuarios_sistema': "FROM usuarios us",
    'mantenimientos': "FROM mantenimientos m JOIN recursos r ON ...",
    'reels': "FROM reels re LEFT JOIN patrocinadores rp ON ...",
    'reels_videos': "FROM videos v JOIN reels re ON ... LEFT JOIN patrocinadores rp ON ...",
}

# Dimensiones: 30+ (entidad, mapa, temporal)
# Métricas: 30+ (COUNT, SUM, AVG, MAX, expresiones custom)
# Filtros: 40+ (texto, entero, float, rango_fecha, opciones estáticas, AJAX)
# Módulos: 10 (cada uno con categorías: resumen + análisis profundos)
```

### Generadores PDF (helpers/generators/)

Cada generador hereda de `BaseReportGenerator`:

```python
class BaseReportGenerator:
    MODULO = ''      # nombre del módulo
    TITULO = ''      # título del PDF
    COLUMNAS = []    # columnas de la tabla

    def generar(self, datos, kpis, filtros, archivo):
        # Header con logo + título + filtros aplicados
        # KPIs (cards resumen)
        # Resumen ejecutivo (si hay Top-N)
        # Tabla principal
        # Comparativa período anterior (si se solicita)
        # Guarda en static/reportes/YYYY/MM/

class GuionesReport(BaseReportGenerator):
    MODULO = 'guiones'
    TITULO = 'Reporte de Guiones'
    COLUMNAS = ['Nombre', 'Estado', 'Elementos', 'Duración total', 'Creado']
```

---

## 9. EN VIVO

### Reglas permanentes (NO se negocian)

- **NO modificar** backend, API, modelos, DB ni SocketIO server para mejoras de vista/UX
- **Secuencia estricta:** `pendiente → en_curso → completado` (sin saltos)
- Retroceso: `completado→en_curso` o `en_curso→pendiente` reactivando el anterior
- Solo UN guion puede estar `en_vivo`
- Operar requiere permiso `envivo.control`; espectadores (`envivo.view`) solo leen
- Backend es autoridad; frontend solo mejora la experiencia
- Interacciones: doble toque para avanzar, botón ↩ para retroceder
- Mantener SocketIO (sin polling), dark/light persistente, mobile-first (~30 usuarios)
- Sin PWA ni modo TV

### Máquina de estados

```
pendiente ──(doble toque)──→ en_curso ──(doble toque)──→ completado
                              ↑                              │
                              └─────(botón ↩)────────────────┘

en_curso ──(botón ↩)──→ pendiente (reactiva el anterior pendiente)
```

### Relojes server-side

| Campo | Tabla | Qué registra |
|-------|-------|-------------|
| `inicio_show` | `guiones` | Momento en que se hizo "Iniciar show" (NULL al finalizar) |
| `inicio_curso` | `elementos_guion` | Momento en que el elemento pasó a `en_curso` (se renueva en cada reingreso) |

El backend envía `servidor_ahora` (epoch ms) + `inicio_show_ms` + cada `inicio_curso_ms`.
El frontend calcula el cronómetro: `ahora - inicio_curso`.

### SocketIO events EN VIVO

```javascript
// Al sincronizar (POST /api/sincronizar/<guion_id>):
socketio.emit('actualizar_estados', {
    guion_id: 1,
    servidor_ahora: 1692000000000,
    estados: [
        { id: 1, estado: 'completado', inicio_curso_ms: 1691999000000 },
        { id: 2, estado: 'en_curso', inicio_curso_ms: 1691999500000 },
        // ...
    ]
});
```

### Archivos clave

| Archivo | Qué hace |
|---------|----------|
| `app/view/en_vivo/vivo.html` | Toda la UI (~53KB): header, hero card, cronómetro, progreso, filtro encargado, offline queue, atajos teclado |
| `app/controller/en_vivo_controller.py` | Rutas + API + broadcast SocketIO |
| `app/model/en_vivo_model.py` | Lógica: iniciar, finalizar, sincronizar, obtener elementos |
| `app/static/js/GestionEnVivo.js` | Client-side mínimo (clock sync) |

---

## 10. Notificaciones

### Tabla

```sql
seguridad.notificaciones (
    id INT AUTO_INCREMENT,
    usuario_id INT NOT NULL,
    tipo VARCHAR(40) DEFAULT 'tarea_asignada',  -- tarea_asignada | tarea_completada
    titulo VARCHAR(120) NOT NULL,
    mensaje VARCHAR(255) NOT NULL,
    url VARCHAR(200),
    leida TINYINT(1) DEFAULT 0,
    fecha_creacion DATETIME
)
```

### API (notificaciones_controller.py)

| Ruta | Método | Descripción | Auth |
|------|--------|-------------|------|
| `/notificaciones/api` | GET | Lista últimas 15 + count no leídas | Login |
| `/notificaciones/leer` | POST | Marca una como leída (anti-IDOR) | Login |
| `/notificaciones/leer-todas` | POST | Marca todas como leídas | Login |

### Campana global

- `components/head.html`: badge con count + dropdown con últimas 15
- `static/js/notificaciones.js`: pull inicial (GET) + push por SocketIO (`notificacion_nueva`)
- Sin polling

### Push SocketIO

```python
# app/__init__.py
def emitir_notificacion(user_ids, payload):
    for uid in set(user_ids):
        socketio.emit('notificacion_nueva', payload, room=f'user_{uid}')
```

---

## 11. Seguridad

### Autenticación

- Flask-Login + hash scrypt (werkzeug)
- CAPTCHA propio en login (baseball-themed)
- Sesión única forzada en `before_request` (`verificar_sesion_unica`)
- Reset password: tokens en `password_reset_tokens`, email vía SMTP

### Permisos (52 códigos)

```
dashboard.view, usuario.view/create/edit/delete/perfil,
guion.view/create/edit/delete/publish/preview,
envivo.view/control,
premio.view/create/edit/delete/entregar,
mantenimiento.view/create/edit/delete,
rol.view/edit,
gestion_tarea.view/create/edit/delete/complete/supervisar,
patrocinador.view/create/edit/delete,
contrato.view/create/edit/delete,
balance.view/create/edit/delete,
inventario.view/create/edit/delete/assign,
reels.view/create/edit/delete,
reportes.view
```

### Defensas

- `SECRET_KEY` sin fallback → falla al arrancar si falta
- CORS de sockets same-origin + `SOCKET_ALLOWED_ORIGINS` opcional
- Handshake SocketIO autenticado contra sesión Flask-Login
- Anti open-redirect en `next` de login
- Validaciones server-side en TODOS los POST (las JS no reemplazan)
- `except Exception` con `logger.exception()` (~205 puntos, auditados)
- Soft-delete en guiones (`status=0`), recursos (`eliminado=1`), premios (`estatus=1`)

### OJO: lo que NO se toca

- Backend/API/DB/SocketIO server para mejoras de vista/UX en EN VIVO
- `venv/`, `__pycache__/`, `.DS_Store`, `run.py.bak`

---

## 12. Tests

### Infrastructure

```python
# tests/conftest.py
# - Clona estadio_db → estadio_db_test, seguridad → seguridad_test
# - App context autouse para flask.g
# - CSRF disabled, email parcheado
# - Fixture crear_usuario: crea en seguridad_test
# - Fixture login: respeta CAPTCHA
# - Fixture superadmin: cliente logueado como Superadmin
```

### Suite actual: 63 tests

| Archivo | Tests | Qué cubre |
|---------|-------|-----------|
| test_auth.py | 10 | Login ok/fallido, CAPTCHA, sesión única, reset password, next |
| test_permisos.py | 3 | Anon→login, sin permiso→rechazo, Superadmin→200 |
| test_validaciones.py | 18 | email, RIF, fechas, campos obligatorios, longitudes |
| test_envivo_vista.py | 12 | Iniciar/finalizar, sincronización, permisos, contrato frontend |
| test_notificaciones.py | 4 | Crear, listar, marcar leída, multi-usuario |
| test_reportes_smoke.py | 4 | Generación básica por módulo |
| test_reportes_pdf.py | 6 | PDF empieza con %PDF-, tamaño > 0 |
| test_reportes_filtros.py | 15 | Filtros progresivos por módulo |
| test_reportes_helpers.py | 4 | _parsear_fecha, _ordenar_datos, _filtrar_por_fecha |
| test_reportes_constructor.py | 10 | Dimensiones, métricas, filtros, SQL generation |

### Cómo correr

```bash
venv/bin/pytest -q              # todos
venv/bin/pytest tests/test_auth.py -v  # archivo específico
```

### Hallazgo del harness

El fixture `_contexto` autouse mantiene un app context y flask_login cachea el usuario en `g._login_user`. Al probar con 2+ usuarios hay que hacer `g.pop('_login_user', None)` al cambiar de actor.

---

## 13. Estado actual

### ✅ COMPLETO

- **Fase 1 — Seguridad:** SECRET_KEY, CORS sockets, handshake autenticado, anti open-redirect
- **Fase 2 — Tests:** 63 tests verdes, conftest clona BDs
- **Fase 3 — Refactor:** bitácora centralizada, reportes divididos, ~205 except con logger
- **Fase 4 — Reportes:** 11 módulos con filtros progresivos + PDFs con resumen/Top-N/comparativa
- **Notificaciones:** tabla + API + campana + SocketIO push + multi-asignación tareas
- **EN VIVO rediseño:** vivo.html reescrito, relojes server-side, 9 skills

### 🔄 BUGS LATENTES (no reintroducir)

| Bug | Dónde | Impacto |
|-----|-------|---------|
| `rol_model._asegurar_schema` lanza "Multiple primary key defined" en cada arranque | `app/model/rol_model.py` | Ruido en logs, no rompe funcionalidad |
| branch `resumen` de reportes revienta (`Usuario` no es dict) | `reportes_data.py` | Inalcanzable vía rutas (categoría `resumen` usa flujo legado) |

### ⏳ PENDIENTES (diferidos por el usuario)

- Backfill defensivo SQL para filas `en_vivo/en_curso` heredadas sin reloj
- Aviso discreto en EN VIVO cuando no hay ninguna actividad `en_curso`
- Presencia SocketIO de dict global a Redis/BD si >1 worker (Fase 5, opcional)

---

## 14. Reglas para IA

### Anti-alucinación (obligatorias)

1. **Nunca inventes tablas, columnas ni campos.** Verifica en `app/model/*.py`, en los `.sql` de la raíz o leyendo la tabla real.
2. **No asumas librerías.** Revisa `requirements.txt` primero.
3. **UI, mensajes, comentarios y commits en español.**
4. **Las validaciones JS no reemplazan server-side.**
5. **Tests contra BDs de test, NUNCA contra las reales.**
6. **No toques `venv/`, `__pycache__/`, `.DS_Store`, `run.py.bak`.**
7. **EN VIVO: NO tocar backend/API/DB/SocketIO server** para mejoras de vista/UX.

### Convenciones

- 1 blueprint por módulo en `controller/`
- 1 modelo por módulo en `model/` con setters validadores
- Templates en `view/<modulo>/`
- JS en `static/js/Gestion<Modulo>.js`
- Helpers centralizados en `helpers/` (nunca duplicar en controladores)
- `registrar_bitacora()` vía helper, nunca directo en controlador

### Recetas de extensión

#### Ruta nueva

```python
# 1. Agregar en controller/<modulo>_controller.py
@bp.route('/nueva-ruta')
@permiso_requerido('modulo.action')
def nueva_ruta():
    ...
    registrar_bitacora('modulo', 'create', 'Acción realizada', 'Detalle')
    return render_template('...')

# 2. Agregar en permission_map.py
MODULO = {
    ...
    'modulo.nueva_ruta': 'modulo.action',
}
```

#### Módulo nuevo

```bash
# 1. Crear archivos
app/controller/<nuevo>_controller.py   # bp = Blueprint('nuevo', __name__, url_prefix='/nuevo')
app/model/<nuevo>_model.py             # clase con setters + SQL
app/view/<nuevo>/dashboard.html        # template
app/static/js/GestionNuevo.js          # JS

# 2. Registrar en app/__init__.py
from app.controller.<nuevo>_controller import bp as nuevo_bp
app.register_blueprint(nuevo_bp)

# 3. Agregar permisos
# - En seguridad.sql: INSERT INTO permisos (...)
# - En permission_map.py: NUEVO = {'nuevo.dashboard': 'nuevo.view', ...}

# 4. Agregar en CHECKLIST.md
```

#### Filtro de reporte progresivo

```python
# 1. En reportes_controller.py: crear endpoint AJAX
@bp.route('/filtros/<modulo>')
def filtros_<modulo>():
    # Retorna opciones para el filtro
    return jsonify({'opciones': [...]})

# 2. En GestionReportes.js: conectar al filtro
$('#filtro_padre').on('change', function() {
    fetch(`/reportes/filtros/${modulo}`, { padre: this.value })
    .then(r => r.json())
    .then(data => populateSelect('#filtro_hijo', data.opciones));
});
```

#### Generador PDF nuevo

```python
# 1. Crear app/helpers/generators/<nuevo>_report.py
from app.helpers.generators.base_report import BaseReportGenerator

class NuevoReport(BaseReportGenerator):
    MODULO = 'nuevo'
    TITULO = 'Reporte de Nuevo'
    COLUMNAS = ['Col1', 'Col2', 'Col3']

    def _build_rows(self, datos):
        return [[d['col1'], d['col2'], d['col3']] for d in datos]

# 2. Registrar en reportes_controller.py dentro de generar()
generadores = {
    ...
    'nuevo': NuevoReport,
}
```

#### Modelo nuevo con transacción cruzada de esquema

```python
# Si necesitas escribir en ambas BDs (estadio_db + seguridad):
def hacer_algo(self, data):
    db_negocio = Database.get_connection('estadio_db')
    db_seguridad = Database.get_connection('seguridad')
    # Usar DATABASE_CONFIG para el nombre real (respetar *_test)
    from app.config import DATABASE_CONFIG
    db_name = DATABASE_CONFIG['seguridad']['database']

    with transaction():
        db_negocio.cursor().execute("INSERT INTO ...")
        db_seguridad.cursor().execute(f"INSERT INTO {db_name}.notificaciones ...")
```

---

## Referencias

- `AGENTS.md` — Guía de orientación para agentes (reglas permanentes, deudas conocidas)
- `CHECKLIST.md` — Tracker de progreso por fases
- `.opencode/reportes-context.md` — Estado detallado del sistema de reportes
- `docs/GUION_Y_ENVIVO_GUIA.md` — Ciclo de vida guiones, mecánica EN VIVO
- `docs/PROMPT_MAESTRO_envivo.md` — Spec completa de rediseño EN VIVO
- `docs/ARQUITECTURA_CONSTRUCTOR_REPORTES.md` — Arquitectura del constructor
- `docs/CATALOGO_REPORTES.md` — Matriz funcional de reportes
- `docs/GUIA_DEFENSA.md` — Guía de seguridad
