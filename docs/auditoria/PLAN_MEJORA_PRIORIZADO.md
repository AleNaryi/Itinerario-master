# PLAN DE MEJORA PRIORIZADO — Itinerario

Fecha: 2026-09-01
Estado: PENDIENTE DE APROBACIÓN DEL USUARIO

---

## FASE 1: SEGURIDAD (inmediato, sin cambios visibles)

| # | Acción | Severidad | Archivos | Esfuerzo |
|---|--------|-----------|----------|----------|
| 1.1 | **Fix XSS `videos_json\|safe`** — Cambiar a `{{ videos_json \| tojson }}` | CRÍTICO | `app/view/reels/editar_reel.html:77` | 5 min |
| 1.2 | **Fix XSS footer.html** — `textContent` en vez de innerHTML | CRÍTICO | `app/view/components/footer.html:50-91` | 15 min |
| 1.3 | **Fix CAPTCHA no consumido** — `session.pop()` en `validate-login` | ALTO | `app/controller/auth_controller.py:172-189` | 5 min |
| 1.4 | **Fix IDOR inventario** — Verificar dueño/supervisor en `devolver_recurso` | ALTO | `app/controller/inventario_controller.py:292-308` | 15 min |
| 1.5 | **Fix CSRF time limit** — `WTF_CSRF_TIME_LIMIT = 3600` | MEDIO | `app/__init__.py:44` | 2 min |
| 1.6 | **Fix logout POST** — Cambiar `@bp.route('/logout')` a POST | MEDIO | `app/controller/auth_controller.py:197-206` | 10 min |
| 1.7 | **Fix SameSite cookies** — `SESSION_COOKIE_SAMESITE = 'Lax'` | MEDIO | `app/__init__.py` | 2 min |

**Tiempo estimado:** ~1 hora
**Impacto:** Elimina 2 CRÍTICOS + 2 ALTOS + 3 MEDIOS de seguridad

---

## FASE 2: TESTS CRÍTICOS (antes de cada fix posterior)

| # | Acción | Prioridad | Archivos | Esfuerzo |
|---|--------|-----------|----------|----------|
| 2.1 | **Test stored XSS reels** — Verificar que videos_json se escapa correctamente | P0 | `tests/test_reels.py` (nuevo) | 30 min |
| 2.2 | **Test IDOR inventario** — Verificar que usuario A no puede devolver asignación de B | P0 | `tests/test_inventario.py` (nuevo) | 20 min |
| 2.3 | **Test brute force** — Verificar que validate-login consume CAPTCHA | P0 | `tests/test_auth.py` (extender) | 15 min |
| 2.4 | **Test CRUD controllers** — Al menos 1 test de integración por módulo | P1 | `tests/test_crud_*.py` (nuevos) | 2-3 hrs |

**Tiempo estimado:** ~3-4 horas
**Impacto:** Cobertura de las 3 vulnerabilidades más críticas + base para futuros fixes

---

## FASE 3: SQL/PERFORMANCE (alto impacto, bajo riesgo)

| # | Acción | Impacto | Archivos | Esfuerzo |
|---|--------|---------|----------|----------|
| 3.1 | **Fix N+1 bitacora** — Batch query `SELECT id, nombre FROM usuarios WHERE id IN (...)` | HIGH | `app/model/bitacora_model.py:16-28` | 20 min |
| 3.2 | **Fix N+1 mantenimiento** — JOIN único en vez de queries separadas | HIGH | `app/model/mantenimiento_model.py:177-198` | 30 min |
| 3.3 | **Fix DELETE sin transacción reels** — `with transaction():` | HIGH | `app/model/reels_model.py:142-143` | 5 min |
| 3.4 | **Agregar índices faltantes** — 4 ALTER TABLE ADD INDEX | MEDIUM | `estadio_db.sql` | 10 min |
| 3.5 | **SELECT explícito sin password_hash** — En usuario_model y auth_model | MEDIUM | `app/model/usuario_model.py:110`, `app/model/auth_model.py:71,124` | 15 min |
| 3.6 | **LIMIT por defecto en bitacora** — `LIMIT 500` en queries sin límite | MEDIUM | `app/model/bitacora_model.py:33` | 5 min |
| 3.7 | **Fix rango_fechas_defecto** — `SELECT MIN(campo) FROM tabla` en vez de cargar todo | MEDIUM | `app/helpers/reportes_data.py:147-166` | 10 min |
| 3.8 | **Fix N+1 reels** — JOIN batch para videos | MEDIUM | `app/model/reels_model.py:33-44` | 15 min |
| 3.9 | **Fix balance_model herencia** — Eliminar `class Pago(Database, ...)` | LOW | `app/model/balance_model.py:16` | 15 min |

