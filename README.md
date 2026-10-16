# CampusPulse — DevSecOps Capstone Project

[![CI/CD Pipeline](https://github.com/Abhiroop-011/CampusPulse_DevSecOps/actions/workflows/ci.yml/badge.svg)](https://github.com/Abhiroop-011/CampusPulse_DevSecOps/actions/workflows/ci.yml)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=black)](https://react.dev)
[![Docker](https://img.shields.io/badge/Docker-Multi--stage-2496ED?logo=docker&logoColor=white)](https://www.docker.com)
[![Kubernetes](https://img.shields.io/badge/Kubernetes-1.31-326CE5?logo=kubernetes&logoColor=white)](https://kubernetes.io)
[![Helm](https://img.shields.io/badge/Helm-3+-0F1689?logo=helm&logoColor=white)](https://helm.sh)
[![ArgoCD](https://img.shields.io/badge/GitOps-ArgoCD-EF7B4D?logo=argo&logoColor=white)](https://argoproj.github.io/cd/)
[![Terraform](https://img.shields.io/badge/Terraform-1.16+-844FBA?logo=terraform&logoColor=white)](https://www.terraform.io)
[![AWS EKS](https://img.shields.io/badge/AWS-EKS%20%7C%20VPC-FF9900?logo=amazon-aws&logoColor=white)](https://aws.amazon.com/eks/)
[![Trivy](https://img.shields.io/badge/Security-Trivy%20Scanned-1E88E5?logo=aqua&logoColor=white)](https://trivy.dev)

> **CampusPulse** is an enterprise-grade Campus Events & Student Club Management platform built with modern full-stack technologies and engineered through a rigorous 12-phase DevSecOps lifecycle: automated testing, container security gating, declarative Helm packaging, GitOps CD via Argo CD, cloud-native observability, and Infrastructure as Code on AWS.

---

## 1. System Architecture

```text
                                  DEVELOPER / USER
                                         │
                                         ▼
                               GITHUB REPOSITORY
                      (Triggers GitHub Actions on main push)
                                         │
                  ┌──────────────────────┴──────────────────────┐
                  ▼                                             ▼
           CI / SECURITY GATES                           GITOPS CD (ARGO CD)
   ├── 1. Pytest Unit Tests (30/30)              ├── Detects Git commits/tags
   ├── 2. Frontend Production Build (Vite)       ├── Syncs declarative manifests
   ├── 3. Trivy Container Vulnerability Scan     └── Enforces cluster state
   └── 4. GHCR Docker Publish (SHA-tagged)
                  │
                  ▼
          INFRASTRUCTURE AS CODE (TERRAFORM)
   ├── AWS VPC (CIDR 10.30.0.0/16, Dual AZ)
   ├── Single Cost-Optimized NAT Gateway
   ├── AWS Managed EKS Cluster (v1.31)
   └── Managed Node Group (2x t3.medium, IMDSv2)
                  │
                  ▼
       KUBERNETES DEPLOYMENT (HELM)
 ┌─────────────────────────────────────────────────────────────┐
 │ Namespace: campuspulse                                      │
 │                                                             │
 │   Ingress (Nginx / ALB)                                     │
 │    ├── /api  ──────────► Backend Service (FastAPI)         │
 │    │                      ├── 2 Replicas                    │
 │    │                      ├── SQLAlchemy ORM + Alembic      │
 │    │                      └── /metrics (Prometheus Exporter)│
 │    │                             │                          │
 │    │                             ▼                          │
 │    │                      PostgreSQL 16 DB (Stateful)       │
 │    │                                                        │
 │    └── /     ──────────► Frontend Service (React 19)        │
 │                           ├── 2 Replicas                    │
 │                           └── Nginx Reverse Proxy           │
 └─────────────────────────────────────────────────────────────┘
                  │
                  ▼
        OBSERVABILITY & MONITORING
   ├── Prometheus Server: Scrapes /metrics every 15s
   └── Grafana: Real-time Dashboards (Latency, Requests, DB Pool)
```

---

## 2. Technology Stack

| Layer | Technology | Key Capabilities & Choices |
|---|---|---|
| **Frontend** | React 19, Vite, Vanilla CSS | Warm brown/espresso aesthetic, responsive club cards, instant event registration modal, KPI stats counter |
| **Backend** | Python 3.12/3.13, FastAPI, Pydantic v2 | Async REST API, CORS middleware, `/health` & `/ready` probes, Prometheus metrics exporter |
| **Database** | PostgreSQL 16 Alpine, SQLAlchemy 2.0 | Transactional schema with Alembic versioning, relational integrity, connection pooling |
| **Testing** | Pytest, HTTPX AsyncClient, SQLite in-memory | 30 comprehensive unit & integration tests running in < 1 second |
| **Containers** | Docker (Multi-stage), Non-root (UID 10001) | Distroless/alpine runtimes, minimal attack surface, health checks |
| **CI/CD** | GitHub Actions | Parallel jobs: tests, frontend bundle, Docker builds, GHCR publishing |
| **Security** | Aqua Trivy, `.trivyignore` | Automated CVE vulnerability scanning blocking CRITICAL/HIGH findings |
| **Orchestration**| Kubernetes 1.31, Helm 3+ | Modular Helm chart with configurable values, replica scaling, Ingress |
| **GitOps** | Argo CD | Declarative application manifest, automated drift detection and self-healing |
| **Observability**| Prometheus, Grafana | Custom dashboard tracking HTTP traffic, error rates, response latencies |
| **Cloud IaC** | Terraform `>= 1.7`, AWS Provider `~> 5.50` | VPC with single NAT gateway, Managed EKS, KMS encryption, IMDSv2 |

---

## 3. Directory Structure

```text
CampusPulse-DevSecOps/
├── .github/
│   └── workflows/
│       └── ci.yml                 # Automated GitHub Actions CI/CD Pipeline
├── backend/
│   ├── alembic/                   # Database migration scripts & initial seed data
│   │   └── versions/
│   │       └── 001_initial_schema.py
│   ├── app/
│   │   ├── core/                  # Database session & config
│   │   ├── models/                # SQLAlchemy Club, Event, Registration models
│   │   ├── routers/               # REST API endpoints (health, clubs, events, stats)
│   │   ├── schemas/               # Pydantic validation schemas
│   │   └── main.py                # FastAPI application entrypoint & Prometheus instrumentator
│   ├── tests/                     # 30 Pytest test suites
│   ├── Dockerfile                 # Multi-stage non-root container definition
│   └── requirements.txt
├── frontend/
│   ├── src/                       # React 19 UI components & dashboard
│   ├── nginx.conf                 # Production reverse proxy configuration
│   ├── Dockerfile                 # Multi-stage Node 22 build -> Nginx Alpine
│   └── package.json
├── helm/
│   └── campuspulse/               # Production Helm chart
│       ├── Chart.yaml
│       ├── values.yaml
│       └── templates/             # Deployments, Services, Ingress, Secrets, ConfigMap
├── k8s/                           # Raw Kubernetes manifests (namespace, backend, frontend, ingress)
├── gitops/                        # Argo CD declarative application and project manifests
├── monitoring/                    # Prometheus scrape configurations and Grafana dashboard JSON
├── terraform/                     # AWS VPC and EKS Infrastructure as Code
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   ├── versions.tf
│   └── terraform.tfvars.example
├── docs/                          # Security reports, vulnerability triage, and cloud evidence
├── docker-compose.yml             # Local 3-tier production container stack
├── .trivyignore                   # Documented CVE triage suppressions
└── AGENTS.md                      # Operational project memory & execution log
```

---

## 4. Local Development & Quickstart

### Option A: Complete Docker Compose Stack (Recommended)
Spin up the entire application (PostgreSQL + FastAPI + React):
```bash
docker compose up --build -d
```
- **Web Dashboard**: http://localhost:3000
- **REST API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **Readiness Probe**: http://localhost:8000/ready
- **Prometheus Metrics**: http://localhost:8000/metrics

### Option B: Local Native Setup
1. **Backend**:
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate  # or .venv\Scripts\activate on Windows
   pip install -r requirements.txt
   pytest -v
   uvicorn app.main:app --reload --port 8000
   ```
2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 5. Security & DevSecOps Implementation

CampusPulse enforces security gates at every layer:
1. **Zero Secret Leakage**: Git history is scanned and protected. Sensitive `.env`, `.tfstate`, and credentials are fully excluded via `.gitignore`.
2. **Container Hardening**: Multi-stage Docker builds run as unprivileged user (`UID 10001` backend, `nginx` frontend) with read-only capabilities where possible.
3. **Automated Vulnerability Scanning**: Aqua Trivy scans all container images inside the CI pipeline before publishing to GHCR.
4. **Cloud Security**: AWS EKS cluster features KMS secret envelope encryption and IMDSv2 mandatory tokens to prevent metadata credential exfiltration.

Detailed triage notes are documented in [docs/security/trivy-scan-report.md](docs/security/trivy-scan-report.md).

---

## 6. Cloud Deployment & Teardown (Terraform)

See [terraform/README.md](terraform/README.md) and [docs/aws-deployment-evidence.md](docs/aws-deployment-evidence.md) for full cloud runbooks.

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

To destroy all cloud resources and prevent runaway costs:
```bash
terraform destroy -auto-approve
```

---

## 7. Submission Checklist

- [x] Working full-stack application (React 19 + FastAPI + PostgreSQL 16)
- [x] 30/30 automated unit tests passing (`pytest -v`)
- [x] Multi-stage non-root Dockerfiles & Docker Compose stack verified healthy
- [x] GitHub Actions CI/CD pipeline passing with GHCR container publishing
- [x] Trivy vulnerability scan integrated and documented
- [x] Modular Kubernetes manifests and production Helm chart (`helm lint` & `template` clean)
- [x] Declarative GitOps deployment configured for Argo CD
- [x] Prometheus metric instrumentation & custom Grafana dashboard
- [x] Production AWS VPC & EKS Terraform infrastructure validated
- [x] Complete technical documentation and evidence guides
