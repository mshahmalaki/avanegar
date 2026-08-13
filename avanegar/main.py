import asyncio
import json
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Annotated
from uuid import uuid4

from fastapi import BackgroundTasks, FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, JSONResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles

from avanegar import __version__
from avanegar.config import get_settings
from avanegar.job_store import JobStore
from avanegar.models import (
    Capabilities,
    JobStatus,
    TranscriptionJob,
    TranscriptionOptions,
)
from avanegar.services.subtitles import segments_to_srt, segments_to_vtt
from avanegar.services.transcriber import DemoTranscriber, create_transcriber

settings = get_settings()
store = JobStore(settings.job_ttl_minutes)

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".ogg", ".webm", ".mp4", ".mpeg", ".flac"}
STATIC_DIR = Path(__file__).parent / "static"


@asynccontextmanager
async def lifespan(application: FastAPI):
    try:
        application.state.transcriber = create_transcriber(settings)
    except Exception:
        if settings.transcriber_mode != "auto":
            raise
        application.state.transcriber = DemoTranscriber(settings)
    yield


app = FastAPI(
    title="AvaNegar API",
    description="Privacy-first Persian voice transcription",
    version=__version__,
    lifespan=lifespan,
)


def update_job(job: TranscriptionJob, progress: int, stage: str) -> None:
    job.progress = progress
    job.stage = stage
    store.set(job)


async def process_audio(job_id: str, path: Path) -> None:
    job = store.get(job_id)
    if not job:
        path.unlink(missing_ok=True)
        return
    try:
        job.status = JobStatus.processing
        update_job(job, 10, "آماده‌سازی فایل صوتی")
        active_transcriber = getattr(app.state, "transcriber", None)
        if active_transcriber is None:
            raise RuntimeError("موتور رونویسی آماده نیست.")

        def progress_callback(progress: int, stage: str) -> None:
            update_job(job, progress, stage)

        if isinstance(active_transcriber, DemoTranscriber):
            job.result = active_transcriber.transcribe(path, job.options, progress_callback)
        else:
            job.result = await asyncio.to_thread(
                active_transcriber.transcribe,
                path,
                job.options,
                progress_callback,
            )
        job.status = JobStatus.completed
        update_job(job, 100, "رونویسی آماده است")
    except Exception as exc:
        job.status = JobStatus.failed
        job.error = str(exc)
        update_job(job, job.progress, "پردازش ناموفق بود")
    finally:
        path.unlink(missing_ok=True)


@app.get("/api/health")
async def health() -> dict:
    active_transcriber = getattr(app.state, "transcriber", None)
    return {
        "status": "ok",
        "engine": active_transcriber.name if active_transcriber else "loading",
    }


@app.get("/api/capabilities", response_model=Capabilities)
async def capabilities() -> Capabilities:
    active_transcriber = getattr(app.state, "transcriber", None)
    is_demo = isinstance(active_transcriber, DemoTranscriber) or active_transcriber is None
    return Capabilities(
        engine="demo" if is_demo else "faster-whisper",
        model="demo" if is_demo else settings.whisper_model,
        word_timestamps=not is_demo,
        supported_formats=sorted(SUPPORTED_EXTENSIONS),
        max_upload_mb=settings.max_upload_mb,
    )


@app.post("/api/transcriptions", status_code=202, response_model=TranscriptionJob)
async def create_transcription(
    background_tasks: BackgroundTasks,
    file: Annotated[UploadFile, File()],
    normalize: Annotated[bool, Form()] = True,
    punctuation: Annotated[bool, Form()] = True,
    word_timestamps: Annotated[bool, Form()] = True,
    mark_uncertain: Annotated[bool, Form()] = True,
    speaker_labels: Annotated[bool, Form()] = False,
) -> TranscriptionJob:
    original_name = Path(file.filename or "audio").name
    suffix = Path(original_name).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=415,
            detail="فرمت فایل پشتیبانی نمی‌شود.",
        )

    job_id = uuid4().hex
    destination = settings.temp_dir / f"{job_id}{suffix}"
    size = 0
    max_bytes = settings.max_upload_mb * 1024 * 1024
    try:
        with destination.open("wb") as target:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                if size > max_bytes:
                    raise HTTPException(
                        status_code=413,
                        detail=f"حجم فایل نباید بیشتر از {settings.max_upload_mb} مگابایت باشد.",
                    )
                target.write(chunk)
    except Exception:
        destination.unlink(missing_ok=True)
        raise
    finally:
        await file.close()

    if size == 0:
        destination.unlink(missing_ok=True)
        raise HTTPException(status_code=400, detail="فایل خالی است.")

    job = TranscriptionJob(
        id=job_id,
        filename=original_name,
        content_type=file.content_type,
        size_bytes=size,
        options=TranscriptionOptions(
            normalize=normalize,
            punctuation=punctuation,
            word_timestamps=word_timestamps,
            mark_uncertain=mark_uncertain,
            speaker_labels=speaker_labels,
        ),
    )
    store.set(job)
    background_tasks.add_task(process_audio, job_id, destination)
    return job


@app.get("/api/transcriptions/{job_id}", response_model=TranscriptionJob)
async def get_transcription(job_id: str) -> TranscriptionJob:
    job = store.get(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="رونویسی پیدا نشد یا منقضی شده است.")
    return job


@app.delete("/api/transcriptions/{job_id}", status_code=204)
async def delete_transcription(job_id: str):
    if not store.delete(job_id):
        raise HTTPException(status_code=404, detail="رونویسی پیدا نشد.")


@app.get("/api/transcriptions/{job_id}/export/{format_name}")
async def export_transcription(job_id: str, format_name: str):
    job = store.get(job_id)
    if not job or job.status != JobStatus.completed or not job.result:
        raise HTTPException(status_code=404, detail="خروجی آماده‌ای برای دریافت وجود ندارد.")

    headers = {"Content-Disposition": f'attachment; filename="transcript.{format_name}"'}
    if format_name == "txt":
        return PlainTextResponse(job.result.text, headers=headers, media_type="text/plain")
    if format_name == "srt":
        return PlainTextResponse(
            segments_to_srt(job.result.segments),
            headers=headers,
            media_type="application/x-subrip",
        )
    if format_name == "vtt":
        return PlainTextResponse(
            segments_to_vtt(job.result.segments),
            headers=headers,
            media_type="text/vtt",
        )
    if format_name == "json":
        return JSONResponse(
            json.loads(job.result.model_dump_json()),
            headers=headers,
        )
    raise HTTPException(status_code=400, detail="فرمت خروجی معتبر نیست.")


@app.get("/", include_in_schema=False)
async def index() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
