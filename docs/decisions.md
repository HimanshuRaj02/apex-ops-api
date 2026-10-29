# Decision memo

Goal: a small service that can be built, tested, released and rolled back safely, with every claim backed by evidence.

| Decision | Why | Trade-off |
|---|---|---|
| Flask + gunicorn | Small and well known; fast to explain and test | Not async; fine for this size |
| PostgreSQL | Real relational DB, same in tests, local and CI | Heavier than SQLite, but tests catch real SQL problems |
| Docker Compose on one host | Reproducible with one command; matches the assignment scope | No multi-host scaling or self-healing beyond restart policy |
| Named volume for data | Data survives container replacement and rollback | Needs backups; down -v deletes it |
| Separate /health and /ready | Alive vs able to serve; avoids restarting the app when only the DB is down | One extra endpoint to maintain |
| Version-tagged images | Rollback means re-running an image that already worked | Old images take disk space |
| deploy.sh with readiness gate | A bad release rolls back automatically within about a minute | Simple script, not a full orchestrator |
| CI chain test -> build -> deploy using needs | A failing test blocks build and deploy (shown on PR #1) | Deploy job is a smoke test on a temporary runner, not a real server |
| Trivy scan reporting only | Visibility without blocking the demo on base-image findings | Findings are not enforced yet; planned next step |
| Demo hook: versions ending in -bad fail /ready | Safe way to show a failed release and rollback | Test-only code path inside the app; documented and covered by a test |

## What I would do with more time
Fail builds on critical vulnerabilities, pin actions by SHA, add real metrics (/metrics with Prometheus), deploy to a small cloud VM, add authentication, automate database backups.

## What went wrong and what I learned
The first CI build failed because the Trivy action version I used had been removed after a supply-chain incident. I bumped to the safe version and noted pinning by commit SHA as a hardening step.
