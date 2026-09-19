terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

# 1. Multi-AZ Corporate VPC Network Topology
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "~> 5.0"

  name = "vpc-agentic-ai-prod"
  cidr = "10.2.0.0/16"

  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  private_subnets = ["10.2.1.0/24", "10.2.2.0/24", "10.2.3.0/24"]
  public_subnets  = ["10.2.101.0/24", "10.2.102.0/24", "10.2.103.0/24"]

  enable_nat_gateway   = true
  single_nat_gateway   = true # Strategic cost optimization for portfolio staging
  enable_dns_hostnames = true

  public_subnet_tags = {
    "kubernetes.io/role/elb" = "1"
  }
  private_subnet_tags = {
    "kubernetes.io/role/internal-elb" = "1"
  }
}

# 2. Enterprise AWS Managed EKS Cluster Control Plane
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 19.0"

  cluster_name    = "eks-agentic-ops-prod"
  cluster_version = "1.28"

  cluster_endpoint_public_access  = false # Total private endpoint network isolation
  cluster_endpoint_private_access = true

  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnets

  # Critical engineering design: Enables secure OpenID pod metadata auth token exchange
  enable_irsa = true

  eks_managed_node_groups = {
    agent_compute_pool = {
      min_size     = 2
      max_size     = 5
      desired_size = 3

      instance_types = ["m6i.xlarge"] # Memory-optimized infrastructure compute sizing
      capacity_type  = "ON_DEMAND"
    }
  }

  tags = {
    Environment  = "Production"
    Architecture = "Forward-Deployed-AI"
  }
}

# Output parameters to map configuration layers downstream
output "eks_cluster_endpoint" {
  value       = module.eks.cluster_endpoint
  description = "The internal security connection endpoint for the EKS control plane."
}
