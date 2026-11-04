# PROMPT MAESTRO — REDISEÑO PROFESIONAL DEL MÓDULO "EN VIVO"

## 0. TU MISIÓN

Estás trabajando sobre un sistema web existente.

Debes realizar un **rediseño profundo de UX/UI y optimización del módulo EN VIVO**, orientado principalmente a:

1. **Uso móvil vertical**
2. **Operación rápida y segura durante un juego**
3. **Experiencia visual moderna, deportiva, Cyber/Neon**
4. Mantener la sincronización en tiempo real mediante SocketIO
5. Mejorar considerablemente la claridad de estados
6. Mejorar el comportamiento cuando existe pérdida temporal de conexión
7. Mantener compatibilidad con el backend existente

NO debes interpretar este trabajo como "cambiar colores y hacer tarjetas bonitas".

Debes tratarlo como una **mejora integral de una herramienta operativa utilizada durante un evento deportivo en tiempo real**.

El resultado debe sentirse como una aplicación profesional de operación de eventos deportivos, pero sin destruir la lógica existente.

---

# 1. CONTEXTO DEL NEGOCIO

El módulo representa la operación de un show EN VIVO durante juegos de béisbol.

Un guion contiene una secuencia ordenada de elementos:

* animaciones
* música
* promociones
* dinámicas
* contenido para el público
* otros eventos

El operador utiliza esta pantalla durante el juego para avanzar el show.

Los usuarios conectados ven el estado actualizado en tiempo real.

El sistema actualmente tiene:

```text
pendiente
   ↓
en_curso
   ↓
completado
```

También existe:

```text
retroceso
```

y el backend contempla:

```text
reiniciado
```

El guion tiene estados:

```text
borrador
publicado
en_vivo
finalizado
```

Solo puede existir UN guion en estado `en_vivo`.

---

# 2. REGLA FUNDAMENTAL DEL SISTEMA

NO cambies la lógica de negocio.

La secuencia debe mantenerse.

Un operador NO puede saltar elementos.

Ejemplo:

```text
1 completado
2 completado
3 en_curso
4 pendiente
5 pendiente
```

El elemento 3 debe ser el único elemento operativo actual.

Cuando se completa:

```text
3 → completado
4 → en_curso
```

Nunca permitir:

```text
3 → 5
```

ni:

```text
3 → 4 → 5
```

de forma manual.

El flujo es estrictamente secuencial.

---

# 3. QUIÉN PUEDE OPERAR

Existen diferentes roles de usuarios.

Solo los usuarios administradores deben poder realizar el marcaje de eventos.

Los demás usuarios son espectadores del guion y deben ver exactamente el mismo estado actualizado.

IMPORTANTE:

No inventes un nuevo sistema de permisos.

No modifiques backend.

Utiliza los mecanismos de permisos/sesión existentes.

Si el frontend ya recibe información sobre permisos, utilízala.

Si actualmente el servidor rechaza una operación no autorizada, conserva ese comportamiento.

La seguridad real siempre pertenece al backend.

El frontend solamente debe mejorar la experiencia.

---

# 4. ARCHIVOS QUE DEBES CONOCER

Los archivos principales son:

```text
app/controller/en_vivo_controller.py
app/model/en_vivo_model.py
app/model/guion_model.py

app/view/en_vivo/index.html
app/view/en_vivo/vivo.html
app/view/en_vivo/log.html

app/__init__.py
```

La vista que debes rediseñar principalmente es:

```text
app/view/en_vivo/vivo.html
```

Actualmente contiene aproximadamente 611 líneas con CSS y JavaScript embebidos.

No asumas que el código funciona como crees.

Primero debes leer el archivo real.

---

# 5. REGLA ABSOLUTA: AUDITAR ANTES DE MODIFICAR

NO comiences modificando código inmediatamente.

Primero:

1. Lee `vivo.html` completo.
2. Lee `en_vivo_controller.py`.
3. Lee `en_vivo_model.py`.
4. Lee `guion_model.py`.
5. Revisa cómo se autentica la sesión.
6. Revisa cómo se determinan los permisos.
7. Revisa los eventos SocketIO.
8. Revisa cómo se construyen los datos enviados al template.
9. Revisa cómo se ejecuta el JavaScript actual.
10. Revisa cómo funciona el tema dark/light.
11. Revisa el logo existente.
12. Revisa si ya existe alguna utilidad JS/CSS reutilizable.

