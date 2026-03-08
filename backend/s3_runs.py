"""
Upload run files to S3.

Env (all optional for S3; if unset, upload is skipped):
  - S3_BUCKET_RUNS: S3 bucket name (e.g. my-app-runs). Required for S3 upload.
  - AWS_REGION: AWS region (e.g. us-east-1). Required for S3 upload.

Credentials: aioboto3 uses the default chain (~/.aws/credentials, IAM role, etc.).
"""
from __future__ import annotations

import os
from typing import Optional

import aioboto3
from botocore.exceptions import ClientError


async def upload_run_file_to_s3(run_id: str, body: bytes) -> Optional[str]:
    """
    Upload run file bytes to S3 at runs/{run_id}.run (async, no threads).
    run_id should be "{start_time}_{seed}" (seed sanitized for S3 key).
    Returns the S3 key if uploaded, None if S3 not configured or on error.
    """
    bucket = os.environ.get("S3_BUCKET_RUNS")
    region = os.environ.get("AWS_REGION")
    if not bucket or not region:
        return None
    # Sanitize for S3 object key (alphanumeric, -, _, ., and / only in prefixes)
    safe_id = run_id.replace("\\", "_").replace(" ", "_")
    key = f"runs/{safe_id}.run"
    try:
        session = aioboto3.Session()
        async with session.client("s3", region_name=region) as client:
            await client.put_object(
                Bucket=bucket,
                Key=key,
                Body=body,
                ContentType="application/json",
            )
        return key
    except ClientError:
        return None
