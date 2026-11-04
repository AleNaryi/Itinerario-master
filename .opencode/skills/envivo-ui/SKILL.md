---
name: envivo-ui
description: Dirección visual del módulo EN VIVO — Cyber/Neon + Sports + Professional, tokens CSS, dark/light con contraste real, uso del logo existente. Use when restyling app/view/en_vivo/vivo.html, creating design tokens, or when the user says "estilo", "neon", "tema claro", "rediseño visual".
---

# envivo-ui

Diseño visual del centro de operación EN VIVO.

## Dirección

```text
Cyber / Neon + Sports + Professional
```

Inspiración: sports technology + live broadcast + SaaS profesional. NO videojuego.

## Moderación obligatoria

Evitar exceso de: glow, animaciones, colores simultáneos, tamaños gigantes, sombras.
Un glow moderado solo para el elemento `en_curso`. Máximo 1 color de acento por estado.

## Tokens mínimos (CSS custom properties, patrón ya usado en vivo.html)

- Superficie: `--bg`, `--card-bg`, `--card-border`
- Texto: `--text`, `--text-secondary` (contraste AA en AMBOS temas)
- Estados: pendiente neutro · en_curso neon-verde (#10b981 familia) · completado atenuado pero LEGIBLE · reiniciado coherente
- Live badge rojo pulsante (#ef4444)
- Pre-game ámbar (#f59e0b), game cyan (#06b6d4)

## Dark/Light

Dark = experiencia principal. Light = REALMENTE usable: revisar contraste de texto, iconos,
bordes, badges, modal, toasts e indicadores en ambos. No basta `background:white`.
Persistencia en `localStorage['vivo-theme']`.

## Logo

Usar el logo existente del proyecto (`app/static/img/Logo-blanco.png`). PROHIBIDO inventar logos o traer imágenes externas.

## Accesibilidad

Contraste AA, focus visible, respeta `prefers-reduced-motion` (apaga animaciones).
