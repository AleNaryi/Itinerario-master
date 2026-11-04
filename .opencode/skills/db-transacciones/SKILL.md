---
name: db-transacciones
description: Reglas de acceso a datos y transacciones para Itinerario (PyMySQL crudo, sin ORM). Use when writing or modifying SQL queries, models in app/model/, database.py usage, multi-table writes, or anything involving estadio_db / seguridad databases. Trigger words: "transacción", "query", "SQL", "modelo", "base de datos".
---

# Base de datos — Itinerario

El proyecto usa PyMySQL crudo vía `app/database.py`: conexión por request guardada en `flask.g` (DictCursor), teardown cierra sola. Dos BD: `estadio_db` (negocio) y `seguridad` (usuarios/roles/sesiones).

## Reglas

1. **Toda escritura multi-statement usa `with transaction():`.** El autocommit está activo por defecto; sin el contextmanager de `app/database.py`, un fallo a mitad de camino deja escrituras parciales. Ejemplo: registrar contrato + pago + bitácora = una transacción.
2. **Queries siempre parametrizadas:** `cursor.execute("... WHERE id = %s", (id,))`. Prohibido f-string/format/`+` con valores en SQL. Los identificadores dinámicos (nombres de tabla/columna) van por whitelist de constantes, nunca del cliente.
3. **Una operación simple** → helpers de `database.py` (`fetch_one`, `fetch_all`, execute). No abrir cursores propios salvo streaming.
4. **Errores de BD nunca silenciosos.** Capturar la excepción específica, loguearla con contexto (módulo + query corta) y propagar o responder 500 genérico. Prohibido tragarla y devolver "ok".
5. **Modelos:** mantener el estilo existente — setters con validación (`ValidacionesMixin`) para rutas de formulario; lectura directa solo en queries de reportes/preview donde ya se hace así.
6. **Fechas y montos:** parsear/validar antes de llegar al SQL (`_parsear_fecha` en reportes es el patrón). NULL explícito (`None`), no cadenas vacías.

## Receta: escritura compuesta

```python
from app.database import transaction

with transaction() as cursor:
    cursor.execute("INSERT INTO contratos (...) VALUES (...)", (...))
    cursor.execute("INSERT INTO pagos (...) VALUES (...)", (...))
# commit automático; rollback ante excepción
```

## Checklist

- [ ] ¿Más de un INSERT/UPDATE seguido? → `transaction()`
- [ ] ¿Algún valor llega a SQL sin `%s`?
- [ ] ¿El fallo de BD deja datos a medias si no hay transacción?
- [ ] ¿El error queda registrado (log/bitácora)?
