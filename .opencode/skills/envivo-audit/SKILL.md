---
name: envivo-audit
description: Auditoría completa del módulo EN VIVO de Itinerario ANTES de modificarlo — arquitectura, HTML/CSS/JS, endpoints, SocketIO, permisos, datos, estados, timers, listeners, tema y logo. Use when the user says "auditar en vivo", "audit envivo", or before any change to app/view/en_vivo/ to map what exists without touching anything.
---

# envivo-audit

Auditar el módulo EN VIVO **sin modificar nada**. La auditoría produce conocimiento, no diffs.

## Qué inspeccionar (en este orden)

1. `app/view/en_vivo/vivo.html` completo (~611 líneas, CSS y JS embebidos)
2. `app/controller/en_vivo_controller.py` — rutas, whitelist de estados, `_fmt12`
3. `app/model/en_vivo_model.py` + `app/model/guion_model.py`
4. `app/__init__.py` — handlers globales SocketIO (`connect`, `registrar_usuario`, `cambio_pagina`, `disconnect`)
5. Autenticación (Flask-Login) y permisos (`verificar_acceso(EN_VIVO)`; operar = `envivo.control`)
6. Eventos socket: servidor emite `actualizar_estados` y `usuarios_actualizados`; cliente maneja `connect`/`reconnect`
7. Datos reales: `duracion_estimada` en SEGUNDOS; `hora` es TIME→`timedelta` formateada server-side
8. Estados: guion (`borrador/publicado/en_vivo/finalizado`) y elemento (`pendiente/en_curso/completado`)
9. Timers/listeners actuales, localStorage (`vivo-theme`), tema dark/light, logo en `app/static/img/Logo-blanco.png`

## Regla dura

NO modificar durante la auditoría. Cero diffs.

## Formato de entrega obligatorio

Para cada hallazgo:

```text
Problema
Impacto
Riesgo
Recomendación
Archivo afectado
```

Cerrar con lista de archivos que UN cambio futuro tocaría.