NO inventes estructuras que ya existen.

NO dupliques funciones.

NO reemplaces una solución existente sin entenderla.

---

# 6. RESTRICCIÓN DE ALCANCE

IMPORTANTE:

Este trabajo es de NIVEL 1.

Puedes modificar:

```text
app/view/en_vivo/vivo.html
```

incluyendo:

* HTML
* CSS
* JavaScript

Puedes utilizar recursos CDN ya compatibles con el proyecto si realmente son necesarios.

NO debes modificar:

```text
controller
model
database
API
SocketIO server
auth
permissions
```

NO agregues endpoints nuevos.

NO cambies el contrato existente.

NO cambies la estructura de la base de datos.

NO cambies las rutas existentes.

---

# 7. CONTRATO API QUE DEBES RESPETAR

El endpoint actual es:

```text
POST /en-vivo/api/sincronizar/<guion_id>
```

Recibe:

```json
{
  "estados": [
    {
      "id": 123,
      "estado": "completado"
    }
  ]
}
```

Los estados permitidos son:

```text
pendiente
en_curso
completado
reiniciado
null
```

La respuesta esperada es:

```json
{
  "success": true
}
```

NO cambies este contrato.

---

# 8. SOCKETIO ES CRÍTICO

La sincronización en tiempo real es una parte fundamental del módulo.

Actualmente el servidor emite:

```text
actualizar_estados
```

con:

```json
{
  "guion_id": "...",
  "estados": [
    {
      "id": 123,
      "estado": "completado"
    }
  ]
}
```

Todos los clientes conectados deben reflejar el cambio inmediatamente.

NO reemplaces SocketIO por polling.

NO hagas que la UI dependa de refrescar la página.

NO introduzcas retrasos artificiales.

La experiencia debe sentirse instantánea.

---

# 9. RECONEXIÓN SOCKETIO

Cuando SocketIO se reconecta:

1. Registrar nuevamente el usuario.
2. Solicitar:

```text
GET /en-vivo/api/estado-actual/<guion_id>
```

3. Reconciliar el estado local.
4. Actualizar la interfaz.
5. Resolver cualquier cambio pendiente de sincronización.

No dejar la UI mostrando un estado viejo después de una reconexión.

---

# 10. OBJETIVO VISUAL

La dirección visual debe ser:

# CYBER / NEON + SPORTS

Pero NO quiero una interfaz exageradamente futurista.

Debe sentirse:

* moderna
* deportiva
* tecnológica
* profesional
* rápida
* limpia
* elegante

Evitar:

* exceso de glow
* demasiados colores
* textos gigantes
* animaciones que distraigan
* exceso de bordes
* aspecto de videojuego

La inspiración debe ser:

```text
Sports technology
+
Live broadcast
+
Cyber/Neon
+
Professional SaaS
```

---

# 11. DARK / LIGHT

Mantener ambos modos.

El modo oscuro debe seguir siendo la experiencia principal.

Pero el modo claro debe ser realmente usable.

Problema actual:

Al pasar a blanco algunos textos pierden contraste.

Debes revisar TODOS los elementos:

* texto
* iconos
* bordes
* estados
* botones
* tarjetas
* badges
* estadísticas
* modal
* drawer
* toast
* indicador de conexión
* progreso

No basta con cambiar:

```text
background: white
```

Debe existir una verdadera jerarquía visual para light mode.

Mantener la persistencia del tema.

---

# 12. DISEÑO MOBILE-FIRST

La interfaz principal será utilizada en:

# TELÉFONO VERTICAL

Por lo tanto:

NO diseñes primero desktop y luego hagas un responsive improvisado.

Diseña primero:

```text
360px
390px
412px
430px
```

Después adapta a:

```text
tablet
desktop
```

Debe ser cómodo para operar con una mano.

No utilizar elementos demasiado pequeños.

No obligar al usuario a hacer zoom.

No utilizar tablas horizontales difíciles de desplazar.

---

# 13. JERARQUÍA VISUAL

No todos los eventos deben tener el mismo peso.

Debe existir una jerarquía clara:

```text
ACTUAL
↓
SIGUIENTE
↓
PENDIENTES
```

