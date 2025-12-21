# Wise-Trad Full Stack Deployment on AWS ECS

A production-ready Infrastructure-as-Code (IaC) deployment using Pulumi to provision a full stack application on AWS ECS Fargate with Application Load Balancer, VPC networking, and multi-AZ high availability.

## Overview

This project deploys a containerized full stack application on AWS using:
- **ECS Fargate** for serverless container orchestration
- **Application Load Balancer** for traffic distribution
- **VPC with public/private subnets** across multiple availability zones
- **Security groups** for network isolation
- **FastAPI backend** with MongoDB integration
- **Frontend web application**

### Architecture

```
Internet
    ↓
Application Load Balancer (Port 80)
    ↓
Target Group (Port 8000, /health)
    ↓
ECS Fargate Tasks (Private Subnets)
    ├── Frontend Container (Port 80)
    └── Backend Container (Port 8000, FastAPI)
            ↓
        MongoDB (External)
```

## Prerequisites

- AWS account with appropriate permissions (VPC, ECS, ALB, EC2, IAM)
- AWS credentials configured locally (AWS CLI or environment variables)
- Python 3.6 or later
- Pulumi CLI installed (v3.x or v4.x)
- Docker images for frontend and backend services
- MongoDB connection string (MONGO_URI)

## Quick Start

### 1. Clone and Setup

```bash
# Navigate to the project directory
cd wise-trad-deployment

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Stack

```bash
# Login to Pulumi (use local backend or Pulumi Cloud)
pulumi login

# Select or create stack
pulumi stack select dev

# Configure AWS region (default: eu-north-1)
pulumi config set aws:region eu-north-1

# Set your MongoDB connection string
pulumi config set --secret mongoUri mongodb://your-connection-string
```

### 3. Deploy Infrastructure

```bash
# Preview changes
pulumi preview

# Deploy the stack
pulumi up

# Retrieve outputs (ALB DNS, VPC ID, etc.)
pulumi stack output
```

### 4. Access Your Application

```bash
# Get the ALB DNS name
pulumi stack output alb_dns_name

# Access your application
curl http://<alb-dns-name>
```

## Project Structure

```
wise-trad-deployment/
├── __main__.py                    # Main Pulumi program entry point
├── Pulumi.yaml                    # Project metadata and configuration
├── Pulumi.dev.yaml                # Dev stack configuration (eu-north-1)
├── requirements.txt               # Python dependencies
├── .gitignore                     # Version control exclusions
├── components/
│   ├── network/
│   │   ├── vpc.py                # VPC, subnets, IGW, route tables
│   │   └── security_group.py     # ALB and ECS security groups
│   ├── alb.py                    # Application Load Balancer setup
│   └── ecs/
│       ├── cluster.py            # ECS Fargate cluster
│       └── task.py               # ECS task definitions (in progress)
└── README.md                      # This file
```

## Infrastructure Components

### Network Layer

#### VPC Configuration
- **CIDR Block**: 10.0.0.0/16
- **Availability Zones**: 2 (for high availability)
- **Public Subnets**: 2 subnets (10.0.0.0/24, 10.0.1.0/24)
  - Internet Gateway attached
  - Public route table (0.0.0.0/0 → IGW)
  - Auto-assign public IPs enabled
- **Private Subnets**: 2 subnets for ECS tasks
- **DNS Support**: Enabled for both DNS names and hostnames

**Outputs**:
- VPC ID
- VPC CIDR block
- Public subnet IDs (list)
- Private subnet IDs (list)

#### Security Groups

**ALB Security Group**:
- Inbound: Port 80 (HTTP) from 0.0.0.0/0
- Outbound: All traffic

**ECS Security Group**:
- Inbound: Port 8000 from ALB Security Group only
- Outbound: All traffic
- Purpose: Isolates ECS tasks from direct internet access

### Load Balancing

#### Application Load Balancer
- **Type**: Application Load Balancer (Layer 7)
- **Scheme**: Internet-facing
- **Subnets**: Deployed in public subnets across multiple AZs
- **Listener**: Port 80 (HTTP)

**Target Group**:
- **Port**: 8000 (backend service)
- **Protocol**: HTTP
- **Target Type**: IP (for Fargate tasks)
- **Health Check**: /health endpoint

**Outputs**:
- ALB ARN
- ALB DNS name
- Target Group ARN

### Compute Layer

#### ECS Cluster
- **Launch Type**: Fargate (serverless)
- **Networking**: Deployed in private subnets
- **Security**: ECS security group attached

#### ECS Task Definition (In Progress)
- **CPU**: 512 CPU units (0.5 vCPU)
- **Memory**: 1024 MB (1 GB)
- **Network Mode**: awsvpc (required for Fargate)

**Containers**:
1. **Frontend Container**
   - Port: 80
   - Web application interface

2. **Backend Container**
   - Port: 8000
   - Framework: FastAPI
   - Environment: MONGO_URI (MongoDB connection)

**Outputs**:
- ECS Cluster ARN
- Task Definition ARN

## Configuration

### Stack Configuration (Pulumi.dev.yaml)

```yaml
config:
  aws:region: eu-north-1  # Stockholm region
  # Add custom configuration as needed
```

### Manage Configuration

```bash
# View current configuration
pulumi config

# Set AWS region
pulumi config set aws:region eu-north-1

# Set secrets (encrypted in stack config)
pulumi config set --secret mongoUri mongodb://your-connection-string

