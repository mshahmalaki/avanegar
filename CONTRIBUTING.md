# Contributing to AvaNegar

Thank you for helping improve Persian speech technology.

## Development setup

```bash
git clone https://github.com/mshahmalaki/avanegar.git
cd avanegar
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
```

Run the application in deterministic demo mode:

```bash
TRANSCRIBER_MODE=demo avanegar --reload
```

To work on real transcription, install the optional engine:

```bash
python -m pip install -e ".[dev,whisper]"
```

## Before opening a pull request

```bash
make lint
make test
make package
docker build -t avanegar:local .
```

Keep changes focused, add tests for new behavior, and update the English and
Persian README sections together when user-facing behavior changes.

Do not commit audio recordings, transcripts, model weights, secrets, or `.env`
files.

## Pull requests

- Explain the problem and the chosen solution.
- Link related issues.
- Include screenshots for visible interface changes.
- Call out privacy, compatibility, or model-performance implications.

## Releasing

Maintainers should:

1. Update `project.version` in `pyproject.toml`.
2. Update `CHANGELOG.md`.
3. Ensure all required checks pass on `main`.
4. Create and push a matching tag, such as `v0.2.0`.
5. Create a non-prerelease GitHub Release from that tag.

The tag publishes the Docker image to GHCR. Publishing the GitHub Release starts
the Trusted Publishing workflow for PyPI. The PyPI project must have a trusted
publisher configured for repository `mshahmalaki/avanegar`, workflow
`publish-pypi.yml`, and environment `pypi`.

