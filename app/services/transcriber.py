import importlib.util
import math
import wave
from abc import ABC, abstractmethod
from collections.abc import Callable
from pathlib import Path
from typing import ClassVar

from app.config import Settings
from app.models import (
    TranscriptionOptions,
    TranscriptResult,
    TranscriptSegment,
    TranscriptWord,
)
from app.services.normalizer import ensure_punctuation, normalize_persian

ProgressCallback = Callable[[int, str], None]


class Transcriber(ABC):
    name: str

    @abstractmethod
    def transcribe(
        self,
        audio_path: Path,
        options: TranscriptionOptions,
        progress: ProgressCallback,
    ) -> TranscriptResult:
        raise NotImplementedError


class FasterWhisperTranscriber(Transcriber):
    name = "faster-whisper"

    def __init__(self, settings: Settings) -> None:
        from faster_whisper import WhisperModel

        self.settings = settings
        self.model = WhisperModel(
            settings.whisper_model,
            device=settings.whisper_device,
            compute_type=settings.whisper_compute_type,
        )

    def transcribe(
        self,
        audio_path: Path,
        options: TranscriptionOptions,
        progress: ProgressCallback,
    ) -> TranscriptResult:
        progress(20, "در حال تشخیص گفتار")
        segments_iterator, info = self.model.transcribe(
            str(audio_path),
            language="fa",
            beam_size=5,
            vad_filter=True,
            vad_parameters={"min_silence_duration_ms": 500},
            word_timestamps=options.word_timestamps,
            condition_on_previous_text=True,
        )
        segments: list[TranscriptSegment] = []
        duration = getattr(info, "duration", None) or 0

        for index, item in enumerate(segments_iterator):
            confidence = math.exp(item.avg_logprob) if item.avg_logprob is not None else None
            raw_text = item.text.strip()
            text = normalize_persian(raw_text) if options.normalize else raw_text
            if options.punctuation:
                text = ensure_punctuation(text)
            words = []
            if options.word_timestamps and item.words:
                words = [
                    TranscriptWord(
                        text=normalize_persian(word.word.strip())
                        if options.normalize
                        else word.word.strip(),
                        start=word.start,
                        end=word.end,
                        confidence=word.probability,
                    )
                    for word in item.words
                ]
            uncertain = (
                confidence is not None
                and confidence < self.settings.low_confidence_threshold
            )
            segments.append(
                TranscriptSegment(
                    id=index,
                    start=item.start,
                    end=item.end,
                    text=text,
                    speaker="گوینده ۱" if options.speaker_labels else None,
                    confidence=confidence,
                    uncertain=uncertain if options.mark_uncertain else False,
                    words=words,
                )
            )
            if duration:
                progress(min(88, 20 + int((item.end / duration) * 68)), "در حال تشخیص گفتار")

        progress(92, "در حال آماده‌سازی متن")
        full_text = "\n".join(segment.text for segment in segments)
        warnings = []
        if options.speaker_labels:
            warnings.append(
                "تفکیک خودکار گویندگان در این نسخه فعال نیست؛ همهٔ بخش‌ها با گوینده ۱ نمایش داده شده‌اند."
            )
        return TranscriptResult(
            text=full_text,
            language=getattr(info, "language", "fa"),
            language_probability=getattr(info, "language_probability", None),
            duration=duration or None,
            model=self.settings.whisper_model,
            segments=segments,
            warnings=warnings,
        )


class DemoTranscriber(Transcriber):
    """Deterministic sample output so the product can be explored without a model."""

    name = "demo"

    SAMPLE_SEGMENTS: ClassVar[tuple[tuple[str, float], ...]] = (
        (
            "سلام، این یک نمونه از آوانگار است؛ فضایی امن برای تبدیل صدای فارسی به متن خوانا.",
            0.92,
        ),
        (
            "در نسخهٔ محلی، فایل صوتی شما از دستگاه خارج نمی‌شود و پس از پردازش حذف خواهد شد.",
            0.87,
        ),
        (
            "برای رونویسی واقعی، بستهٔ faster-whisper و مدل مورد نظر را نصب کنید.",
            0.51,
        ),
    )

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    @staticmethod
    def _wav_duration(path: Path) -> float | None:
        try:
            with wave.open(str(path), "rb") as audio:
                return audio.getnframes() / audio.getframerate()
        except (wave.Error, EOFError, OSError):
            return None

    def transcribe(
        self,
        audio_path: Path,
        options: TranscriptionOptions,
        progress: ProgressCallback,
    ) -> TranscriptResult:
        progress(35, "اجرای حالت نمایشی")
        duration = self._wav_duration(audio_path) or 18.0
        segment_length = max(2.0, duration / len(self.SAMPLE_SEGMENTS))
        segments = []
        for index, (sample, confidence) in enumerate(self.SAMPLE_SEGMENTS):
            text = normalize_persian(sample) if options.normalize else sample
            if options.punctuation:
                text = ensure_punctuation(text)
            start = index * segment_length
            end = min(duration, (index + 1) * segment_length)
            segments.append(
                TranscriptSegment(
                    id=index,
                    start=start,
                    end=max(start + 0.5, end),
                    text=text,
                    speaker="گوینده ۱" if options.speaker_labels else None,
                    confidence=confidence,
                    uncertain=(
                        options.mark_uncertain
                        and confidence < self.settings.low_confidence_threshold
                    ),
                )
            )
            progress(45 + index * 18, "ساخت رونویسی نمونه")
        return TranscriptResult(
            text="\n".join(segment.text for segment in segments),
            language="fa",
            language_probability=1.0,
            duration=duration,
            model="demo",
            segments=segments,
            warnings=[
                "این خروجی نمایشی است و از محتوای فایل صوتی استخراج نشده است. برای رونویسی واقعی، موتور Whisper را نصب کنید."
            ],
        )


def create_transcriber(settings: Settings) -> Transcriber:
    whisper_available = importlib.util.find_spec("faster_whisper") is not None
    if settings.transcriber_mode == "demo":
        return DemoTranscriber(settings)
    if settings.transcriber_mode == "whisper" and not whisper_available:
        raise RuntimeError(
            "TRANSCRIBER_MODE روی whisper است، اما faster-whisper نصب نشده است."
        )
    if whisper_available:
        return FasterWhisperTranscriber(settings)
    return DemoTranscriber(settings)
