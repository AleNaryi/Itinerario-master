# PROMPT — CREAR SISTEMA DE SKILLS PARA OPENCode

Quiero que prepares el proyecto para trabajar de forma consistente con OpenCode.

Antes de crear las skills, inspecciona el repositorio y entiende realmente cómo funciona el módulo:

```text
app/view/en_vivo/vivo.html
app/controller/en_vivo_controller.py
app/model/en_vivo_model.py
app/model/guion_model.py
app/view/en_vivo/index.html
app/view/en_vivo/log.html
app/__init__.py
```

NO inventes información.

Las skills deben servir específicamente para mejorar y mantener el módulo EN VIVO.

---

# OBJETIVO

Crear skills reutilizables bajo:

```text
.opencode/skills/
```

siguiendo la estructura recomendada por OpenCode:

```text
.opencode/skills/
├── envivo-audit/
│   └── SKILL.md
├── envivo-ux/
│   └── SKILL.md
├── envivo-ui/
│   └── SKILL.md
├── envivo-socketio/
│   └── SKILL.md
├── envivo-mobile/
│   └── SKILL.md
├── envivo-offline/
│   └── SKILL.md
├── envivo-performance/
│   └── SKILL.md
├── envivo-testing/
│   └── SKILL.md
└── envivo-review/
    └── SKILL.md
```

Utiliza nombres lowercase/kebab-case.

Cada `SKILL.md` debe tener frontmatter válido:

```yaml
---
name: ...
description: ...
---
```

---

# SKILL 1 — envivo-audit

Debe enseñar al agente a auditar el módulo antes de modificarlo.

Debe verificar:

* arquitectura
* HTML
* CSS
* JS
* endpoints
* SocketIO
* permisos
* datos
* estados
* timers
* eventos
* listeners
* localStorage
* tema
* logo

Regla:

NO modificar durante la auditoría.

Debe producir:

```text
Problema
Impacto
Riesgo
Recomendación
Archivo afectado
```

---

# SKILL 2 — envivo-ux

Debe enseñar a analizar la experiencia del operador.

Debe preservar:

```text
pendiente
↓
en_curso
↓
completado
```

y:

```text
retroceso
```

Nunca permitir saltos.

Prioridad:

1. mobile
2. operación rápida
3. claridad
4. estética

Debe evaluar:

* jerarquía
* elemento actual
* siguiente
* acciones
* feedback
* carga cognitiva
* errores humanos
* doble toque
* retroceso
* estadísticas
* cronómetro

---

# SKILL 3 — envivo-ui

Debe encargarse del diseño visual.

Dirección:

```text
Cyber/Neon
+
Sports
+
Professional
```

Debe evitar exceso de:

* glow
* animaciones
* colores
* tamaños
* sombras

Debe mantener:

* dark
* light

y garantizar contraste correcto en ambos.

Debe utilizar el logo existente del proyecto.

No crear logos falsos.

---

# SKILL 4 — envivo-socketio

Debe ser extremadamente cuidadosa con tiempo real.

Debe preservar:

```text
actualizar_estados
usuarios_actualizados
registrar_usuario
reconnect
```

Debe evitar:

* polling
* render completo innecesario
* listeners duplicados
* eventos duplicados
* timers duplicados

Debe verificar que los cambios se reflejen inmediatamente.

---

# SKILL 5 — envivo-mobile

Esta skill debe considerar móvil como plataforma principal.

Probar:

```text
360px
390px
412px
430px
```

Principalmente vertical.

Debe revisar:

* doble tap
* scroll
* touch
* botones
* header
* cards
* cronómetro
* legibilidad
* safe areas
* orientación
* viewport
* overflow

No crear PWA.

---

# SKILL 6 — envivo-offline

Debe gestionar la experiencia cuando se pierde temporalmente la conexión.

Debe implementar únicamente soluciones compatibles con frontend.

Debe mantener:

```text
estado local
cola de cambios
reintento
reconexión
reconciliación
```

Debe mostrar claramente:

```text
CONECTADO
RECONECTANDO
SIN CONEXIÓN
CAMBIOS PENDIENTES
```

Nunca perder silenciosamente una acción.

No modificar backend.

No modificar API.

---

# SKILL 7 — envivo-performance

Debe revisar:

* reflows
* repaints
* DOM
* timers
* listeners
* memoria
* animaciones
* SocketIO
* frecuencia de actualización

Especial atención:

No reconstruir todos los eventos cada segundo.

El contador debe modificar únicamente el elemento actual.

Debe poder manejar aproximadamente 30 espectadores.

---

# SKILL 8 — envivo-testing

Debe enseñar al agente a probar:

### Secuencia

```text
pendiente
en_curso
completado
```

### Retroceso

```text
completado
→
en_curso
```

### SocketIO

Dos o más navegadores.

### Mobile

Touch/double tap.

### Offline

Desconexión/reconexión.

### Tema

Dark/light.

### Permisos

Administrador/no administrador.

### Finalización

Con elementos pendientes.

Debe ejecutar:

```bash
venv/bin/pytest -q
```

y pruebas manuales.

---

# SKILL 9 — envivo-review

Debe utilizarse después de cualquier modificación importante.

Debe revisar:

* lógica
* UX
* UI
* SocketIO
* permisos
* performance
* mobile
* accesibilidad
* dark/light
* offline
* regresiones

Debe intentar encontrar errores que el desarrollador haya pasado por alto.

No modificar inmediatamente.

Primero generar:

```text
CRÍTICO
ALTO
MEDIO
BAJO
```

Después de la aprobación o según el flujo del agente, corregir.

---

# REGLAS GENERALES DE TODAS LAS SKILLS

Todas deben recordar:

1. No modificar backend.
2. No modificar API.
3. No modificar DB.
4. No modificar SocketIO server.
5. No romper permisos.
6. No permitir saltos de secuencia.
7. Mantener doble toque.
8. Mantener retroceso.
9. Mantener SocketIO.
10. Mantener dark/light.
11. Mobile-first.
12. Hasta aproximadamente 30 usuarios conectados.
13. No PWA.
14. No modo TV todavía.
15. No introducir dependencias innecesarias.

---

# AGENTS.MD

Después de crear las skills, crea o actualiza:

```text
AGENTS.md
```

en la raíz del proyecto.

Debe contener las reglas permanentes del módulo EN VIVO.

Debe indicar especialmente:

```text
NO modificar backend para este rediseño.

NO modificar API.

NO modificar SocketIO server.

NO modificar DB.

La vista principal es:

app/view/en_vivo/vivo.html
```

También debe explicar:

```text
pendiente → en_curso → completado
```

y el comportamiento de retroceso.

---

# RESULTADO FINAL

Al terminar debes mostrar:

```text
SKILLS CREADAS

.opencode/skills/envivo-audit/SKILL.md
.opencode/skills/envivo-ux/SKILL.md
.opencode/skills/envivo-ui/SKILL.md
.opencode/skills/envivo-socketio/SKILL.md
.opencode/skills/envivo-mobile/SKILL.md
.opencode/skills/envivo-offline/SKILL.md
.opencode/skills/envivo-performance/SKILL.md
.opencode/skills/envivo-testing/SKILL.md
.opencode/skills/envivo-review/SKILL.md

AGENTS.md
```

Después verifica que las skills sean detectables por OpenCode.

No crees skills genéricas.

Deben estar orientadas específicamente al módulo EN VIVO y a su arquitectura real.

No escribas documentación inventada.

Lee primero el código.
