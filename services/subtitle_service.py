import os
import json
from faster_whisper import WhisperModel


def extract_subtitles(
    media_path,
    output_format="srt",
    model_name="base",
    language="en"
):
    """
    Extract subtitles in a SINGLE format.
    Supported formats: srt, txt, vtt, json
    """
    model = WhisperModel(
        model_name,
        device="cpu",
        compute_type="int8",
        cpu_threads=6
    )
    segments, _ = model.transcribe(
        media_path,
        language=language,
        vad_filter=True
    )

    base = os.path.splitext(media_path)[0]
    output_path = f"{base}.{output_format}"

    if output_format == "srt":
        _write_srt(segments, output_path)
    elif output_format == "txt":
        _write_txt(segments, output_path)
    elif output_format == "vtt":
        _write_vtt(segments, output_path)
    elif output_format == "json":
        _write_json(segments, output_path)
    else:
        raise ValueError(f"Unsupported subtitle format: {output_format}")

    return output_path


def _write_srt(segments, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments, 1):
            f.write(f"{i}\n")
            f.write(f"{ts(seg.start)} --> {ts(seg.end)}\n")
            f.write(seg.text.strip() + "\n")

def _write_txt(segments, output_path):
    with open(output_path, "w", encoding="utf-8") as f:
        for seg in segments:
            f.write(seg.text.strip() + " ")

def _write_vtt(segments, path):
    with open(path, "w", encoding="utf-8") as f:
        f.write("WEBVTT\n\n")
        for seg in segments:
            f.write(f"{ts(seg.start)} --> {ts(seg.end)}\n")
            f.write(seg.text.strip() + "\n")

def _write_json(segments, path):
    data = [
        {"start": seg.start, "end": seg.end, "text": seg.text.strip()}
        for seg in segments
    ]
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def ts(t):
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t - int(t)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"
