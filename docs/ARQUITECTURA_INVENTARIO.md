# Arquitectura del Módulo Inventario

Guía de funcionamiento, conexiones y decisiones técnicas del módulo `inventario`, adaptado del patrón PHP `gestionActivos`.

---

## 1. Vista General

El módulo `inventario` es un CRUD de activos/recursos con los siguientes componentes:

| Capa | Archivo | Rol |
|---|---|---|
| Modelo | `app/model/inventario_model.py` | Lógica de negocio + acceso a DB |
| Controlador | `app/controller/inventario_controller.py` | Rutas, auth, dispatch AJAX |
| Vista | `app/view/inventario/dashboard.html` | SPA con DataTable + 3 modales |
| JS principal | `app/static/js/GestionInventario.js` | DataTable + CRUD asíncrono |
| Validación | `app/static/js/validaciones/GestionInventarioValidacion.js` | Solo composición de formularios |

Está diseñado para imitar la arquitectura del PHP original: controlador procedural sin clases, setters uno a uno con los campos del formulario, y respuestas JSON con nombres de columna PHP (`id_activo`, `Nombre_Activo`, etc.).

---

## 2. Flujo MVC Completo

### 2.1. GET — Carga inicial de la página

```
Usuario → GET /inventario/
                │
                ▼
         controller.dashboard()
                │
                ├─ Crea InventarioModel()
                ├─ Crea TipoRecursoModel()
                ├─ request.method == 'GET' → no entra en bloque POST
                │
                ├─ Llama obj_model.obtener_tipos()
                ├─ Llama obj_model.obtener_estados()
                │
                ▼
         render_template('inventario/dashboard.html',
                tipos_activos=...,
                id_ubicacion=...,
                mensaje=None)
                │
                ▼
         Template renderiza:
           - <select> options con loop {% for t in tipos %}
           - Input hidden csrf_token
           - <table id="activoTable"> con <tbody></tbody> VACÍO
                │
                ▼
         GestionInventario.js (ES module)
           - initActivoTable() → DataTable AJAX
           - Vincula eventos blur (verificar_nombre)
           - Vincula modales (formulario_activo, formulario_tipo_activo, eliminar)
```

**¿Por qué el `<tbody>` está vacío?** Porque se imita el patrón PHP: el template renderiza la estructura HTML, y el JavaScript llena los datos vía AJAX. Esto separa la carga de la página (rápida) de la carga de datos (asíncrona).

**¿Por qué los dropdowns se renderizan server-side y no vía AJAX?** Porque los selects (`tipo`, `ubicacion`) son datos pequeños y estáticos que nunca cambian durante la sesión del usuario. Cargarlos vía AJAX añadiría latencia innecesaria al abrir un modal.

### 2.2. POST AJAX — Operaciones CRUD

```
Usuario → click en botón "Guardar"
                │
                ▼
         GestionInventario.js
           - validaFormularioActivo() → validación cliente
           - fetch('/inventario/', {
               method: 'POST',
               body: new URLSearchParams({
                 registrar: 'true',
                 csrf_token: getCSRF(),
                 Nombre: ...,
                 Descripcion: ...,
                 id_tipo_activo: ...,
                 Fecha_adquisicion: ...
               })
             })
                │
                ▼
         controller.dashboard()
           - before_request:
               if not current_user.is_authenticated → 401 JSON
               if not tiene_permiso('inventario.create') → 403 JSON
           - request.method == 'POST'
           - request.form.get('registrar') → True
                │
                ├─ obj_model = InventarioModel()
                ├─ obj_model.set_nombre(request.form['Nombre'])
                ├─ obj_model.set_descripcion(...)
                ├─ obj_model.set_tipo_id(...)
                ├─ obj_model.set_fecha_compra(...)
                │
                ├─ resultado = obj_model.confirmar_registro()
                │     │
                │     ├─ _validar_datos_recurso()
                │     │   └─ valida con ValidacionesMixin
                │     ├─ si falla → return {'mensaje': 'Error: ...'}
                │     └─ si ok → _registrar()
                │           └─ INSERT en recursos + return {'mensaje': 'Registrado'}
                │
                ▼
         jsonify(resultado) → respuesta JSON
                │
                ▼
         GestionInventario.js
           - const data = await res.json()
           - if (data.error) → Swal.error
           - if (data.mensaje.startswith('Error')) → Swal.error
           - else → Swal.success + recarga DataTable + cierra modal
```

