# AUDITORÍA FRONTEND — Itinerario

Fecha: 2026-09-01
Metodología: Revisión manual de templates HTML, JavaScript, CSS

---

## CRÍTICOS

### 1. XSS en vivo.html — `toast()`
- **Archivo:** `app/view/en_vivo/vivo.html:613`
- **Problema:** `toast()` construye HTML desde parámetro `texto` sin escaping
- **Fix:** Usar `textContent` o escape HTML

### 2. XSS en footer.html — `usuarios_actualizados`
- **Archivo:** `app/view/components/footer.html:50-91`
- **Problema:** `u.nombre` inyectado via string concatenation en innerHTML
- **Fix:** `textContent` en vez de innerHTML

### 3. XSS en GestionReportes.js — `cargarOpcionesAjax()`
- **Archivo:** `app/static/js/GestionReportes.js:492-557`
- **Problema:** Opciones AJAX inyectadas en innerHTML sin escaping
- **Fix:** `document.createElement('option')` + `textContent`

### 4. XSS en GestionReportes.js — `mostrarPreview()`
- **Archivo:** `app/static/js/GestionReportes.js:670-676`
- **Problema:** `previewBody.innerHTML` inserta valores sin escaping
- **Fix:** Escapar valores antes de innerHTML

### 5. XSS en ReportesConstructor.js — `cargarOpciones()`
- **Archivo:** `app/static/js/ReportesConstructor.js:294-299`
- **Problema:** Verificar que `esc()` cubre todos los vectores
- **Severidad:** MEDIO (usa `esc()` pero patrón frágil)

---

## ALTOS

### 6. vivo.html — 1100+ líneas de CSS/JS inline
- **Archivo:** `app/view/en_vivo/vivo.html:14-1111`
- **Problema:** 550 líneas CSS inline + 550 líneas JS inline. Sin cache, sin minification, sin code splitting.
- **Fix:** Extraer a archivos externos

### 7. GestionBalance.js — 60% código muerto
- **Archivo:** `app/static/js/GestionBalance.js:1-386`
- **Problema:** 386 líneas de código comentado/muerto en un archivo de 659 líneas
- **Fix:** Eliminar código muerto

### 8. `getCSRF()` duplicado 5+ veces
- **Archivos:** GestionInventario.js:7, GestionBalance.js, ReportesConstructor.js:36, GestionTarea.js:3, GestionGuion.js:3, vivo.html:671
- **Problema:** Función helper duplicada en múltiples archivos
- **Fix:** Crear archivo shared.js con función única

### 9. Sin dark mode en app principal
- **Archivos:** estilo.css, dashboard.css
- **Problema:** Solo vivo.html tiene dark/light. El resto de la app es light-only.
- **Fix:** Agregar `prefers-color-scheme` media query

---

## MEDIOS

### 10. vivo.html — Template duplication
- **Archivo:** `app/view/en_vivo/vivo.html:501-533`
- **Problema:** Bloques pregame y game casi idénticos (~12 líneas cada uno)
- **Fix:** Extraer a Jinja macro

### 11. GestionReportes.js — Archivo grande (802 líneas)
- **Problema:** Maneja MODULE_CONFIG, filtros, preview, PDF, delete en un solo archivo
- **Fix:** Dividir en módulos más pequeños

### 12. ReportesConstructor.js — Archivo grande (586 líneas)
- **Problema:** Wizard state, 5 steps, 4 visualizaciones, export en un archivo
- **Fix:** Dividir por responsabilidad

### 13. Font import duplicado
- **Archivos:** head.html:10 + dashboard.css:1
- **Problema:** Google Fonts importado dos veces
- **Fix:** Eliminar de dashboard.css

### 14. SocketIO CDN sin SRI hash
- **Archivo:** `app/view/components/footer.html:9`
- **Problema:** `cdn.socket.io/4.5.4/socket.io.min.js` sin hash de integridad
- **Fix:** Agregar atributo `integrity`

### 15. Estilos inline innecesarios
- **Archivos:** vivo.html:539, vivo.html:554
- **Problema:** `style="color:var(--text-muted);"` y `style="font-size:1.1rem;"`
- **Fix:** Crear clases CSS

### 16. Chatbot sin label
- **Archivo:** `app/view/components/chatbot.html:37`
- **Problema:** Input de chat sin label ni aria-label
- **Fix:** Agregar `aria-label="Mensaje para Aurora"`

### 17. CSS reset conflicta con Bootstrap
- **Archivo:** `app/static/css/estilo.css:36-43`
- **Problema:** `* { margin: 0; padding: 0 }` conflicta con Bootstrap reboot
- **Fix:** Eliminar reset global

### 18. Select filtro sin label visible
- **Archivo:** `app/view/en_vivo/vivo.html:501-512`
- **Problema:** Filtros con `aria-label` pero sin `<label>` visible
- **Fix:** Agregar label visible o asegurar aria-label correcto

---

## BAJOS

### 19. Flash message ternario no-op
- **Archivo:** `app/view/components/head.html:70`
- **Problema:** `{{ category if category != 'warning' else 'warning' }}` retorna el mismo valor

### 20. vivo.html: Atajo `R` para retroceso
- **Problema:** No documentado en UI, podría sorprender usuarios

### 21. Password toggle CSS pequeño en móvil
- **Archivo:** `app/static/css/estilo.css:992-1023`
- **Problema:** `.password-eye` con width/height de 1em puede ser muy pequeño

---

## ACCESIBILIDAD

| Aspecto | Estado |
|---------|--------|
| Labels en formularios | Parcial (algunos usan aria-label, otros nada) |
| Navegación por teclado | Parcial (vivo.html tiene atajos, el resto no) |
| ARIA roles | Mínimos |
| Contraste de colores | vivo.html tiene dark/light con contraste AA. resto solo light. |
| `prefers-reduced-motion` | Solo en vivo.html |
| `lang` attribute | No verificado en head.html |
| Skip links | No existen |

---

## RESUMEN

| Severidad | Cantidad |
|-----------|----------|
| CRÍTICO (XSS) | 5 |
| ALTO | 4 |
| MEDIO | 9 |
| BAJO | 3 |
| **Total** | **21** |
