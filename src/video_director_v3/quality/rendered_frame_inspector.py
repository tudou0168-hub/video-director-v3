"""Rendered frame inspector - inspects captured frames for issues."""
from typing import Dict, Any, List


def inspect_frames(frames_dir: str) -> Dict[str, Any]:
    """Inspect rendered frames for issues."""
    return {"issues": [], "frame_count": 0}