**¿Por qué `request.form.get('registrar')` en vez de `request.json['registrar']`?** Porque el frontend envía `application/x-www-form-urlencoded` (vía `URLSearchParams`), NO `application/json`. Esto es intencional: imita el comportamiento de un formulario HTML tradicional PHP. Flask recibe estos datos en `request.form`, no en `request.json`.

**¿Por qué `confirmar_registro()` en dos fases?** Porque el PHP original separa validación de persistencia. `_validar_datos_recurso()` chequea reglas de negocio (campos requeridos, longitudes, fechas) y `_registrar()` hace el INSERT. Si la validación falla, nunca se llega a la DB.

### 2.3. POST Tradicional — Rutas secundarias

```
Usuario → GET /inventario/crear
                │
                ▼
         render_template('inventario/crear.html') → formulario HTML
                │
                ▼
         Usuario llena y hace POST /inventario/crear
                │
                ├─ obj_model.set_nombre(request.form['Nombre'])
                ├─ resultado = obj_model.confirmar_registro()
                │
                ├─ si éxito → flash + redirect('/inventario/')
                └─ si error → flash + redirect back
```

Estas rutas (`crear`, `editar`, `eliminar`, `asignar`) existen por **compatibilidad con vistas existentes**. El flujo principal hoy es el AJAX vía `dashboard()`, pero estas rutas permiten que enlaces directos y formularios tradicionales sigan funcionando.

---

## 3. Conexiones del MVC Explicadas

### 3.1. Controlador procedural (sin clases)

**¿Por qué sin clases?** El PHP original usa funciones sueltas, no clases. Cada función crea su propio `obj_model = InventarioModel()` local. Esto evita efectos secundarios entre peticiones (no hay estado compartido en el objeto controlador).

```python
# Bien — cada función tiene su instancia
def dashboard():
    obj_model = InventarioModel()
    ...

# Mal — estado compartido no es seguro en Flask (multi-hilo)
class InventarioController:
    def __init__(self):
        self.obj_model = InventarioModel()  # no hacer
```

### 3.2. Modelo con setters + dos fases

**¿Por qué setters?** El PHP original asigna valores uno a uno desde `$_POST`. Los setters permiten:
- Validar por campo (aunque hoy se hace en `_validar_datos_recurso`)
- Agregar aliases PHP-compatibles (`set_fecha_adquisicion` → `set_fecha_compra`)
- Consistencia con el patrón PHP

**¿Por qué `confirmar_registro()` → `_validar_datos_recurso()` → `_registrar()`?** Porque así funciona el PHP original: primero validas todas las reglas de negocio, y si todo ok, persistes. Si la validación falla, nunca tocas la DB.

### 3.3. `try/except` en todos los métodos DB

**¿Por qué?** Porque la DB puede fallar (conexión perdida, timeout, constraint violation). En un sistema PHP típico, los errores silenciosos son comunes. Python lanza excepciones que, sin manejo, matan la petición. Cada método debe retornar un valor seguro:

| Operación | Retorno en éxito | Retorno en error |
|---|---|---|
| INSERT/UPDATE/DELETE | `True` o `{'mensaje': '...'}` | `False` o `{'mensaje': 'Error: ...'}` |
| SELECT (lista) | `[{...}, {...}]` | `[]` |
| SELECT (uno) | `{...}` | `None` |
| COUNT | `5` | `0` |

---

## 4. AJAX

### 4.1. `request.method == 'POST'` en vez de `request.is_json`

Cuando el frontend envía `URLSearchParams`, el Content-Type es `application/x-www-form-urlencoded; charset=UTF-8`. Para Flask, `request.is_json` es `False` y `request.json` es `None`. Los datos están en `request.form`.

