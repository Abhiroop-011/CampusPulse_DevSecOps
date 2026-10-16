# ==============================================================================
# CampusPulse AWS Infrastructure — Input Variables
# ==============================================================================
variable "aws_region" {
  description = "AWS deployment region"
  type        = string
  default     = "ap-south-1"
}

variable "environment" {
  description = "Deployment lifecycle environment name"
  type        = string
  default     = "prod"
}

variable "cluster_name" {
  description = "EKS Cluster identifier"
  type        = string
  default     = "campuspulse-eks"
}

variable "cluster_version" {
  description = "Kubernetes control plane minor version"
  type        = string
  default     = "1.31"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.30.0.0/16"
}

variable "node_instance_types" {
  description = "EC2 instance types for EKS managed node group"
  type        = list(string)
  default     = ["t3.medium"]
}

variable "min_nodes" {
  description = "Minimum number of worker nodes in node group"
  type        = number
  default     = 2
}

variable "max_nodes" {
  description = "Maximum number of worker nodes in node group"
  type        = number
  default     = 4
}

variable "desired_nodes" {
  description = "Target number of worker nodes in node group"
  type        = number
  default     = 2
}
