from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import boto3
import json
from datetime import datetime, timezone

app = FastAPI(
    title="CloudSentinel AI",
    description="AI-powered Cloud Security Platform",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "CloudSentinel AI is running"}

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

@app.get("/findings")
def get_findings():
    """Get security findings from GuardDuty and CloudTrail"""
    findings = []
    
    try:
        # GuardDuty findings
        gd = boto3.client("guardduty", region_name="eu-north-1")
        detectors = gd.list_detectors()
        
        if detectors["DetectorIds"]:
            detector_id = detectors["DetectorIds"][0]
            response = gd.list_findings(
                DetectorId=detector_id,
                FindingCriteria={
                    "Criterion": {
                        "severity": {"Gte": 4}
                    }
                },
                MaxResults=20
            )
            
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
                        "source": "GuardDuty",
                        "timestamp": f["UpdatedAt"]
                    })
    except Exception as e:
        findings.append({
            "id": "error-gd",
            "title": f"GuardDuty not enabled: {str(e)}",
            "severity": 0,
            "type": "ERROR",
            "source": "System",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
    
    return {"findings": findings, "total": len(findings)}
