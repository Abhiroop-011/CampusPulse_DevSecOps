# CampusPulse GitOps — Argo CD Operations Guide

This directory defines the **GitOps workflow** for CampusPulse, enabling fully automated, declarative deployments to Kubernetes using **Argo CD**.

---

## 1. Architecture Overview

```
                      +-----------------------------+
                      |   Git Repository (GitHub)   |
                      |  - helm/campuspulse/        |
                      |  - values.yaml              |
                      |  - values-prod.yaml         |
                      +--------------+--------------+
                                     |
                                     | Webhook / Polling (3 min)
                                     v
                      +-----------------------------+
                      |       Argo CD Controller    |
                      |    (Application: campuspulse)
                      +--------------+--------------+
                                     |
                        Reconcile & Self-Heal
                                     |
                                     v
         +-------------------------------------------------------+
         |                 Kubernetes Cluster                    |
         |  Namespace: campuspulse                               |
         |  - campuspulse-backend (Deployment + Service)        |
         |  - campuspulse-frontend (Deployment + Service)       |
         |  - campuspulse-postgres (Deployment + PVC + Secret)  |
         |  - campuspulse-ingress (Ingress)                     |
         |  - HPA (HorizontalPodAutoscalers)                    |
         +-------------------------------------------------------+
```

---

## 2. Bootstrapping Argo CD

### Step 1: Install Argo CD into the cluster
```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### Step 2: Verify all Argo CD pods are ready
```bash
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=argocd-server -n argocd --timeout=300s
```

### Step 3: Access Argo CD UI
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
- **URL:** `https://localhost:8080`
- **Username:** `admin`
- **Initial Password:**
  ```bash
  kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
  ```

---

## 3. Register CampusPulse GitOps Application

Apply the project boundaries and the declarative application definition:
```bash
kubectl apply -f gitops/argocd-project.yaml
kubectl apply -f gitops/argocd-application.yaml
```

---

## 4. Key GitOps Capabilities Configured

1. **Automated Sync (`automated.prune: true`, `automated.selfHeal: true`):**
   - When any developer pushes updates to `helm/campuspulse/`, Argo CD detects the git drift within seconds and applies the update automatically.
   - If someone manually edits a pod or replica count with `kubectl`, Argo CD detects out-of-sync state and automatically restores the desired state from Git.
2. **Resource Pruning (`prune: true`):**
   - If a template is removed from Git, the corresponding Kubernetes resource is automatically cleanly deleted.
3. **Progressive Rollout & Retries:**
   - Exponential backoff retry policy ensures smooth recovery from transient cluster blips.
