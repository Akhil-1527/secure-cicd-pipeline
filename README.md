# secure-cicd-pipeline

A reference "shift-left" CI/CD security pipeline for GitHub Actions. It wires
the gates I run on every change so known-bad code never reaches a deployable
state. Each job fails the build on its own severity threshold.

The repo ships a tiny Flask app purely as a target; the point is
[`.github/workflows/security.yml`](.github/workflows/security.yml).

## The gates

| Stage | Tool | Fails on |
|-------|------|----------|
| **Secret scanning** | [secretscan](https://github.com/Akhil-1527/secretscan) | any hardcoded credential |
| **SAST** | Bandit + Semgrep (`p/security-audit`, `p/owasp-top-ten`) | MEDIUM+ findings |
| **Dependency audit** | pip-audit | known-vulnerable dependency |
| **IaC scan** | Checkov | misconfigured Terraform/Dockerfile |
| **Container scan** | Trivy | HIGH/CRITICAL image CVEs (fixed) |
| **DAST** | OWASP ZAP baseline | active-scan alerts on the running app |

The secret-scanning stage runs my own
[secretscan](https://github.com/Akhil-1527/secretscan), so the toolchain is
self-hosted rather than dependent on a SaaS.

## Run it locally

```bash
./scripts/security-scan.sh
```

Installs the scanners on demand and runs the same gates the pipeline does.

## The app

A minimal Flask notes API (`/health`, `GET /notes`, `POST /notes`) with tests,
packaged in a hardened Dockerfile (pinned slim base, non-root user, gunicorn).
Kept clean so the pipeline stays green. Swap in your own service and the gates
carry over unchanged.

```bash
pip install -r app/requirements.txt
pytest -q
```

## Design notes

- **Severity gates, not reports.** Each job exits non-zero on its threshold;
  a green pipeline means the bar was actually met, not just that scans ran.
- **Least privilege.** Workflows request `contents: read` only.
- **Defense in depth.** SAST + DAST + deps + secrets + IaC + image scanning
  cover code, runtime, supply chain, and infrastructure.
