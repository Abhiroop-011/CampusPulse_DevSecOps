# ==============================================================================
# CampusPulse AWS Infrastructure — Core VPC and Managed EKS Cluster
# Production-ready, cost-conscious architecture (Single NAT Gateway, t3.medium nodes)
# ==============================================================================

# ── Local Variables & Helpers ─────────────────────────────────────────────────
locals {
  azs = ["${var.aws_region}a", "${var.aws_region}b"]
}

# ── Module 1: AWS Virtual Private Cloud (VPC) ─────────────────────────────────
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.8"

  name = "${var.cluster_name}-vpc"
  cidr = var.vpc_cidr

  azs             = local.azs
  private_subnets = ["10.30.1.0/24", "10.30.2.0/24"]
  public_subnets  = ["10.30.101.0/24", "10.30.102.0/24"]

  # Cost management: single NAT Gateway for private outbound traffic
  enable_nat_gateway     = true
  single_nat_gateway     = true
  one_nat_gateway_per_az = false

  enable_dns_hostnames = true
  enable_dns_support   = true

  # Kubernetes Ingress & AWS Load Balancer Controller discovery tags
  public_subnet_tags = {
    "kubernetes.io/role/elb"                    = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }

  private_subnet_tags = {
    "kubernetes.io/role/internal-elb"           = "1"
    "kubernetes.io/cluster/${var.cluster_name}" = "shared"
  }
}

# ── Module 2: Managed AWS EKS Cluster ─────────────────────────────────────────
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.31"

  cluster_name    = var.cluster_name
  cluster_version = var.cluster_version

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  cluster_endpoint_public_access           = true
  enable_cluster_creator_admin_permissions = true
  enable_irsa                              = false

  # Managed Node Group: Spot/On-Demand balanced EC2 compute
  eks_managed_node_groups = {
    main = {
      name           = "${var.cluster_name}-ng"
      instance_types = var.node_instance_types

      min_size     = var.min_nodes
      max_size     = var.max_nodes
      desired_size = var.desired_nodes

      capacity_type = "ON_DEMAND"
      disk_size     = 30

      labels = {
        role        = "worker"
        environment = var.environment
      }
    }
  }
}
