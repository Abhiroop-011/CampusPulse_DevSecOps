# CampusPulse DevSecOps — AWS Infrastructure Deployment & Evidence

## 1. Overview & Cloud Architecture

CampusPulse uses **Terraform (Infrastructure as Code)** to deploy a production-grade, highly available, and cost-conscious Kubernetes environment on Amazon Web Services (AWS).

```text
                               AWS Cloud (ap-southeast-2)
 ┌───────────────────────────────────────────────────────────────────────────────┐
 │ VPC (10.30.0.0/16) — campuspulse-eks-vpc                                     │
 │                                                                               │
 │  ┌── Public Subnet 1 (10.30.101.0/24) ──┐  ┌── Public Subnet 2 (10.30.102.0/24) ──┐
 │  │ • Internet Gateway                   │  │                                  │
 │  │ • Single NAT Gateway (Cost Savings)  │  │                                  │
 │  │ • AWS ALB / Ingress (Public Facing)  │  │                                  │
 │  └──────────────────────────────────────┘  └──────────────────────────────────┘
 │                        │                                     │
 │  ┌─────────────────────┴─────────────────────────────────────┴─────────────┐   │
 │  │ Private Subnets (10.30.1.0/24, 10.30.2.0/24)                            │   │
 │  │                                                                         │   │
 │  │  Managed AWS EKS Cluster: campuspulse-eks (Kubernetes 1.31)             │   │
 │  │  ┌───────────────────────────────────────────────────────────────────┐  │   │
 │  │  │ EKS Managed Node Group: campuspulse-eks-ng                        │  │   │
 │  │  │ • 2x t3.medium EC2 Worker Nodes                                   │  │   │
 │  │  │ • IMDSv2 Enforced (http_tokens = "required")                      │  │   │
 │  │  │ • Encrypted EBS Volumes (gp3)                                     │  │   │
 │  │  │ • KMS Envelope Encryption for Kubernetes Secrets                  │  │   │
 │  │  │                                                                   │  │   │
 │  │  │ Pods:                                                             │  │   │
 │  │  │ ├── campuspulse-backend (FastAPI REST API, Python 3.12-slim)      │  │   │
 │  │  │ ├── campuspulse-frontend (React 19 + Nginx 1.27-alpine)           │  │   │
 │  │  │ └── campuspulse-postgres (PostgreSQL 16-alpine)                   │  │   │
 │  │  └───────────────────────────────────────────────────────────────────┘  │   │
 │  └─────────────────────────────────────────────────────────────────────────┘   │
 └───────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. Infrastructure Identity & Configuration

| Parameter | Deployed Value | Rationale |
|---|---|---|
| **Cloud Provider** | Amazon Web Services (AWS) | Target Capstone Production Environment |
| **AWS Region** | `ap-southeast-2` (Sydney) | Configured host region |
| **VPC CIDR** | `10.30.0.0/16` | Isolated address space avoiding default collisions |
| **Availability Zones** | `ap-southeast-2a`, `ap-southeast-2b` | Dual-AZ high availability |
| **NAT Gateway Strategy** | Single NAT Gateway | **Cost Optimization:** Saves ~$65/mo vs multi-AZ NAT |
| **EKS Version** | Kubernetes 1.31 | Stable modern enterprise release |
| **Worker Compute** | 2x `t3.medium` (Burst-capable) | Balances memory requirements for React+FastAPI+DB |
| **Cluster Security** | KMS Secret Envelope Encryption | Zero plain-text Kubernetes secrets at rest in etcd |
| **Node Security** | IMDSv2 Required | Protects against SSRF IAM credential theft |

---

## 3. Terraform Execution Records

### A. Initialization
```bash
terraform init -backend=false
```
**Output Highlights:**
- `hashicorp/aws v5.100.0`
- `hashicorp/tls v4.4.1`
- `hashicorp/cloudinit v2.4.1`
- `hashicorp/time v0.14.2`
- `hashicorp/null v3.3.2`
- Initialized modules: `vpc`, `eks`, `kms`, `eks_managed_node_group`

### B. Plan Validation & Deployment
```bash
terraform plan -out=tfplan
terraform apply "tfplan"
```
**Live Provisioned Outputs:**
```json
{
  "cluster_name": "campuspulse-eks",
  "cluster_version": "1.31",
  "cluster_status": "ACTIVE",
  "cluster_endpoint": "https://B989956BF67F2E43FB2D33C497A98F68.gr7.ap-southeast-2.eks.amazonaws.com",
  "vpc_id": "vpc-06f423d041575e774",
  "private_subnets": [
    "subnet-0a7e7ace66133ee5c",
    "subnet-02a462e0f6452a4a5"
  ],
  "public_subnets": [
    "subnet-00f3933f6ea43413e",
    "subnet-0514820ca23e90784"
  ],
  "cluster_security_group_id": "sg-07080a477568e155c"
}
```

---

## 4. Live Cluster Verification Evidence

### A. Control Plane Status
```text
$ kubectl cluster-info
Kubernetes control plane is running at https://B989956BF67F2E43FB2D33C497A98F68.gr7.ap-southeast-2.eks.amazonaws.com
CoreDNS is running at https://B989956BF67F2E43FB2D33C497A98F68.gr7.ap-southeast-2.eks.amazonaws.com/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy
```

### B. Worker Nodes (`Ready` Status)
```text
$ kubectl get nodes -o wide
NAME                                            STATUS   ROLES    AGE    VERSION                INTERNAL-IP   EXTERNAL-IP   OS-IMAGE                        KERNEL-VERSION                    CONTAINER-RUNTIME
ip-10-30-1-7.ap-southeast-2.compute.internal    Ready    <none>   103s   v1.31.14-eks-b9510e3   10.30.1.7     <none>        Amazon Linux 2023.12.20261012   6.1.188-233.393.amzn2023.x86_64   containerd://2.3.5+unknown
ip-10-30-2-30.ap-southeast-2.compute.internal   Ready    <none>   101s   v1.31.14-eks-b9510e3   10.30.2.30    <none>        Amazon Linux 2023.12.20261012   6.1.188-233.393.amzn2023.x86_64   containerd://2.3.5+unknown
```

### C. System Pods Status (`Running`)
```text
$ kubectl get pods -A
NAMESPACE     NAME                       READY   STATUS    RESTARTS   AGE
kube-system   aws-node-j7m48             2/2     Running   0          2m4s
kube-system   aws-node-kmbww             2/2     Running   0          2m2s
kube-system   coredns-7585b665d8-twqwb   1/1     Running   0          5m52s
kube-system   coredns-7585b665d8-wcjvz   1/1     Running   0          5m52s
kube-system   kube-proxy-l4pzw           1/1     Running   0          2m4s
kube-system   kube-proxy-wqpzh           1/1     Running   0          2m2s
```

---

## 5. Teardown Procedure (Runaway Cost Prevention)

To cleanly destroy all provisioned cloud resources:
```bash
cd terraform
terraform destroy -auto-approve
```

Confirm all 54 resources are destroyed cleanly, leaving no orphaned VPCs, EIPs, or EBS volumes.
