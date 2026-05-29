"""TTS adapter - handles text-to-speech with fallback."""
from typing import Dict, Any, Optional
import subprocess


def generate_tts(
    text: str,
    mode: str = "edge_tts",
    fallback: str = "system_say",
    output_path: Optional[str] = None,
) -> Dict[str, Any]:
    """Generate TTS audio."""
    return {
        "success": False,
        "error": "TTS not implemented - stub",
        "duration": 0.0,
    }


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                audio_path,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        return float(result.stdout.strip())
    except Exception:
        return 0.0