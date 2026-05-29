"""Configuration for video-director-v3."""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_SAMPLES_DIR = PROJECT_ROOT / "samples"

# Design dial defaults
DEFAULT_DESIGN_VARIANCE = 7
DEFAULT_MOTION_INTENSITY = 6
DEFAULT_VISUAL_DENSITY = 8

# Audio contract
AUDIO_DURATION_MIN = 38.0
AUDIO_DURATION_MAX = 43.0

# P0 gate thresholds
INPUT_RELEVANCE_THRESHOLD = 0.7
MIN_CAPTION_BEATS_PER_SCENE = 2

# TTS defaults
DEFAULT_TTS_MODE = "edge_tts"
DEFAULT_TTS_FALLBACK = "system_say"