El evento `en_curso` debe ser notablemente más importante.

Pero NO debe ocupar media pantalla.

Debe existir una diferencia visual clara, no una diferencia absurda de tamaño.

Ejemplo conceptual:

```text
ACTUAL
┌──────────────────────────┐
│ 🟢 EN CURSO              │
│                          │
│ PROMO                    │
│ "Contenido..."           │
│                          │
│ ⏱ 00:43                  │
└──────────────────────────┘

SIGUIENTE
┌──────────────────────────┐
│ Música                    │
│ 00:30                     │
└──────────────────────────┘

PENDIENTE
┌──────────────────────────┐
│ Animación                 │
└──────────────────────────┘
```

---

# 14. MANTENER EL DOBLE TOQUE

La interacción principal debe seguir siendo:

```text
doble toque / doble clic
```

para completar el elemento actual.

NO reemplazar completamente esta interacción.

NO crear un botón gigante de completar.

Sí puedes mejorar su descubribilidad de manera sutil.

Por ejemplo:

* pequeño indicador visual
* microanimación
* icono
* tooltip/hint discreto
* feedback al completar

El diseño debe comunicar que el elemento actual es interactivo sin parecer una pantalla llena de botones.

---

# 15. RETROCEDER

El retroceso NO significa simplemente "volver al elemento anterior".

La intención es:

> "Marqué accidentalmente este evento como completado y todavía necesito ejecutarlo."

Por lo tanto:

Si:

```text
Evento A = completado
Evento B = en_curso
```

y se retrocede:

```text
Evento B → pendiente
Evento A → en_curso
```

El operador vuelve a ejecutar el evento anterior.

Mantener esta lógica.

El botón de retroceso puede ser:

* pequeño
* moderno
* claramente visible
* accesible
* con tooltip

No convertirlo en un botón dominante.

---

# 16. ELEMENTO ACTUAL

El elemento actual debe mostrar:

* estado
* contenido
* encargado
* duración
* hora programada
* cronómetro
* progreso
* sobretiempo si corresponde

Ejemplo:

```text
● EN CURSO

PROMOCIÓN ESPECIAL

"Vamos a regalar..."

Encargado
Keiver

Programado
4:36 PM

Duración
02:00

00:42

████████████░░░
```

---

# 17. CRONÓMETRO

Cuando un elemento entra en `en_curso`:

iniciar un contador visual.

La duración viene del backend en segundos.

IMPORTANTE:

`duracion_estimada` está expresada en segundos.

No confundas:

```text
120 segundos
```

con:

```text
120 minutos
```

Cuando el contador llega a cero:

NO detener el contador.

Debe comenzar a mostrar:

```text
+00:01
SOBRETIEMPO
```

Luego:

```text
+00:02
SOBRETIEMPO
```

etc.

El sobretiempo debe tener una señal visual clara pero no agresiva.

---

# 18. HORA

El campo `hora` viene desde MySQL como TIME y puede llegar a Python como `timedelta`.

NO intentes tratarlo ingenuamente como string.

El backend actual ya posee lógica de formateo.

Respeta el formato existente y no rompas la hora.

---

# 19. PROGRESO GLOBAL

Agregar una estadística sutil en vivo.

Ejemplo:

```text
SHOW
████████████░░░░ 68%

14 / 21
```

No convertirlo en un dashboard enorme.

Debe ser información secundaria.

Puede ubicarse en el header.

Mostrar:

```text
14 completados
7 restantes
68%
```

La información debe actualizarse inmediatamente.

---

# 20. ESTADO DE CONEXIÓN

Agregar un indicador pequeño:

```text
● CONECTADO
```

Cuando SocketIO esté activo.

Si se pierde:

```text
● SIN CONEXIÓN
```

Si está intentando:

```text
↻ RECONECTANDO...
```

No utilizar un modal que bloquee toda la aplicación.

Debe ser un indicador persistente y discreto.

---

# 21. MODO OFFLINE

Debe existir un modo degradado.

NO es necesario implementar PWA.

Si se pierde temporalmente la conexión:

1. La UI no debe quedar congelada.
2. El estado local debe mantenerse.
3. Las acciones del administrador pueden quedar en una cola local.
4. La interfaz debe mostrar claramente:

