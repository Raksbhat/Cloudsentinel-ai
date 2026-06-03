import json
import boto3
import urllib.request
import urllib.error
from datetime import datetime, timezone

MOCK_FINDINGS = [
    {"id": "mock-001", "title": "IAM User Performing Unusual API Activity", "severity": 8.0, "type": "UnauthorizedAccess:IAMUser/MaliciousIPCaller", "source": "GuardDuty", "timestamp": "2026-05-30T06:00:00Z", "description": "An IAM user is making API calls from a known malicious IP address."},
    {"id": "mock-002", "title": "EC2 Instance Communicating with C2 Server", "severity": 9.0, "type": "Backdoor:EC2/C2Activity.B", "source": "GuardDuty", "timestamp": "2026-05-30T07:00:00Z", "description": "An EC2 instance is communicating with a command and control server."},
    {"id": "mock-003", "title": "S3 Bucket Made Public", "severity": 7.0, "type": "Policy:S3/BucketPublicAccessGranted", "source": "CloudTrail", "timestamp": "2026-05-30T08:00:00Z", "description": "An S3 bucket ACL was changed to allow public access."},
    {"id": "mock-004", "title": "Root Account Console Login", "severity": 6.0, "type": "UnauthorizedAccess:IAMUser/ConsoleLoginSuccess", "source": "CloudTrail", "timestamp": "2026-05-30T09:00:00Z", "description": "Root account was used to log into the AWS console."},
    {"id": "mock-005", "title": "CloudTrail Logging Disabled", "severity": 9.5, "type": "Stealth:IAMUser/CloudTrailLoggingDisabled", "source": "GuardDuty", "timestamp": "2026-05-30T09:30:00Z", "description": "CloudTrail logging was disabled — possible attacker evasion."}
]
MITRE_MAPPING = {
    "Backdoor:EC2/C2Activity.B": {
        "id": "T1071",
        "technique": "Application Layer Protocol"
    },
    "UnauthorizedAccess:IAMUser/MaliciousIPCaller": {
        "id": "T1078",
        "technique": "Valid Accounts"
    },
    "Policy:S3/BucketPublicAccessGranted": {
        "id": "T1530",
        "technique": "Data from Cloud Storage"
    },
    "UnauthorizedAccess:IAMUser/ConsoleLoginSuccess": {
        "id": "T1078",
        "technique": "Valid Accounts"
    },
    "Stealth:IAMUser/CloudTrailLoggingDisabled": {
        "id": "T1562.008",
        "technique": "Disable Cloud Logs"
    },
    "Recon:IAMUser/NetworkPermissions": {
        "id": "T1595",
        "technique": "Active Scanning"
    },
    "Recon:IAMUser/UserPermissions": {
        "id": "T1069",
        "technique": "Permission Groups Discovery"
    },
    "CredentialAccess:IAMUser/AnomalousBehavior": {
        "id": "T1078",
        "technique": "Valid Accounts"
    },
    "Execution:EC2/RunInstances": {
        "id": "T1583.002",
        "technique": "Acquire Infrastructure - Virtual Private Server"
    },
    "Persistence:IAMUser/CreateAccessKey": {
        "id": "T1098",
        "technique": "Account Manipulation"
    },
    "Persistence:IAMUser/CreateUser": {
        "id": "T1136",
        "technique": "Create Account"
    },
    "DefenseEvasion:CloudTrail/StopLogging": {
        "id": "T1562.008",
        "technique": "Disable Cloud Logs"
    },
    "PrivilegeEscalation:IAMUser/AttachAdminPolicy": {
        "id": "T1098",
        "technique": "Account Manipulation"
    },
    "Discovery:EC2/DescribeInstances": {
        "id": "T1580",
        "technique": "Cloud Infrastructure Discovery"
    },
    "Discovery:S3/ListBuckets": {
        "id": "T1619",
        "technique": "Cloud Storage Discovery"
    },
    "Exfiltration:S3/GetObject": {
        "id": "T1537",
        "technique": "Transfer Data to Cloud Account"
    },
    "Impact:EC2/TerminateInstances": {
        "id": "T1485",
        "technique": "Data Destruction"
    },
    "LateralMovement:STS/AssumeRole": {
        "id": "T1078.004",
        "technique": "Cloud Accounts"
    },
    "Collection:S3/ListObjects": {
        "id": "T1530",
        "technique": "Data from Cloud Storage"
    },
    "Persistence:EC2/UserDataBackdoor": {
        "id": "T1053",
        "technique": "Scheduled Task/Job"
    }
}

