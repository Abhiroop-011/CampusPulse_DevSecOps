# ==============================================================================
# CampusPulse AWS Infrastructure — Outputs
# Values required for kubeconfig generation and network integration
# ==============================================================================

output "cluster_name" {
  description = "EKS cluster name"
  value       = module.eks.cluster_name
}

output "cluster_endpoint" {
  description = "EKS control plane API server endpoint URL"
  value       = module.eks.cluster_endpoint
}

output "cluster_security_group_id" {
  description = "Security group ID attached to the EKS control plane"
  value       = module.eks.cluster_security_group_id
}

output "vpc_id" {
  description = "VPC ID where the EKS cluster and workloads reside"
  value       = module.vpc.vpc_id
}

output "private_subnets" {
  description = "List of private subnet IDs for worker nodes and databases"
  value       = module.vpc.private_subnets
}

output "public_subnets" {
  description = "List of public subnet IDs for external Ingress Load Balancers"
  value       = module.vpc.public_subnets
}
