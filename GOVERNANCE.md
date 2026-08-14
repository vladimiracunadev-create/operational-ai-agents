# Gobernanza

> Quién decide qué, y qué decisiones no puede tomar nunca un agente — incluidos los de este catálogo.

[Repositorio](README.md) · [Contribuir](CONTRIBUTING.md) · [Modelo de madurez](docs/MATURITY_MODEL.md)

---

## Decisión final

El propietario del repositorio mantiene la decisión final sobre el catálogo, los releases y la promoción de madurez.

## Cambios que exigen revisión explícita

Estos no se aceptan como cambio rutinario, aunque la build quede verde:

| Cambio | Por qué |
|---|---|
| Añadir, quitar o relajar un gate humano | altera la frontera de autorización del agente |
| Ampliar la tool allowlist de un agente | amplía lo que puede tocar sin que nadie lo note |
| Cambiar `permission_mode` o `isolation` | puede convertir un agente contenido en uno que muta libremente |
| Cambiar la definición de evidencia | afecta a qué se puede afirmar |
| Promover el estado de madurez de un agente | es una afirmación pública sobre adopción |
| Retirar una prueba que respalda una garantía | convierte una garantía verificada en una promesa |

## Reglas que no dependen de nadie

1. **Ningún agente puede autopromover su estado de madurez.** El `status` lo cambia una persona con evidencia revisada.
2. **Ningún agente puede aprobar su propia publicación**, ni la de otro agente.
3. **La aprobación de un agente no sustituye la del usuario.** Un coordinador eleva la decisión; no la resuelve.
4. **Las garantías se retiran con su prueba, no sin ella.** Si una garantía deja de cumplirse, se elimina de la documentación en el mismo cambio.

## Versionado

- El repositorio y cada agente versionan por separado: un agente puede evolucionar su contrato sin arrastrar al resto.
- Un cambio material del contrato de un agente —misión, tools o gates— invalida la evidencia previa y puede degradar su estado.
- El formato de changelog y el criterio semántico están en [CHANGELOG.md](CHANGELOG.md).

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="CODE_OF_CONDUCT.md">Código de conducta</a> · <a href="ROADMAP.md">Roadmap</a></sub></div>