```javascript
// Frontend — Content-Type es form-urlencoded
body: new URLSearchParams({ registrar: 'true', Nombre: 'Micrófono' })

// Backend — así se lee
request.form.get('registrar')   // → 'true'
request.form['Nombre']          // → 'Micrófono'
request.is_json                 // → False (NO usar)
```

**¿Por qué no enviar JSON directamente?** Porque el PHP original no usa JSON. El patrón es enviar datos como si fueran de un formulario HTML. Además, Flask-WTF valida CSRF contra `request.form['csrf_token']`, no contra `request.json`.

### 4.2. DataTable AJAX

```javascript
activoTable = $('#activoTable').DataTable({
    ajax: {
        url: '/inventario/',
        type: 'POST',
        data: function(d) {
            d.consultar = true;
            d.csrf_token = getCSRF();
        },
        dataSrc: ''  // la respuesta es directamente el array, no {data: [...]}
    },
    columns: [
        { data: 'id_activo' },         // PHP column name
        { data: 'Nombre_Activo' },     // PHP column name
        ...
    ]
});
```

**Flujo:**
1. DataTable llama a `/inventario/` con parámetros extras (`consultar`, `csrf_token`)
2. Controller ve `request.form.get('consultar')` → llama a `obj_model.listar()`
3. `listar()` ejecuta SELECT, mapea filas a objetos con nombres PHP
4. Controller retorna `jsonify(lista)` — devuelve un array plano
5. DataTable recibe `[{id_activo: 1, Nombre_Activo: ...}, ...]`
6. `dataSrc: ''` le dice a DataTable que el array está en la raíz, no en `response.data`

### 4.3. `URLSearchParams` en vez de `JSON.stringify`

```javascript
// Cómo se hace en inventario
body: new URLSearchParams({
    registrar: 'true',
    Nombre: nombre,
    csrf_token: getCSRF()
})

// Cómo NO se hace
body: JSON.stringify({
    registrar: true,
    Nombre: nombre,
    csrf_token: getCSRF()
})
headers: { 'Content-Type': 'application/json' }
```

**¿Por qué?** `URLSearchParams` genera `application/x-www-form-urlencoded`, que es lo que un formulario HTML enviaría. Esto permite que Flask-WTF valide el CSRF token desde `request.form['csrf_token']`. Con JSON, el token estaría en `request.json['csrf_token']`, que Flask-WTF no lee.

---

## 5. CSRF

### 5.1. El problema original

Flask-WTF (`CSRFProtect`) intercepta **todas** las peticiones POST antes de que lleguen al controlador. Si el token falta o es inválido, retorna una página HTML 400. Esto significa que:

```
Antes:
  CSRFProtect.before_request → ¿token válido?
    ↓ NO → retorna HTML 400 (nunca llega a inventario_controller)
    ↓ SÍ → inventario_controller.before_request → dashboard()

Con el fix:
  Token se envía en el BODY (csrf_token en URLSearchParams)
  CSRFProtect lo lee de request.form['csrf_token']
  → todo ok → llega a nuestra lógica
```

### 5.2. Configuración

```python
# app/__init__.py
csrf = CSRFProtect()
csrf.init_app(app)
WTF_CSRF_TIME_LIMIT = None  # tokens no expiran
csrf.exempt(en_vivo_bp)      # SocketIO POSTs no llevan CSRF
```

### 5.3. Reglas por capa

| Dónde | Cómo se envía |
|---|---|
| Formulario HTML | `<input type="hidden" name="csrf_token" value="{{ csrf_token() }}">` |
| Fetch POST | `params.append('csrf_token', getCSRF())` en el body |
| DataTable AJAX | `data: function(d) { d.csrf_token = getCSRF(); }` |
| `before_request` | Retorna `jsonify({error: ...})` en vez de redirect |

**`getCSRF()`** lee el valor del input oculto renderizado en el template:
```javascript
function getCSRF() {
    return document.querySelector('input[name="csrf_token"]').value || '';
}
```

