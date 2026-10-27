# CampusPulse — Presentation & Video Artifacts

> **Presenter:** Abhiroop Sistu  
> **Roll No:** 10287  
> **Batch:** A  
> **Project:** CampusPulse (DevSecOps Final Capstone)  

---

## 🎥 Presentation Video

As per **GRADING.md (Module M10)**, the full walkthrough presentation video is hosted directly on this repository as an official release asset:

- 📥 **Direct MP4 Download:** [Screen.Recording.2026-10-27.182346.mp4 (764 MB)](https://github.com/Abhiroop-011/CampusPulse_DevSecOps/releases/download/v1.0.0/Screen.Recording.2026-10-27.182346.mp4)
- 🏷️ **GitHub Release:** [v1.0.0 — CampusPulse Capstone Presentation & Video](https://github.com/Abhiroop-011/CampusPulse_DevSecOps/releases/tag/v1.0.0)

---

## 📊 Presentation Slide Deck

The 16-slide presentation deck is committed in this folder:
- **Interactive Slides:** [`campuspulse-presentation.html`](./campuspulse-presentation.html)
- Open in any modern web browser and press `F11` for full screen. Navigate using arrow keys (`→` and `←`).

---

## Video Walkthrough Topics Covered

1. **Slide Presentation:** Project overview, architecture, tech stack, security gates, Terraform infrastructure, Kubernetes Helm packaging, and GitOps lifecycle.
2. **Codebase Overview:** Folder structure, FastAPI routes, SQLAlchemy models, Alembic migrations, Helm templates, and GitHub Actions workflow.
3. **Automated Testing:** 30/30 Pytest suite running in-memory with transactional rollback.
4. **Container Stack:** Local three-tier Docker Compose stack (frontend, backend, PostgreSQL).
5. **Terraform:** 53-resource execution plan (`terraform plan`) targeting AWS VPC and EKS cluster.
6. **Live AWS Management Console:** Dedicated `terraform-admin` IAM user and active VPC environment.
7. **Live Application:** CampusPulse React 19 UI with real-time seat reservation.
8. **Observability:** Prometheus targets discovery (`UP 1/1`) and real-time telemetry.
9. **CI/CD & Security:** GitHub Actions 100% green pipeline and Aqua Trivy container scan gating.
10. **FinOps Teardown:** Verified `terraform destroy` output ensuring zero residual cloud costs.
