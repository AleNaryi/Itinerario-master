# AUDITORÍA DE TESTING — Itinerario

Fecha: 2026-09-01
Metodología: Revisión de tests/conftest.py, todos los archivos test_*.py, cobertura

---

## INFRAESTRUCTURA

### conftest.py — Calificación: BUENA

**Fortalezas:**
- Clona BDs desde dumps .sql reales via fixture session-scoped
- `WTF_CSRF_ENABLED = False` para test client
- Monkeypatch en servicios de email
- Emails únicos por test via uuid
- Login fixture respeta CAPTCHA

**Problemas:**

| Línea | Problema | Severidad |
|-------|---------|-----------|
| 84 | `_contexto` autouse mantiene app context vivo → flask_login cachea usuario en `g._login_user` entre tests multi-usuario | MEDIO |
| 46 | `bases_de_prueba` es session-scoped → BD compartida entre tests, sin cleanup/rollback | MEDIO |
| 99 | `crear_usuario` setea `usuario._password` como atributo monkey-patched → frágil | BAJO |

---

## LO QUE SÍ ESTÁ TESTEADO (63 tests)

| Área | Tests | Cobertura |
|------|-------|-----------|
| Auth (login, CAPTCHA, next, reset, sesión) | 10 | Sólida |
| Permisos (anon, superadmin, denegado, JSON 403) | 4 | Buena |
| ValidacionesMixin (unit puras) | 13 | Buena |
| Notificaciones (multi-asignación, API, completar) | 4 | Buena |
| EN VIVO (render, relojes, sync, rollback, CSRF) | 8 | Buena |
| Reportes smoke (auth, preview, inválido) | 4 | Básica |
| Reportes filtros (progresivos, SQL) | 13 | Sólida |
| Reportes helpers (unit puras) | 7 | Sólida |
| Reportes constructor (catálogo, ejecución, injection, export) | 16 | Sólida |
| Reportes PDF (básico, análisis, edge cases) | 6 | Básica |

---

## LO QUE NO ESTÁ TESTEADO

| Categoría | Cobertura actual | Severidad |
|-----------|-----------------|-----------|
| **CRUD controllers** (guiones, inventario, patrocinadores, premios, mantenimiento, reels, usuarios, roles, balance) | Cero tests de integración | **ALTO** |
| **File uploads** (fotos premios, videos reels) | Cero cobertura | **ALTO** |
| **IDOR protection** | Sin test verificando que usuario A no acceda a recursos de B | **ALTO** |
| **Rate limiting / brute force** | Sin test de lockout | MEDIO |
| **SocketIO handlers** | registrar_usuario, usuarios_actualizados sin test | MEDIO |
| **Chatbot Aurora** | Cero cobertura | MEDIO |
| **Dashboard** | Solo test de status 200, no contenido | BAJO |
| **Error paths** (DB caída, JSON malformado) | Sin test | MEDIO |
| **Concurrent state mutations** | Sin tests de race condition EN VIVO | BAJO |
| **Password complexity** | Solo test de password válida, no débiles | BAJO |
| **Session fixation** | Sin test | MEDIO |
| **HTML injection en templates** | Sin test verificando XSS en output renderizado | MEDIO |

---

## PRIORIDADES DE TESTS NUEVOS

### P0 — Críticos

1. **Tests de integración CRUD** para los 8 controllers sin cobertura
2. **Test de IDOR** en inventario (devolver asignación de otro)
3. **Test de stored XSS** en reels (verificar escaping)
4. **Test de brute force** (validate-login sin CAPTCHA consumption)

### P1 — Importantes

5. **Tests de file upload** (validación de extensión, tamaño)
6. **Tests de SocketIO** (registrar_usuario, reconnect)
7. **Tests de chatbot** (respuestas esperadas)
8. **Tests de error paths** (DB down, JSON inválido)
9. **Tests de session fixation** (login → sesión heredada)

### P2 — Deseables

10. **Tests de password complexity** (débiles rechazadas)
11. **Tests de dashboard** (contenido, no solo 200)
12. **Tests de EN VIVO concurrente** (race conditions)

---

## COBUSTIBLES

```bash
# Ejecutar suite actual
venv/bin/pytest -q

# Tests específicos
venv/bin/pytest tests/test_auth.py -v
venv/bin/pytest tests/test_notificaciones.py -v

# Con cobertura (requiere pytest-cov)
venv/bin/pytest --cov=app --cov-report=term-missing
```

---

## HALLAZGO DEL HARNESS

El fixture `_contexto` autouse mantiene un app context vivo. Flask-Login cachea el usuario en `g._login_user`. Al probar con 2+ usuarios hay que hacer `g.pop('_login_user', None)` al cambiar de actor. Ver `tests/test_notificaciones.py` para el workaround.