def get_groq_api_key():
    try:
        sm = boto3.client("secretsmanager", region_name="eu-north-1")
        response = sm.get_secret_value(
            SecretId="cloudsentinel/groq-api-key"
        )
        return response["SecretString"], None
    except Exception as e:
        return None, str(e)

def explain_finding_with_ai(finding, api_key):
    try:
        prompt = f"""You are a cloud security expert. Analyze this AWS security finding and respond ONLY with valid JSON.

Finding: {finding.get('title')}
Type: {finding.get('type')}
Severity: {finding.get('severity')}/10
Description: {finding.get('description')}

Respond with exactly this JSON:
{{"what_happened":"plain english explanation","why_dangerous":"why this is dangerous","attacker_goal":"what attacker wants","immediate_action":"what to do now","remediation":["step1","step2","step3"]}}
"""

        payload = json.dumps({
            "model": "llama-3.1-8b-instant",
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.3,
            "max_tokens": 500
        }).encode("utf-8")

        req = urllib.request.Request(
    "https://api.groq.com/openai/v1/chat/completions",
    data=payload,
    headers={
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
)

        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

            content = result["choices"][0]["message"]["content"].strip()

            return json.loads(content), None

    except urllib.error.HTTPError as e:
        try:
            error_body = e.read().decode("utf-8")
            return None, f"GROQ_HTTP_ERROR: {error_body}"
        except:
            return None, f"GROQ_HTTP_ERROR: {e.code}"

    except Exception as e:
        return None, f"GROQ_EXCEPTION: {str(e)}"

def get_guardduty_findings():
    try:
        gd = boto3.client("guardduty", region_name="eu-north-1")

        detectors = gd.list_detectors()

        if detectors["DetectorIds"]:
            detector_id = detectors["DetectorIds"][0]

            response = gd.list_findings(
                DetectorId=detector_id,
                MaxResults=20
            )

            if response["FindingIds"]:
                details = gd.get_findings(
                    DetectorId=detector_id,
                    FindingIds=response["FindingIds"]
                )

                return [
                    {
                        "id": f["Id"],
                        "title": f["Title"],
                        "severity": f["Severity"],
                        "type": f["Type"],
                        "source": "GuardDuty",
                        "timestamp": f["UpdatedAt"],
                        "description": f.get("Description", "")
                    }
                    for f in details["Findings"]
                ]
    except Exception:
        pass

    return None
def enrich_with_mitre(findings):
    enriched = []

    for finding in findings:
        finding_copy = finding.copy()

        finding_copy["mitre"] = MITRE_MAPPING.get(
            finding.get("type"),
            {
                "id": "Unknown",
                "technique": "Unknown"
            }
        )

        enriched.append(finding_copy)

    return enriched

def handler(event, context):
    path = event.get("rawPath", "/")

    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }

    if path in ["/", ""]:
        body = {
            "status": "CloudSentinel AI is running",
            "version": "1.0.0"
        }

    elif path == "/health":
        body = {
            "status": "healthy",
            "timestamp": datetime.now(
                timezone.utc
            ).isoformat()
        }

    elif path == "/findings":
        real_findings = get_guardduty_findings()

        findings = real_findings if real_findings else MOCK_FINDINGS
        findings = enrich_with_mitre(findings)

        body = {
            "findings": findings,
            "total": len(findings),
            "source": "live" if real_findings else "demo"
        }

    elif path == "/explain":
        try:
            body_data = json.loads(
                event.get("body", "{}")
            )

            finding = body_data.get("finding", {})

            api_key, err = get_groq_api_key()

            if not api_key:
                body = {
                    "error": f"Could not get API key: {err}"
                }
            else:
                explanation, err = explain_finding_with_ai(
                    finding,
                    api_key
                )

                if err:
                    body = {
                        "error": err
                    }
                else:
                    body = {
                        "explanation": explanation,
                        "finding_id": finding.get("id")
                    }

        except Exception as e:
            body = {
                "error": str(e)
            }

    else:
        body = {
            "error": "Not found"
        }

    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(body)
    }
