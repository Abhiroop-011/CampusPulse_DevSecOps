# CampusPulse — DevSecOps Capstone Project

> **Name:** Abhiroop Sistu &nbsp;|&nbsp; **Roll No:** 10287 &nbsp;|&nbsp; **Batch:** A  
> 🎥 **Presentation Video:** [CampusPulse Walkthrough (MP4 Download)](https://github.com/Abhiroop-011/CampusPulse_DevSecOps/releases/download/v1.0.0/Screen.Recording.2026-10-27.182346.mp4) &nbsp;|&nbsp; [GitHub Release v1.0.0](https://github.com/Abhiroop-011/CampusPulse_DevSecOps/releases/tag/v1.0.0)  
> 📊 **Presentation Slides:** [demo/campuspulse-presentation.html](demo/campuspulse-presentation.html)

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

<p align="center">
  <img src="screenshots/01_app_browser_dashboard.png" alt="CampusPulse Application Web Dashboard" width="900" />
</p>

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

<p align="center">
  <img src="screenshots/04_docker_compose_up.png" alt="Docker Compose Running Healthy" width="850" />
</p>

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
   <p align="center">
     <img src="screenshots/02_pytest_30_passing.png" alt="30/30 Pytest Passing" width="850" />
   </p>

2. **Frontend**:
   ```bash
   cd frontend
   npm install
   npm run dev
   ```

---

## 5. Security & DevSecOps Implementation

CampusPulse enforces automated security gates at every layer:
1. **Zero Secret Leakage**: Git history is scanned and protected. Sensitive `.env`, `.tfstate`, and credentials are fully excluded via `.gitignore`.
2. **Container Hardening**: Multi-stage Docker builds run as unprivileged user (`UID 10001` backend, `nginx` frontend) with read-only capabilities where possible.
3. **Automated Vulnerability Scanning**: Aqua Trivy scans all container images inside the CI pipeline before publishing to GHCR.
4. **Cloud Security**: AWS EKS cluster features KMS secret envelope encryption and IMDSv2 mandatory tokens to prevent metadata credential exfiltration.

<p align="center">
  <img src="screenshots/07_trivy_security_scan.png" alt="Aqua Trivy Security Scan Gate" width="850" />
</p>

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

<p align="center">
  <img src="screenshots/09_aws_console_vpc_and_eks.png" alt="AWS Console VPC and EKS Active" width="850" />
</p>

To destroy all cloud resources and prevent runaway costs:
```bash
terraform destroy -auto-approve
```

<p align="center">
  <img src="screenshots/17_terraform_destroy_complete.png" alt="Terraform Destroy Complete" width="850" />
</p>

---

## 7. Capstone Verification Evidence Gallery (All 17 Milestones)

All 17 required grading milestones have been executed, validated, and archived in the [screenshots/](screenshots/) directory:

### Phase A: Application & Automated Testing
| # | Evidence Milestone | Description |
|---|---|---|
| **01** | **[Live Web Application Dashboard](screenshots/01_app_browser_dashboard.png)** | Interactive React 19 UI with event registration modal, club directory, and real-time KPI stats. |
| **02** | **[30/30 Pytest Test Suite Passing](screenshots/02_pytest_30_passing.png)** | Full unit and integration coverage for models, schemas, and API routers executing in < 1 second. |
| **03** | **[Git Commit History](screenshots/03_git_commit_history.png)** | Clean semantic conventional commit log documenting all development phases and security hardening. |
| **04** | **[Docker Compose 3-Tier Stack](screenshots/04_docker_compose_up.png)** | Multi-container stack (React + FastAPI + PostgreSQL) running healthy with non-root privileges. |

<details open>
<summary><b>Click to expand Phase A Screenshots</b></summary>

#### 01. Live Web Application Dashboard
![01 App Browser Dashboard](screenshots/01_app_browser_dashboard.png)

#### 02. 30/30 Automated Pytest Tests Passing
![02 Pytest 30 Passing](screenshots/02_pytest_30_passing.png)

#### 03. Git Commit History
![03 Git Commit History](screenshots/03_git_commit_history.png)

#### 04. Local Multi-Container Docker Compose Stack
![04 Docker Compose Stack](screenshots/04_docker_compose_up.png)
</details>

---

### Phase B: CI/CD Automation & Container Security
| # | Evidence Milestone | Description |
|---|---|---|
| **05** | **[GitHub Actions 100% Green Run](screenshots/05_github_actions_green_run.png)** | End-to-end CI pipeline executing tests, frontend builds, Trivy security gates, and GHCR publishing. |
| **06** | **[GHCR Packages with SHA Tags](screenshots/06_ghcr_packages_sha_tags.png)** | Immutable container artifacts published to GitHub Container Registry tagged with Git commit SHAs. |
| **07** | **[Aqua Trivy Vulnerability Scan](screenshots/07_trivy_security_scan.png)** | Automated vulnerability scanning verifying zero unmitigated HIGH or CRITICAL CVEs. |

<details open>
<summary><b>Click to expand Phase B Screenshots</b></summary>

#### 05. GitHub Actions 100% Green Pipeline Run
![05 GitHub Actions Green Run](screenshots/05_github_actions_green_run.png)

#### 06. GHCR Packages with Commit SHA Tags
![06 GHCR Packages](screenshots/06_ghcr_packages_sha_tags.png)

#### 07. Aqua Trivy Vulnerability Security Scan
![07 Trivy Security Scan](screenshots/07_trivy_security_scan.png)
</details>

---

### Phase C: Infrastructure as Code & AWS EKS Orchestration
| # | Evidence Milestone | Description |
|---|---|---|
| **08** | **[Terraform Plan Output](screenshots/08_terraform_plan_output.png)** | Declarative IaC plan validating 53 AWS resources to add with 0 to change or destroy. |
| **09** | **[AWS Console VPC & Active EKS](screenshots/09_aws_console_vpc_and_eks.png)** | AWS Management Console verifying VPC `10.30.0.0/16` and EKS Cluster `campuspulse-eks` active. |
| **10** | **[EKS Nodes Ready (`kubectl get nodes`)](screenshots/10_kubectl_get_nodes.png)** | Managed Node Group worker EC2 instances joined and in `Ready` status on Kubernetes v1.31. |
| **11** | **[Application Pods Running (`kubectl get pods`)](screenshots/11_kubectl_get_pods_running.png)** | All backend, frontend, and database pods `1/1 Running` with 0 restarts in `campuspulse` namespace. |
| **12** | **[Kubernetes Services (`kubectl get svc`)](screenshots/12_kubectl_get_svc.png)** | Internal ClusterIP networking and Ingress routing for frontend and backend microservices. |
| **13** | **[Helm Release Status (`helm list`)](screenshots/13_helm_list.png)** | Production Helm chart release `campuspulse` successfully deployed in target namespace. |

<details open>
<summary><b>Click to expand Phase C Screenshots</b></summary>

#### 08. Terraform Plan Infrastructure as Code Execution
![08 Terraform Plan Output](screenshots/08_terraform_plan_output.png)

#### 09. AWS Web Console — VPC and Active EKS Cluster
![09 AWS Console VPC and EKS](screenshots/09_aws_console_vpc_and_eks.png)

#### 10. EKS Nodes in Ready State (`kubectl get nodes`)
![10 Kubectl Get Nodes](screenshots/10_kubectl_get_nodes.png)

#### 11. Application Pods Running Healthy (`kubectl get pods -n campuspulse`)
![11 Kubectl Get Pods](screenshots/11_kubectl_get_pods_running.png)

#### 12. Kubernetes Services (`kubectl get svc -n campuspulse`)
![12 Kubectl Get Svc](screenshots/12_kubectl_get_svc.png)

#### 13. Production Helm Release Deployed (`helm list -n campuspulse`)
![13 Helm List](screenshots/13_helm_list.png)
</details>

---

### Phase D: Cloud-Native Observability & Clean Teardown
| # | Evidence Milestone | Description |
|---|---|---|
| **14** | **[Prometheus `/metrics` Endpoint](screenshots/14_curl_metrics_endpoint.png)** | FastAPI exporter serving live Prometheus metrics (HTTP request counts, latencies, process stats). |
| **15** | **[Prometheus Targets Dashboard](screenshots/15_prometheus_targets_up.png)** | Prometheus server target discovery showing scraping endpoint in healthy `UP (1/1)` state. |
| **16** | **[Custom Grafana Visual Dashboard](screenshots/16_grafana_dashboard.png)** | Real-time observability dashboard displaying request throughput, error rates, and p95 latency. |
| **17** | **[Terraform Cloud Teardown Verification](screenshots/17_terraform_destroy_complete.png)** | Clean destruction of all 53 AWS resources confirming zero runaway costs and complete lifecycle closure. |

<details open>
<summary><b>Click to expand Phase D Screenshots</b></summary>

#### 14. Live Prometheus `/metrics` Endpoint Output
![14 Curl Metrics Endpoint](screenshots/14_curl_metrics_endpoint.png)

#### 15. Prometheus Target Discovery Healthy (`UP 1/1`)
![15 Prometheus Targets UP](screenshots/15_prometheus_targets_up.png)

#### 16. Custom Grafana Visual Monitoring Dashboard
![16 Grafana Dashboard](screenshots/16_grafana_dashboard.png)

#### 17. Complete AWS Cloud Teardown (`terraform destroy`)
![17 Terraform Destroy Complete](screenshots/17_terraform_destroy_complete.png)
</details>

---

## 8. Submission Checklist

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
- [x] All 17 verification evidence screenshots captured, verified, and linked in `README.md`
- [x] Mandatory presentation video recorded and published: [Release v1.0.0 Asset](https://github.com/Abhiroop-011/CampusPulse_DevSecOps/releases/tag/v1.0.0)
- [x] Mandatory presentation slide deck committed: [demo/campuspulse-presentation.html](demo/campuspulse-presentation.html)

