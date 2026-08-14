# Seguridad

## Reporte

No publiques vulnerabilidades explotables ni secretos en issues. Usa un canal privado del propietario del repositorio.

## Garantías y límites

- La CLI no usa `shell=True` ni agrega flags para omitir permisos.
- El servidor escucha en loopback por defecto y no implementa autenticación; el bind externo exige una variable explícita y no debe exponerse a Internet. Compose publica únicamente en loopback del host.
- La evidencia es opt-in y pasa por redacción básica, que no sustituye una revisión humana.
- Los agentes que escriben usan permisos normales y aislamiento worktree en el adaptador Claude.
- Publicar, desplegar, borrar, rotar credenciales o tocar producción siempre requiere aprobación humana.

Consulta [docs/SECURITY_MODEL.md](docs/SECURITY_MODEL.md) para amenazas, controles y límites.
