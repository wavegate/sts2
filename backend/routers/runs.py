from fastapi import APIRouter, Depends, HTTPException, UploadFile
from pydantic import ValidationError
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


@router.get("", response_model=list[Run])
async def list_runs(
    session: AsyncSession = Depends(get_session),
) -> list[Run]:
    """List all runs, newest first."""
    result = await session.execute(
        sqlmodel_select(Run).order_by(Run.start_time.desc())
    )
    return list(result.scalars().all())


@router.post("/upload", response_model=Run)
async def upload_run(
    file: UploadFile,
    session: AsyncSession = Depends(get_session),
) -> Run:
    """
    Accept a .run file only. Uploads the file to S3, then ingests into the database.
    Replaces an existing run with the same start_time (id) if present.
    """
    if not file.filename or not file.filename.lower().endswith(".run"):
        raise HTTPException(
            status_code=400,
            detail="Only .run files are accepted",
        )
    try:
        contents = await file.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Failed to read file") from e

    if len(contents) > RUN_FILE_MAX_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File too large (max {RUN_FILE_MAX_BYTES // (1024*1024)} MiB)",
        )

    try:
        data = json.loads(contents.decode("utf-8"))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}") from e
    except UnicodeDecodeError as e:
        raise HTTPException(status_code=400, detail="File must be UTF-8") from e

    if not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="File must be a JSON object")

    try:
        RunFileSchema.model_validate(data)
    except ValidationError as e:
        raise HTTPException(
            status_code=400,
            detail={"message": "Run file does not match schema", "errors": e.errors()},
        ) from e

    start_time = data["start_time"]
    seed = data.get("seed") or ""
    run_id = f"{start_time}_{seed.replace('/', '_').replace(' ', '_')}"

    # Upload file to S3 first (key: runs/{start_time}_{seed}.run)
    await upload_run_file_to_s3(run_id, contents)

    try:
        run = run_from_dict(data)
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Invalid run file: missing {e}") from e

    run = await ingest_run(session, run)
    await session.commit()
    await session.refresh(run)

    return run
