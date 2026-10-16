# CampusPulse Infrastructure as Code — AWS VPC & EKS Cluster

This directory defines the cloud infrastructure for **CampusPulse** on Amazon Web Services (AWS) using Terraform, satisfying **Module 7** of the capstone rubric.

---

## 1. Cloud Architecture

```
                       AWS Cloud (Region: ap-south-1)
 +-----------------------------------------------------------------------+
 |  VPC: campuspulse-vpc (10.30.0.0/16)                                  |
 |                                                                       |
 |   Public Subnets (10.30.101.0/24, 10.30.102.0/24)                     |
 |   +------------------------------------+--------------------------+  |
 |   | Single NAT Gateway (Cost Savings)  | Internet Gateway (IGW)   |  |
 |   | AWS Application Load Balancer (ALB)|                          |  |
 |   +------------------------------------+--------------------------+  |
 |                                                                       |
 |   Private Subnets (10.30.1.0/24, 10.30.2.0/24)                        |
 |   +---------------------------------------------------------------+  |
 |   | EKS Control Plane (Kubernetes v1.31)                          |  |
 |   | Managed Node Group (2x t3.medium EC2 Instances)               |  |
 |   |   - campuspulse-backend Pods (Replicas: 2)                    |  |
 |   |   - campuspulse-frontend Pods (Replicas: 2)                   |  |
 |   |   - campuspulse-postgres (Stateful Storage PVC)               |  |
 |   |   - Prometheus & Grafana Monitoring Pods                      |  |
 |   +---------------------------------------------------------------+  |
 +-----------------------------------------------------------------------+
```

---

## 2. Cost Management & Student Budget Optimization

EKS cluster and NAT Gateway costs can add up if unmanaged. The following measures are baked into our design:
1. **Single NAT Gateway (`single_nat_gateway = true`):** Reduces AWS NAT Gateway charges by 50% compared to standard multi-AZ deployments (~$32.40/month instead of ~$65+/month).
2. **Right-Sized Node Pool (`t3.medium`):** Burstable compute with 2 vCPUs and 4 GiB RAM per node provides sufficient capacity for both backend and frontend microservices at ~$0.0416/hr.
3. **Cluster Teardown Workflow:** Explicit teardown steps ensure resources can be destroyed immediately after evaluation.

---

## 3. Deployment Runbook

### Prerequisites
- Terraform CLI >= 1.7.0 installed
- AWS CLI configured with active credentials (`aws configure`)
- IAM permissions: VPC, EC2, EKS, IAM Role creation

### Step 1: Initialize Terraform & Download Modules
```bash
terraform init
```

### Step 2: Validate HCL Syntax
```bash
terraform fmt -check
terraform validate
```

### Step 3: Generate Execution Plan
```bash
terraform plan -out=tfplan
```

### Step 4: Provision Infrastructure (Requires Prior Approval)
```bash
terraform apply tfplan
```

### Step 5: Configure kubectl for the new EKS Cluster
```bash
aws eks update-kubeconfig --region ap-south-1 --name campuspulse-eks
kubectl get nodes
```

---

## 4. Teardown Procedure (Prevent Cloud Overages)

When grading/demonstration is complete, teardown all provisioned AWS assets:
```bash
# 1. First remove any Helm releases with active Load Balancers
helm uninstall campuspulse -n campuspulse

# 2. Destroy all AWS infrastructure
terraform destroy -auto-approve
```
