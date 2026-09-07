# Modelo de seguridad

> Qué puede hacer un agente, qué no, dónde se detiene a preguntar y qué garantías están cubiertas por pruebas en vez de por promesas.

[← Documentación](README.md) · [Repositorio](../README.md) · [Política de reporte](../SECURITY.md)

---

## Principio rector

> **Acceso no es autorización.**

Que un agente pueda leer un repositorio, listar credenciales o alcanzar un endpoint no le concede permiso para publicar, desplegar, borrar ni gastar dinero. Cada una de esas acciones exige una decisión humana en el momento de ejecutarla, y una aprobación acotada nunca habilita las fases posteriores.

## Amenazas consideradas

| Amenaza | Control |
|---|---|
| El agente interpreta acceso técnico como permiso | `approval_points` obligatorios y fases de inspección antes de mutar |
| Un agente aprueba en nombre del usuario | ningún gate puede satisfacerse con la salida de otro agente |
| Escalada silenciosa de alcance | `scope_expansion` es un gate en todos los agentes que pueden ampliarlo |
| Mutación sin comprensión previa | el contrato exige inspección y plan antes de la fase de implementación |
| Cambios que contaminan la copia de trabajo | `isolation: worktree` en todo agente que escribe |
| Secretos filtrados en trazas | evidencia opt-in y redacción antes de persistir |
| Ejecución de comandos construida por concatenación | la CLI invoca con listas de argumentos, nunca `shell=True` |
| Panel local expuesto a la red | bind en loopback; salir de ahí exige una variable de entorno explícita |
| Sobrescritura de agentes que el usuario escribió | el exportador se niega si el destino no lleva su marca de gestión |
| Superficie de supply chain | cero dependencias runtime y acciones de CI fijadas por SHA |
| Movimiento financiero autónomo | familia financiera sin `Write`, `Edit` ni `Bash`; políticas niegan claves, trading, retiros y mutación productiva |

## Garantías verificadas

Cada fila está cubierta por una prueba automatizada que corre en cada push. No son promesas de documentación:

| Garantía | Prueba |
|---|---|
| La CLI no usa `shell=True` ni añade flags para omitir permisos | `test_cli_adds_no_permission_bypass` |
| Ningún adaptador de runtime amplía permisos por su cuenta | `test_no_runtime_adds_permission_bypass` |
| Una capacidad ofrecida por el runtime y no autorizada queda `BLOCKED` | `test_offered_but_unauthorized_capability_is_blocked` |
| Falta una capacidad requerida: se declara y **no** se ejecuta nada | `test_run_refuses_when_a_required_capability_is_missing` |
| Un runtime desconocido falla en vez de caer en otro proveedor | `test_unknown_runtime_fails_instead_of_falling_back` |
| El sobre de evidencia nunca marca una aprobación como concedida | `test_envelope_never_marks_an_approval_as_granted` |
| La evidencia no arrastra rutas locales del ejecutable | `test_envelope_keeps_local_paths_out_of_the_command` |
| Un agente que escribe no puede omitir la aprobación de permisos | `test_mutating_agents_do_not_bypass_permissions` |
| Un agente de solo lectura deniega `Write` y `Edit` explícitamente | `test_read_only_agents_deny_writes` |
| Todo agente declara al menos un gate humano | `test_every_agent_has_human_gates` |
| El bind fuera de loopback exige opt-in explícito | `test_server_refuses_non_loopback_bind_without_optin` |
| Los secretos se redactan antes de persistir | `test_redaction` |
| El exportador preserva agentes que no administra | `test_export_preserves_unmanaged_agent` |
| La desinstalación no toca agentes ajenos | `test_uninstall_preserves_unmanaged_agent` |
| El catálogo público no contiene datos personales ni rutas locales | `test_agents_carry_no_personal_data` |
| Todo agente financiero es de solo lectura y carece de shell | `test_financial_agents_are_strictly_read_only` |
| Sus políticas niegan claves privadas y acciones financieras | `test_financial_policies_forbid_asset_authority` |

## Gates humanos

Aparecen en `approval_points` y el agente debe detenerse **antes** de la acción, presentando opciones concretas:

- publicar, etiquetar o desplegar;
- borrar o cualquier cambio destructivo;
- rotar o usar credenciales;
- contratar o consumir un servicio de pago;
- ampliar el alcance más allá de lo acordado;
- modificar perfiles o descripciones visibles públicamente.

> [!WARNING]
> Una aprobación de otro agente **no** sustituye la del usuario. Un coordinador puede reunir evidencia y proponer, pero eleva la decisión: no la resuelve.

## Límites conocidos

Declarados explícitamente, porque un modelo de seguridad que solo enumera sus fortalezas es propaganda:

- **El panel local no implementa autenticación.** Está pensado para loopback y no debe exponerse a Internet.
- **La redacción de secretos es heurística.** Reduce el riesgo de filtración accidental; no sustituye la revisión humana antes de publicar evidencia.
- **Las garantías cubren esta CLI y estos contratos**, no el comportamiento del modelo dentro del runtime, que depende de los permisos que el propio runtime aplique.
- **`isolation: worktree` aísla archivos, no efectos externos.** Un comando que llama a un servicio remoto sale del aislamiento.
- **Las evaluaciones son deterministas.** Comprueban que el contrato no pierda controles al evolucionar; no miden la calidad del razonamiento del modelo.
- **La matriz de compatibilidad resuelve contratos, no observa ejecuciones.** Un `SUPPORTED` dice que el runtime declara las capacidades necesarias, no que el agente cumpla la misión al ejecutarse.
- **Un plugin de terceros que registre un runtime corre con los permisos de tu intérprete.** El registro lo aísla de romper la CLI, no de lo que haga el propio paquete: instala plugins con el mismo criterio que cualquier dependencia.

## Reportar una vulnerabilidad

No abras un issue público. El procedimiento está en [SECURITY.md](../SECURITY.md).

---

<div align="center"><sub><a href="README.md">Documentación</a> · <a href="AGENT_CONTRACT.md">Contrato</a> · <a href="EVIDENCE_GUIDE.md">Evidencia</a></sub></div>
