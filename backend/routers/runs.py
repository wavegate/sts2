from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from pydantic import BaseModel, ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlmodel import select as sqlmodel_select

import json
from auth import get_current_user_id_optional
from database import get_session
from models import Run, User
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


class UserOut(BaseModel):
    id: str


class RunResponse(BaseModel):
    """Run with optional user (owner). Supports single- and multiplayer runs."""

    model_config = {"from_attributes": True}

    user_id: str | None = None
    start_time: int = 0
    seed: str = ""
    build_id: str = ""
    schema_version: int = 0
    run_time: int = 0
    win: bool = False
    was_abandoned: bool = False
    killed_by_encounter: str = "NONE.NONE"
    killed_by_event: str = "NONE.NONE"
    character: str = ""
    ascension: int = 0
    game_mode: str = "standard"
    acts: list[str] | None = None
    modifiers: list[dict] | None = None
    platform_type: str | None = None
    deck_size: int = 0
    upgraded_card_count: int = 0
    relic_count: int = 0
    floor_reached: int = 0
    bosses_killed: int = 0
    map_point_counts: dict[str, int] | None = None
    deck: list[dict] | None = None
    relics: list[dict] | None = None
    players: list[dict] | None = None
    user: UserOut | None = None


@router.get("", response_model=list[RunResponse])
async def list_runs(
    session: AsyncSession = Depends(get_session),
) -> list[RunResponse]:
    """List all runs across users. Each run includes its owner (user) when present."""
    result = await session.execute(
        sqlmodel_select(Run)
        .options(selectinload(Run.user))
        .order_by(Run.start_time.desc())
    )
    runs = list(result.unique().scalars().all())
    return [
        RunResponse(
            **run.model_dump(exclude={"user"}),
            user=UserOut(id=run.user.id) if run.user else None,
        )
        for run in runs
    ]


@router.post("/upload", response_model=UploadRunsResponse)
async def upload_runs(
    files: list[UploadFile] = File(..., description="One or more .run files"),
    session: AsyncSession = Depends(get_session),
    user_id: str | None = Depends(get_current_user_id_optional),
) -> UploadRunsResponse:
    """
    Accept one or more .run files. Each is uploaded to S3 and ingested.
    Replaces an existing run with the same (start_time, seed) if present.
    If signed in, runs are associated with that user; otherwise anonymous.
    """
    runs: list[Run] = []
    errors: list[UploadError] = []

    for file in files:
        filename = file.filename or "(unnamed)"
        if not filename.lower().endswith(".run"):
            errors.append(UploadError(filename=filename,
                          detail="Only .run files are accepted"))
            continue
        try:
            contents = await file.read()
        except Exception as e:
            errors.append(UploadError(filename=filename,
                          detail="Failed to read file"))
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
            errors.append(UploadError(filename=filename,
                          detail=f"Invalid JSON: {e}"))
            continue
        except UnicodeDecodeError as e:
            errors.append(UploadError(filename=filename,
                          detail="File must be UTF-8"))
            continue

        if not isinstance(data, dict):
            errors.append(UploadError(filename=filename,
                          detail="File must be a JSON object"))
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

        if user_id is not None:
            existing_user = await session.get(User, user_id)
            if existing_user is None:
                session.add(User(id=user_id))
                await session.flush()

        try:
            run = run_from_dict(data, user_id)
        except KeyError as e:
            errors.append(UploadError(filename=filename,
                          detail=f"Invalid run file: missing {e}"))
            continue

        run = await ingest_run(session, run)
        await session.commit()
        await session.refresh(run)
        runs.append(run)

    return UploadRunsResponse(runs=runs, errors=errors)
