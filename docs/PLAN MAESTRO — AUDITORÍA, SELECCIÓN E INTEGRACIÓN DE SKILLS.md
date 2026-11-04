# PLAN MAESTRO — AUDITORÍA, SELECCIÓN E INTEGRACIÓN DE SKILLS

## MISIÓN

Actúa como un equipo senior de ingeniería de software, seguridad, QA, arquitectura, UX, performance y auditoría.

Tu objetivo es analizar exhaustivamente el sistema existente y determinar cuáles son las mejores skills disponibles actualmente en:

https://www.skills.sh/

para mejorar el proyecto al máximo nivel posible.

IMPORTANTE:

NO debes rehacer el sistema.

NO debes cambiar la arquitectura base.

NO debes migrar tecnologías por moda.

NO debes sustituir Flask.

NO debes sustituir PyMySQL por un ORM.

NO debes cambiar MySQL.

NO debes reemplazar Bootstrap/jQuery/DataTables/SweetAlert2 sin una justificación excepcional.

NO debes modificar el modelo de datos simplemente para "modernizarlo".

NO debes convertir el proyecto a React, Vue, Next.js, FastAPI, Django, SQLAlchemy u otra tecnología.

NO debes introducir Docker como requisito.

El sistema debe continuar funcionando localmente.

La misión es MEJORAR el sistema existente, no reconstruirlo.

---

# 1. DOCUMENTOS OBLIGATORIOS

Antes de realizar cualquier modificación debes leer:

- SISTEMA_COMPLETO.md
- AGENTS.md
- CHECKLIST.md
- requirements.txt
- estructura completa del proyecto
- archivos SQL existentes
- .opencode/
- .opencode/skills/
- documentación existente en docs/
- tests/
- configuración existente

Si existe una contradicción entre documentación y código real:

EL CÓDIGO REAL TIENE PRIORIDAD.

No inventes tablas, columnas, rutas, funciones, permisos ni dependencias.

---

# 2. ESTADO BASE DEL SISTEMA

El sistema utiliza:

Backend:
- Python 3
- Flask 3
- Flask application factory
- PyMySQL
- Flask-Login
- Flask-WTF
- Flask-SocketIO
- eventlet

Frontend:
- HTML
- Bootstrap 5.3
- Font Awesome
- jQuery
- DataTables
- SweetAlert2

Base de datos:
- MySQL
- estadio_db
- seguridad

PDF:
- ReportLab

Testing:
- pytest

La arquitectura principal es:

controller/
model/
view/
helpers/
static/
tests/
docs/

Mantener esta estructura.

---

# 3. PRIMERA FASE — INVENTARIO

NO MODIFIQUES CÓDIGO.

Realiza primero una auditoría completa.

Identifica:

- arquitectura
- dependencias
- blueprints
- modelos
- rutas
- endpoints
- permisos
- tablas
- relaciones
- transacciones
- SocketIO
- frontend
- JavaScript
- CSS
- reportes
- PDFs
- chatbot
- autenticación
- autorización
- logging
- auditoría
- tests
- documentación
- skills existentes

Genera:

docs/auditoria/INVENTARIO_SISTEMA.md

---

# 4. SEGUNDA FASE — AUDITAR SKILLS EXISTENTES

Inspecciona:

.opencode/skills/

Para cada skill existente determina:

- nombre
- objetivo
- área
- archivos afectados
- cuándo debe utilizarse
- posibles conflictos
- redundancias
- calidad
- utilidad real

NO reemplaces automáticamente ninguna skill existente.

---

# 5. TERCERA FASE — INVESTIGACIÓN DE SKILLS.SH

Investiga https://www.skills.sh/

No te limites a las skills populares.

Busca skills relacionadas con:

- Python
- Flask
- web applications
- security
- OWASP
- SQL
- MySQL
- testing
- pytest
- Playwright
- browser testing
- accessibility
- performance
- code review
- architecture
- refactoring
- frontend quality
- JavaScript
- HTML
- CSS
- Git
- observability
- debugging
- documentation
- maintainability