### 5.4. ¿Por qué header `X-CSRFToken` no funciona?

Flask-WTF **sí** lee el header `X-CSRFToken`. El problema era que el `before_request` de Flask-WTF se ejecutaba **antes** que el del blueprint. Cuando CSRF fallaba, retornaba HTML 400 antes de que nuestro `before_request` pudiera interceptar y retornar JSON. Al poner el token en el body, CSRFProtect lo valida correctamente y la petición continúa a nuestra lógica.

---

## 6. Validaciones

### 6.1. Capa global (`RegExp.js` + `validacion.js`)

```
js/RegExp.js        → 25 patrones regex compartidos
js/validacion.js    → 23 validadores unitarios (validarNombre, validarFecha, etc.)
```

**`RegExp.js`** contiene solo expresiones regulares, sin lógica:

```javascript
export const regExp = {
    nombre: /^[A-Za-zÁÉÍÓÚáéíóúÑñ_\-.,;:/\*\+\$ ]{2,100}$/,
    fecha: /^\d{4}-\d{2}-\d{2}$/,
    select: /.+/,
    ...
};
```

**`validacion.js`** contiene validadores que usan los regex y manipulan clases CSS:

```javascript
export function validarNombre(campo) {
    const valido = regExp.nombre.test(campo.value.trim());
    validarCampo(campo, valido, 'El nombre debe tener entre 2 y 100 caracteres');
    return valido;
}
```

Cada validador:
1. Ejecuta el regex contra el valor del campo
2. Añade `is-valid` o `is-invalid` (Bootstrap)
3. Retorna `true/false`

### 6.2. Capa de módulo (solo composición)

`GestionInventarioValidacion.js` NO redefinie validadores. Solo los **compone**:

```javascript
import { validarNombre, validarDescripcion, validarFechaOpcional, validarSelect } from '../validacion.js';

export function validarFormularioActivo() {
    return (
        validarSelect(document.getElementById('id_tipo_activo')) &&
        validarSelect(document.getElementById('id_ubicacion')) &&
        validarNombre(document.getElementById('Nombre')) &&
        validarDescripcion(document.getElementById('Descripcion')) &&
        validarFechaOpcional(document.getElementById('Fecha_adquisicion'))
    );
}
```

**¿Por qué este diseño?** Porque los validadores unitarios son genéricos (nombre, email, fecha, select). Si cada módulo redefiniera `validarNombreActivo`, `validarNombreTipo`, etc., tendríamos 10 formas distintas de validar un nombre. Centralizándolos, cualquier cambio en el regex de nombre se aplica a todos los módulos.

### 6.3. ¿Cuándo agregar algo a la capa global?

Si un módulo necesita un validador que no existe:
1. Agregar el regex a `RegExp.js`
2. Agregar el validador a `validacion.js`
3. Usarlo desde `GestionXValidacion.js`

Así queda disponible para cualquier otro módulo futuro.

---

## 7. SocketIO

**SocketIO NO está en el módulo inventario.** Es un error común asumir que "el módulo se integra con SocketIO".

### 7.1. ¿Dónde está SocketIO realmente?

**`app/__init__.py`** — Solo para tracking de usuarios conectados:

```python
socketio = SocketIO(cors_allowed_origins="*")
usuarios_conectados = {}  # sid → {user_id, nombre, pagina}

@socketio.on('connect')
def handle_connect(): pass  # solo acepta conexión

@socketio.on('registrar_usuario')
def handle_registrar(data):
    usuarios_conectados[request.sid] = {
        'user_id': data['user_id'],
        'nombre': data['nombre']
    }
    _emit_usuarios_actualizados()

@socketio.on('disconnect')
def handle_disconnect():
    usuarios_conectados.pop(request.sid, None)
    _emit_usuarios_actualizados()
```

Esto alimenta un widget de "usuarios en línea" en el layout general.

**`en_vivo_controller.py`** — Para sincronización de guiones en vivo:
```python
socketio.emit('actualizar_estados', {'guion_id': id, 'estados': estados})
```

