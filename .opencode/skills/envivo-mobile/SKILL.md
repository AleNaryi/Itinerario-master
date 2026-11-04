---
name: envivo-mobile
description: El teléfono vertical es la plataforma principal del módulo EN VIVO — probar 360/390/412/430px, doble tap robusto, scroll, safe areas y legibilidad. Use when styling or debugging vivo.html on mobile, when the user says "móvil", "responsive", "doble tap", "touch".
---

# envivo-mobile

Mobile-first REAL: se diseña primero en 360–430px verticales y luego se adapta a tablet/desktop. Nunca al revés.

## Viewports de prueba obligatorios

```text
360px · 390px · 412px · 430px   (vertical)
```

Luego 768 / 1024 / 1280+.

## Checklist móvil

- Doble tap: detección robusta sin zoom accidental, click fantasma ni doble ejecución (debounce ~300ms, ignorar taps sobre botones).
- Scroll fluido; los toques no deben pelear con el gesto de scroll.
- Botones/touch targets ≥ 40px; nada que obligue a zoom.
- Header compacto que no se aplaste (usar filas: nombre+live · progreso+viendo · acciones).
- Cards legibles una columna; nada de tablas con scroll horizontal.
- Cronómetro visible sin ocupar la pantalla.
- Safe areas (notch) y orientación: probar giro del teléfono.
- `overflow` controlado; body sin scroll horizontal.
- Legibilidad de todos los estados en tema dark Y light.

## Prohibido

PWA. Dependencias nuevas para gestures (el touchstart manual existente basta).
