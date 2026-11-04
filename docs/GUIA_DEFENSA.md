# Guia de Defensa — Sistema Itinerario

> Guia concisa para defensa tecnica ante profesores. Cubre arquitectura, modulos clave, seguridad y preguntas frecuentes.

---

## 1. Que es Itinerario

Sistema web para gestionar eventos en vivo en el Estadio Antonio Herrera Gutierrez. Migrado de PHP a Python/Flask. Administra 13 modulos: guiones para shows, control en vivo, inventario, contratos, patrocinadores, premios, mantenimiento, tareas, usuarios, roles, reels, reportes y bitacora.

**Problema que resuelve:** Coordinar shows en vivo donde multiples personas deben saber que elemento esta activo en tiempo real, sin depender de WhatsApp o llamadas.

---

## 2. Arquitectura General

### Stack tecnologico

| Capa | Tecnologia |
|------|------------|
| Backend | Flask 3.1 (Python) |
| Base de datos | MySQL (PyMySQL) |
| Tiempo real | Flask-SocketIO + eventlet |
| Frontend | Bootstrap 5, jQuery, DataTables, SweetAlert2 |
| Auth | Flask-Login + werkzeug password hashing |
| CSRF | Flask-WTF |
| PDF | ReportLab |

### Dos bases de datos

```
estadio_db                    seguridad
├── guiones                   ├── usuarios
├── elementos_guion           ├── roles
├── guion_fechas              ├── permisos
├── recursos                  ├── rol_permiso
├── contratos                 ├── usuario_permiso
├── patrocinadores            ├── sesiones_usuario
├── premios                   ├── actividad_usuario
├── tareas                    └── sincronizaciones
├── reels
└── ...
```

**Por que dos BD?** Separacion de responsabilidades: datos de negocio vs datos de seguridad/auditoria. Permite escalar y auditar independientemente.

### Patron de conexion a BD

```python
# Se crea UNA conexion por request, se reutiliza, se cierra automaticamente
def get_connection(db_name='estadio_db'):
    if db_name not in g._db_connections:
        g._db_connections[db_name] = pymysql.connect(**cfg)
        g._db_connections[db_name].autocommit(True)
    return g._db_connections[db_name]
```

**Ventaja:** No hay fugas de conexiones. Flask cierra todo al terminar cada request via `teardown_appcontext`.

---

## 3. Patron MVC (adaptado de PHP)

Flask no es un framework MVC puro, pero el codigo separa claramente las tres capas:

### Modelo (`app/model/`)

Clases Active Record con patrong de setters (heredado del PHP original):

```python
class GuionModel(ValidacionesMixin):
    def set_nombre(self, valor):    # Setter
        self.__nombre = valor

    def confirmar_registro(self):   # Valida + persiste
        if not self._validar_datos():
            return False
        return self._registrar()

    def _registrar(self):           # INSERT real
        sql = "INSERT INTO guiones ..."
        cur.execute(sql, (self.__nombre, ...))
```

**Patron de dos fases:** `confirmar_registro()` primero valida, luego persiste. Si hay errores, no toca la BD.

**Mixins reutilizables:**
- `ValidacionesMixin`: campos obligatorios, longitudes, fechas
- `CrudInterface`: contrato abstracto (confirmar_registro, consultar, etc.)

### Vista (`app/view/`)

Templates Jinja2 con componentes reutilizables:

```
head.html  →  abre HTML, sidebar, flash messages
menu.html  →  sidebar navigation (permisos-based)
footer.html → cierra HTML, carga JS globales
```

Cada pagina:
```html
{% include 'components/head.html' %}
    <!-- contenido del modulo -->
    <script src="GestionX.js"></script>
{% include 'components/footer.html' %}
```

### Controlador (`app/controller/`)

Blueprints Flask, uno por modulo:

