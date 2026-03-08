from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select as sqlmodel_select

import json
from database import get_session
from models import Run
from run_ingest import ingest_run, run_from_dict
from schemas.run_upload import RunFileSchema
from s3_runs import upload_run_file_to_s3

router = APIRouter(prefix="/runs", tags=["runs"])

# Reject huge uploads (real .run files are typically hundreds of KB to a few MB)
RUN_FILE_MAX_BYTES = 15 * 1024 * 1024  # 15 MiB


class UploadError(BaseModel):
    filename: str
    detail: str


class UploadRunsResponse(BaseModel):
    runs: list[Run]
    errors: list[UploadError]


@router.get("", response_model=list[Run])
async def list_runs(
    session: AsyncSession = Depends(get_session),
) -> list[Run]:
    """List all runs, newest first."""
    result = await session.execute(
        sqlmodel_select(Run).order_by(Run.start_time.desc())
    )
    return list(result.scalars().all())


@router.post("/upload", response_model=UploadRunsResponse)
async def upload_runs(
    files: list[UploadFile] = File(..., description="One or more .run files"),
    session: AsyncSession = Depends(get_session),
) -> UploadRunsResponse:
    """
    Accept one or more .run files. Each is uploaded to S3 and ingested.
    Replaces an existing run with the same (start_time, seed) if present.
    Returns runs that succeeded and per-file errors for any that failed.
    """
    runs: list[Run] = []
    errors: list[UploadError] = []

    for file in files:
        filename = file.filename or "(unnamed)"
        if not filename.lower().endswith(".run"):
            errors.append(UploadError(filename=filename, detail="Only .run files are accepted"))
            continue
        try:
            contents = await file.read()
        except Exception as e:
            errors.append(UploadError(filename=filename, detail="Failed to read file"))
            continue

        if len(contents) > RUN_FILE_MAX_BYTES:
            errors.append(
                UploadError(
                    filename=filename,
                    detail=f"File too large (max {RUN_FILE_MAX_BYTES // (1024*1024)} MiB)",
                )
            )
            continue

        try:
            data = json.loads(contents.decode("utf-8"))
        except ValueError as e:
            errors.append(UploadError(filename=filename, detail=f"Invalid JSON: {e}"))
            continue
        except UnicodeDecodeError as e:
            errors.append(UploadError(filename=filename, detail="File must be UTF-8"))
            continue

        if not isinstance(data, dict):
            errors.append(UploadError(filename=filename, detail="File must be a JSON object"))
            continue

        try:
            RunFileSchema.model_validate(data)
        except ValidationError as e:
            errors.append(
                UploadError(
                    filename=filename,
                    detail=f"Schema validation failed: {e.errors()!r}",
                )
            )
            continue

        start_time = data["start_time"]
        seed = data.get("seed") or ""
        run_id = f"{start_time}_{seed.replace('/', '_').replace(' ', '_')}"

        await upload_run_file_to_s3(run_id, contents)

        try:
            run = run_from_dict(data)
        except KeyError as e:
            errors.append(UploadError(filename=filename, detail=f"Invalid run file: missing {e}"))
            continue

        run = await ingest_run(session, run)
        await session.commit()
        await session.refresh(run)
        runs.append(run)

    return UploadRunsResponse(runs=runs, errors=errors)