Utiliza la información actual disponible en skills.sh.

No instales una skill únicamente porque tenga muchas instalaciones.

Evalúa:

1. relevancia para ESTE proyecto
2. calidad de la metodología
3. reputación del repositorio
4. instalaciones
5. actividad
6. auditorías de seguridad disponibles
7. compatibilidad con OpenCode
8. compatibilidad tecnológica
9. solapamiento con skills existentes
10. riesgo de modificar la arquitectura
11. utilidad práctica
12. capacidad de producir mejoras verificables

---

# 6. CUARTA FASE — SKILL MATRIX

Crea:

docs/auditoria/SKILL_MATRIX.md

Para cada skill candidata utiliza:

| Campo | Evaluación |
|---|---|
| Skill | nombre |
| Repositorio | owner/repo |
| Área | categoría |
| Compatibilidad | 0-10 |
| Relevancia | 0-10 |
| Calidad | 0-10 |
| Seguridad | 0-10 |
| Mantenibilidad | 0-10 |
| Riesgo | 0-10 |
| Duplicación | 0-10 |
| Beneficio esperado | 0-10 |
| Decisión | instalar/no instalar |
| Justificación | explicación |

Calcula una puntuación global.

---

# 7. REGLA DE NO DUPLICACIÓN

Antes de instalar una skill:

1. comprueba .opencode/skills/
2. comprueba skills ya instaladas
3. compara funcionalidad
4. compara instrucciones
5. identifica solapamientos

Si una skill existente ya cubre el problema suficientemente:

NO INSTALAR.

Si la nueva skill es claramente superior:

proponer reemplazo.

Pero NO eliminar la skill existente automáticamente.

---

# 8. SKILLS PRIORITARIAS A INVESTIGAR

Como punto inicial investiga especialmente:

- improve-codebase-architecture
- code-review-and-quality
- security-and-hardening
- code-security
- tdd
- webapp-testing
- browser-testing-with-devtools
- web-quality-audit
- accessibility
- performance
- core-web-vitals
- sql-code-review

Estas son candidatas.

NO son instalación automática.

Debes descubrir también otras skills que puedan ser mejores.

---

# 9. QUINTA FASE — PLAN DE INTEGRACIÓN

Después de terminar la matriz:

clasifica las skills:

## NIVEL A — IMPRESCINDIBLES

Skills que aportan una mejora directa y clara.

## NIVEL B — MUY RECOMENDADAS

Skills de alto valor pero no indispensables.

## NIVEL C — ESPECIALIZADAS

Solo utilizarlas cuando se trabaje determinada área.

## NIVEL D — REDUNDANTES

No instalar.

## NIVEL E — PELIGROSAS PARA ESTE PROYECTO

No instalar porque puedan provocar migraciones, reestructuraciones o cambios innecesarios.

---

# 10. REGLA FUNDAMENTAL DE ARQUITECTURA

No modificar:

controller/
model/
view/
helpers/

por el simple hecho de que una skill recomiende otra arquitectura.

Una recomendación arquitectónica solo puede aplicarse si:

- mejora una deficiencia real
- mantiene compatibilidad
- no rompe contratos existentes
- tiene pruebas
- tiene justificación
- mantiene la estructura general

Preferir:

MEJORA INCREMENTAL

sobre:

REESCRITURA.

---

# 11. SEGURIDAD

Realiza una auditoría específica de:

- autenticación
- autorización
- permisos
- IDOR
- CSRF
- XSS
- SQL Injection
- open redirects
- file uploads
- path traversal
- sesiones
- password reset
- secretos
- cookies
- headers
- CORS
- SocketIO
- validación server-side
- logging
- exposición de información
- errores
- rate limiting
- control de acceso horizontal
- control de acceso vertical

IMPORTANTE:

Las validaciones JavaScript nunca sustituyen las validaciones server-side.

Los tests nunca deben ejecutarse contra bases reales.

