# Runbook

Commands run from the project folder. Version tags look like 1.0.0.

## Check status
~~~bash
docker compose ps                       # app and db should be healthy
curl -s localhost:8000/health           # liveness, shows running version
curl -s localhost:8000/ready            # readiness, 200 if DB reachable
docker compose logs app --tail 20       # JSON logs
cat .current_version .previous_version  # what is deployed and what we can roll back to
~~~

## Deploy a new version
~~~bash
git pull
./deploy.sh 1.2.0
~~~
The script builds the image apex-ops-api:1.2.0, starts it, waits up to 60 seconds for /ready, and records the version. If /ready never turns healthy, it rolls back automatically.

## Roll back
~~~bash
./rollback.sh            # previous version
./rollback.sh 1.0.0      # specific version
~~~
Rollback reuses the existing image (no rebuild) and the database volume is untouched.

## Incident: /ready returns 503
1. curl /health. If 200, the app is alive and the problem is a dependency.
2. docker compose ps. Is the db container running and healthy?
3. docker compose logs app --tail 20. Read the readiness error.
   - could not translate host name "db": db container is stopped.
   - connection refused: db is running but not accepting connections.
   - simulated bug in release: a -bad demo version is running.
4. Fix: docker compose start db, or ./rollback.sh if a new release caused it.
5. Confirm: curl /ready returns 200 and /incidents still returns data.

## Incident: error rate high after a release
1. Check the version in /health.
2. ./rollback.sh to the last known good version.
3. Read logs for the failing endpoint; fix forward in a branch, let CI pass, redeploy.

## Database backup and restore
~~~bash
mkdir -p backups
docker compose exec -T db pg_dump -U apex apexops > backups/backup.sql
# restore
cat backups/backup.sql | docker compose exec -T db psql -U apex -d apexops
~~~
Values apex and apexops come from .env (POSTGRES_USER, POSTGRES_DB).

## Safety rules
- Never run docker compose down -v on a real environment: it deletes the database volume.
- Never commit .env. Real secrets stay outside Git.
- Every change goes through a branch and pull request so CI runs first.
