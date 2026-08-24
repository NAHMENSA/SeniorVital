---
title: "S3-04 — Implementar comunicación y delegación entre agentes · Issue #20 · YaskCode-laboratory/wellness-platform-team5"
source: "https://github.com/YaskCode-laboratory/wellness-platform-team5/issues/20"
author:
  - "[[yaskelly]]"
published: 2026-08-21
created: 2026-08-22
description: "Objetivo Implementar el mecanismo de comunicación, coordinación y delegación que permita al Orchestrator Agent y a los agentes especializado"
tags:
  - "clippings"
---
## Objetivo

Implementar el mecanismo de comunicación, coordinación y delegación que permita al Orchestrator Agent y a los agentes especializados colaborar para resolver solicitudes dentro de la plataforma Wellness.

## Actividades

- Definir el formato de los mensajes intercambiados entre agentes.
- Establecer qué información de contexto debe acompañar cada solicitud.
- Implementar la delegación desde el Orchestrator Agent hacia el agente correspondiente.
- Implementar el retorno de resultados hacia el orquestador.
- Permitir flujos en los que intervenga más de un agente cuando el caso de uso lo requiera.
- Evitar ciclos de delegación o llamadas innecesarias.
- Mantener trazabilidad básica de qué agente fue invocado y por qué.
- Documentar el protocolo de interacción utilizado.
- Analizar brevemente cómo la arquitectura podría evolucionar hacia mecanismos de interoperabilidad como MCP o A2A.

## Entregables

- Mecanismo de comunicación entre agentes.
- Delegación funcional de tareas.
- Flujo de retorno de respuestas.
- Caso de colaboración entre agentes.
- Registro básico de las delegaciones realizadas.
- Documentación del protocolo de interacción.
- Nota arquitectónica sobre posible evolución hacia MCP y/o A2A.

## Criterios de aceptación

- El Orchestrator Agent puede delegar tareas correctamente.
- Los agentes reciben suficiente contexto para ejecutar su responsabilidad.
- Las respuestas regresan correctamente al orquestador.
- Existe al menos un escenario verificable de colaboración entre agentes.
- La comunicación posee una estructura definida y documentada.
- Es posible identificar qué agente intervino durante una ejecución.
- MCP y A2A se consideran arquitectónicamente sin requerir una implementación completa.