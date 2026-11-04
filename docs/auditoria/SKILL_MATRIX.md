# MATRIZ DE EVALUACIÓN DE SKILLS — Itinerario (v2)

Fecha: 2026-09-01
Versión: 2 (segunda evaluación)

---

## CRITERIOS DE EVALUACIÓN

| Criterio | Peso | Descripción |
|----------|------|-------------|
| Compatibilidad Python/Flask/MySQL | 25% | ¿Funciona con nuestro stack? ¿No asume ORM, React, etc.? |
| Cobertura de necesidades reales | 25% | ¿Resuelve problemas encontrados en la auditoría? |
| Calidad intrínseca | 20% | ¿Es exhaustiva, clara, accionable? |
| Sin solapamiento | 15% | ¿Aporta algo que no cubra otra skill ya instalada? |
| Mantenimiento | 15% | ¿Está activamente mantenida? |

---

## ANÁLISIS POR CATEGORÍA

### SEGURIDAD

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `seguridad` (local) | Propia | — | 100% | Checklist específica del proyecto, 9 reglas duras, finding reales | Ninguno | **MANTENER** |
| `security-and-hardening` | addyosmani/agent-skills | 30.4K | 95% | OWASP Top 10, threat modeling (STRIDE), auth patterns, secrets, dependency audit, 3-tier boundaries | Parcial con `seguridad` (_OWASP vs checklist propia)_ | **AGREGAR** — complementa: OWASP systemático + threat modeling que `seguridad` no cubre |

**Decisión seguridad:** MANTENER `seguridad` (específica del proyecto) + AGREGAR `security-and-hardening` (marco OWASP general). No se pisan: una es "qué verificar en Itinerario", la otra es "cómo pensar en seguridad de forma sistemática".

---

### SQL

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `db-transacciones` (local) | Propia | — | 100% | Reglas PyMySQL, transaction(), parametrización, error handling, receta escritura compuesta | Ninguno | **MANTENER** |
| `sql-code-review` | github/awesome-copilot | 12.9K | 95% | Inyección, acceso, rendimiento, naming, schema design, MySQL específico, batch ops, paginación | Parcial con `db-transacciones` (_inyección y parametrización_) | **AGREGAR** — complementa: análisis de rendimiento de queries, índices, naming conventions que `db-transacciones` no cubre |

**Decisión SQL:** MANTENER `db-transacciones` (reglas Itinerario) + AGREGAR `sql-code-review` (revisión sistemática SQL/MySQL). Complementarios.

---

### TESTING

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `tests-pytest` (local) | Propia | — | 100% | Convenciones pytest, fixtures, BD test, prioridades, checklist | Ninguno | **MANTENER** |
| `tdd` | mattpocock/skills | 825K | 100% | Red-green-refactor, vertical slicing, behavior tests, pre-agreed seams | Bajo (metodología vs convenciones) | **AGREGAR** — aporta disciplina TDD que `tests-pytest` no enseña |
| `webapp-testing` | anthropics/skills | 148.6K | 95% | Playwright Python, with_server.py, DOM inspection, screenshots | Bajo (E2E vs unit) | **AGREGAR** — cubre E2E que pytest no cubre (uploads, SocketIO, JS rendering) |

**Decisión testing:** MANTENER `tests-pytest` + AGREGAR `tdd` (metodología) + AGREGAR `webapp-testing` (E2E). Los tres son complementarios.

---

### DEBUGGING

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `diagnosing-bugs` | mattpocock/skills | 528K | 100% | 6 fases: feedback loop, bisect, hypothesis, fix, verify, ship | Ninguno (no hay skill local de debugging) | **AGREGAR** — cubre gap real |

**Decisión debugging:** AGREGAR `diagnosing-bugs`.

---

### VERIFICACIÓN

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `verification-before-completion` | obra/superpowers | 198K | 100% | Gate de 5 pasos: comando → ejecutar → leer → verificar → declarar | Ninguno | **AGREGAR** — previene falsas declaraciones de "completado" |

**Decisión verificación:** AGREGAR `verification-before-completion`.

---