```python
bp = Blueprint('guion', __name__, url_prefix='/guiones')
bp.before_request(verificar_acceso(GUION))  # RBAC global

@bp.route('/crear', methods=['GET', 'POST'])
def crear():
    if request.method == 'POST':
        # Procesar formulario
        model.set_nombre(nombre)
        model.confirmar_registro()
        return redirect(...)
    return render_template('guion/crear.html')
```

### Patron de endpoint unico (estilo PHP)

Algunos modulos (como inventario) usan un solo URL para todo el CRUD:

```python
@bp.route('/', methods=['GET', 'POST'])
def dashboard():
    if 'registrar' in request.form:    # Crear
    if 'editar' in request.form:       # Actualizar
    if 'eliminar' in request.form:     # Eliminar
    if 'consultar' in request.form:    # Listar (AJAX)
```

El JavaScript envia el mismo URL con campos ocultos diferentes para despachar acciones. Esto es una traduccion directa de `isset($_POST['action'])` de PHP.

---

## 4. RBAC — Control de Acceso por Roles

### Estructura de 3 niveles

```
Superadmin (57 permisos)  →  Todo el sistema
Administrador (55)        →  Todo excepto gestionar roles
Usuario (13)              →  Solo lectura en todos los modulos
```

### 57 permisos en 13 modulos

| Modulo | Permisos | Acciones |
|--------|----------|----------|
| Dashboard | 1 | view |
| Usuarios | 5 | view, create, edit, delete, perfil |
| Guion | 6 | view, create, edit, delete, publish, preview |
| En Vivo | 2 | view, control |
| Premios | 5 | view, create, edit, delete, entregar |
| Mantenimiento | 3 | view, edit, delete |
| Tareas | 6 | view, create, edit, delete, complete, supervisar |
| Patrocinadores | 4 | view, create, edit, delete |
| Contratos | 4 | view, create, edit, delete |
| Balance | 4 | view, create, edit, delete |
| Roles | 2 | view, edit |
| Inventario | 5 | view, create, edit, delete, assign |
| Reels | 4 | view, create, edit, delete |

### Dos niveles de verificacion

**Nivel 1 — por Blueprint (before_request):**
```python
bp.before_request(verificar_acceso(GUION))
```
Verifica TODAS las rutas del blueprint antes de ejecutarlas.

**Nivel 2 — por ruta (decorador):**
```python
@permiso_requerido('guion.publish')
def publicar(id):
    ...
```
Para control fino en rutas especificas.

### Resolucion de permisos (UNION query)

```sql
SELECT p.codigo FROM permisos p
JOIN rol_permiso rp ON p.id = rp.permiso_id
JOIN roles r ON r.id = rp.rol_id
WHERE r.nombre = 'Administrador'
UNION
SELECT p.codigo FROM permisos p
JOIN usuario_permiso up ON p.id = up.permiso_id
WHERE up.usuario_id = 5
```

**Resultado:** Un usuario recibe permisos de SU ROL + permisos INDIVIDUALES extras. La UNION fusiona ambos conjuntos.

### Cache por request

```python
def tiene_permiso(self, codigo):
    if self.rol == 'Superadmin':
        return True  # Sin query a BD
    if self.__permisos_cache is None:
        self.__permisos_cache = obtener_permisos(self.id, self.rol)
    return codigo in self.__permisos_cache  # Lookup O(1)
```

Los permisos se cargan UNA vez por request y se cachean en el objeto usuario.

---

## 5. Modulo Guion — Ciclo de Vida Completo

### Maquina de estados

```
                    ┌─────────────────────────────────────┐
                    │                                     │
                    ▼                                     │
  ┌──────────┐   publicar   ┌───────────┐   iniciar   ┌──────────┐
  │ BORRADOR │ ──────────→ │ PUBLICADO │ ──────────→ │ EN VIVO  │
  └──────────┘              └───────────┘              └──────────┘
       │                                                   │
       │                                              finalizar
       │                                                   │
       │                                                   ▼
       │                                            ┌────────────┐
       └──────────────────────────────────────────→ │ FINALIZADO │
                        (reiniciar)                 └────────────┘
```

### Tablas involucradas

