# Security notes and cost-aware cloud path

## Security measures in this project
- No hard-coded secrets: configuration comes from environment variables; .env is git-ignored; .env.example has dummy values only.
- Non-root container: the app runs as appuser (uid 10001), not root.
- Least privilege: the Postgres port is not published to the host; only the app port 8000 is exposed.
- Small base image (python slim, postgres alpine) to reduce attack surface.
- Parameterised SQL queries and input validation (400 on bad input) against injection and bad data.
- Image scanning with Trivy in CI. It reports HIGH and CRITICAL findings but does not yet fail the build (exit-code 0).
- Third-party actions pinned to version tags. In March 2026 the Trivy action tags were hijacked and removed, which broke our first build; we moved to the safe 0.35.0. Next step: pin to full commit SHAs.
- CI uses throwaway test credentials only.

## Known gaps and next steps
- Make Trivy fail the build on CRITICAL findings.
- Pin all actions by commit SHA and enable Dependabot.
- Use a real secret store (cloud secrets manager) instead of a .env file.
- Add TLS and authentication in front of the API.
- Add rate limiting and a read-only database role for read endpoints.

## Cost-aware cloud path
1. Start: one small VM (for example a t3.micro or t4g.small class instance) running Docker Compose. Cheapest and closest to what is already tested. Use the free tier where available.
2. Use a cloud Postgres only when data matters: managed database with automated backups, smallest instance size, pause or stop it outside working hours for non-production.
3. Registry: push versioned images to a container registry (a private registry has a small storage cost); keep only the last few versions.
4. Later, if traffic grows: move to a managed container service and add autoscaling with a minimum of one task.
5. Cost controls: billing alarm and budget alert from day one, tag resources by project, delete unused images, volumes and snapshots.
6. Monitoring on a budget: start with container logs and the free Prometheus plus Grafana setup (see observability.md) before paying for a hosted platform.
