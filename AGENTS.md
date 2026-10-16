# CampusPulse DevSecOps Capstone — Project Memory (AGENTS.md)

## 1. Project Overview & Context
- **Project Name:** CampusPulse (Campus Events & Club Management Platform)
- **Role:** Senior DevSecOps Engineer & Implementation Agent
- **Workspace:** `c:\Users\Abhiroop\Desktop\CampusPulse-DevSecOps`
- **GitHub Repository:** `https://github.com/Abhiroop-011/CampusPulse_DevSecOps.git`
- **Reference Repository:** `c:\Users\Abhiroop\Downloads\devsecops-python-main\devsecops-python-main` (Read-only reference)
- **Submission Deadline:** Sunday, 19 October 2026, 11:59 PM IST (Late penalty: -5 pts / 24h)
- **Current Status:** Phase 9 COMPLETE (Prometheus scraping & Grafana dashboard configured) — ready to start Phase 10 (Terraform: AWS VPC & EKS Infrastructure)

## 2. Critical Constraints & Operating Rules
1. **Git commits and pushes:** Agent CAN run `git commit` and `git push` directly. Agent MUST announce the commit message and what is being staged BEFORE executing. Never stage secrets, `.env`, credentials, `__pycache__`, `.venv`, or `*.tfstate`.
2. **Never provision AWS or run `terraform apply`/`destroy` without explicit prior approval.**
3. **No secrets in Git:** Never commit `.env`, AWS credentials, tokens, or kubeconfig.
4. **100% Original Domain & Code:** Zero cloning from TaskBoard. Campus events, clubs, registrations domain.
5. **Honest reporting:** No fabricated scan outputs or test results. Report real outputs only.
6. **Local-first validation:** Test backend, frontend, Docker Compose, Kind/K8s, and Helm locally before cloud deployment.
7. **UI Aesthetic:** Rich warm brown, cream, ivory, espresso, caramel accents; clean typography; no heavy animations.
8. **GitOps with Argo CD:** Synchronize Helm release declaratively; Git tag update flow.

## 3. Progress Log
- **2026-10-16 (Session 1):**
  - Read GRADING.md, SUBMISSION.md, README.md from reference project.
  - Formulated 12-section master plan — approved by user.
  - Initialized Git repo in CampusPulse-DevSecOps. Remote: https://github.com/Abhiroop-011/CampusPulse_DevSecOps.git
  - Created `.gitignore`, `.env.example`.
  - **Phase 1 (DB Core):** SQLAlchemy models (Club, Event, Registration), Alembic migration `001_initial_schema` with 6 clubs + 6 events seed data. Verified on postgres:16-alpine container.
  - **Phase 2 (API):** FastAPI entrypoint with CORS + Prometheus instrumentation, health/ready, events/clubs CRUD, registration/cancellation with capacity enforcement, stats endpoint.
  - **Phase 3 (Tests):** 30 tests across test_health.py, test_clubs.py, test_events.py — SQLite in-memory with transactional rollback. **30/30 PASSED in 0.84s.**
  - Live API verified: /health → healthy, /ready → ready+connected, /api/clubs → 6 clubs, /api/stats → correct aggregates.
  - **Phase 4 (Frontend):** React 19 + Vite dashboard styled with custom warm brown/espresso/cream design system, full API proxying, event registration, attendees modal, club explorer, real-time KPI metrics, oxlint clean (0 warnings), verified in browser subagent with real student registration.
  - **Phase 5 (Docker Stack):** Production multi-stage Dockerfiles for backend (Python 3.12 slim, non-root UID 10001, Alembic migration, healthchecks) and frontend (Node 22 build → Nginx 1.27 Alpine, reverse-proxy for API/metrics/health, IPv4/IPv6 dual stack). Coordinated via `docker-compose.yml` with PostgreSQL 16 Alpine. All 3 containers healthy, tested end-to-end registration.

## 4. Environment Details
- **Python:** 3.13.5 (Anaconda base)
- **Virtualenv:** `backend/.venv` (excluded from Git)
- **Postgres (Dev):** Docker container `campuspulse-pg-dev` on port 5432
  - Start: `docker run --name campuspulse-pg-dev -e POSTGRES_USER=campuspulse -e POSTGRES_PASSWORD=campuspulse_dev_pass -e POSTGRES_DB=campuspulse_db -p 5432:5432 -d postgres:16-alpine`
  - Resume: `docker start campuspulse-pg-dev`
- **Docker Desktop:** v29.7.2 (WSL2 backend — must be running before starting Postgres container)
- **Node.js:** Available at C:\Program Files\nodejs\
- **Kubernetes (Local):** Docker Desktop K8s — NOT yet enabled. Enable in Docker Desktop > Settings > Kubernetes before Phase 7.
- **Terraform:** NOT installed. Install via `choco install terraform` or winget before Phase 10.
- **Helm:** NOT installed. Install via `choco install kubernetes-helm` or winget before Phase 7.

## 5. Commit Plan Status

| # | Commit Message | Status |
|---|---|---|
| 1 | `chore(repo): initialize project structure and git hygiene` | ✅ Done |
| 2 | `feat(backend): configure database models and initial alembic migration` | ✅ Done |
| 3 | `feat(api): implement campuspulse rest endpoints, health checks, and metrics` | ✅ Done |
| 4 | `test(api): add comprehensive test suite for events and registration logic` | ✅ Done |
| 5 | `feat(frontend): build responsive brown-themed campuspulse dashboard` | ✅ Done |
| 6 | `build(docker): containerize stack with non-root images and docker compose` | ✅ Done |
| 7 | `ci(pipeline): add test, trivy security scan, and ghcr publishing workflow` | ✅ Done |
| 8 | `docs(security): document trivy vulnerability scan findings and triage` | ✅ Done |
| 9 | `feat(k8s): implement modular helm chart with ingress and replica scaling` | ✅ Done |
| 10 | `feat(gitops): configure declarative argo cd application and sync policy` | ✅ Done |
| 11 | `feat(monitoring): configure prometheus scraping and grafana dashboard` | ✅ Done |
| 12 | `feat(terraform): define cost-conscious aws vpc and eks cluster infrastructure` | ⬜ Phase 10 |
| 13 | `docs(evidence): record aws cluster deployment, ingress verification, and teardown` | ⬜ Phase 11 |
| 14 | `docs(capstone): complete technical documentation and video presentation script` | ⬜ Phase 12 |

## 6. Evidence Checklist
- [x] Browser screenshot: CampusPulse at localhost:3000 (Phase 4)
- [x] pytest -v 30/30 passing (capture terminal screenshot after commit)
- [x] docker compose up --build success (Phase 5)
- [ ] GitHub Actions green run + GHCR packages (Phase 6)
- [x] Trivy scan output (Phase 6)
- [ ] terraform plan output (Phase 10)
- [ ] AWS Console: VPC + EKS (Phase 11)
- [ ] kubectl get pods -n campuspulse (Phase 7/11)
- [x] Prometheus Targets UP (Phase 9)
- [ ] Grafana dashboard screenshot (Phase 9)
