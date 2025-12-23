# Required GitHub Secrets

This document lists all the GitHub secrets that need to be configured in your repository settings for the CI/CD workflow to work.

## Required Secrets

### AWS Credentials (NOT NEEDED with Webhook Integration)
> **Note**: When using CodeBuild webhook integration (recommended), you do NOT need AWS credentials in GitHub.
> CodeBuild is triggered directly by GitHub webhooks, and authentication is handled in AWS.
> 
> See `CODEBUILD_WEBHOOK_SETUP.md` for webhook setup instructions.

- ~~`AWS_ACCESS_KEY_ID`~~ - **Not needed with webhook integration**
- ~~`AWS_SECRET_ACCESS_KEY`~~ - **Not needed with webhook integration**
- `AWS_ACCOUNT_ID` - Your AWS account ID (12-digit number) - Only needed if used in buildspec

### Container Registry Configuration
Choose one of the following options:

#### Option 1: Amazon ECR (Recommended for AWS deployments)
- `USE_ECR` - Set to `"true"` to use ECR
- `AWS_ACCOUNT_ID` - Required for ECR (already listed above)

#### Option 2: Docker Hub
- `DOCKER_HUB_TOKEN` - Docker Hub access token
- `USE_ECR` - Set to `"false"` or leave unset

### Pulumi Configuration
- `PULUMI_ACCESS_TOKEN` - Pulumi access token (optional if using file backend)
  - Get from: https://app.pulumi.com/account/tokens
  - Or use file backend by leaving this unset

### Application Configuration
- `MONGO_URI` - MongoDB connection string (if not already in Pulumi config)
  - Format: `mongodb+srv://user:password@cluster.mongodb.net/?retryWrites=true&w=majority`

## How to Add Secrets

1. Go to your GitHub repository
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**
4. Add each secret with the exact name listed above

## Permissions Required for AWS IAM User/Role

The AWS credentials need the following permissions:
- `ecr:*` - For pushing Docker images
- `ecs:*` - For managing ECS services
- `ec2:*` - For VPC, subnets, security groups
- `elasticloadbalancing:*` - For Application Load Balancer
- `iam:*` - For creating ECS execution roles
- `logs:*` - For CloudWatch logs (optional but recommended)

Or attach the following AWS managed policies:
- `AmazonECS_FullAccess`
- `AmazonEC2ContainerRegistryFullAccess`
- `AmazonVPCFullAccess`
- `ElasticLoadBalancingFullAccess`
- `IAMFullAccess` (or create a custom policy with minimal permissions)

## Testing the Workflow

### With Webhook Integration (Recommended)
1. Configure CodeBuild webhook (see `CODEBUILD_WEBHOOK_SETUP.md`)
2. Push to the `main` or `master` branch - CodeBuild will trigger automatically
3. Check build status in AWS CodeBuild console

### With GitHub Actions (Legacy - requires AWS credentials)
1. Add AWS credentials to GitHub secrets
2. Push to the `main` or `master` branch to trigger the workflow
3. Or manually trigger it from the **Actions** tab → **Build and Deploy with CodeBuild** → **Run workflow**

