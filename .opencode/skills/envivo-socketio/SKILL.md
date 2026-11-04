---
name: envivo-socketio
description: Reglas críticas de tiempo real para el módulo EN VIVO — eventos actualizar_estados/usuarios_actualizados/registrar_usuario/reconnect, actualización parcial del DOM, prohibición de polling. Use when touching socket handlers in vivo.html, reconnect logic, or when the user says "socket", "tiempo real", "sincronización".
---

# envivo-socketio

El tiempo real es el corazón del módulo. Cero margen de error.

## Contrato de eventos (NO cambiar)

- Servidor emite: `actualizar_estados` `{guion_id, estados:[{id,estado}]}` y `usuarios_actualizados` `{count, usuarios}`.
- Cliente emite: `registrar_usuario` con `{pagina, en_vivo_id}` — la identidad la toma el servidor de la sesión Flask-Login, NUNCA del payload del cliente.
- Al `connect`/`reconnect`: re-registrar usuario y llamar `GET /en-vivo/api/estado-actual/<guion_id>` para reconciliar.

## Prohibido

- Polling o reemplazar SocketIO.
- Re-render completo de la lista ante cada evento (`renderEverything()`).
- Listeners, eventos o timers duplicados.
- Retrasos artificiales; la UI debe sentirse instantánea.

## Patrón correcto ante `actualizar_estados`

```text
updateElement(id)   # solo las filas afectadas
updateCounters()    # listos/restantes/progreso/viendo
updateCurrentTimer()
```

Filtrar siempre por `data.guion_id === guionId`. Actualizar dataset + clases del nodo, no reconstruirlo.

## Deuda conocida

Presencia en dict en memoria del server (solo válida con 1 worker). No agravarla.
