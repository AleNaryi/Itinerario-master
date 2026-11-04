# AUDITORÍA DE SEGURIDAD — Itinerario

Fecha: 2026-09-01
Metodología: Revisión manual de código fuente, controller/, model/, helpers/, templates/

---

## HALLAZGOS

### CRÍTICO

#### 1. Stored XSS via `videos_json|safe`

- **Archivo:** `app/view/reels/editar_reel.html:77`
- **Código:** `const videosIniciales = {{ videos_json|safe }};`
- **Riesgo:** `videos_json_str` se construye con `json.dumps` desde valores de BD (`v['nombre']`) y se renderiza con `|safe`, bypasseando el auto-escaping de Jinja2. Un nombre de video como `"; alert(1); //` se ejecuta como JS en el browser del admin.
- **Fix:** Eliminar `|safe`. Pasar la lista Python (no JSON string) y usar `{{ videos_json | tojson }}` que escapa correctamente.

#### 2. XSS en `footer.html` — `usuarios_actualizados`

- **Archivo:** `app/view/components/footer.html:50-91`
- **Código:** `u.nombre` se inyecta via string concatenation en innerHTML
- **Riesgo:** Si un usuario tiene HTML en su nombre, se ejecuta al renderizar la lista de conectados.
- **Fix:** Usar `textContent` en lugar de innerHTML, o escapar el nombre.

### ALTO

#### 3. XSS en `GestionReportes.js` — `cargarOpcionesAjax()`

- **Archivo:** `app/static/js/GestionReportes.js:492-557`
- **Código:** Opciones AJAX inyectadas via `innerHTML` sin escaping
- **Riesgo:** Datos del servidor (nombres de patrocinadores, usuarios) se insertan directamente en `<option>`.
- **Fix:** Usar `document.createElement('option')` + `textContent`.

#### 4. XSS en `GestionReportes.js` — `mostrarPreview()`

- **Archivo:** `app/static/js/GestionReportes.js:670-676`
- **Código:** `previewBody.innerHTML` inserta valores de filas sin escaping
- **Riesgo:** Si la BD contiene `<script>`, se ejecuta al previsualizar reportes.
- **Fix:** Escapar valores antes de insertar en innerHTML.

#### 5. XSS en `vivo.html` — `toast()`

- **Archivo:** `app/view/en_vivo/vivo.html:613`
- **Código:** `toast()` construye HTML desde parámetro `texto` sin escaping
- **Riesgo:** Si algún caller pasa texto controlado por usuario, es inyectable.
- **Fix:** Usar `textContent` o escapar el texto.

#### 6. CAPTCHA no consumido en `validate-login`

- **Archivo:** `app/controller/auth_controller.py:172-189`
- **Código:** `session.get('captcha_code')` en vez de `session.pop()`
- **Riesgo:** Un atacante puede resolver el CAPTCHA una vez y hacer brute-force ilimitado de contraseñas, ya que el CAPTCHA no se consume.
- **Fix:** Usar `session.pop('captcha_code')` igual que en el login normal. Agregar rate-limiting.

#### 7. IDOR en devolución de inventario

- **Archivo:** `app/controller/inventario_controller.py:292-308`
- **Código:** `devolver_recurso()` no verifica que `current_user` sea dueño de la asignación
- **Riesgo:** Cualquier usuario con `inventario.assign` puede devolver asignaciones de otros.
- **Fix:** Verificar que el usuario actual es dueño o supervisor.

### MEDIO

#### 8. IDOR en vista de perfil de usuario

- **Archivo:** `app/controller/usuario_controller.py:131-138`
- **Código:** `/ver/<id>` expone datos de cualquier usuario (incluyendo cédula)
- **Riesgo:** Un usuario regular puede enumerar todos los perfiles.
- **Fix:** Restringir a admins o solo perfil propio.

#### 9. CSRF token nunca expira

- **Archivo:** `app/__init__.py:44`
- **Código:** `WTF_CSRF_TIME_LIMIT = None`
- **Riesgo:** Tokens filtrados son válidos indefinidamente.
- **Fix:** `WTF_CSRF_TIME_LIMIT = 3600` (1 hora).

#### 10. `remote_addr` incorrecto detrás de proxy

- **Archivo:** `app/controller/auth_controller.py:80`, `app/helpers/bitacora_helper.py:23`
- **Código:** `request.remote_addr` siempre retorna IP del proxy
- **Riesgo:** Toda la auditoría IP es inútil detrás de nginx/load balancer.
- **Fix:** Configurar `ProxyFix` middleware de werkzeug.

#### 11. Upload sin validación de extensión

- **Archivo:** `app/controller/premio_controller.py:59-66`
- **Código:** `ALLOWED_EXTENSIONS` definido en config pero nunca verificado
- **Riesgo:** Archivos que no son imágenes podrían subirse.
- **Fix:** Validar extensión antes de `optimizar_imagen()`.

#### 12. Logout vía GET (CSRF-able)

- **Archivo:** `app/controller/auth_controller.py:197-206`
- **Código:** `@bp.route('/logout')` sin restricción de método
- **Riesgo:** `<img src="/auth/logout">` en cualquier página cierra sesión del usuario.
- **Fix:** Cambiar a POST con CSRF token.

### BAJO

#### 13. Reset tokens no se invalidan al cambiar contraseña

- **Archivo:** `app/controller/auth_controller.py:150-161`
- **Riesgo:** Tokens de reset siguen válidos si el usuario cambia contraseña por otro medio.
- **Fix:** Invalidar tokens pendientes al cambiar contraseña.

#### 14. Sin SameSite en cookies de sesión

- **Archivo:** `app/__init__.py`
- **Riesgo:** Cookies cross-site por defecto.
- **Fix:** `SESSION_COOKIE_SAMESITE = 'Lax'`.

#### 15. Sin complejidad en contraseñas

- **Archivo:** `app/controller/auth_controller.py:142`
- **Riesgo:** `12345678` es aceptado.
- **Fix:** Agregar reglas de complejidad o verificar contra lista de contraseñas comunes.

---

## POSITIVOS

- Todas las queries SQL usan `%s` parametrizado (sin SQL injection encontrado)
- Password hashing con werkzeug scrypt
- SocketIO rechaza conexiones anónimas
- `next` validado contra URLs absolutas y protocol-relative
- Jinja2 auto-escaping activo (excepto el caso `|safe` encontrado)
- Validaciones server-side en todos los POST
- Anti-IDOR en notificaciones

---

## RESUMEN

| Severidad | Cantidad |
|-----------|----------|
| CRÍTICO | 2 |
| ALTO | 5 |
| MEDIO | 5 |
| BAJO | 3 |
| **Total** | **15** |
