"""Test TTS audio duration contract."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from video_director_v3.config import AUDIO_DURATION_MIN, AUDIO_DURATION_MAX


def test_audio_duration_contract_boundaries():
    """Test that audio duration boundaries are set correctly."""
    assert AUDIO_DURATION_MIN == 38.0
    assert AUDIO_DURATION_MAX == 43.0
    assert AUDIO_DURATION_MIN < AUDIO_DURATION_MAX


def test_audio_duration_contract_range():
    """Test that valid durations are in range."""
    valid_duration = 40.0
    assert AUDIO_DURATION_MIN <= valid_duration <= AUDIO_DURATION_MAX


def test_audio_duration_contract_too_short():
    """Test that too-short duration is rejected."""
    too_short = 30.0
    assert not (AUDIO_DURATION_MIN <= too_short <= AUDIO_DURATION_MAX)


def test_audio_duration_contract_too_long():
    """Test that too-long duration is rejected."""
    too_long = 50.0
    assert not (AUDIO_DURATION_MIN <= too_long <= AUDIO_DURATION_MAX)