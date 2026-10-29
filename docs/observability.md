# Observability plan

## What we have today
- Structured JSON logs on stdout (time, level, message), readable by any log collector.
- /health (liveness) and /ready (readiness: can reach the database).
- Docker HEALTHCHECK on the app and pg_isready on the database.
- Version in /health, so we always know which release is running.

## Metrics to collect (proposal)
| Metric | Why |
|---|---|
| Request count by endpoint and status code | Traffic and error share |
| Error rate (5xx / total) | Primary signal that a release is broken |
| Latency p50 / p95 | Slowness shows before failures do |
| DB connection failures | Direct cause of /ready returning 503 |
| Container restarts | Crash loops |
| Disk used by the pgdata volume | Database stops when disk is full |

## Alerts (proposal)
1. Error rate above 5% for 5 minutes: page the on-call. Likely a bad release; action is rollback.
2. /ready failing for more than 2 minutes: DB or dependency down. Check DB container and logs.
3. Container restarted more than 3 times in 10 minutes: crash loop; read logs, roll back.
4. p95 latency above 1 second for 10 minutes: investigate load or slow queries (warning level).
5. pgdata disk above 80%: warning before the database runs out of space.

## Suggested tooling (cost-aware)
Start with docker logs plus a free Prometheus and Grafana pair, or CloudWatch if hosted on AWS.
Add the /metrics endpoint with a Prometheus client library when needed.