### CÓDIGO / REVISIÓN

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `code-review` | mattpocock/skills | 472K | 100% | Review de diff (Standards + Spec) via sub-agentes paralelos | Bajo (review de diff vs arquitectura) | **MANTENER** |
| `code-review-and-quality` | addyosmani/agent-skills | 34.5K | 95% | Multi-axis review (correctness, readability, architecture, security, performance) | ALTO con `code-review` (ambas son review de código) | **NO AGREGAR** — `code-review` ya cubre review; `code-review-and-quality` es más genérica y menos popular |
| `improve-codebase-architecture` | mattpocock/skills | 853K | 100% | Shallow modules, deepening refactors, git hot-spots, HTML report | MEDIO con `refactor-controladores` (arquitectura vs refactor de controladores) | **MANTENER** `code-review`; `improve-codebase-architecture` es complementaria pero la maneja el usuario bajo demanda, no como skill instalada |

**Decisión código:** MANTENER `code-review`. No instalar `code-review-and-quality` (redundante). `improve-codebase-architecture` queda como skill de uso bajo demanda, no instalada.

---

### FRONTEND / ACCESIBILIDAD

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `accessibility` | addyosmani/web-quality-skills | ~173/sem | 100% | WCAG 2.2, POUR, ARIA, keyboard nav, contrast, focus, form labels, target size | Bajo con `envivo-ux` (WCAG global vs UX EN VIVO) | **AGREGAR** — cubre accesibilidad global del proyecto |
| `web-quality-audit` | addyosmani/web-quality-skills | ~60K | 95% | Lighthouse 13+, Performance + A11y + SEO + Best Practices, 150+ checks | MEDIO con `accessibility` + `performance` | **NO AGREGAR** — requiere Lighthouse CLI/MCP; `accessibility` + `performance` ya cubren sus áreas principales |
| `browser-testing-with-devtools` | addyosmani/agent-skills | 26K | 90% | Chrome DevTools MCP, DOM, console, network, profiling | ALTO con `webapp-testing` (ambas son testing browser) | **NO AGREGAR** — `webapp-testing` es más práctica (Playwright Python); DevTools MCP añade infraestructura innecesaria |

**Decisión frontend:** AGREGAR `accessibility`. No instalar `web-quality-audit` (requiere Lighthouse MCP) ni `browser-testing-with-devtools` (requiere Chrome DevTools MCP).

---

### PERFORMANCE

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `envivo-performance` (local) | Propia | — | 100% | Reflows, repaints, timers, listeners, DOM updates EN VIVO | Ninguno | **MANTENER** |
| `performance` | addyosmani/web-quality-skills | 32.7K | 95% | Lighthouse-based: budgets, CWV, critical rendering, caching, images, runtime | MEDIO con `envivo-performance` (frontend global vs EN VIVO) | **NO AGREGAR** — `envivo-performance` cubre EN VIVO; el performance general del proyecto ya se auditó |
| `core-web-vitals` | addyosmani/web-quality-skills | 23.8K | 95% | LCP, INP, CLS diagnosis. CrUX + DevTools | ALTO con `performance` (es sub-conjunto) | **NO AGREGAR** — demasiado específico; sub-conjunto de `performance` |

**Decisión performance:** MANTENER `envivo-performance`. No instalar `performance` ni `core-web-vitals` (requieren Lighthouse MCP, ya cubierto por auditoría existente).

---

### DISEÑO UI

| Skill | Fuente | Installs | Compat. | Cubre | Solapamiento | **Decisión** |
|-------|--------|----------|---------|-------|-------------|-------------|
| `emil-design-eng` (local) | emilkowalski/skills | 246K | 60% | UI polish, animations, springs, gestures. Ejemplos en React/JSX/Framer Motion | ALTO con `interface-design` (ambas son UI design) | **ELIMINAR** — ejemplos React/JSX incompatibles; `interface-design` cubre mejor dashboards/admin panels |
| `interface-design` (local) | Propia | — | 90% | Dashboards, admin panels, visual hierarchy, tokens, design systems | Bajo (product UI vs animations) | **MANTENER** — directamente relevante para módulos admin del proyecto |
| `envivo-ui` (local) | Propia | — | 100% | Dirección visual EN VIVO (Cyber/Neon + Sports) | Ninguno | **MANTENER** |
| `envivo-ux` (local) | Propia | — | 100% | UX del operador EN VIVO | Ninguno | **MANTENER** |

**Decisión diseño:** ELIMINAR `emil-design-eng` (React-focused). MANTENER `interface-design`, `envivo-ui`, `envivo-ux`.

---

### EN VIVO (9 skills)

Todas las envivo-* son específicas del proyecto, sin equivalente externo. **MANTENER TODAS.**

| Skill | Decisión |
|-------|----------|
| envivo-audit | MANTENER |
| envivo-ux | MANTENER |
| envivo-ui | MANTENER |
| envivo-mobile | MANTENER |
| envivo-socketio | MANTENER |
| envivo-performance | MANTENER |
| envivo-offline | MANTENER |
| envivo-testing | MANTENER |
| envivo-review | MANTENER |

