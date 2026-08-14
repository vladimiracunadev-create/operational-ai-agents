# Caso de uso — `<agent-id>` v`<x.y.z>`

<!--
Plantilla para promover un agente de IMPLEMENTED a OPERATIONAL_LOCAL.
Antes de guardarlo en evidence/case-studies/, léelo entero: la redacción
automática es una primera barrera, no una revisión.
Sustituye lo eliminado por <redactado: motivo>, nunca lo borres en silencio.
-->

| | |
|---|---|
| **Agente y versión** | `<agent-id>` v`<x.y.z>` |
| **Fecha** | `<AAAA-MM-DD>` — absoluta, nunca «hoy» |
| **Runtime y modelo** | `<p. ej. Claude Code, modelo heredado>` |
| **Estado final** | `COMPLETED` · `PARTIAL` · `BLOCKED` · `NO_CHANGE` |

## Objetivo real

Qué se le encargó, en las palabras con las que se le encargó.

## Alcance autorizado

Qué se le permitió tocar y qué quedó explícitamente fuera. Incluye el momento en que se concedió la autorización.

## Qué hizo

Las decisiones que tomó por su cuenta, no solo el resultado.

## Verificaciones

Una fila por comprobación. Sin comando no es una verificación, es una impresión.

| Qué se verificó | Comando | Resultado |
|---|---|---|
| | | |

## Intervención humana

| Momento | Por qué hizo falta | Qué se decidió |
|---|---|---|
| | | |

Si no hubo ninguna, dilo explícitamente: también es un dato.

## Evidencia sanitizada

Hashes, conteos y extractos mínimos. Nunca volcados completos.

## Limitaciones y riesgo residual

Qué quedó sin comprobar, qué supuestos no se validaron y qué podría fallar por ello.

## Decisión de madurez

| | |
|---|---|
| **Estado propuesto** | `<estado>` |
| **Quién lo revisó** | `<persona>` |
| **Justificación** | por qué esta evidencia sostiene ese estado |

> Recuerda: pasar las pruebas **mantiene** el estado; solo la evidencia revisada lo sube.
> Criterios en [`docs/MATURITY_MODEL.md`](../../docs/MATURITY_MODEL.md).
