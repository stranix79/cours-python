# statusboard

Surveille des cibles HTTP, TCP et ping ; API REST + flux SSE + CLI. Solution du [labo 21](../README.md) du cours *Python de zéro à FastAPI*.

```bash
pip install -e ".[dev]"
statusboard add site http https://stranix.net
statusboard add dns tcp 1.1.1.1:53 --interval 10
statusboard add box ping 192.168.1.1
statusboard serve                          # http://127.0.0.1:8000/docs
curl -N http://127.0.0.1:8000/events       # le flux SSE, en direct
```

Configuration par variables d'environnement `STATUSBOARD_*` (voir `src/statusboard/config.py`). Compte par défaut : `admin` / `admin`, à changer avec `STATUSBOARD_ADMIN_PASSWORD`.

```bash
pytest                                     # tests
docker compose up --build                  # l'API dans un conteneur, base dans un volume
```
