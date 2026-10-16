# CampusPulse DevSecOps — Trivy Security Audit & Vulnerability Triage Report

## 1. Executive Summary

As part of the **DevSecOps Pipeline (Module 6)**, automated static vulnerability scanning was executed using **Aqua Security Trivy** against the production container images built for CampusPulse:
- **Backend Image:** `campuspulse-backend:latest` (`python:3.12-slim`, non-root user `UID 10001`)
- **Frontend Image:** `campuspulse-frontend:latest` (`nginx:1.27-alpine`, multi-stage build from `node:22-alpine`)

Scanning parameters were strictly configured to evaluate **CRITICAL** and **HIGH** severity vulnerabilities across both OS packages and application dependencies, with unfixed CVEs filtered out and triage managed via `.trivyignore`.

---

## 2. Scan Summary Matrix

| Image | Base Image | Total HIGH | Total CRITICAL | Status / Gate Result |
|---|---|---|---|---|
| `campuspulse-backend:latest` | `python:3.12-slim` | 3 (application) | 0 | **PASS (Triaged)** |
| `campuspulse-frontend:latest` | `nginx:1.27-alpine` | 8 (base OS) | 0 | **PASS (Triaged)** |

---

## 3. Backend Image Vulnerability Breakdown (`campuspulse-backend`)

The Python 3.12-slim operating system layer contained **0 HIGH and 0 CRITICAL vulnerabilities**. All 3 findings originated from the transitive dependency `starlette==0.41.3`, introduced by `fastapi==0.115.6`.

### Findings Details & Risk Assessment

#### 1. CVE-2025-62727 — Starlette DoS via Range Header Merging
- **Severity:** HIGH
- **Component:** `starlette` (version: `0.41.3`, fixed in: `0.49.1`)
- **Vulnerability Description:** Improper handling of multiple or overlapping `Range` request headers can cause excessive memory consumption and Denial of Service.
- **CampusPulse Risk Evaluation:** **NO IMPACT / INAPPLICABLE**. CampusPulse is an asynchronous REST API serving lightweight JSON payloads (`/api/events`, `/api/clubs`, `/api/stats`). The backend does not stream media files or honor HTTP Range requests.
- **Triage Decision:** Documented and ignored via `.trivyignore`.

#### 2. CVE-2026-48818 — Starlette SSRF and NTLM Credential Theft via UNC Paths
- **Severity:** HIGH
- **Component:** `starlette` (version: `0.41.3`, fixed in: `1.1.0`)
- **Vulnerability Description:** If `StaticFiles` is exposed on Windows or environments accepting UNC paths, path traversal or SSRF can leak NTLM hashes.
- **CampusPulse Risk Evaluation:** **NO IMPACT / INAPPLICABLE**. CampusPulse runs in Linux container environments and never mounts `StaticFiles` on the FastAPI backend. All static assets are served exclusively by the Nginx reverse-proxy frontend.
- **Triage Decision:** Documented and ignored via `.trivyignore`.

#### 3. CVE-2026-54283 — Starlette `request.form()` Limit Bypass
- **Severity:** HIGH
- **Component:** `starlette` (version: `0.41.3`, fixed in: `1.3.1`)
- **Vulnerability Description:** Form field and part limits are silently ignored when processing `application/x-www-form-urlencoded` request bodies.
- **CampusPulse Risk Evaluation:** **NO IMPACT / INAPPLICABLE**. All CampusPulse endpoints strictly accept `application/json` payloads validated against strict Pydantic schemas. Form-data is not accepted on any API route.
- **Triage Decision:** Documented and ignored via `.trivyignore`.

---

## 4. Frontend Image Vulnerability Breakdown (`campuspulse-frontend`)

The frontend application uses a multi-stage Docker build where Node.js build dependencies are discarded, and only static assets are copied to `nginx:1.27-alpine`. The detected findings are upstream vulnerabilities in Alpine shared C libraries:

| Library | CVE | Severity | Component Purpose in Image | Exploitability & Rationale |
|---|---|---|---|---|
| `musl` / `musl-utils` | CVE-2026-40200 | HIGH | Alpine C standard library | Internal memory safety flaw. Container is non-privileged and has no interactive shells exposed. |
| `nghttp2-libs` | CVE-2026-27135 | HIGH | HTTP/2 parser | CampusPulse operates behind Kubernetes Ingress / Docker Compose bridge; HTTP/2 multiplexing edge is handled by Ingress controller. |
| `zlib` | CVE-2026-22184 | HIGH | Compression library | Flaw exists in `untgz` utility, not invoked by the Nginx runtime process. |
| `libxml2` | CVE-2025-49794, CVE-2025-49795, CVE-2025-49796, CVE-2026-6732 | HIGH | XML parsing library | Nginx configuration does not use XML filtering or XSD validation directives. |
| `tiff` | CVE-2026-4775 | HIGH | Image library | Static assets served are pre-compiled SVG/CSS/JS; dynamic TIFF parsing is disabled. |

---

## 5. Security Gates & Enforcement in CI/CD

Our GitHub Actions pipeline (`.github/workflows/ci-cd.yml`) implements DevSecOps policy as code:
1. **Automated Scan on PR & Push:** Every commit is scanned before images can be tagged or deployed.
2. **Strict Failure Gate (`exit-code: 1`):** The pipeline will immediately fail if any **HIGH** or **CRITICAL** vulnerability is detected that has not been reviewed and listed in `.trivyignore`.
3. **Audit Trail:** Every suppression in `.trivyignore` requires an accompanying rationale in this documentation.

---

## 6. Raw Trivy Scan Output (Evidence)

```text
2026-10-16T14:44:26Z    INFO    Vulnerability scanning is enabled
2026-10-16T14:44:26Z    INFO    Detected OS: debian (12.9)
2026-10-16T14:44:26Z    INFO    Detecting Debian vulnerabilities...
2026-10-16T14:44:26Z    INFO    Number of language-specific files: 33
2026-10-16T14:44:26Z    INFO    Detecting python-pkg vulnerabilities...

campuspulse-backend:latest (debian 12.9)
========================================
Total: 0 (HIGH: 0, CRITICAL: 0)

Python (python-pkg)
===================
Total: 3 (HIGH: 3, CRITICAL: 0)

┌──────────────────────┬────────────────┬──────────┬────────┬───────────────────┬───────────────┬──────────────────────────────────────────────────────────────┐
│       Library        │ Vulnerability  │ Severity │ Status │ Installed Version │ Fixed Version │                            Title                             │
├──────────────────────┼────────────────┼──────────┼────────┼───────────────────┼───────────────┼──────────────────────────────────────────────────────────────┤
│ starlette (METADATA) │ CVE-2025-62727 │ HIGH     │ fixed  │ 0.41.3            │ 0.49.1        │ starlette: Starlette DoS via Range header merging            │
│                      ├────────────────┤          │        │                   ├───────────────┼──────────────────────────────────────────────────────────────┤
│                      │ CVE-2026-48818 │          │        │                   │ 1.1.0         │ starlette: Starlette: SSRF and NTLM credential theft via UNC │
│                      │                │          │        │                   │               │ paths in StaticFiles...                                      │
│                      ├────────────────┤          │        │                   ├───────────────┼──────────────────────────────────────────────────────────────┤
│                      │ CVE-2026-54283 │          │        │                   │ 1.3.1         │ starlette: Starlette: request.form() limits silently ignored │
│                      │                │          │        │                   │               │ for application/x-www-form-urlencoded enable DoS             │
└──────────────────────┴────────────────┴──────────┴────────┴───────────────────┴───────────────┴──────────────────────────────────────────────────────────────┘
```
