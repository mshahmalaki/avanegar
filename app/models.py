from datetime import UTC, datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


def utc_now() -> datetime:
    return datetime.now(UTC)


class JobStatus(str, Enum):
    queued = "queued"
    processing = "processing"
    completed = "completed"
    failed = "failed"


class TranscriptWord(BaseModel):
    text: str
    start: float
    end: float
    confidence: float | None = None


class TranscriptSegment(BaseModel):
    id: int
    start: float
    end: float
    text: str
    speaker: str | None = None
    confidence: float | None = None
    uncertain: bool = False
    words: list[TranscriptWord] = Field(default_factory=list)


class TranscriptResult(BaseModel):
    text: str
    language: str = "fa"
    language_probability: float | None = None
    duration: float | None = None
    model: str
    segments: list[TranscriptSegment]
    warnings: list[str] = Field(default_factory=list)


class TranscriptionOptions(BaseModel):
    normalize: bool = True
    punctuation: bool = True
    word_timestamps: bool = True
    mark_uncertain: bool = True
    speaker_labels: bool = False


class TranscriptionJob(BaseModel):
    id: str
    filename: str
    content_type: str | None = None
    size_bytes: int
    status: JobStatus = JobStatus.queued
    progress: int = 0
    stage: str = "در صف پردازش"
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
    options: TranscriptionOptions = Field(default_factory=TranscriptionOptions)
    result: TranscriptResult | None = None
    error: str | None = None


class Capabilities(BaseModel):
    engine: Literal["faster-whisper", "demo"]
    model: str
    local_processing: bool = True
    streaming: bool = False
    word_timestamps: bool
    speaker_diarization: bool = False
    supported_formats: list[str]
    max_upload_mb: int
