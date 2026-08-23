---
title: "S2-04 - Integrar herramientas mediante Tool Calling · Issue #13 · YaskCode-laboratory/wellness-platform-team5"
source: "https://github.com/YaskCode-laboratory/wellness-platform-team5/issues/13"
author:
  - "[[yaskelly]]"
published: 2026-08-21
created: 2026-08-22
description: "Objetivo Integrar herramientas externas mediante Tool Calling para permitir que el Wellness Coach Agent 2.0 pueda ejecutar acciones o consul"
tags:
  - "clippings"
---
## Objetivo

Integrar herramientas externas mediante Tool Calling para permitir que el Wellness Coach Agent 2.0 pueda ejecutar acciones o consultar servicios necesarios para resolver tareas del dominio Wellness.

## Actividades

- Identificar herramientas relevantes para las responsabilidades del agente.
- Definir los parámetros de entrada y salida de cada herramienta seleccionada.
- Implementar al menos una herramienta funcional.
- Integrar la herramienta con el agente.
- Implementar el mecanismo de Tool Calling.
- Procesar correctamente los resultados obtenidos por las herramientas.
- Gestionar posibles errores durante la ejecución.
- Realizar pruebas con escenarios que requieran y que no requieran utilización de herramientas.
- Documentar la integración realizada.

## Entregables

- Herramienta externa integrada con el agente.
- Implementación funcional de Tool Calling.
- Código de invocación y procesamiento de resultados.
- Casos de prueba.
- Evidencia del funcionamiento de la integración.
- Documentación de las herramientas utilizadas.

## Criterios de aceptación

- El agente identifica correctamente cuándo necesita utilizar una herramienta.
- La herramienta recibe parámetros válidos.
- La herramienta puede ejecutarse correctamente desde el flujo del agente.
- El resultado obtenido se incorpora adecuadamente a la respuesta.
- Los errores de ejecución son gestionados de manera controlada.
- La integración puede ejecutarse de forma reproducible.
- El código y la documentación correspondiente están disponibles en el repositorio.