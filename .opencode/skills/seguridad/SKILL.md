---
name: seguridad
description: Checklist de seguridad obligatoria para el proyecto Itinerario (Flask). Use when touching authentication, sessions, SocketIO/websockets, login, passwords, permissions, CSRF, redirects, or any route that accepts user input. Also use when the user says "seguridad", "vulnerabilidad", "auth", "sockets" or asks to audit security.
---

# Seguridad — Itinerario

Checklist obligatoria al modificar auth, sesiones, sockets o rutas que reciben input del usuario. Basada en fallas reales detectadas en este código.

## Reglas duras

1. **SocketIO autenticado.** El handshake debe identificar al usuario desde la sesión Flask-Login (`current_user` / cookie de sesión), NUNCA desde datos enviados por el cliente. Hoy `handle_registrar_usuario` confía en el `user_id` del cliente → cualquiera puede suplantar a otro usuario en la lista de presencia. Al tocar sockets: validar identidad server-side en `connect`.
2. **CORS de sockets cerrado.** `socketio = SocketIO(cors_allowed_origins="*")` en `app/__init__.py` es inaceptable. Usar lista explícita de orígenes desde config.
3. **Redirects validados.** Todo `next`/`return_to` debe validar `url_has_allowed_host_and_scheme()` (werkzeug) o comparar contra rutas internas. Nunca redirigir a URLs absolutas del cliente.
4. **Sin fallbacks de secretos.** Prohibido `os.environ.get('SECRET_KEY', 'valor-fijo')`. Si falta la variable → fallar con error claro al arrancar.
5. **Prohibido `except Exception: pass`.** Los errores silenciosos ocultan brechas. Mínimo: log del error real + respuesta genérica al cliente (sin filtrar stack traces).
6. **Validación server-side SIEMPRE.** La validación JS en `static/js/validaciones/` es solo UX. Toda escritura valida en servidor: tipos, rangos, longitudes, enums permitidos. Whitelist sobre blacklist.
7. **Queries parametrizadas.** Solo `%s` con tupla en PyMySQL. Concatenar SQL con input del usuario está prohibido.
8. **Permisos en cada ruta nueva.** Toda ruta de escritura usa los decoradores de `app/helpers/decorators.py` (`permiso_requerido`, `verificar_acceso`). Ruta sin decorador = bug.
9. **Contraseñas:** solo `werkzeug.security.generate_password_hash` / `check_password_hash`. Nunca loguear ni devolver hashes.

## Checklist antes de cerrar un cambio

- [ ] ¿La ruta valida permisos y CSRF?
- [ ] ¿Todo input se valida en servidor?
- [ ] ¿Algún error nuevo queda atrapado en silencio?
- [ ] ¿El socket/route expone más datos de los necesarios?
