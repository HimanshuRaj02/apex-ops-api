# Failure investigation: database down

## Symptom
With the database stopped, /health returned 200 but /ready returned 503.

## Steps taken
1. Checked liveness and readiness with curl: app alive (200), not ready (503).
2. `docker compose ps` showed only the app container; the db container was not running.
3. `docker compose logs app --tail 5` showed a structured JSON error line:
   `readiness check failed: could not translate host name "db" to address: Name or service not known`

## Root cause
The database container was stopped (simulated with `docker compose stop db`). When it stops, the service name `db` no longer resolves on the Compose network, so the app cannot reach Postgres.
(If the database were running but refusing connections, the message would say "connection refused" instead.)

## Fix
`docker compose start db`. After about 8 seconds /ready returned 200 and the earlier incident (id 1, "disk full") was still present, because the data lives in the pgdata volume.

## Why this is safe
- /ready returning 503 tells a load balancer to stop sending traffic, while /health stays 200 so the app is not needlessly restarted.
- The app has no hard dependency crash: it keeps running and recovers without a restart once the database is back.

## Prevention
- Alert when /ready fails for more than 2 minutes (see observability.md).
- `restart: unless-stopped` brings the database back after a crash.
- Healthcheck plus `depends_on: service_healthy` stop the app from starting before the database is ready.