```text
SIN CONEXIÓN
Cambios pendientes: 2
```

5. Al recuperar conexión:

   * reconectar SocketIO
   * consultar estado actual
   * comparar estado local
   * intentar sincronizar cambios pendientes
   * actualizar interfaz

IMPORTANTE:

No inventar una sincronización compleja que contradiga el backend.

Si existe riesgo de conflicto:

```text
⚠ Cambio remoto detectado
```

debe mostrarse y prevalecer el estado confirmado por el servidor cuando corresponda.

No perder silenciosamente acciones.

---

# 22. CONFLICTOS ENTRE OPERADORES

Puede ocurrir que otro administrador modifique un elemento.

Cuando el SocketIO notifique un cambio remoto:

si el cambio no fue originado localmente:

mostrar un feedback sutil:

```text
Otro operador actualizó el guion
```

No mostrar alertas molestas constantemente.

No utilizar SweetAlert para cada actualización SocketIO.

Utilizar toast/notificación pequeña.

---

# 23. PRESENCIA

Mantener el indicador:

```text
N viendo
```

porque puede haber hasta aproximadamente 30 usuarios conectados.

No hacer que esta información domine la pantalla.

Ejemplo:

```text
👥 12 viendo
```

---

# 24. ENCARGADOS

Mantener los encargados.

Agregar un filtro discreto:

```text
Todos
Mis eventos
```

Si existen varios encargados, permitir seleccionar uno.

Pero:

IMPORTANTE:

Filtrar visualmente NO debe alterar el estado real ni la secuencia.

Nunca permitir que el filtro haga parecer que el siguiente evento de la secuencia es otro diferente.

---

# 25. ANIMACIONES

Utilizar animaciones deportivas/espectaculares, pero profesionales.

Ejemplos:

Cuando un elemento pasa a `en_curso`:

```text
slide/fade + glow
```

Cuando se completa:

```text
check + transición
```

Cuando aparece el siguiente:

```text
entrada suave
```

Cuando el show llega al 100%:

una celebración breve.

NO utilizar confeti excesivo.

NO usar animaciones permanentes que distraigan.

Las animaciones deben respetar:

```text
prefers-reduced-motion
```

---

# 26. ESTADOS VISUALES

Crear una jerarquía mucho mejor para:

### PENDIENTE

Neutro.

### EN CURSO

Destacado:

* neon
* glow moderado
* borde
* indicador vivo
* cronómetro

### COMPLETADO

Atenuado.

Pero debe seguir siendo legible.

### REINICIADO

Si aparece, debe tener un tratamiento visual coherente.

---

# 27. HEADER

El header debe ser compacto en móvil.

Debe conservar:

* volver
* nombre del guion
* fecha
* estado EN VIVO
* progreso
* viendo
* tema
* finalizar

Pero reorganizarlo para que no parezca una barra de escritorio aplastada.

En móvil puede utilizar:

```text
Fila 1:
← Nombre del guion        🔴

Fila 2:
14/21    68%    👥 12

Fila 3:
Tema / Finalizar
```

Siempre manteniendo acceso a las acciones importantes.

---

# 28. FINALIZAR

Mantener la acción de finalizar.

Pero mejorar la confirmación.

Antes de finalizar mostrar:

```text
¿Finalizar guion?

Completados: 14
Pendientes: 7

Esta acción finalizará el show actual.
```

No modificar la lógica backend.

No cambiar el comportamiento de reset existente.

---

# 29. LOG

El log actualmente está en otra vista.

NO es obligatorio rediseñarlo completamente.

Pero desde `vivo.html` puedes crear un drawer/panel lateral o modal que cargue/abra el log existente si es posible sin modificar backend.

Si hacerlo requiere backend nuevo:

NO hacerlo.

Priorizar el rediseño de la operación.

---

# 30. DESKTOP

Aunque mobile es prioridad, desktop debe quedar excelente.

En desktop:

* utilizar mejor el espacio horizontal
* permitir ver más elementos
* mantener claramente destacado el actual
* evitar filas excesivamente altas
* conservar la lectura secuencial

No convertir desktop en una copia gigante de móvil.

---

# 31. RESPONSIVE

Crear breakpoints razonables.

Verificar especialmente:

```text
320px
360px
375px
390px
412px
430px
768px
1024px
1280px
1440px
```

