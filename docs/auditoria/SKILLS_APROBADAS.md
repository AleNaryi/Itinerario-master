# SKILLS APROBADAS — Itinerario (v2)

Fecha: 2026-09-01
Versión: 2 (segunda evaluación)
Estado: PENDIENTE DE APROBACIÓN DEL USUARIO

---

## CONJUNTO FINAL

**24 skills** (18 locales + 6 externas)

---

## SKILLS LOCALES (18) — Se mantienen

| # | Skill | Categoría | Acción |
|---|-------|-----------|--------|
| 1 | `seguridad` | Seguridad | MANTENER — Checklist específica del proyecto |
| 2 | `db-transacciones` | Database | MANTENER — Reglas PyMySQL Itinerario |
| 3 | `tests-pytest` | Testing | MANTENER — Convenciones pytest Itinerario |
| 4 | `refactor-controladores` | Refactoring | MANTENER — Patrones refactor controladores |
| 5 | `reportes-pdf` | Reportes/PDF | MANTENER — Motor PDF con reportlab |
| 6 | `reportes-detallados` | Reportes/Data | MANTENER — Patrón "efecto bitácora" |
| 7 | `envivo-audit` | EN VIVO | MANTENER — Auditoría EN VIVO |
| 8 | `envivo-ux` | EN VIVO | MANTENER — UX operador |
| 9 | `envivo-ui` | EN VIVO | MANTENER — Dirección visual |
| 10 | `envivo-mobile` | EN VIVO | MANTENER — Mobile/touch |
| 11 | `envivo-socketio` | EN VIVO | MANTENER — SocketIO real-time |
| 12 | `envivo-performance` | EN VIVO | MANTENER — Performance EN VIVO |
| 13 | `envivo-offline` | EN VIVO | MANTENER — Modo offline |
| 14 | `envivo-testing` | EN VIVO | MANTENER — Testing EN VIVO |
| 15 | `envivo-review` | EN VIVO | MANTENER — Review post-cambio |
| 16 | `interface-design` | UI/Dashboard | MANTENER — Design system admin panels |
| 17 | `code-review` | Code review | MANTENER — Review de diff (mattpocock) |
| 18 | `diagnosing-bugs` | Debugging | MANTENER — Metodología debugging 6 fases |

---

## SKILLS EXTERNAS (6) — Se agregan

| # | Skill | Fuente | Installs | Uso |
|---|-------|--------|----------|-----|
| 1 | `security-and-hardening` | addyosmani/agent-skills | 30.4K | OWASP Top 10, threat modeling (STRIDE), auth patterns, secrets, dependency audit |
| 2 | `sql-code-review` | github/awesome-copilot | 12.9K | Análisis SQL/MySQL: inyección, índices, rendimiento, naming, schema, batch ops |
| 3 | `tdd` | mattpocock/skills | 825K | Red-green-refactor, vertical slicing, behavior tests, pre-agreed seams |
| 4 | `webapp-testing` | anthropics/skills | 148.6K | E2E con Playwright Python: with_server.py, DOM, screenshots, console |
| 5 | `accessibility` | addyosmani/web-quality-skills | ~173/sem | WCAG 2.2: POUR, ARIA, keyboard nav, contrast, focus, form labels |
| 6 | `verification-before-completion` | obra/superpowers | 198K | Gate de 5 pasos: comando → ejecutar → leer → verificar → declarar |

---

## SKILLS ELIMINADAS (1)

| Skill | Fuente | Razón de eliminación |
|-------|--------|---------------------|
| `emil-design-eng` | emilkowalski/skills (246K) | Ejemplos en React/JSX/Framer Motion. Incompatible con Flask/Bootstrap/jQuery. `interface-design` cubre mejor UI para dashboards admin panels. |

---

## SKILLS REEMPLAZADAS (0)

No hubo reemplazos directos. Las skills externas son complementarias, no sustitutas.

---

## SKILLS NO APROBADAS (12)

| Skill | Razón |
|-------|-------|
| `code-review-and-quality` (addyosmani) | Solapamiento ALTO con `code-review` (mattpocock) que es más popular |
| `improve-codebase-architecture` (mattpocock) | Análisis general; `refactor-controladores` cubre el patrón específico |
| `web-quality-audit` (addyosmani) | Requiere Lighthouse CLI o Chrome DevTools MCP |
| `browser-testing-with-devtools` (addyosmani) | Requiere Chrome DevTools MCP; `webapp-testing` es más práctica |
| `performance` (addyosmani) | Requiere Lighthouse; `envivo-performance` ya cubre EN VIVO |
| `core-web-vitals` (addyosmani) | Sub-conjunto de `performance`; demasiado específico |
| `code-security` | NO EXISTE en skills.sh (404) |
| `flask` (teachingai) | Skills Flask propias ya existentes |
| `socketio` (TerminalSkills) | Node.js focused; `envivo-socketio` es mejor |
| `api-rate-limiting` | Flask-Limiter lo hace |
| `deploying-flask` | Gunicorn ya configurado |
| `api-gateway` | No aplica |

---

## INSTALACIÓN

### Skills a instalar (6)

```bash
claude skills add addyosmani/agent-skills/security-and-hardening
claude skills add github/awesome-copilot/sql-code-review
claude skills add mattpocock/skills/tdd
claude skills add anthropics/skills/webapp-testing
claude skills add addyosmani/web-quality-skills/accessibility
claude skills add obra/superpowers/verification-before-completion
```

### Skills a eliminar (1)

```bash
rm -rf .opencode/skills/emil-design-eng
```

---

## JUSTIFICACIÓN DEL CONJUNTO FINAL

### Por qué 24 skills (no más, no menos)

- **18 locales** cubren las áreas específicas del proyecto que ninguna skill externa puede cubrir: EN VIVO (9), reportes (2), seguridad/db/tests/refactoring específicos (5), UI admin (1), code review (1), debugging (1)
- **6 externas** complementan con marcos genéricos de alta calidad: OWASP (1), SQL (1), TDD (1), E2E (1), accesibilidad (1), verificación (1)
- **1 eliminada** por incompatibilidad técnica (React en proyecto Flask/Bootstrap)

### Por qué no instalar más

Cada skill adicional es ruido en el contexto del agente. Skills que requieren infraestructura adicional (Lighthouse, Chrome DevTools MCP) o que solapan significativamente con las existentes generan más confusión que valor.

### Cobertura de la auditoría

| Hallazgo de auditoría | Skill que lo addressa |
|----------------------|----------------------|
| 15 vulnerabilidades seguridad | `seguridad` + `security-and-hardening` |
| 19 SQL issues (N+1, índices, transacciones) | `db-transacciones` + `sql-code-review` |
| 21 frontend issues (XSS, accesibilidad) | `accessibility` + `code-review` |
| 63 tests, ~30% cobertura | `tests-pytest` + `tdd` + `webapp-testing` |
| Bugs conocidos (DDL, branch roto) | `diagnosing-bugs` |
| Falsas declaraciones de completado | `verification-before-completion` |
| UI admin panels | `interface-design` |