---

### REFACTOR / REPORTES

| Skill | Decisión | Razón |
|-------|----------|-------|
| refactor-controladores | MANTENER | Específica del proyecto, patrones de refactor comprobados |
| reportes-pdf | MANTENER | Específica del proyecto, motor PDF con reportlab |
| reportes-detallados | MANTENER | Específica del proyecto, patrón "efecto bitácora" |

---

## SKILLS CANDIDATAS RECHAZADAS

| Skill | Razón del rechazo |
|-------|-------------------|
| `code-security` | NO EXISTE en skills.sh (404) |
| `code-review-and-quality` | Solapamiento ALTO con `code-review` (mattpocock) que es más popular y más enfocada |
| `improve-codebase-architecture` | 853K installs pero es análisis de arquitectura general; `refactor-controladores` ya cubre el patrón específico del proyecto. Se usa bajo demanda, no como skill instalada |
| `web-quality-audit` | Requiere Lighthouse CLI o Chrome DevTools MCP; infraestructura adicional innecesaria |
| `browser-testing-with-devtools` | Requiere Chrome DevTools MCP; `webapp-testing` (Playwright) es más práctica |
| `performance` | Requiere Lighthouse; `envivo-performance` ya cubre EN VIVO; auditoría general ya hecha |
| `core-web-vitals` | Sub-conjunto de `performance`; demasiado específico |
| `emil-design-eng` | Ejemplos en React/JSX/Framer Motion; incompatible con nuestro stack |
| `flask` (teachingai) | Ya tenemos skills Flask propias (seguridad, db-transacciones) |
| `socketio` (TerminalSkills) | Node.js focused; `envivo-socketio` es mejor |
| `api-rate-limiting` | Flask-Limiter lo hace |
| `deploying-flask` | Gunicorn ya configurado |

---

## RESUMEN DE DECISIONES

### MANTENER (18 skills locales)

| # | Skill | Categoría |
|---|-------|-----------|
| 1 | seguridad | Seguridad |
| 2 | db-transacciones | Database |
| 3 | tests-pytest | Testing |
| 4 | refactor-controladores | Refactoring |
| 5 | reportes-pdf | Reportes/PDF |
| 6 | reportes-detallados | Reportes/Data |
| 7 | envivo-audit | EN VIVO |
| 8 | envivo-ux | EN VIVO |
| 9 | envivo-ui | EN VIVO |
| 10 | envivo-mobile | EN VIVO |
| 11 | envivo-socketio | EN VIVO |
| 12 | envivo-performance | EN VIVO |
| 13 | envivo-offline | EN VIVO |
| 14 | envivo-testing | EN VIVO |
| 15 | envivo-review | EN VIVO |
| 16 | interface-design | UI/Dashboard |
| 17 | code-review | Code review |
| 18 | diagnosing-bugs | Debugging |

### AGREGAR (6 skills externas)

| # | Skill | Fuente | Installs | Razón principal |
|---|-------|--------|----------|----------------|
| 1 | `security-and-hardening` | addyosmani/agent-skills | 30.4K | OWASP systemático + threat modeling |
| 2 | `sql-code-review` | github/awesome-copilot | 12.9K | Análisis SQL/MySQL específico |
| 3 | `tdd` | mattpocock/skills | 825K | Disciplina red-green-refactor |
| 4 | `webapp-testing` | anthropics/skills | 148.6K | E2E con Playwright Python |
| 5 | `accessibility` | addyosmani/web-quality-skills | ~173/sem | WCAG 2.2 global |
| 6 | `verification-before-completion` | obra/superpowers | 198K | Gate de verificación |

### ELIMINAR (1 skill)

| # | Skill | Razón |
|---|-------|-------|
| 1 | `emil-design-eng` | Ejemplos React/JSX; incompatibile con Flask/Bootstrap/jQuery |

### CONJUNTO FINAL: 24 skills

```
Local (18):
  seguridad, db-transacciones, tests-pytest, refactor-controladores,
  reportes-pdf, reportes-detallados, envivo-audit, envivo-ux, envivo-ui,
  envivo-mobile, envivo-socketio, envivo-performance, envivo-offline,
  envivo-testing, envivo-review, interface-design, code-review,
  diagnosing-bugs

Externas (6):
  security-and-hardening, sql-code-review, tdd, webapp-testing,
  accessibility, verification-before-completion
```
