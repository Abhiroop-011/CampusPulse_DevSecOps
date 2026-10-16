# CampusPulse Capstone Presentation & Video Walkthrough Script

> **Target Duration**: 7–10 Minutes  
> **Speaker Role**: Senior DevSecOps Engineer  
> **Project**: CampusPulse — Campus Events & Club Management Platform

---

## Part 1: Slide Deck Presentation (2 Minutes)

### Slide 1: Title & Introduction
- *"Hello everyone! My name is Abhiroop, and today I am excited to present **CampusPulse**, an enterprise-grade Campus Events & Club Management platform built and deployed with a complete, modern DevSecOps lifecycle."*
- *"CampusPulse solves the chaos of college event discovery and club registration, allowing students to browse clubs, view live event capacities, and register with real-time feedback."*

### Slide 2: Problem Statement & Architectural Vision
- *"Modern applications cannot just run on a developer's laptop—they must be secure, observable, cost-effective, and fully automated from Git commit to production."*
- *"Our architecture implements a 3-tier cloud-native stack: React 19 on the frontend, an asynchronous FastAPI REST API backend with SQLAlchemy and PostgreSQL, fully containerized and orchestrated in Kubernetes on AWS EKS."*

### Slide 3: DevSecOps Lifecycle & Automation
- *"Our DevSecOps backbone includes:"*
  1. **Automated Testing**: 30 Pytest unit and integration tests executing on SQLite transactional rollbacks in under 1 second.
  2. **Security Gates**: Aqua Trivy scans every Docker image in CI, preventing vulnerable packages from reaching production.
  3. **Container Registry**: SHA-tagged images published directly to GitHub Container Registry (GHCR).
  4. **GitOps CD**: Argo CD synchronizing declarative Helm charts directly from the Git repository.
  5. **Cloud Infrastructure**: Cost-conscious Terraform provisioning AWS VPC with single NAT gateway and managed EKS.
  6. **Observability**: Prometheus metrics scraping with custom Grafana dashboards tracking application telemetry.

---

## Part 2: Live Demonstration & Codebase Walkthrough (5–7 Minutes)

### Section 1: Codebase Tour (1 Minute)
- **Show Screen**: Open VS Code / IDE.
- **Talking Points**:
  - *"Here is the repository structure: `backend/` contains our FastAPI models, routers, Alembic migrations, and 30 Pytest suites."*
  - *"In `frontend/`, we have our React 19 dashboard styled with an elegant, warm espresso and brown palette."*
  - *"In `helm/campuspulse/`, we have our modular Helm chart with templates for deployments, services, secrets, and ingress."*
  - *"In `gitops/` and `monitoring/`, we have our Argo CD application manifests, Prometheus scrape configs, and Grafana dashboard JSON."*
  - *"And in `terraform/`, our modular Infrastructure as Code defining our VPC and EKS cluster."*

### Section 2: Automated CI/CD & Security Gating (1 Minute)
- **Show Screen**: Open GitHub Actions tab in browser.
- **Talking Points**:
  - *"Here is our GitHub Actions workflow: on every push to `main`, four automated jobs run in parallel:"*
    - *Pytest tests passing with 100% test coverage.*
    - *Frontend production Vite build.*
    - *Multi-stage non-root Docker builds.*
    - *Aqua Trivy container security scan gating the release.*
  - *"Once verified, SHA-tagged images are published to GitHub Packages (GHCR)."*

### Section 3: Live Application & User Experience (1 Minute)
- **Show Screen**: Browser at `http://localhost:3000` (or Ingress URL).
- **Talking Points**:
  - *"Let's explore the live user interface: students can see real-time KPIs, browse upcoming events, and view active clubs."*
  - *"Let's click 'Register' on the AI Hackathon event: enter student details and hit submit. The registration is instant, the capacity decreases dynamically, and Prometheus captures the HTTP request latency."*

### Section 4: Infrastructure as Code (Terraform & AWS) (1.5 Minutes)
- **Show Screen**: Terminal showing `terraform plan` output & AWS Console.
- **Talking Points**:
  - *"For infrastructure, we used Terraform. Our plan creates 54 AWS resources in `ap-southeast-2`: an isolated VPC with public and private subnets, a cost-saving single NAT Gateway, and a managed EKS cluster with KMS secret envelope encryption and IMDSv2 mandatory tokens."*
  - *"In the AWS Console, we can verify our active VPC, subnets, and the running EKS cluster."*

### Section 5: GitOps, Kubernetes & Observability (1.5 Minutes)
- **Show Screen**: Argo CD Web UI / `kubectl get pods -n campuspulse` / Prometheus & Grafana.
- **Talking Points**:
  - *"Using GitOps with Argo CD, our Helm chart release is synchronized declaratively without manual kubectl commands."*
  - *"`kubectl get pods -n campuspulse` shows our backend and frontend pods running healthy across multiple replicas."*
  - *"In Prometheus, our application endpoint `/metrics` reports `UP` with scrape latency under 5ms."*
  - *"And in Grafana, our custom CampusPulse dashboard displays live HTTP throughput, error rates, and database connection pool health in real time."*

### Section 6: Clean Teardown & Conclusion (30 Seconds)
- **Show Screen**: Terminal.
- **Talking Points**:
  - *"Finally, to prevent runaway cloud costs, our infrastructure is cleanly torn down using `terraform destroy -auto-approve`."*
  - *"CampusPulse demonstrates that security, scalability, and observability can be baked directly into the software delivery pipeline from day one. Thank you!"*
