import asyncio

import httpx

from avanegar.main import app


def test_demo_transcription_flow(monkeypatch) -> None:
    monkeypatch.setenv("TRANSCRIBER_MODE", "demo")

    async def run_flow() -> None:
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://test",
            ) as client:
                health = await client.get("/api/health")
                assert health.status_code == 200

                capabilities = await client.get("/api/capabilities")
                assert capabilities.status_code == 200
                assert capabilities.json()["engine"] == "demo"

                upload = await client.post(
                    "/api/transcriptions",
                    files={"file": ("sample.wav", b"RIFF" + b"0" * 128, "audio/wav")},
                )
                assert upload.status_code == 202
                job_id = upload.json()["id"]

                job = await client.get(f"/api/transcriptions/{job_id}")
                assert job.json()["status"] == "completed"
                assert len(job.json()["result"]["segments"]) == 3

                subtitle = await client.get(f"/api/transcriptions/{job_id}/export/srt")
                assert subtitle.status_code == 200
                assert "-->" in subtitle.text

    asyncio.run(run_flow())


def test_unsupported_file_type_is_rejected(monkeypatch) -> None:
    monkeypatch.setenv("TRANSCRIBER_MODE", "demo")

    async def run_request() -> None:
        async with app.router.lifespan_context(app):
            transport = httpx.ASGITransport(app=app)
            async with httpx.AsyncClient(
                transport=transport,
                base_url="http://test",
            ) as client:
                response = await client.post(
                    "/api/transcriptions",
                    files={"file": ("notes.txt", b"not audio", "text/plain")},
                )
                assert response.status_code == 415

    asyncio.run(run_request())