---

# 12. SQL

Debido a que el sistema utiliza PyMySQL crudo:

revisar:

- queries parametrizadas
- concatenación SQL
- SELECT innecesarios
- JOINs
- índices
- N+1
- consultas repetidas
- transacciones
- deadlocks potenciales
- integridad referencial
- consultas de reportes
- filtros dinámicos
- whitelist del constructor de reportes
- rendimiento

NO migrar a ORM.

---

# 13. TESTING

El sistema actualmente posee una suite existente.

NO reemplazarla.

Mejorarla.

Objetivos:

- unit tests
- integration tests
- security tests
- authorization tests
- regression tests
- browser/E2E tests
- critical user journeys

Especial atención a:

- login
- permisos
- usuarios
- tareas
- notificaciones
- inventario
- mantenimiento
- contratos
- pagos
- reportes
- PDFs
- EN VIVO

Todo test debe ejecutarse contra bases de prueba.

---

# 14. EN VIVO — REGLAS ABSOLUTAS

NO modificar:

- backend
- API
- modelos
- DB
- SocketIO server

para mejoras puramente visuales o UX.

Mantener:

pendiente
→
en_curso
→
completado

Mantener retroceso.

Mantener autoridad del backend.

Mantener SocketIO.

Mantener server-side clocks.

Mantener mobile-first.

Mantener dark/light.

No introducir PWA.

No introducir modo TV.

No introducir polling.

Cualquier skill que contradiga estas reglas queda descartada para EN VIVO.

---

# 15. FRONTEND

Auditar:

- UX
- responsive design
- accesibilidad
- navegación
- formularios
- feedback
- estados loading/error/empty
- tablas
- modales
- mensajes
- JavaScript
- eventos
- duplicación
- errores de consola
- network requests
- rendimiento
- compatibilidad móvil

NO cambiar de framework.

---

# 16. PERFORMANCE

No optimices por intuición.

Primero medir.

Para cada problema:

1. establecer baseline
2. identificar cuello de botella
3. aplicar cambio mínimo
4. medir nuevamente
5. conservar el cambio solo si existe mejora verificable

Medir:

- tiempo de carga
- consultas SQL
- tamaño de recursos
- JavaScript
- CSS
- imágenes
- respuesta backend
- rendimiento de tablas
- reportes
- navegación
- EN VIVO

---

# 17. CALIDAD DEL CÓDIGO

Buscar:

- duplicación
- funciones demasiado grandes
- módulos poco cohesionados
- código muerto
- imports innecesarios
- errores silenciosos
- manejo deficiente de excepciones
- nombres inconsistentes
- responsabilidades mezcladas
- consultas duplicadas
- lógica duplicada
- JavaScript duplicado
- CSS duplicado

Pero:

NO refactorizar por estética.

Solo refactorizar cuando exista beneficio verificable.

---

# 18. DOCUMENTACIÓN

Toda mejora importante debe actualizar documentación.

Mantener sincronizados:

- AGENTS.md
- CHECKLIST.md
- SISTEMA_COMPLETO.md
- documentación de módulos
- documentación de seguridad
- documentación de testing

Si una skill introduce una nueva regla útil:

documentarla.

---

# 19. INSTALACIÓN

Una vez terminada la auditoría:

NO instalar inmediatamente.

Primero presentar:

### SKILLS RECOMENDADAS

Lista:

1. skill
2. repositorio
3. razón
4. beneficio
5. riesgo
6. compatibilidad
7. duplicación
8. prioridad

Después generar:

docs/auditoria/SKILLS_APROBADAS.md

Solo después de determinar que son seguras y compatibles proceder a instalarlas.

---

# 20. INSTALACIÓN SEGURA

Usar:

npx skills add ...

No instalar paquetes desconocidos sin revisar su origen.

Preferir repositorios reconocidos.

Revisar auditorías de seguridad cuando estén disponibles.

No instalar skills que soliciten cambios innecesarios al sistema.

---

# 21. DESPUÉS DE INSTALAR

