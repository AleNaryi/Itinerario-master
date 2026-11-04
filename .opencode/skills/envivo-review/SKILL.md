---
name: envivo-review
description: Revisión post-cambio del módulo EN VIVO — lógica, UX, UI, SocketIO, permisos, performance, mobile, accesibilidad, dark/light, offline y regresiones; clasifica hallazgos CRÍTICO/ALTO/MEDIO/BAJO antes de corregir. Use after ANY significant modification to app/view/en_vivo/, or when the user says "revisa el cambio", "review en vivo".
---

# envivo-review

Ejecutar DESPUÉS de cualquier modificación importante del módulo. Primero se reporta, después se corrige (con aprobación o según flujo).

## No modificar inmediatamente

Primero producir el informe completo con severidades:

```text
CRÍTICO · ALTO · MEDIO · BAJO
```

## Checklist de revisión

- **Lógica de secuencia**: imposible saltar elementos; avance exactamente 1; retroceso con semántica correcta ("lo marqué mal y aún lo debo ejecutar").
- **UX**: jerarquía ACTUAL/SIGUIENTE/PENDIENTES clara; feedback de guardado presente; cronómetro con sobretiempo correcto (`duracion_estimada` en SEGUNDOS).
- **UI**: tokens consistentes; glow moderado solo en en_curso; logo existente, sin logos inventados.
- **SocketIO**: sin polling; actualización parcial del DOM; listeners/timers únicos; reconnect re-registra y reconcilia.
- **Offline**: cola visible (CAMBIOS PENDIENTES: n); ninguna acción perdida en silencio; servidor gana conflictos.
- **Permisos**: frontend solo mejora experiencia; el backend sigue siendo autoridad; nada de seguridad nueva inventada.
- **Mobile**: 360px usable con una mano; doble tap robusto sin zoom fantasma; header compacto.
- **Desktop**: excelente sin ser copia gigante del móvil.
- **Accesibilidad**: contraste AA ambos temas, focus visible, aria-labels, atajos teclado no invasivos, `prefers-reduced-motion`.
- **Regresiones**: comparar contra comportamiento anterior (doble toque, retroceso, contadores, presencia "N viendo", finalizar).
- **Performance**: sin timers duplicados ni re-renders globales; fluido con ~30 usuarios.

## Reglas generales recordatorias

Sin backend/API/DB/SocketIO-server modificado. Mobile-first. Sin PWA ni modo TV. Sin dependencias nuevas innecesarias.
