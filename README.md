#CloudSentinel AI

CloudSentinel AI is a serverless cloud security monitoring platform built on AWS. It combines cloud threat detection, MITRE ATT&CK enrichment, CloudTrail detection engineering, and AI-powered security analysis into a single dashboard.

Architecture

S3 Static Website
        │
        ▼
API Gateway
        │
        ▼
AWS Lambda
        │
        ├── GuardDuty Findings
        ├── MITRE ATT&CK Mapping
        ├── CloudTrail Detections
        └── AI Security Analysis (Groq)

Features

MITRE ATT&CK Enrichment

Maps GuardDuty findings to MITRE ATT&CK techniques to provide attacker behavior context.

Example:

- T1071 - Application Layer Protocol
- T1562.008 - Disable Cloud Logs
- T1078 - Valid Accounts

CloudTrail Detection Engine

Monitors critical AWS API activity:

- RunInstances
- StopLogging
- ConsoleLogin
- PutBucketAcl
- AuthorizeSecurityGroupIngress

Generates security findings with severity, title, and remediation context.

AI Security Analysis

Uses Groq LLMs to explain:

- What happened
- Why it is dangerous
- Attacker objectives
- Immediate actions
- Remediation steps

Security Dashboard

Provides:

- Severity-based findings
- MITRE ATT&CK tags
- CloudTrail detections
- AI-powered investigation assistance

Technology Stack

AWS

- AWS Lambda
- Amazon API Gateway
- Amazon S3
- AWS CloudTrail
- Amazon GuardDuty
- AWS Secrets Manager
- IAM

Development

- Python
- HTML
- JavaScript
- Git
- GitHub

Infrastructure

- Terraform

AI

- Groq API
- Llama 3.1

Repository Structure

Cloudsentinel-ai/
│
├── backend/          # Lambda backend
├── frontend/         # S3-hosted dashboard
├── infrastructure/   # Terraform IaC
├── scanners/         # Security scanning modules
├── README.md
└── LICENSE

Security Workflow

Cloud Security Event
          │
          ▼
GuardDuty / CloudTrail
          │
          ▼
CloudSentinel AI
          │
          ├── MITRE Mapping
          ├── Severity Classification
          └── AI Analysis
          │
          ▼
Security Dashboard

Key Capabilities

- Serverless architecture
- MITRE ATT&CK mapping
- CloudTrail detection engineering
- AI-assisted incident analysis
- Infrastructure as Code (Terraform)
- AWS-native security integrations

Future Enhancements

- Security Hub integration
- EventBridge-based real-time detections
- User attribution and investigation workflows
- Risk scoring engine
- Multi-account AWS support
- Automated remediation

Author

Rakshit Bhat

Cloud Security | DevSecOps | AWS Security

License

MIT License