### 7.2. ¿Por qué inventario no usa SocketIO?

Inventario es un CRUD tradicional. Cuando un usuario crea/edita/elimina un recurso, el DataTable se recarga vía `activoTable.ajax.reload()`. Eso es suficiente. No hay necesidad de tiempo real.

Si en el futuro quisieras que dos usuarios vean cambios en vivo sin refrescar (ej. un almacén donde todos ven el stock actualizarse automáticamente), ahí conectarías SocketIO al módulo. Pero hoy no es el caso.

### 7.3. ¿Cómo se arranca el servidor?

```python
# run.py
socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
```

Se usa `socketio.run()` en vez de `app.run()` porque SocketIO necesita su propio loop de eventos.

---

## 8. Bitácora

### 8.1. Modelos disponibles

En `app/model/bitacora_model.py`:

| Modelo | Tabla | Propósito |
|---|---|---|
| `SesionModel` | `seguridad.sesiones_usuario` | Inicio/fin de sesión con IP, user-agent, duración |
| `ActividadModel` | `seguridad.actividad_usuario` | Acciones del usuario: tipo, módulo, detalle, página |
| `CambioModel` | `seguridad.cambios_por_modulo` | Cambios campo por campo (valor anterior → nuevo) |
| `ErrorModel` | `seguridad.errores_aplicacion` | Errores con traceback completo |

### 8.2. ¿Quién la usa hoy?

- **`auth_controller.py`** — Al login/logout registra sesión y actividad
- **`en_vivo_controller.py`** — Al iniciar/finalizar/sincronizar guion registra actividad

### 8.3. ¿Por qué NO está en inventario?

**Porque no se ha implementado aún.** El módulo inventario no registra actividad en la bitácora. Cuando se complete, debería llamarse algo como:

```python
from app.model.bitacora_model import ActividadModel
ActividadModel().registrar(
    id_usuario=current_user.id,
    tip_accion='create',
    modulo='inventario',
    detalle=f"Creó recurso: {nombre}",
    pagina=request.path
)
```

Capturaría también los cambios con `CambioModel().registrar()` para tener un historial detallado de cada modificación.

Esto implicaría agregar un import del `bitacora_model` en el controlador y llamarlo en cada operación CRUD (registrar, modificar, eliminar).

---

## 9. Sesiones y Permisos

### 9.1. Sesión del usuario

```python
# app/__init__.py
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

@login_manager.user_loader
def load_user(user_id):
    return UsuarioModel().obtener_por_id(int(user_id))
```

Cada request, Flask-Login carga al usuario desde la DB y lo deja disponible en `current_user`.

**Objeto `Usuario`** implementa la interfaz de Flask-Login:
- `is_authenticated` → `True`
- `is_active` → `self.activo`
- `is_anonymous` → `False`
- `get_id()` → `str(self.id)`

### 9.2. Permisos (dos patrones)

**Patrón nuevo — `before_request` + `PERMISSION_MAP`:**

```python
PERMISSION_MAP = {
    'inventario.dashboard': 'inventario.view',
    'inventario.crear': 'inventario.create',
    'inventario.eliminar': 'inventario.delete',
}

@bp.before_request
def verificar_acceso():
    if not current_user.is_authenticated:
        if request.method == 'POST':
            return jsonify({'error': 'No autenticado'}), 401
        return redirect(url_for('auth.login'))
    permiso = PERMISSION_MAP.get(request.endpoint)
    if permiso and not current_user.tiene_permiso(permiso):
        if request.method == 'POST':
            return jsonify({'error': 'Sin permiso'}), 403
        flash('Sin permiso', 'danger')
        return redirect(url_for('dashboard.panel'))
```

**¿Por qué `before_request` en vez de decoradores?** Porque:
- Centraliza la lógica de auth en un solo lugar
- Retorna JSON para AJAX (POST) y HTML para navegación (GET)
- No hay riesgo de olvidar un decorador en una ruta nueva

**Patrón viejo — decoradores:**