Verificar:

- OpenCode reconoce las skills
- no existen duplicados
- no hay conflictos
- no cambió la aplicación
- tests continúan funcionando
- configuración intacta

Ejecutar:

pytest

y las verificaciones adicionales correspondientes.

---

# 22. FASE DE MEJORA

Solo después de tener:

- inventario
- skill matrix
- skills seleccionadas
- baseline
- tests verdes

comenzar las mejoras.

Orden recomendado:

1. Seguridad
2. Testing
3. Bugs
4. Arquitectura incremental
5. SQL
6. Performance backend
7. Frontend
8. Accessibility
9. UX
10. Documentación

---

# 23. QUALITY GATE

Ningún trabajo se considera terminado simplemente porque "el código funciona".

Antes de finalizar una tarea comprobar:

### Correctness
¿Funciona?

### Security
¿Es seguro?

### Tests
¿Está probado?

### Regression
¿Rompió algo existente?

### Performance
¿Mejoró o se mantuvo?

### UX
¿La experiencia mejoró?

### Accessibility
¿Es accesible?

### Maintainability
¿Es más fácil mantenerlo?

### Documentation
¿La documentación sigue siendo correcta?

---

# 24. REGLA DE VERIFICACIÓN

Nunca afirmar:

"mejorado"

sin evidencia.

Siempre indicar:

ANTES
→
DESPUÉS

Ejemplo:

Tests:
63 → 81

Errores:
12 → 3

Carga:
2.4s → 1.6s

Queries:
X → Y

Accessibility:
X → Y

Security findings:
X → Y

Si no existe medición:

indicar:

"NO MEDIDO".

Nunca inventar resultados.

---

# 25. REGLA DE CONSERVACIÓN

El sistema actual tiene funcionalidades y reglas que ya fueron diseñadas deliberadamente.

NO eliminar:

- funcionalidades
- permisos
- tablas
- endpoints
- reportes
- auditoría
- SocketIO
- EN VIVO
- chatbot Aurora
- notificaciones

sin evidencia de que están obsoletos.

---

# 26. BUGS CONOCIDOS

No reintroducir:

- Multiple primary key en rol_model
- problema del branch resumen de reportes
- problemas conocidos de sesión
- problemas conocidos de SocketIO

Registrar cualquier nuevo hallazgo.

---

# 27. RESULTADO FINAL

El objetivo final NO es producir una nueva aplicación.

El objetivo es producir:

LA MISMA APLICACIÓN

pero:

- más segura
- más estable
- más rápida
- mejor probada
- mejor documentada
- más mantenible
- más accesible
- con mejor UX
- con mejor calidad de código
- con mejor diagnóstico
- con mejor observabilidad
- con menos deuda técnica

manteniendo la arquitectura y comportamiento existentes.

---

# 28. ENTREGABLES OBLIGATORIOS

Generar:

docs/auditoria/
├── INVENTARIO_SISTEMA.md
├── SKILL_MATRIX.md
├── SKILLS_APROBADAS.md
├── AUDITORIA_SEGURIDAD.md
├── AUDITORIA_SQL.md
├── AUDITORIA_TESTING.md
├── AUDITORIA_FRONTEND.md
├── AUDITORIA_PERFORMANCE.md
├── PLAN_MEJORA_PRIORIZADO.md
└── BASELINE.md

No comenzar cambios de código importantes hasta completar esta fase.

---

# 29. PRINCIPIO FINAL

Piensa como un equipo de ingeniería que debe mantener un sistema empresarial en producción.

NO busques la arquitectura más moderna.

Busca:

LA MEJOR VERSIÓN POSIBLE DE ESTA ARQUITECTURA.

Cada cambio debe responder:

¿Por qué?

¿Qué problema resuelve?

¿Qué riesgo introduce?

¿Cómo se prueba?

¿Cómo sabemos que realmente mejoró?

Si no puedes responder esas preguntas:

NO CAMBIES EL CÓDIGO.