No asumir que 768px es "mobile terminado".

---

# 32. ACCESIBILIDAD

Mejorar:

* contraste
* focus visible
* aria-label
* botones accesibles
* estados anunciables
* navegación por teclado

Atajos recomendados:

```text
Space → completar actual
R → retroceder
```

Pero:

NO quitar el doble clic.

Los atajos deben estar disponibles solamente para usuarios que puedan operar.

---

# 33. SEGURIDAD

No confiar en JavaScript para seguridad.

Nunca asumir:

```javascript
if (isAdmin) {
   ...
}
```

como única protección.

El backend sigue siendo autoridad.

No introducir endpoints inseguros.

No exponer datos innecesarios.

No modificar CSRF existente.

---

# 34. RENDIMIENTO

La aplicación puede tener hasta aproximadamente 30 personas viendo simultáneamente.

Optimiza para:

* pocos reflows
* pocas operaciones DOM
* no recrear toda la lista ante cada evento SocketIO
* actualizar solamente los elementos afectados
* evitar timers duplicados
* limpiar listeners
* limpiar intervalos
* evitar memory leaks
* evitar animaciones costosas

Especialmente:

NO reconstruir todo el DOM cada segundo para actualizar el contador.

El cronómetro debe actualizar solamente el elemento actual.

---

# 35. SOCKETIO Y DOM

Cuando llegue:

```text
actualizar_estados
```

NO hagas:

```text
renderEverything()
```

si no es necesario.

Haz:

```text
updateElement(id)
updateCounters()
updateCurrentTimer()
```

y solamente los componentes necesarios.

---

# 36. OPTIMIZACIÓN DEL CRONÓMETRO

Debe existir un único timer activo para el elemento actual.

Cuando cambia el elemento:

```text
clearInterval(previousTimer)
startTimer(newElement)
```

Nunca permitir múltiples timers ejecutándose simultáneamente.

---

# 37. DOBLE TOQUE

Implementar correctamente:

Desktop:

```text
dblclick
```

Mobile:

detección robusta de doble tap.

Evitar:

* doble ejecución
* zoom accidental
* click fantasma
* completar dos veces
* conflictos con scroll

Agregar debounce.

---

# 38. FEEDBACK DE SINCRONIZACIÓN

Después de una operación:

mostrar un indicador pequeño:

```text
✓ Guardado
```

o:

```text
↻ Sincronizando...
```

o:

```text
⚠ Pendiente
```

Nunca bloquear la pantalla.

---

# 39. NO ABUSAR DE SWEETALERT

SweetAlert debe reservarse para:

* finalizar
* errores importantes
* situaciones realmente relevantes

Para eventos normales usar:

* toast
* microfeedback
* animaciones

---

# 40. LOGO

El sistema ya posee un logo.

NO inventes uno.

Busca en el proyecto dónde está almacenado y reutilízalo.

No agregues una imagen externa si el logo existente puede utilizarse.

---

# 41. NO CAMBIAR EL NOMBRE DEL GUION

No es necesario mostrar información del partido.

El nombre del guion es suficiente.

Puedes mejorar la presentación del nombre y fecha.

---

# 42. NO CREAR MODO TV AHORA

No implementar todavía un modo TV.

No crear una arquitectura innecesaria para ello.

La prioridad es:

```text
mobile
operador
desktop
```

El diseño puede quedar preparado para futura expansión, pero no implementar esa funcionalidad ahora.

---

# 43. QUÉ NO HACER

NO:

* cambiar backend
* cambiar API
* cambiar modelos
* cambiar DB
* cambiar SocketIO server
* crear endpoints
* eliminar SocketIO
* eliminar doble toque
* permitir saltos
* crear botones gigantes
* convertirlo en PWA
* crear modo TV
* instalar frameworks innecesarios
* agregar build pipeline
* reemplazar Bootstrap si no es necesario
* crear cientos de dependencias
* reescribir toda la aplicación

---

# 44. FASES DE TRABAJO

Debes trabajar obligatoriamente en fases.

## FASE 1 — AUDITORÍA

Analizar:

* archivos
* HTML
* CSS
* JS
* endpoints
* SocketIO
* permisos
* datos
* eventos
* tema
* logo

NO modificar código.

Al finalizar entrega:

