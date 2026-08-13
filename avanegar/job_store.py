import threading
from datetime import timedelta

from avanegar.models import TranscriptionJob, utc_now


class JobStore:
    def __init__(self, ttl_minutes: int) -> None:
        self._jobs: dict[str, TranscriptionJob] = {}
        self._lock = threading.RLock()
        self._ttl = timedelta(minutes=ttl_minutes)

    def set(self, job: TranscriptionJob) -> None:
        with self._lock:
            job.updated_at = utc_now()
            self._jobs[job.id] = job

    def get(self, job_id: str) -> TranscriptionJob | None:
        self.cleanup()
        with self._lock:
            return self._jobs.get(job_id)

    def delete(self, job_id: str) -> bool:
        with self._lock:
            return self._jobs.pop(job_id, None) is not None

    def cleanup(self) -> None:
        cutoff = utc_now() - self._ttl
        with self._lock:
            expired = [job_id for job_id, job in self._jobs.items() if job.updated_at < cutoff]
            for job_id in expired:
                del self._jobs[job_id]
