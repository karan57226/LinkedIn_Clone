# EC2 deployment and rollback

Pushes to main run tests and build React, then publish both images with commit-SHA and latest tags. The workflow deploys the SHA-tagged backend first and frontend second through SSM, waiting for each command result. It then checks the React page and database-backed /api/feed through the public ALB.

## Requirements

- GitHub secret AWS_GITHUB_ACTIONS_ROLE_ARN and OIDC trust restricted to this repository's main branch; audience sts.amazonaws.com.
- GitHub role: ECR publishing permissions, ssm:SendCommand for AWS-RunShellScript and the two instances, plus ssm:GetCommandInvocation.
- EC2 roles: SSM agent permissions and ECR pull permissions. Both instances must be Online.
- Servers need Docker, AWS CLI, Python 3, base64, and flock.
- Existing containers: backend on 8000 and frontend on 80, default Docker networking, no mounts. Backend must use external PostgreSQL.

## Deployment behavior

The script checks current health and pulls the new image before stopping the live container. It preserves APP_ENV, DATABASE_URL, and FRONTEND_ORIGIN if present via a private temporary environment file on the server. Values never enter GitHub logs. Review the script when adding new configuration.

The old container is retained as SERVICE-previous, with automatic restart disabled. The replacement uses the original service name. Backend checks request /health and /api/feed; frontend checks request /. A failed local deployment restores the old container and fails the workflow. Public ALB smoke-check failure marks the workflow failed but requires investigation and manual rollback; it does not automatically revert both services.

## First run

Commit the workflow, scripts, tests, and documentation, then push main. Check both deployment jobs and the public smoke check in Actions. Verify the app in a browser. Local recovery tests simulate Docker; live deployment and rollback must still be demonstrated.

## Manual rollback

GitHub Actions → CI/CD → Run workflow → main → select backend or frontend. This runs rollback only. It restores the retained previous container, checks health, and keeps the displaced container as the next rollback target. Restore the other service separately if needed. The first successful deployment must exist before rollback is available.

Rollback restores containers, not database schema or data. Use a separate migration plan for schema changes. After SSM timeout or interruption, inspect the command ID and container state before retrying; abrupt server failure can interrupt recovery.

## Limits and infrastructure follow-up

Single-container replacement causes brief downtime. Frontend and backend releases are not atomic. Health checks are smoke checks, not full browser tests.

Targets are fixed: frontend i-00bf665dad7167928 and backend i-0255cb08c63d77f5c in us-west-1. The frontend belongs to an Auto Scaling Group. Replacement instances are not yet handled by these fixed deployment targets or local rollback containers. Review/import launch templates, bootstrap configuration, and ASG membership when implementing Terraform; define how new instances obtain the approved release. Check whether existing bootstrap scripts consume latest, which is published before deployment validation.

Production URL: http://linkedin-alb-976933077.us-west-1.elb.amazonaws.com/. The ALB must route /api/* to the backend and the frontend page to the frontend.

Older GitHub action versions may emit runtime warnings. These are separate from deployment behavior and should be updated and pinned in a maintenance change.