```text
AUDITORÍA
Problemas encontrados
Riesgos
Oportunidades
Archivos que se modificarán
```

---

## FASE 2 — PLAN UX

Crear una propuesta de:

* estructura
* jerarquía
* mobile
* desktop
* estados
* interacción
* cronómetro
* offline
* conexión
* filtros
* estadísticas

NO programar todavía.

---

## FASE 3 — PLAN VISUAL

Definir:

* colores
* tokens CSS
* tipografía
* spacing
* bordes
* sombras
* glow
* estados
* dark
* light
* responsive

Mantener Cyber/Neon deportivo.

---

## FASE 4 — IMPLEMENTACIÓN

Modificar únicamente:

```text
app/view/en_vivo/vivo.html
```

Mantener funcionalidad existente.

---

## FASE 5 — SOCKETIO

Verificar:

* sincronización inmediata
* reconexión
* múltiples usuarios
* actualización parcial
* conflictos
* estado local

---

## FASE 6 — MOBILE

Probar especialmente:

```text
360x800
390x844
412x915
```

Verificar:

* doble tap
* scroll
* botones
* header
* cronómetro
* cards
* filtros
* tema
* legibilidad

---

## FASE 7 — DESKTOP

Probar:

```text
1280
1440
1920
```

---

## FASE 8 — OFFLINE

Simular:

```text
online
↓
offline
↓
marcar evento
↓
estado pendiente
↓
online
↓
reconectar
↓
sincronizar
```

No perder acciones.

---

## FASE 9 — TESTING

Ejecutar:

```bash
venv/bin/python run.py
```

y:

```bash
venv/bin/pytest -q
```

Además realizar pruebas manuales.

---

# 45. PRUEBA MULTIUSUARIO

Abrir:

```text
Navegador A
Navegador B
Navegador C
```

con el mismo guion.

En A:

```text
doble clic/tap
```

B y C deben reflejarlo inmediatamente.

Probar también:

```text
A completa
B retrocede
C observa
```

---

# 46. PRUEBA DE ERROR

Probar:

* servidor lento
* API devuelve error
* SocketIO desconectado
* reconexión
* doble toque rápido
* doble toque accidental
* usuario sin permiso
* completar cuando ya está completado
* retroceder
* finalizar
* recargar
* cambiar tema
* cambiar orientación del teléfono

---

# 47. CRITERIO DE ÉXITO

El trabajo se considera exitoso solamente si:

### UX

El operador puede entender inmediatamente:

```text
qué está ocurriendo
qué debe hacer
qué viene después
cuánto tiempo queda
```

sin leer instrucciones.

### Mobile

La interfaz funciona perfectamente en vertical.

### Tiempo real

Los cambios se reflejan inmediatamente mediante SocketIO.

### Visual

La interfaz parece un producto profesional.

### Estados

Es imposible confundir:

```text
pendiente
en_curso
completado
```

### Seguridad

Solo usuarios autorizados pueden operar.

### Backend

El backend no fue modificado.

### Performance

La interfaz sigue fluida con aproximadamente 30 usuarios conectados.

### Offline

La pérdida temporal de conexión no destruye la experiencia ni pierde silenciosamente acciones.

---

# 48. DOCUMENTACIÓN FINAL

Al finalizar debes entregar un resumen:

```text
CAMBIOS REALIZADOS

1.
2.
3.

ARCHIVOS MODIFICADOS

1.

COMPORTAMIENTO SOCKETIO

...

MODO OFFLINE

...

RESPONSIVE

...

TESTS EJECUTADOS

...

PROBLEMAS PENDIENTES

...
```

Además debes indicar explícitamente:

```text
Backend modificado: NO
API modificada: NO
Database modificada: NO
SocketIO server modificado: NO
```

---

# 49. REGLA FINAL

NO quiero una simple "limpieza visual".

Quiero una evolución real de la experiencia de operación.

El resultado debe sentirse:

```text
ANTES
lista de eventos
↓
AHORA
centro de control operativo en vivo
```

Pero manteniendo:

* la lógica secuencial
* doble toque
* retroceso
* SocketIO
* permisos
* API
* backend
* dark/light
* datos existentes

Primero piensa.

Después audita.

Después presenta el plan.

Después implementa.

Después prueba.

NO improvises.
