# CampusPulse Observability — Prometheus & Grafana Guide

This directory contains the complete observability and monitoring stack for the **CampusPulse** platform, satisfying **Module 9** of the capstone curriculum.

---

## 1. Observability Architecture

```
                       +------------------------------+
                       |      FastAPI Backend         |
                       |  Exposes: /metrics (port 8000)|
                       +--------------+---------------+
                                      |
                         Scraped by ServiceMonitor
                                  (15s)
                                      v
                       +------------------------------+
                       |   Prometheus TSDB Server     |
                       | Stores: Latency, Count, RSS  |
                       +--------------+---------------+
                                      |
                                PromQL Queries
                                      v
                       +------------------------------+
                       |       Grafana UI             |
                       | Dashboard: campuspulse-main  |
                       +------------------------------+
```

---

## 2. Deploying Prometheus Stack via Helm

### Step 1: Add the Prometheus Community Helm repository
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update
```

### Step 2: Deploy `kube-prometheus-stack`
```bash
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  -f monitoring/prometheus-values.yaml
```

### Step 3: Verify all monitoring components are Running
```bash
kubectl get pods -n monitoring
```

---

## 3. Accessing Prometheus & Grafana

### Access Prometheus Web UI
```bash
kubectl port-forward svc/prometheus-kube-prometheus-prometheus -n monitoring 9090:9090
```
- Open in browser: `http://localhost:9090`
- Navigate to **Status -> Targets** to verify `campuspulse-backend` shows state **UP (1/1)**.

### Access Grafana Dashboard
```bash
kubectl port-forward svc/prometheus-grafana -n monitoring 3001:80
```
- Open in browser: `http://localhost:3001`
- **Username:** `admin`
- **Password:** `admin_campuspulse_secure_2026` (from `prometheus-values.yaml`)

---

## 4. Importing the Dashboard

1. In Grafana, click **Dashboards -> New -> Import**.
2. Upload `monitoring/grafana-dashboard.json` or paste its contents.
3. Select the `Prometheus` datasource and click **Import**.
4. The following 5 live panels will render:
   - **API Request Throughput by Endpoint:** `sum by (handler) (rate(http_request_duration_seconds_count[1m]))`
   - **p95 / p50 Request Latency:** `histogram_quantile(0.95, sum(rate(http_request_duration_highr_seconds_bucket[1m])) by (le))`
   - **HTTP Status Distribution:** `sum by (status) (http_request_duration_seconds_count)`
   - **Resident Memory Consumption (RSS):** `process_resident_memory_bytes`
   - **CPU Utilization Rate (%):** `rate(process_cpu_seconds_total[1m]) * 100`

---

## 5. Sample Live Metric Output (Evidence)

```text
# HELP http_requests_total Total number of requests by method, status and handler.
# TYPE http_requests_total counter
http_requests_total{handler="/api/clubs",method="GET",status="200"} 6.0
http_requests_total{handler="/api/events",method="GET",status="200"} 4.0
http_requests_total{handler="/api/events/{event_id}/registrations",method="POST",status="201"} 2.0
http_requests_total{handler="/api/stats",method="GET",status="200"} 8.0
http_requests_total{handler="/health",method="GET",status="200"} 142.0

# HELP http_request_duration_highr_seconds Latency with many buckets.
# TYPE http_request_duration_highr_seconds histogram
http_request_duration_highr_seconds_bucket{le="0.01"} 130.0
http_request_duration_highr_seconds_bucket{le="0.05"} 148.0
http_request_duration_highr_seconds_bucket{le="0.1"} 152.0
http_request_duration_highr_seconds_bucket{le="+Inf"} 152.0
```
