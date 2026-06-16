# DevOps Pipeline

This project can use GitHub Actions as the CI/CD pipeline.

## What The Pipeline Does

On every pull request to `main`:

```text
Install backend dependencies
Run backend unit tests
Install frontend dependencies
Build the React frontend
```

On every push to `main`:

```text
Run the same tests
Build frontend Docker image for linux/amd64
Push frontend image to ECR
Build backend Docker image for linux/amd64
Push backend image to ECR
```

## Unit Tests Added

The backend has two tests in `backend/tests/test_api.py`:

```text
GET /health returns status ok
GET /api/feed returns seeded posts
```

These tests use a temporary SQLite database so they do not touch the local dev database or RDS.

## Required GitHub Secret

Create this repository secret:

```text
AWS_GITHUB_ACTIONS_ROLE_ARN
```

Its value should be the ARN of an IAM role GitHub Actions can assume, for example:

```text
arn:aws:iam::488709146192:role/github-actions-ecr-deploy-role
```

## IAM Role Permissions

The GitHub Actions role needs permission to push to these ECR repositories:

```text
488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/frontend
488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/backend
```

For learning, attaching this managed policy is the simplest path:

```text
AmazonEC2ContainerRegistryPowerUser
```

For a tighter production setup, create a custom policy limited to:

```text
ecr:GetAuthorizationToken
ecr:BatchCheckLayerAvailability
ecr:InitiateLayerUpload
ecr:UploadLayerPart
ecr:CompleteLayerUpload
ecr:PutImage
```

## After Images Are Pushed

The pipeline currently pushes new images to ECR. Your EC2 instances still need to pull and restart containers.

Manual restart commands:

```bash
sudo docker pull 488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/frontend:latest
sudo docker rm -f frontend
sudo docker run -d --name frontend --restart always -p 80:80 488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/frontend:latest
```

```bash
sudo docker pull 488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/backend:latest
sudo docker rm -f backend
sudo docker run -d \
  --name backend \
  --restart always \
  -p 8000:8000 \
  -e APP_ENV=aws \
  -e DATABASE_URL="postgresql+psycopg://app_user:REPLACE_ME@database-1.cpmc6ek8ktsn.us-west-1.rds.amazonaws.com:5432/postgres" \
  488709146192.dkr.ecr.us-west-1.amazonaws.com/linkedin/backend:latest
```

The next automation step would be replacing manual EC2 restarts with one of these:

```text
CodeDeploy
ECS/Fargate
SSM Run Command
Auto Scaling instance refresh
```
