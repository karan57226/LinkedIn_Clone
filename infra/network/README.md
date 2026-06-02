# Network Foundation

This Terraform folder creates the networking layer for the mini professional network app.

Region:

```text
us-east-1
```

Availability zones:

```text
us-east-1a
us-east-1b
```

## What This Creates

```text
VPC: 10.0.0.0/16

us-east-1a
├── Public subnet:      10.0.1.0/24
├── Private app subnet: 10.0.11.0/24
└── Private DB subnet:  10.0.21.0/24

us-east-1b
├── Public subnet:      10.0.2.0/24
├── Private app subnet: 10.0.12.0/24
└── Private DB subnet:  10.0.22.0/24
```

It also creates:

- Internet Gateway
- One NAT Gateway
- Public route table
- Private app route table
- Private DB route table
- Security groups for the ALB, backend API, and RDS PostgreSQL

## Traffic Model

```text
Internet
↓
ALB in public subnets
↓
Backend API in private app subnets
↓
RDS PostgreSQL in private DB subnets
```

## Route Tables

Public subnets:

```text
0.0.0.0/0 -> Internet Gateway
```

Private app subnets:

```text
0.0.0.0/0 -> NAT Gateway
```

Private DB subnets:

```text
No internet route
```

The DB subnets can still communicate inside the VPC, but they cannot directly reach the public internet.

## Security Groups

ALB:

```text
Inbound 80 from the internet
Inbound 443 from the internet
Outbound to backend
```

Backend:

```text
Inbound 8000 only from ALB security group
Outbound to internet and RDS
```

RDS:

```text
Inbound 5432 only from backend security group
```

## Commands

From this folder:

```bash
terraform init
terraform plan
terraform apply
```

Do not run `terraform apply` until you are ready to create AWS resources that may cost money.