```
guiones (1) ──< guion_fechas (N)      Fechas programadas
guiones (1) ──< elementos_guion (N)   Elementos del show
guiones (1) ──< sincronizaciones (N)  Log de eventos en vivo
```

### Dos tipos de elementos

**Pre-Game (por hora):**
- Se programan por hora especifica: 19:46, 20:11, etc.
- Validacion: no puede haber dos elementos a la misma hora
- Ejemplo: "Warning Song" a las 19:46, "National Anthem" a las 19:52

**Game (por inning):**
- Se programan por inning (1-9) + medio (alta/baja)
- Validacion: no puede haber dos elementos en el mismo inning+medio
- Duracion auto-llenada desde `tiempo_inning` del guion
- Ejemplo: "3ra Baja - Jumbotron" (inning 3, baja)

### Algoritmo de deteccion de conflictos

```python
# Pre-game: set de horas ocupadas
horas_ocupadas = {"19:46", "20:11"}
if hora_nueva in horas_ocupadas:
    errores.append('Esa hora ya esta ocupada')

# Game: diccionario de innings ocupados
innings_ocupados = {"3-baja": 15, "4-alta": 30}
clave = f"{inning}-{medio_inning}"
if clave in innings_ocupados:
    errores.append('Ese inning ya esta ocupado')
```

### Replicacion (deep copy)

Cuando un guion se replica a multiples fechas:

```python
def replicar(origen_id, fechas, nombre_base):
    for fecha in fechas:
        # 1. Crear nuevo guion
        nuevo_id = INSERT INTO guiones (nombre, estado, ...)
        # 2. Clonar TODOS los elementos
        for elemento in elementos_origen:
            INSERT INTO elementos_guion (guion_id=nuevo_id, ...)
        # 3. Copiar fechas
        INSERT INTO guion_fechas (guion_id=nuevo_id, fecha=...)
```

Resultado: por cada fecha, se crea un guion nuevo con todos los elementos clonados.

---

## 6. Modulo En Vivo — Tiempo Real

### Flujo completo

```
INICIAR                    SINCRONIZAR                   FINALIZAR
   │                          │                             │
   ▼                          ▼                             ▼
publicado ──→ en_vivo ──→[SocketIO broadcast]──→ en_vivo ──→ finalizado
   │                          │                             │
   │                     Todos los                         │
   │                     clientes                          │
   │                     reciben                           │
   │                     el cambio                         │
   │                                                       │
   └───────────── Puede reiniciar ─────────────────────────┘
```

### Constraint critico: SOLO 1 guion en vivo

```sql
UPDATE guiones SET estado = 'en_vivo'
WHERE id = %s
AND NOT EXISTS (
    SELECT 1 FROM guiones
    WHERE estado = 'en_vivo' AND id != %s AND status = 1
)
```

**Por que?** En un estadio fisicamente solo puede estar pasando UN show a la vez. El constraint a nivel de BD previene condiciones de carrera.

### Transiciones de estado de elementos

```
  ┌──────────┐  iniciar()  ┌───────────┐  doble clic  ┌────────────┐
  │   NULL   │ ──────────→ │ PENDIENTE │ ──────────→  │ EN_CURSO   │
  └──────────┘             └───────────┘              └────────────┘
                                    ↑                        │
                                    │                  doble clic
                                    │                        │
                                    │                        ▼
                                    │                 ┌────────────┐
                                    └── retroceder ── │ COMPLETADO │
                                                      └────────────┘
```

### SocketIO — flujo de sincronizacion

**Paso 1: Usuario hace doble clic en "en_curso"**
```javascript
// vivo.html
function completarYAvanzar(el) {
    el.dataset.estado = 'completado';          // 1. Actualizar DOM
    siguiente.dataset.estado = 'en_curso';     // 2. Avanzar al siguiente
    enviarEstados(cambios);                    // 3. Enviar al servidor
}
```

