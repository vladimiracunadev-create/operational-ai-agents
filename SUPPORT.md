# Soporte

> Cómo pedir ayuda de forma que se pueda resolver, y qué no debes adjuntar nunca.

[Repositorio](README.md) · [Instalación](INSTALL.md) · [CLI](docs/CLI.md)

---

## Antes de reportar

Ejecuta el diagnóstico y adjunta su salida:

```bash
operational-agents doctor
operational-agents validate
python -m unittest discover -s tests -v
```

Muchos problemas de instalación se resuelven con la tabla de [síntomas frecuentes](INSTALL.md#problemas-frecuentes).

## Dónde escribir

| Situación | Canal |
|---|---|
| Defecto reproducible | [Abrir un issue de bug](https://github.com/vladimiracunadev-create/operational-ai-agents/issues/new?template=bug.yml) |
| Proponer un agente nuevo | [Propuesta de agente](https://github.com/vladimiracunadev-create/operational-ai-agents/issues/new?template=agent_proposal.yml) |
| Duda de uso o instalación | [Discussions](https://github.com/vladimiracunadev-create/operational-ai-agents/discussions) |
| Vulnerabilidad | [Aviso privado](https://github.com/vladimiracunadev-create/operational-ai-agents/security/advisories/new) — nunca un issue público |

## Qué incluir

- Sistema operativo y versión de Python.
- Comando exacto que ejecutaste y salida completa **sanitizada**.
- Agente afectado, si aplica.
- Qué esperabas que ocurriera.

## Qué no incluir

> [!CAUTION]
> Nada de esto debe aparecer en un issue: secretos, tokens, credenciales, prompts privados, datos personales, rutas locales que te identifiquen ni trazas de repositorios de terceros.

Si la evidencia relevante contiene algo de eso, sustitúyelo por `<redactado: motivo>` en vez de borrarlo en silencio, para que el reporte siga siendo legible.

---

<div align="center"><sub><a href="README.md">Repositorio</a> · <a href="CONTRIBUTING.md">Contribuir</a> · <a href="SECURITY.md">Seguridad</a></sub></div>
