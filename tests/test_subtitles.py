from avanegar.models import TranscriptSegment
from avanegar.services.subtitles import format_timestamp, segments_to_srt, segments_to_vtt


def sample_segments() -> list[TranscriptSegment]:
    return [
        TranscriptSegment(
            id=0,
            start=1.25,
            end=4.8,
            text="سلام دنیا.",
            speaker="گوینده ۱",
            confidence=0.91,
        )
    ]


def test_srt_timestamp() -> None:
    assert format_timestamp(3661.234) == "01:01:01,234"


def test_srt_export() -> None:
    output = segments_to_srt(sample_segments())
    assert "00:00:01,250 --> 00:00:04,800" in output
    assert "گوینده ۱: سلام دنیا." in output


def test_vtt_export() -> None:
    output = segments_to_vtt(sample_segments())
    assert output.startswith("WEBVTT")
    assert "00:00:01.250 --> 00:00:04.800" in output
