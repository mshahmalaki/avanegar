# Transcribe Persian voices

This project transcribes spoken Persian (Farsi) audio into accurate, readable text.

Its purpose is to make Persian voice content searchable, accessible, and easy to reuse across applications such as meeting transcription, voice notes, call-center analysis, subtitles, podcasts, and speech-enabled products.

## Core Principles

- **Persian-first accuracy:** Handle Persian phonetics, vocabulary, grammar, and common conversational forms carefully.
- **Robust real-world transcription:** Support varied accents, speaking speeds, background noise, recording quality, and informal speech.
- **Readable output:** Produce properly normalized Persian text with correct character forms, spacing, punctuation, and optional paragraph segmentation.
- **Context-aware processing:** Preserve the intended meaning where possible, including names, numbers, dates, technical terms, and mixed Persian–English speech.
- **Privacy by design:** Treat voice recordings and transcripts as sensitive data. Minimize retention, protect user data, and make processing behavior transparent.
- **Honest uncertainty:** Never silently invent words. When audio is unclear, expose confidence scores or mark uncertain segments when supported.
- **Developer-friendly integration:** Provide clean APIs, predictable outputs, useful metadata, and operational observability suitable for production systems.

## Expected Capabilities

- Transcribe Persian audio files and live/streaming audio.
- Detect speech segments and remove or ignore silence where appropriate.
- Optionally identify multiple speakers and timestamp each segment.
- Normalize Persian text, including Arabic/Persian character variants and spoken numbers.
- Support code-switching between Persian and English.
- Return timestamps, confidence information, language metadata, and structured transcript formats.
- Enable post-processing for punctuation, formatting, subtitle generation, and export.

## Non-Goals

This project should not present machine-generated transcripts as guaranteed verbatim legal, medical, or forensic records. Human review remains necessary when transcription accuracy has high-stakes consequences.

## Success

A successful transcription is not merely a sequence of recognized words. It should be understandable, faithful to the speaker’s intent, appropriately formatted for Persian readers, and reliable enough to be used confidently in real products.
