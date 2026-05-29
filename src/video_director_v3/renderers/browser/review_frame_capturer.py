"""Review frame capturer - captures screenshots from HTML at key timestamps."""
import asyncio
from pathlib import Path
from typing import List, Dict, Any


TIMESTAMPS = [0.5, 1.5, 3.0, 8.0, 15.0, 24.5, 25.0, 25.5, 35.0]


async def capture_review_frames(
    html_path: str,
    output_dir: str,
    timestamps: List[float] = TIMESTAMPS,
) -> List[Dict[str, Any]]:
    """Capture review frames from HTML at specified timestamps."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Stub - actual implementation uses Playwright
    return [{"timestamp": ts, "path": str(output_path / f"frame_{int(ts*1000):07d}.png")} for ts in timestamps]