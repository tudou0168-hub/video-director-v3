"""Configuration for video-director-v3."""
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent.parent
DEFAULT_SAMPLES_DIR = PROJECT_ROOT / "samples"

# Design dial defaults
DEFAULT_DESIGN_VARIANCE = 7
DEFAULT_MOTION_INTENSITY = 6
DEFAULT_VISUAL_DENSITY = 8

# Audio-first contract
DEFAULT_EDGE_TTS_RATE = "+0%"
MAX_SYNC_DRIFT_SECONDS = 1.0
TARGET_NARRATION_SECONDS = 120.0
MAX_NARRATION_SECONDS = 150.0
TARGET_NARRATION_CHARS = 620

# P0 gate thresholds
INPUT_RELEVANCE_THRESHOLD = 0.7
MIN_CAPTION_BEATS_PER_SCENE = 2

# TTS defaults
DEFAULT_TTS_MODE = "edge_tts"
DEFAULT_TTS_FALLBACK = "system_say"
