# CloudSentinel AI 🛡️

> **Open-source Cloud Security Posture Management (CSPM) platform built on AWS.**  
> Real-time threat detection · MITRE ATT&CK enrichment · AI-powered analysis · Auto-remediation

[![AWS](https://img.shields.io/badge/AWS-Cloud%20Native-FF9900?logo=amazonaws&logoColor=white)](https://aws.amazon.com)
[![Terraform](https://img.shields.io/badge/IaC-Terraform-7B42BC?logo=terraform&logoColor=white)](https://www.terraform.io)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://www.python.org)
[![CI/CD](https://img.shields.io/badge/CI%2FCD-GitHub%20Actions%20OIDC-2088FF?logo=githubactions&logoColor=white)](https://github.com/features/actions)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## What is CloudSentinel?

CloudSentinel is a serverless CSPM dashboard that monitors your AWS environment for security misconfigurations and threats — in real time. It maps findings to the MITRE ATT&CK framework, enriches them with AI-powered analysis, and provides actionable remediation guidance from a single dashboard.

Built as a portfolio project demonstrating real-world Cloud Security and DevSecOps engineering practices.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     CloudSentinel AI                        │
│                                                             │
│   CloudTrail ──────────────────────────────────────────┐   │
│   GuardDuty  ──→  EventBridge  ──→  Lambda  ──→  API   │   │
│                                      │        Gateway  │   │
│                                      │                 │   │
│                              ┌───────▼────────┐        │   │
│                              │  MITRE ATT&CK  │        │   │
│                              │  Mapper        │        │   │
│                              │  Severity      │        │   │
│                              │  Classifier    │        │   │
│                              │  AI Analysis   │        │   │
│                              │  (Groq/Llama)  │        │   │
│                              └───────┬────────┘        │   │
│                                      │                 │   │
│                              S3 Static Dashboard ◄─────┘   │
└─────────────────────────────────────────────────────────────┘
```

**Infrastructure:** All resources provisioned via Terraform IaC, deployed via GitHub Actions with OIDC authentication (no long-lived credentials).

---

## Key Features

### 🔍 CloudTrail Detection Engine
Monitors critical AWS API calls and generates findings with severity, context, and remediation steps:

| API Event | Detection | Severity |
|-----------|-----------|----------|
| `StopLogging` | CloudTrail disabled | 🔴 Critical |
| `AuthorizeSecurityGroupIngress` | Security group opened to 0.0.0.0/0 | 🔴 Critical |
| `PutBucketAcl` | S3 bucket made public | 🟠 High |
| `RunInstances` | Unexpected EC2 launch | 🟡 Medium |
| `ConsoleLogin` | Root/unusual login detected | 🟡 Medium |

### 🧠 MITRE ATT&CK Enrichment
Maps every GuardDuty finding to a MITRE ATT&CK technique for attacker behavior context:

```
T1071   - Application Layer Protocol
T1562.008 - Disable Cloud Logs
T1078   - Valid Accounts (credential abuse)
T1190   - Exploit Public-Facing Application
```

### 🤖 AI-Powered Security Analysis
Groq LLM (Llama 3.1) explains each finding in plain English:
- **What happened** — human-readable event summary
- **Why it's dangerous** — business and security impact
- **Attacker objectives** — what the adversary is likely attempting
- **Immediate actions** — what to do right now
- **Remediation steps** — how to fix and prevent recurrence

### 🔧 Auto-Remediation
Lambda-based remediators automatically respond to common misconfigurations — reducing mean time to remediation.

### 📊 Security Dashboard
S3-hosted React dashboard with:
- Severity-based findings view
- MITRE ATT&CK technique tags
- CloudTrail detection feed
- AI investigation assistant

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Compute** | AWS Lambda (Python 3.11) |
| **Event Routing** | Amazon EventBridge |
| **Detection Sources** | AWS CloudTrail, Amazon GuardDuty |
| **Secrets** | AWS Secrets Manager |
| **Storage** | Amazon S3 (dashboard + Terraform state) |
| **API** | Amazon API Gateway |
| **IaC** | Terraform (remote state: S3 + DynamoDB lock) |
| **CI/CD** | GitHub Actions + OIDC (keyless auth) |
| **IaC Security** | Checkov |
| **AI** | Groq API / Llama 3.1 |
| **Language** | Python, HCL, HTML/JS |

---

## CI/CD Pipeline

```
git push
    │
    ▼
GitHub Actions (OIDC → AWS — no long-lived keys)
    │
    ├── Checkov IaC Security Scan
    ├── Terraform Plan
    └── Terraform Apply → AWS eu-north-1
```

OIDC-based authentication means **zero long-lived AWS credentials** stored in GitHub secrets.

---

## Repository Structure

```
Cloudsentinel-ai/
│
├── .github/
│   └── workflows/          # GitHub Actions CI/CD pipeline
│
├── backend/                # Lambda functions (detection + AI analysis)
├── frontend/               # S3-hosted security dashboard
├── infrastructure/         # Terraform IaC (VPC, Lambda, API GW, IAM)
├── scanners/               # CIS Benchmark security scanning modules
│
├── README.md
└── LICENSE
```

---

## Getting Started

### Prerequisites
- AWS Account with appropriate permissions
- Terraform >= 1.5
- Python 3.11+
- GitHub repository with Actions enabled

### Deploy

```bash
# 1. Clone the repo
git clone https://github.com/Raksbhat/Cloudsentinel-ai.git
cd Cloudsentinel-ai

# 2. Configure AWS credentials
aws configure

# 3. Initialize Terraform
cd infrastructure
terraform init

# 4. Deploy
terraform plan
terraform apply
```

CI/CD is fully automated — push to `main` triggers the GitHub Actions pipeline.

---

## Security Design Decisions

| Decision | Rationale |
|----------|-----------|
| OIDC for GitHub Actions | Eliminates long-lived credentials; tokens expire per job |
| Remote Terraform state | S3 backend with DynamoDB locking prevents state corruption |
| Secrets Manager for API keys | No hardcoded credentials anywhere in codebase |
| Least-privilege IAM | Each Lambda has scoped role; no wildcard `*` permissions |
| Checkov in CI | Catches IaC misconfigurations before they reach AWS |

---

## Roadmap

- [x] CloudTrail detection engine
- [x] MITRE ATT&CK enrichment
- [x] AI-powered analysis (Groq)
- [x] GitHub Actions CI/CD with OIDC
- [x] Remote Terraform state
- [x] Checkov IaC scanning
- [ ] AWS Security Hub integration
- [ ] EventBridge real-time detections
- [ ] Risk scoring engine
- [ ] Multi-account AWS support
- [ ] CIS AWS Benchmark v1.5 full compliance report

---

## Author

**Rakshit Bhat**  
Cloud Security Engineer | DevSecOps | AWS Security  

[![LinkedIn](https://img.shields.io/badge/LinkedIn-rakshit--bhat-0A66C2?logo=linkedin)](https://linkedin.com/in/rakshit-bhat)
[![GitHub](https://img.shields.io/badge/GitHub-Raksbhat-181717?logo=github)](https://github.com/Raksbhat)

---

## License

MIT License — see [LICENSE](LICENSE) for details.
