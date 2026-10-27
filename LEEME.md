# Llamado a Tiempo

La app se actualiza sola cada 15 minutos con los llamados del portal Educacionales.

- `index.html`: la app que ven los docentes.
- `scripts/actualizar.py`: trae los llamados y arma `data.json` (sin datos de personas).
- `.github/workflows/actualizar.yml`: ejecuta el programa cada 15 minutos y publica el sitio.
- `data_manual.json` (opcional): si el portal no responde desde GitHub, subí acá el archivo bajado a mano y se usa como respaldo.

Pasos de instalación: ver el mensaje del chat. En Settings > Pages, la fuente (Source) debe ser **GitHub Actions**.
