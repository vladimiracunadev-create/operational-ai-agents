# Docker

`docker compose up --build` sirve el catálogo y planner local. El proceso escucha dentro del contenedor, pero Compose publica el puerto únicamente en `127.0.0.1`. El contenedor es read-only, no ejecuta modelos y no debe recibir credenciales.
