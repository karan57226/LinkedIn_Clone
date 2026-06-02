# How The Subnets Interact

The VPC is the private network. Subnets are sections of that network placed in availability zones.

In this design, every subnet is inside:

```text
10.0.0.0/16
```

That means AWS automatically creates local VPC routing that lets subnets reach each other internally:

```text
10.0.0.0/16 -> local
```

You do not manually create that local route. AWS adds it to every VPC route table.

## Public Subnets

Public subnets have this route:

```text
0.0.0.0/0 -> Internet Gateway
```

That makes them suitable for internet-facing resources:

- Application Load Balancer
- NAT Gateway

The public subnet is not public because of its name. It is public because its route table points internet-bound traffic to the Internet Gateway.

## Private App Subnets

Private app subnets have this route:

```text
0.0.0.0/0 -> NAT Gateway
```

The backend can make outbound internet requests through NAT, but outside users cannot directly start connections into the backend.

The backend receives user traffic through the ALB:

```text
Internet -> ALB -> Backend
```

## Private DB Subnets

Private DB subnets do not have an internet route.

That means RDS can communicate inside the VPC, but it does not have direct internet access.

The only intended app path is:

```text
Backend -> RDS
```

## Routing Versus Security Groups

Routing decides whether a network path exists.

Security groups decide whether traffic is allowed to use that path.

Example:

```text
Backend and RDS are both in the VPC.
The route exists through local VPC routing.
But RDS only accepts port 5432 from the backend security group.
```

So the database is protected by both placement and permissions:

- It sits in private DB subnets.
- It has no public internet route.
- Its security group only trusts the backend.

## Request Flow

```text
User browser
↓
Internet
↓
Public subnet
↓
Application Load Balancer
↓
Private app subnet
↓
FastAPI backend
↓
Private DB subnet
↓
RDS PostgreSQL
```

## Outbound Backend Flow

If the backend needs to download packages, call an external API, or reach AWS services over the internet:

```text
Backend
↓
Private app subnet route table
↓
NAT Gateway in public subnet
↓
Internet Gateway
↓
Internet
```

The response comes back through the same NAT path.

## Why Two AZs

Two AZs make the network resilient.

If `us-east-1a` has a problem, the load balancer can still send traffic to backend tasks in `us-east-1b`.

RDS can also use both DB subnets for Multi-AZ failover later.
