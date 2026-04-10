# Deployment Guide

This document describes the production deployment strategy for the AI Query Assistant using a containerized architecture on AWS. The system is designed to run as a multi-container stack on a single EC2 instance, protected by an Application Load Balancer and optional edge security layers.

---

## Target Architecture

```text
Browser
  └── Cloudflare (optional: WAF, DDoS protection)
        └── Route 53 (DNS Alias → ALB)
              └── Application Load Balancer (HTTPS termination, ACM)
                    └── EC2 Instance (Ubuntu 24.04, Docker Compose)
                          ├── Gateway Container (Port 80)
                          ├── UI Container (Internal only)
                          └── Backend Container (Internal only)
```

The Application Load Balancer (ALB) handles SSL/TLS termination, providing an encrypted entry point for clients. Traffic is then forwarded over the internal AWS network to the EC2 instance on port 80. The Nginx Gateway container inside the instance routes this traffic to the appropriate service.

---

## Step-by-Step Deployment

### 1. Provision the EC2 Instance
- **AMI**: Ubuntu 24.04 LTS
- **Instance Type**: `t3.small` (Minimum 2GB RAM required for stable builds)
- **Security Group**:
  - Inbound: SSH (22) from your IP only.
  - Inbound: HTTP (80) restricted to the ALB security group.
  - Outbound: All traffic.

### 2. Install Docker
```bash
ssh ubuntu@<ec2-ip>
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker ubuntu && newgrp docker
```

### 3. Deploy Application
```bash
git clone https://github.com/kotalabhay/ai-assistant-backend
git clone https://github.com/kotalabhay/ai-assistant-ui ../ai-assistant-ui

cd ai-assistant-backend
cp .env.example .env
# Edit .env with production credentials
nano .env

docker compose up --build -d
```

### 4. Application Load Balancer (ALB) Setup
1.  **Target Group**: Create a target group using the 'Instances' type, Protocol: HTTP, Port: 80.
2.  **Health Check**: Set the path to `/api/v1/health`. Ensure the threshold is 2 healthy and 3 unhealthy.
3.  **ALB Creation**: Provision an Internet-facing ALB in the same VPC as the EC2.
4.  **Listeners**:
    - **HTTPS (443)**: Forward to the Target Group. Attach a certificate from AWS Certificate Manager (ACM).
    - **HTTP (80)**: Redirect to HTTPS (301).

---

## DNS and Edge Configuration

**Route 53**: Create an A record using the 'Alias' option. Point your domain (e.g., `api.example.com`) to the ALB's DNS name.

**Cloudflare (Optional)**:
1.  Set the CNAME record to the ALB and enable the Proxy (Orange Cloud).
2.  Set the SSL/TLS encryption mode to **Full** (this ensures encryption between Cloudflare and the ALB).
3.  Enable WAF rules to rate-limit the `/api/v1/query` endpoint if needed.

---

## Secrets Management

In this exercise, secrets are managed via a `.env` file on the EC2 disk. While acceptable for a transitionary phase, a production-grade deployment should utilize **AWS Secrets Manager**:
1.  Store API keys as encrypted secrets.
2.  Attach an IAM Instance Profile to the EC2 with read access to these specific secrets.
3.  Update the entrypoint script to pull values from Secrets Manager at runtime.

---

## Update Frequency and Maintenance

To redeploy the latest version from main:
```bash
cd ai-assistant-backend
git pull
cd ../ai-assistant-ui && git pull && cd ../ai-assistant-backend
docker compose up --build -d
```

---

## Architectural Rationale

This approach (EC2 + Docker Compose) was chosen over more complex alternatives like Kubernetes (EKS) or ECS for the following reasons:
- **Simplicity**: No overhead of managing control planes or complex ingress controllers.
- **Portability**: The exact environment used in development is replicated in production.
- **Cost Efficiency**: A single `t3.small` can handle the current workload without the cluster management overhead costs associated with EKS.
- **Speed of Recovery**: In the event of a failure, the entire stack can be rebuilt or moved to a different instance in minutes via simple git and docker commands.

For high-scale production, moving towards **AWS ECS Fargate** would be the logical next step to remove the burden of patching the underlying OS while maintaining a similar container-first mental model.
