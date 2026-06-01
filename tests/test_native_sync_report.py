"""Test Native MP4 synchronization reporting."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.renderers.hyperframes.native_mp4_renderer import build_sync_report


def test_sync_report_passes_within_one_second():
    report = build_sync_report(
        audio_duration=61.2,
        video_duration=61.6,
        caption_end=61.0,
        scene_end=61.2,
        has_video=True,
        has_audio=True,
    )

    assert report["status"] == "PASS"
    assert report["checks"]["max_drift_seconds"] <= 1.0


def test_sync_report_fails_missing_audio_stream():
    report = build_sync_report(
        audio_duration=61.2,
        video_duration=61.2,
        caption_end=61.2,
        scene_end=61.2,
        has_video=True,
        has_audio=False,
    )

    assert report["status"] == "FAIL"
    assert "final video audio stream missing" in report["issues"]


def test_sync_report_fails_caption_drift():
    report = build_sync_report(
        audio_duration=61.2,
        video_duration=61.2,
        caption_end=58.0,
        scene_end=61.2,
        has_video=True,
        has_audio=True,
    )

    assert report["status"] == "FAIL"
    assert report["checks"]["caption_audio_drift_seconds"] > 1.0
