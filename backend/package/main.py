import json
import boto3
from datetime import datetime, timezone

def get_findings():
    findings = []
    try:
        gd = boto3.client("guardduty", region_name="eu-north-1")
        detectors = gd.list_detectors()
        if detectors["DetectorIds"]:
            detector_id = detectors["DetectorIds"][0]
            response = gd.list_findings(DetectorId=detector_id, MaxResults=20)
            if response["FindingIds"]:
                details = gd.get_findings(
                    DetectorId=detector_id,
                    FindingIds=response["FindingIds"]
                )
                for f in details["Findings"]:
                    findings.append({
                        "id": f["Id"],
                        "title": f["Title"],
                        "severity": f["Severity"],
                        "type": f["Type"],
                        "source": "GuardDuty"
                    })
    except Exception as e:
        findings.append({
            "id": "error",
            "title": str(e),
            "severity": 0,
            "type": "ERROR",
            "source": "System"
        })
    return findings

def handler(event, context):
    path = event.get("rawPath", "/")
    
    headers = {
        "Content-Type": "application/json",
        "Access-Control-Allow-Origin": "*"
    }
    
    if path == "/" or path == "":
        body = {"status": "CloudSentinel AI is running", "version": "1.0.0"}
    elif path == "/health":
        body = {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}
    elif path == "/findings":
        findings = get_findings()
        body = {"findings": findings, "total": len(findings)}
    else:
        body = {"error": "Not found"}
    
    return {
        "statusCode": 200,
        "headers": headers,
        "body": json.dumps(body)
    }