**Paso 2: Servidor recibe y procesa**
```python
# en_vivo_controller.py
@bp.route('/api/sincronizar/<guion_id>', methods=['POST'])
def sincronizar(guion_id):
    estados = request.json['estados']
    EnVivoModel().sincronizar_estados(guion_id, estados)  # UPDATE DB
    socketio.emit('actualizar_estados', {                 # BROADCAST
        'guion_id': guion_id,
        'estados': [{'id': i['id'], 'estado': i['estado']} for i in estados]
    })
```

**Paso 3: Todos los clientes reciben el cambio**
```javascript
// vivo.html (todos los clientes conectados)
socket.on('actualizar_estados', function(data) {
    if (data.guion_id == guionId) {
        data.estados.forEach(function(e) {
            document.querySelector('[data-id="'+e.id+'"]').dataset.estado = e.estado;
        });
        actualizarColores();  // Aplicar CSS segun estado
    }
});
```

### Sincronizacion optimista

```python
def sincronizar_estados(guion_id, estados):
    for elem in estados:
        estado_actual = obtener_estado(elem['id'])
        if elem['estado'] != estado_actual:  # Solo si cambio
            UPDATE elementos_guion SET estado = ...
            # Registrar en log
```

**Por que optimista?** En un show en vivo, la velocidad es critica. No se usan locks pesados. Si dos usuarios intentan cambiar lo mismo, el ultimo写入 gana. En la practica, solo UN operador controla el show.

### vivo.html — pagina standalone

`vivo.html` NO usa `head.html` ni `footer.html`. Es una pagina completamente independiente con:

- Tema oscuro/glassmorphism (no el sidebar azul)
- Layout de grid para elementos
- SocketIO client integrado
- Logica de doble clic + retroceder
- Contador de espectadores en tiempo real

**Por que standalone?** La vista en vivo se proyecta en pantallas grandes en el estadio. No necesita sidebar ni navegacion.

---

## 7. Seguridad

### Autenticacion

```python
# Registro de password (werkzeug)
password_hash = generate_password_hash(password, method='pbkdf2:sha256')

# Verificacion
if usuario and usuario.check_password(password):
    login_user(usuario)
```

### Proteccion CSRF

```python
# app/__init__.py
csrf = CSRFProtect(app)  # Protege TODOS los formularios

# Excepcion: en_vivo usa SocketIO con JSON
csrf.exempt(en_vivo_bp)  # SocketIO no puede enviar CSRF tokens
```

### Sesion unica server-side

```python
@app.before_request
def verificar_sesion_unica():
    sid = session.get('bitacora_sesion_id')
    db_sesion = SesionModel().obtener_por_id(sid)
    if not db_sesion or db_sesion.get('fin_sesion'):
        logout_user()  # Cerrada desde otro dispositivo
        return redirect(url_for('auth.login'))
```

**Cada request** verifica que la sesion siga activa en la BD. Si otro login la cerro, el usuario es expulsado.

### Bitacora (auditoria)

Tres tablas de auditoria:

| Tabla | Que registra |
|-------|--------------|
| `sesiones_usuario` | Login/logout con duracion |
| `actividad_usuario` | Cada accion CRUD (quien, que, cuando, donde) |
| `sincronizaciones` | Eventos de en vivo (iniciar, sincronizar, finalizar) |

```python
# Patron en TODOS los controladores
def _registrar_bitacora(tipo, accion, detalle):
    ActividadModel().registrar({
        'usuario_id': current_user.id,
        'tipo_accion': tipo,        # create, update, delete
        'modulo': 'guion',
        'accion': accion,           # "Crear guion"
        'detalle': json.dumps({'detalle': detalle}),
        'pagina': request.path,
        'ip_address': request.remote_addr,
    })
```

### SQL parametrizado

```python
# BIEM (parametrizado)
cur.execute("SELECT * FROM guiones WHERE id = %s", (id,))

# MAL (nunca hacer esto)
cur.execute(f"SELECT * FROM guiones WHERE id = {id}")  # SQL Injection
```

**Todos los queries** en el sistema usan parametros `%s`. No hay concatenacion de strings en SQL.