**Tiempo estimado:** ~2 horas
**Impacto:** Elimina 5 N+1 queries + 3 transacciones faltantes + 4 índices

---

## FASE 4: FRONTEND (CSS/JS cleanup)

| # | Acción | Impacto | Archivos | Esfuerzo |
|---|--------|---------|----------|----------|
| 4.1 | **Extraer vivo.html CSS/JS** — Mover a archivos externos | MEDIUM | `app/view/en_vivo/vivo.html`, `app/static/css/vivo.css`, `app/static/js/vivo.js` | 30 min |
| 4.2 | **Eliminar código muerto GestionBalance.js** — 386 líneas | LOW | `app/static/js/GestionBalance.js` | 5 min |
| 4.3 | **Deduplicar getCSRF()** — Crear shared.js | LOW | `app/static/js/shared.js` + 5 archivos | 15 min |
| 4.4 | **Eliminar font import duplicado** — Quitar de dashboard.css | LOW | `app/static/css/dashboard.css:1` | 2 min |
| 4.5 | **Fix XSS GestionReportes.js** — `createElement` + `textContent` | HIGH | `app/static/js/GestionReportes.js:492-557,670-676` | 20 min |

**Tiempo estimado:** ~1.5 horas
**Impacto:** Elimina 3 XSS front-end + limpia ~400 líneas muertas

---

## FASE 5: TESTING EXPANDIDO

| # | Acción | Prioridad | Esfuerzo |
|---|--------|-----------|----------|
| 5.1 | Tests de uploads (premios, reels) | P1 | 1-2 hrs |
| 5.2 | Tests de SocketIO (registrar_usuario) | P1 | 1 hr |
| 5.3 | Tests de chatbot Aurora | P2 | 30 min |
| 5.4 | Tests de error paths (DB down, JSON inválido) | P2 | 30 min |
| 5.5 | Tests de dashboard (contenido) | P2 | 20 min |

**Tiempo estimado:** ~3-4 horas

---

## FASE 6: DEUDA TÉCNICA (opcional, bajo prioridad)

| # | Acción | Impacto | Esfuerzo |
|---|--------|---------|----------|
| 6.1 | Fix rol_model DDL bug (`Multiple primary key defined`) | BAJO | 20 min |
| 6.2 | Agregar dark mode a módulos principales | BAJO | 2-3 hrs |
| 6.3 | Refactor usuario_model (350 líneas duplicadas) | BAJO | 1 hr |
| 6.4 | Labels visibles en formularios (accesibilidad) | MEDIO | 1-2 hrs |
| 6.5 | Agregar `aria-label` a chatbot input | BAJO | 5 min |

**Tiempo estimado:** ~4-5 horas

---

## RESUMEN DE IMPACTO

| Fase | Hallazgos eliminados | Tiempo | Riesgo |
|------|---------------------|--------|--------|
| 1. Seguridad | 7 (2 CRÍT, 2 ALTO, 3 MEDIO) | ~1 hr | BAJO |
| 2. Tests | 3 vulnerabilidades cubiertas | ~3-4 hrs | BAJO |
| 3. SQL/Performance | 12 (5 N+1, 3 TX, 4 índices) | ~2 hrs | BAJO |
| 4. Frontend | 6 (3 XSS, 3 limpieza) | ~1.5 hrs | BAJO |
| 5. Tests expandidos | +5 archivos, ~20 tests | ~3-4 hrs | BAJO |
| 6. Deuda técnica | 5 mejoras | ~4-5 hrs | BAJO |
| **TOTAL** | **~32 hallazgos resueltos** | **~14-17 hrs** | **BAJO** |

---

## RIESGOS

1. **Regresiones:** Cada fix puede romper algo existente. Mitigación: tests antes y después de cada cambio.
2. **Breaking changes en API interna:** Cambiar queries puede afectar otros consumers. Mitigación: revisar todos los callers antes de cambiar.
3. **Performance regression:** JOINs más complejos pueden ser más lentos en tablas pequeñas. Mitigación: medir ANTES y DESPUÉS.

---

## ORDEN DE EJECUCIÓN RECOMENDADO

```
FASE 1 (Seguridad) → FASE 2 (Tests) → FASE 3 (SQL) → FASE 4 (Frontend) → FASE 5 (Tests expandidos) → FASE 6 (Deuda)
```

Cada fase es independiente y puede ejecutarse por separado. Fases 1-4 son las más críticas. Fases 5-6 son deseables pero no urgentes.
