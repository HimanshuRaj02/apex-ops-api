# AI assistance disclosure

The assessment instructions asked me to document AI assistance. I used one AI tool for this work.

## Tool used
- Claude (Anthropic), through the Claude chat interface. I did not use any other AI tool.

## What Claude did
- Read the assessment and helped me turn it into a checklist and plan.
- Drafted the first versions of the Flask app, Dockerfile, Docker Compose file, tests, GitHub Actions workflow, deploy and rollback scripts, and the documents in this repo (README, runbook, observability plan, failure investigation, security and cost notes, decision memo).
- Explained what each part does and why, so I could discuss it in the review.
- Helped diagnose errors I pasted from my terminal and from GitHub (missing Docker Compose plugin, files created in the wrong folder, git push to a repository that did not exist yet, and the failed Trivy action version in CI).

## What I did myself
- Set up Docker Engine on WSL and ran every command on my own machine.
- Created the GitHub repository, pushed the code, opened the pull request, and produced the failing and passing CI runs.
- Ran the deployment, failed-release rollback and database-down demonstrations and saved the screenshots and outputs as evidence.
- Reviewed the generated code and documents, and I can explain each part: health vs readiness, non-root container, volumes, the CI needs chain, versioned images and rollback.

## Things worth knowing
- The "-bad" version hook in the app is a deliberate demo mechanism to show a failed release and automatic rollback; it is covered by a test.
- Where an AI suggestion did not work (the removed Trivy action tag), CI exposed it and we fixed it by moving to a safe version.
