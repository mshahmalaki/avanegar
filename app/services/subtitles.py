from app.models import TranscriptSegment


def format_timestamp(seconds: float, separator: str = ",") -> str:
    milliseconds = max(0, round(seconds * 1000))
    hours, remainder = divmod(milliseconds, 3_600_000)
    minutes, remainder = divmod(remainder, 60_000)
    secs, millis = divmod(remainder, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02}{separator}{millis:03}"


def segments_to_srt(segments: list[TranscriptSegment]) -> str:
    blocks = []
    for index, segment in enumerate(segments, start=1):
        speaker = f"{segment.speaker}: " if segment.speaker else ""
        blocks.append(
            f"{index}\n"
            f"{format_timestamp(segment.start)} --> {format_timestamp(segment.end)}\n"
            f"{speaker}{segment.text}"
        )
    return "\n\n".join(blocks) + ("\n" if blocks else "")


def segments_to_vtt(segments: list[TranscriptSegment]) -> str:
    blocks = ["WEBVTT"]
    for segment in segments:
        speaker = f"<v {segment.speaker}>" if segment.speaker else ""
        blocks.append(
            f"{format_timestamp(segment.start, '.')} --> {format_timestamp(segment.end, '.')}\n"
            f"{speaker}{segment.text}"
        )
    return "\n\n".join(blocks) + "\n"

