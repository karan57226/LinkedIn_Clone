# Dockerisation

Docker gives each layer of the app a repeatable runtime:

```text
frontend container -> React build served by Nginx
backend container  -> FastAPI app
db container       -> PostgreSQL, standing in for RDS locally
```

## Local Docker Stack

From the project root:

```bash
docker compose up --build
```

Then open:

```text
Frontend: http://localhost:5173
Backend:  http://localhost:8000/health
```

## Services

### `db`

Runs PostgreSQL locally.

In AWS, this becomes RDS PostgreSQL in the private DB subnets.

### `backend`

Runs FastAPI on port `8000`.

It connects to Postgres with:

```text
postgresql+psycopg://app_user:app_password@db:5432/professional_network
```

In AWS, this container image will be pushed to ECR and run on ECS/Fargate in the private app subnets.

### `frontend`

Builds the React app and serves static files with Nginx.

In AWS, the usual deployment path is S3 + CloudFront rather than a frontend container, but the frontend Docker image is still useful for learning and local consistency.

## Deployment Mapping

```text
Local Docker Compose              AWS Deployment
--------------------              --------------
Postgres container                RDS PostgreSQL
Backend container                 ECS Fargate task
Frontend Nginx container          S3 + CloudFront or ECS
localhost:8000                    Application Load Balancer
Docker network                    VPC + subnets + security groups
```

## Important Environment Variables

Backend:

```text
DATABASE_URL
FRONTEND_ORIGIN
APP_ENV
```

Frontend:

```text
VITE_API_BASE_URL
```

`VITE_API_BASE_URL` is compiled into the React build, so for AWS it should point to the deployed API URL, such as:

```text
https://api.example.com
```
