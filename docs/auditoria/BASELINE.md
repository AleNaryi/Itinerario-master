# BASELINE — Itinerario

Fecha: 2026-09-01

---

## MÉTRICAS ACTUALES

### Tests

| Métrica | Valor |
|---------|-------|
| Tests totales | 63 |
| Tests pasando | 63 |
| Tests fallando | 0 |
| Archivos de test | 11 (10 test_*.py + conftest.py) |
| Cobertura estimada | ~30% (auth, permisos, validaciones, reportes) |
| Cobertura faltante | CRUD controllers, uploads, IDOR, SocketIO, chatbot |

### Seguridad

| Hallazgo | Cantidad |
|----------|----------|
| CRÍTICOS (XSS) | 2 |
| ALTOS | 5 |
| MEDIOS | 5 |
| BAJOS | 3 |
| **Total vulnerabilidades** | **15** |
| SQL Injection | 0 (limpio) |

### Frontend

| Hallazgo | Cantidad |
|----------|----------|
| XSS (CRÍTICO) | 5 |
| ALTOS | 4 |
| MEDIOS | 9 |
| BAJOS | 3 |
| **Total** | **21** |

### SQL/Performance

| Hallazgo | Cantidad |
|----------|----------|
| N+1 queries | 5 |
| Índices faltantes | 4 |
| Sin transacción | 3 |
| Sin límite | 4 |
| SELECT * problemático | 3 |
| **Total** | **19** |

### Skills

| Métrica | Valor |
|---------|-------|
| Skills locales | 17 |
| Skills externas | 2 |
| **Total skills** | **19** |

### Archivos

| Tipo | Cantidad | Líneas totales |
|------|----------|---------------|
| Python (app/) | ~65 | ~12,550 |
| JavaScript | 28 | ~5,917 |
| CSS | 6 | ~2,173 |
| HTML templates | 55 | ~5,000+ |
| Tests | 11 | ~1,542 |
| Documentación | 15 | ~7,584 |
| SQL | 5 | ~1,749 |
| **Total** | **~185** | **~36,500+** |

### Dependencias Python

| Paquete | Versión |
|---------|---------|
| Flask | 3.1.3 |
| Werkzeug | 3.1.8 |
| Flask-Login | 0.6.3 |
| Flask-WTF | 1.3.0 |
| Flask-SocketIO | 5.6.1 |
| PyMySQL | 1.2.0 |
| reportlab | -- |
| gunicorn | -- |
| eventlet | -- |
| python-dotenv | -- |

---

## ESTADO BASELINE

- **Functional:** Sistema funcional con 18 módulos, 63 tests verdes
- **Security:** 15 vulnerabilidades identificadas (2 críticas XSS)
- **Performance:** 5 N+1 queries, 4 índices faltantes
- **Testing:** ~30% cobertura, 0 tests de integración CRUD
- **Frontend:** 5 XSS via innerHTML, código muerto, duplicación
- **Docs:** Documentación extensa pero desactualizada en CHECKLIST.md

---

## REFERENCIA PARA MEJORAS

Cualquier mejora debe compararse contra este baseline:

```
Tests:             63 → ?
Seguridad:         15 hallazgos → ?
N+1 queries:       5 → ?
Índices faltantes: 4 → ?
XSS frontend:      5 → ?
Cobertura:         ~30% → ?
```
