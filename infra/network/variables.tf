variable "project_name" {
  description = "Name used to tag networking resources."
  type        = string
  default     = "mini-professional-network"
}

variable "aws_region" {
  description = "AWS region for the network."
  type        = string
  default     = "us-east-1"
}

variable "vpc_cidr" {
  description = "CIDR block for the VPC."
  type        = string
  default     = "10.0.0.0/16"
}

variable "backend_port" {
  description = "Port the backend API listens on."
  type        = number
  default     = 8000
}

variable "public_subnets" {
  description = "Public subnets across two availability zones."
  type = map(object({
    cidr = string
    az   = string
  }))
  default = {
    a = {
      cidr = "10.0.1.0/24"
      az   = "us-east-1a"
    }
    b = {
      cidr = "10.0.2.0/24"
      az   = "us-east-1b"
    }
  }
}

variable "private_app_subnets" {
  description = "Private subnets for backend application workloads."
  type = map(object({
    cidr = string
    az   = string
  }))
  default = {
    a = {
      cidr = "10.0.11.0/24"
      az   = "us-east-1a"
    }
    b = {
      cidr = "10.0.12.0/24"
      az   = "us-east-1b"
    }
  }
}

variable "private_db_subnets" {
  description = "Private subnets for RDS."
  type = map(object({
    cidr = string
    az   = string
  }))
  default = {
    a = {
      cidr = "10.0.21.0/24"
      az   = "us-east-1a"
    }
    b = {
      cidr = "10.0.22.0/24"
      az   = "us-east-1b"
    }
  }
}