```python
@login_required
@permiso_requerido('inventario.view')
def dashboard():
    ...
```

Este patrón aún existe en otros módulos (`bitacora`, `en_vivo`). Los módulos nuevos deben usar el patrón `before_request`.

### 9.3. `tiene_permiso()` con caché

```python
def tiene_permiso(self, codigo):
    if self.rol in ('Superadmin', 'Administrador'):
        return True  # admins siempre pasan
    if self._permisos_cache is None:
        self._permisos_cache = UsuarioPermisoModel().obtener_permisos_usuario(self.id, self.rol)
    return codigo in self._permisos_cache
```

La caché se calcula una vez por request. La consulta SQL hace un UNION entre permisos del rol y permisos individuales del usuario, permitiendo que un usuario tenga más (o menos) permisos que su rol base.

### 9.4. Catálogo de permisos

Definido en `app/model/rol_model.py`:

| Código | Módulo | Descripción |
|---|---|---|
| `inventario.view` | inventario | Ver inventario de recursos |
| `inventario.create` | inventario | Crear recursos |
| `inventario.edit` | inventario | Editar recursos |
| `inventario.delete` | inventario | Eliminar recursos |
| `inventario.assign` | inventario | Asignar y devolver recursos |

---

## 10. Errores Comunes Ya Corregidos

| Error | Causa | Fix |
|---|---|---|
| CSRF retorna HTML 400 en vez de JSON | Token en header `X-CSRFToken`, no en body | Mover token al body como `csrf_token` |
| `request.is_json` es `False` | Frontend envía form-urlencoded, no JSON | Usar `request.method == 'POST'` + `request.form` |
| `AttributeError: 'InventarioModel' has no attribute 'set_id_tipo'` | Controlador llama a `set_id_tipo()` pero el modelo tiene `set_tipo_id()` | Agregar alias `set_id_tipo(self, v): self.set_tipo_id(v)` |
| DataTable recibe HTML en vez de JSON | `before_request` retorna redirect en POST | Retornar `jsonify({error: ...})` para POST |
| Módulo duplica validadores de `validacion.js` | Cada archivo de validación redefinía `validarNombre`, `validarSelect` etc. | Reducir a solo compose functions importando de `validacion.js` |

---

## 11. Resumen de Flujo Completo

```
                   ┌──────────────────────────────────────┐
                   │           NAVEGADOR                   │
                   │                                      │
                   │  GestionInventario.js                 │
                   │    ├─ initActivoTable() → DataTable   │
                   │    ├─ blur → verificar_nombre()      │
                   │    └─ CRUD → fetch POST              │
                   └──────────┬───────────────────────────┘
                              │ GET / POST
                              ▼
                   ┌──────────────────────────────────────┐
                   │    before_request                     │
                   │      ¿autenticado?                    │
                   │      ¿tiene permiso?                  │
                   └──────────┬───────────────────────────┘
                              │ pasa
                              ▼
                   ┌──────────────────────────────────────┐
                   │    dashboard() — dispatcher           │
                   │                                      │
                   │  GET → render_template + dropdowns    │
                   │  POST → según campo del form:         │
                   │    consultar → obj_model.listar()     │
                   │    registrar → obj_model.confirmar()  │
                   │    editar → obj_model.modificar()     │
                   │    eliminar → obj_model.eliminar()    │
                   └──────────┬───────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────────────────┐
                   │    InventarioModel                    │
                   │      ├─ Setters (set_nombre, etc.)   │
                   │      ├─ _validar_datos_recurso()     │
                   │      ├─ confirmar_registro()          │
                   │      │    └─ _registrar() → INSERT   │
                   │      ├─ listar() → SELECT            │
                   │      └─ try/except en todo           │
                   └──────────┬───────────────────────────┘
                              │
                              ▼
                   ┌──────────────────────────────────────┐
                   │    Respuesta JSON / HTML              │
                   │                                      │
                   │  POST → jsonify({mensaje, ...})      │
                   │  GET  → render_template()            │
                   └──────────────────────────────────────┘
```