# Get specific config value
pulumi config get aws:region
```

## Deployment Workflow

### Initial Deployment

1. Set up AWS credentials
2. Install dependencies
3. Configure stack (region, secrets)
4. Run `pulumi up`
5. Verify resources in AWS Console

### Update Existing Stack

```bash
# Make code changes
# Preview changes
pulumi preview

# Apply updates
pulumi up

# Rollback if needed
pulumi refresh
```

### Destroy Infrastructure

```bash
# Remove all resources
pulumi destroy

# Remove stack entirely
pulumi stack rm dev
```

## Outputs

After deployment, retrieve outputs:

```bash
# View all outputs
pulumi stack output

# Specific outputs
pulumi stack output alb_dns_name      # ALB public endpoint
pulumi stack output vpc_id            # VPC identifier
pulumi stack output cluster_arn       # ECS cluster ARN
pulumi stack output target_group_arn  # ALB target group ARN
```

## High Availability & Scaling

### Current Configuration
- **Multi-AZ Deployment**: Resources span 2 availability zones
- **Load Balancing**: ALB distributes traffic across tasks
- **Health Checks**: Automatic task health monitoring via /health endpoint

### Future Enhancements
- Auto-scaling policies for ECS tasks
- CloudWatch alarms and monitoring
- NAT Gateway for private subnet internet access
- RDS or DocumentDB for managed database
- WAF integration for security
- SSL/TLS certificates via ACM

## Monitoring and Debugging

### View ECS Tasks

```bash
# List running tasks
aws ecs list-tasks --cluster <cluster-name> --region eu-north-1

# Describe task
aws ecs describe-tasks --cluster <cluster-name> --tasks <task-arn> --region eu-north-1
```

### Check ALB Health

```bash
# Describe target health
aws elbv2 describe-target-health --target-group-arn <target-group-arn> --region eu-north-1
```

### View Logs

- Navigate to AWS CloudWatch Logs
- Look for log groups matching your ECS task definitions
- Filter by task ID or time range

## Known Issues & TODO

### Current Status
- ✅ VPC with multi-AZ public/private subnets
- ✅ Internet Gateway and routing
- ✅ ALB with target group and listener
- ✅ ECS Cluster creation
- ✅ Security groups configuration
- ⚠️ ECS Task Definition (incomplete, has syntax errors)
- ❌ IAM roles for ECS task execution
- ❌ Container image configuration
- ❌ CI/CD pipeline integration
- ❌ Domain name and SSL/TLS setup

### Code Issues to Fix
- [vpc.py](components/network/vpc.py): Typo `availabilitiy_zone` → `availability_zone`
- [alb.py](components/alb.py): Missing comma after `health_check` dictionary
- [task.py](components/ecs/task.py): Multiple syntax errors, incomplete implementation
- [security_group.py](components/network/security_group.py): Typos `protocl` → `protocol`, `cird_blocks` → `cidr_blocks`

## Security Best Practices

✅ **Currently Implemented**:
- ECS tasks in private subnets (no direct internet access)
- Security groups with least-privilege access
- ALB as single public entry point
- Secrets stored encrypted in Pulumi config

🔒 **Recommended Additions**:
- Enable VPC Flow Logs
- Implement AWS WAF rules
- Use AWS Secrets Manager for credentials
- Enable container image scanning (ECR)
- Configure IAM roles with minimal permissions
- Enable CloudTrail for audit logging
- Use HTTPS with ACM certificates

## Cost Optimization

- **Fargate**: Pay only for vCPU and memory used
- **ALB**: Charged per hour + LCU (Load Balancer Capacity Units)
- **VPC**: NAT Gateway charges (if added)
- **Data Transfer**: Outbound data transfer costs

**Estimated Monthly Cost** (eu-north-1):
- ECS Fargate (2 tasks, 0.5 vCPU, 1GB): ~$30-40
- ALB: ~$20-25
- Data Transfer: Variable
- **Total**: ~$50-70/month (excluding database)

## Troubleshooting

### Tasks Not Starting
- Check IAM roles and permissions
- Verify container images are accessible
- Check security group rules
- Review CloudWatch logs

### ALB Health Check Failing
- Ensure /health endpoint exists in backend
- Verify port 8000 is exposed in container
- Check ECS task security group allows ALB traffic

### Cannot Access Application
- Verify ALB security group allows port 80 inbound
- Check ALB is in public subnets
- Ensure target group has healthy targets
- Confirm route table and IGW configuration

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy to ECS
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: pulumi/actions@v4
        with:
          command: up
          stack-name: dev
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
          AWS_ACCESS_KEY_ID: ${{ secrets.AWS_ACCESS_KEY_ID }}
          AWS_SECRET_ACCESS_KEY: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

## References

- [Pulumi AWS Documentation](https://www.pulumi.com/registry/packages/aws/)
- [AWS ECS Fargate Documentation](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/AWS_Fargate.html)
- [Pulumi Python SDK](https://www.pulumi.com/docs/reference/pkg/python/)
- [AWS VPC Best Practices](https://docs.aws.amazon.com/vpc/latest/userguide/vpc-best-practices.html)

## Support

For issues or questions:
- Review AWS CloudWatch logs
- Check Pulumi stack state: `pulumi stack`
- Pulumi Community Slack: https://slack.pulumi.com/
- AWS Support: https://console.aws.amazon.com/support

## License

[Specify your license here]

## Contributors

[Add contributor information]

---

**Last Updated**: 2025-12-21
**Pulumi Version**: 3.0.0 - 4.0.0
**AWS Region**: eu-north-1 (Stockholm)