---

## 8. Preguntas Frecuentes de Defensa

### Arquitectura General

**P: Por que Flask y no Django?**
R: Flask es mas ligero y flexible. El sistema no necesita el ORM pesado de Django ni su admin. PyMySQL con queries directas da mas control sobre la BD.

**P: Por que dos bases de datos?**
R: Separacion de responsabilidades. Los datos de negocio (guiones, inventario) van en `estadio_db`. Los datos de seguridad y auditoria van en `seguridad`. Permite auditar independientemente y escalar por separado.

**P: Como manejas las conexiones a BD?**
R: Una conexion por request, almacenada en `flask.g`. Se reutiliza durante todo el request y se cierra automaticamente en `teardown_appcontext`. No hay fugas de conexiones.

**P: Por que no usan ORM como SQLAlchemy?**
R: El sistema fue migrado de PHP que usaba queries directas. Mantener el patron de queries SQL facilito la migracion y da control total sobre la optimizacion.

### RBAC (Roles y Permisos)

**P: Como funciona el control de acceso?**
R: Hay 3 roles con 57 permisos. Cada blueprint tiene un `before_request` que verifica si el usuario tiene el permiso necesario. Ademas, el Superadmin bypasea todas las verificaciones.

**P: Que pasa si un usuario necesita permisos extras?**
R: Se usan permisos individuales (`usuario_permiso`). La UNION query combina permisos del rol + permisos individuales. Un Usuario puede recibir permisos de Administrador sin cambiar de rol.

**P: Como se\Cachean los permisos?**
R: Se cargan UNA vez por request cuando el usuario llama `tiene_permiso()`. Se guardan en `__permisos_cache` como un set. Los subsiguientes checks son O(1).

**P: Por que Superadmin bypasea todo?**
R: Eficiencia. El Superadmin tiene todos los 57 permisos. Verificar contra la BD en cada request seria innecesario. `if self.rol == 'Superadmin': return True` evita la query.

### Modulo Guion

**P: Cual es el ciclo de vida de un guion?**
R: Borrador → Publicado → En Vivo → Finalizado. Puede reiniciarse desde Finalizado.

**P: Por que hay dos tipos de elementos?**
R: Los shows tienen dos fases: pre-game (actividades antes del juego, programadas por hora) y game (actividades durante el juego, programadas por inning). Cada fase tiene reglas de validacion diferentes.

**P: Como se detectan conflictos de horario?**
R: Pre-game usa un set de horas ocupadas. Game usa un diccionario de inning+medio. Al crear/editar, se verifica que la hora/inning no este ocupada. Si esta ocupada, muestra error.

**P: Que es la replicacion?**
R: Copia profunda de un guion a multiples fechas. Crea N guiones nuevos, cada uno con todos los elementos clonados. Utile cuando el mismo show se repite en diferentes dias.

**P: Por que los elementos se eliminan permanentemente pero los guiones solo se desactivan?**
R: Los guiones necesitan trazabilidad (auditoria). Los elementos son efimeros dentro de un guion. Si se elimina un guion, los elementos se eliminan en cascada.

### Modulo En Vivo

**P: Como funciona el tiempo real?**
R: Flask-SocketIO con eventlet. Cuando un operador cambia el estado de un elemento, el servidor hace UPDATE en la BD y luego hace `socketio.emit()` a TODOS los clientes conectados. Los clientes filtran por `guion_id` en JavaScript.

**P: Por que solo puede haber un guion en vivo?**
R: Constraint de negocio. Fisicamente solo puede estar pasando UN show en el estadio. Se enforce a nivel de BD con `NOT EXISTS` subquery, no solo en la aplicacion.

**P: Que pasa si dos usuarios intentan sincronizar al mismo tiempo?**
R: Usamos sincronizacion optimista. Cada sync verifica el estado actual antes de actualizar. El ultimo写入 gana. En la practica, solo un operador controla el show.

