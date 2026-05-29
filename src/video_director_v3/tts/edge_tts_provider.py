"""Edge TTS provider."""
from typing import Dict, Any, Optional


async def generate_speech(
    text: str,
    output_path: str,
    voice: str = "zh-CN-XiaoxiaoNeural",
) -> Dict[str, Any]:
    """Generate speech using Edge TTS."""
    return {
        "success": False,
        "error": "Edge TTS not implemented - stub",
        "duration": 0.0,
    }