**P: Por que vivo.html es standalone?**
R: Se proyecta en pantallas grandes del estadio. No necesita sidebar, navegacion ni el layout normal. Tiene tema oscuro para mejor visibilidad.

**P: Como se maneja la reconexion?**
R: SocketIO maneja reconexion automatica. Al reconectar, el cliente llama `sincronizarEstado()` para obtener el estado actual de la BD, no depende del cache del socket.

### Seguridad

**P: Como protegen contra SQL Injection?**
R: Todos los queries usan parametros `%s`. Nunca se concatenan strings en SQL. PyMySQL escapa automaticamente los valores.

**P: Como funciona la sesion unica?**
R: Cada request verifica en la BD si la sesion sigue activa. Si otro dispositivo hizo login, cierra la sesion anterior y redirige al login.

**P: Por que en_vivo no tiene CSRF?**
R: SocketIO envia JSON POST desde una pagina standalone. No tiene formulario HTML con CSRF token. Se exempta `en_vivo_bp` de CSRF.

**P: Que es la bitacora?**
R: Sistema de auditoria de 3 tablas. Registra cada accion CRUD con: quien, que hizo, cuando, desde que IP, en que pagina. Tambien registra sesiones y eventos de en vivo.

### Decisiones de Diseno

**P: Por que el patron de endpoint unico (inventario)?**
R: Herencia del PHP original. Un solo URL maneja todo el CRUD via campos ocultos en el formulario. Facilito la migracion pero es menos RESTful.

**P: Por que no usan Redis/WebSockets nativos?**
R: Flask-SocketIO es suficiente para el volumen actual (decenas de usuarios concurrentes). Redis seria over-engineering para este caso de uso.

**P: Como escalaria este sistema?**
R: Para mas usuarios: Redis para sesiones + SocketIO con Redis adapter. Para mas datos: particionar la BD por fechas. Para alta disponibilidad: load balancer + multiples workers con gunicorn+eventlet.

---

## 9. Diagramas Clave

### Maquina de estados del Guion

```
                  ┌──────────────────────────────────────────────────┐
                  │                                                  │
                  ▼                                                  │
  ┌──────────┐  publicar  ┌───────────┐  iniciar()  ┌──────────┐   │
  │BORRADOR  │ ─────────→ │ PUBLICADO │ ──────────→ │ EN VIVO  │   │
  └──────────┘             └───────────┘             └──────────┘   │
       │                                                  │         │
       │                                            finalizar()     │
       │                                                  │         │
       │                                                  ▼         │
       │                                           ┌────────────┐   │
       └──────── reiniciar() ─────────────────────→│ FINALIZADO │   │
                                                   └────────────┘
```

### Flujo de permisos (RBAC)

```
Request HTTP
    │
    ▼
Blueprint.before_request
    │
    ▼
verificar_acceso(permiso_map)
    │
    ├── No autenticado → redirect login
    │
    ├── Superadmin → PASS (bypass)
    │
    └── Normal:
            │
            ▼
        tiene_permiso(codigo)
            │
            ├── Cache hit? → buscar en __permisos_cache (O(1))
            │
            └── Cache miss?
                    │
                    ▼
                UNION query:
                permisos_rol + permisos_usuario
                    │
                    ▼
                Guardar en cache
                    │
                    ▼
                RETURN True/False
```

### Flujo de sincronizacion en vivo

```
┌─────────────────────────────────────────────────────────────────┐
│ OPERADOR (vivo.html)                                            │
│                                                                  │
│  Doble clic en elemento "en_curso"                              │
│       │                                                          │
│       ▼                                                          │
│  1. Actualizar DOM: actual → completado                         │
│  2. Actualizar DOM: siguiente → en_curso                        │
│       │                                                          │
│       ▼                                                          │
│  3. POST /en-vivo/api/sincronizar/{id}                          │
│     Body: {estados: [{id:1, estado:'completado'}, ...]}         │
└──────────────────────────────┬──────────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ SERVIDOR (en_vivo_controller.py)                                 │
│                                                                   │
│  1. Recibir JSON con estados                                     │
│  2. EnVivoModel.sincronizar_estados()                           │
│     └─ Para cada elemento:                                       │
│         ├─ Verificar si cambio (optimista)                      │
│         ├─ UPDATE elementos_guion SET estado = ...              │
│         └─ Registrar en log de sincronizaciones                 │
│  3. socketio.emit('actualizar_estados', {guion_id, estados})    │
└──────────────────────────────┬──────────────────────────────────┘
                               │ BROADCAST
                               ▼
┌──────────────────────────────────────────────────────────────────┐
│ TODOS LOS CLIENTES CONECTADOS                                    │
│                                                                   │
│  socket.on('actualizar_estados')                                 │
│    └─ Si data.guion_id == miGuionId:                           │
│         ├─ Actualizar data-estado en DOM                        │
│         └─ Aplicar colores CSS (en_curso=verde, completado=dim) │
└──────────────────────────────────────────────────────────────────┘
```

### Relaciones de base de datos

```
┌─────────────────┐     ┌──────────────────┐
│    usuarios      │     │      roles        │
│─────────────────│     │──────────────────│
│ id              │     │ id               │
│ nombre          │     │ nombre           │
│ email           │     │ descripcion      │
│ password_hash   │     └────────┬─────────┘
│ rol             │              │
│ activo          │              │ 1:N
└────────┬────────┘              │
         │                       ▼
         │              ┌──────────────────┐
         │              │   rol_permiso     │
         │              │──────────────────│
         │              │ rol_id            │
         │              │ permiso_id        │
         │              └────────┬─────────┘
         │                       │
         │                       │ N:1
         │                       ▼
         │              ┌──────────────────┐
         │              │    permisos       │
         │              │──────────────────│
         │              │ id               │
         │              │ codigo           │
         │              │ modulo           │
         │              └──────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────┐     ┌──────────────────┐
│sesiones_usuario  │     │actividad_usuario  │
│─────────────────│     │──────────────────│
│ usuario_id      │     │ usuario_id       │
│ inicio_sesion   │     │ tipo_accion      │
│ fin_sesion      │     │ modulo           │
│ duracion_seg    │     │ accion           │
└─────────────────┘     │ detalle          │
                        └──────────────────┘

┌─────────────────┐     ┌──────────────────┐
│    guiones       │     │  elementos_guion  │
│─────────────────│     │──────────────────│
│ id              │◄───│ guion_id          │
│ nombre          │     │ tipo             │
│ estado          │     │ hora/inning      │
│ tiempo_inning   │     │ contenido        │
│ status          │     │ estado           │
└────────┬────────┘     │ orden            │
         │              └──────────────────┘
         │ 1:N
         ▼
┌─────────────────┐
│ guion_fechas    │
│─────────────────│
│ guion_id        │
│ fecha           │
└─────────────────┘
```

---

## 10. Resumen para la Defensa

### Que demuestra este proyecto

1. **Arquitectura separada:** MVC claro sin framework pesado
2. **Seguridad:** RBAC de 3 niveles, CSRF, sesion unica, SQL parametrizado
3. **Tiempo real:** SocketIO para sincronizacion en vivo
4. **Auditoria:** Sistema completo de bitacora
5. **Validacion:** Backend + frontend, mixins reutilizables
6. **Escalabilidad:** Dos BDs, conexiones por request, cache de permisos

### Fortalezas tecnicas

- Constraint a nivel de BD (solo 1 guion en vivo)
- Sincronizacion optimista para bajo latencia
- Permisos flexibles (rol + individuales via UNION)
- Seed idempotente (seguro reiniciar multiples veces)
- Componentes reutilizables (head/footer/menu)

### Limitaciones conocidas (para discusion)

- Sin ORM (queries manuales dan control pero mas codigo)
- Sin rate limiting en login
- `usuarios_conectados` es in-memory (se pierde al reiniciar)
- `_registrar_bitacora()` duplicado en cada controlador

---

*Guia preparada para defensa tecnica del Sistema Itinerario.*
