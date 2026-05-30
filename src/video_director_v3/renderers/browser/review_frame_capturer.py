#!/usr/bin/env python3
"""Real review frame capturer using Playwright — migrated from V2."""
from __future__ import annotations

import asyncio
import json
from pathlib import Path
from typing import Any


TIMESTAMPS = [0.5, 1.5, 3.0, 8.0, 15.0, 25.0, 35.0]
MIN_FRAME_SIZE = 5000  # bytes


async def _capture_single_frame(
    page,
    ts: float,
    output_dir: Path,
) -> dict[str, Any]:
    ts_int = int(ts * 1000)
    frame_name = f"frame_{ts_int:07d}.png"
    output_path = output_dir / frame_name

    # Seek and pause
    await page.evaluate(f"""
        () => {{
            const master = window.__timelines["combined"];
            if (!master) throw new Error("No timeline found");
            master.seek({ts});
            master.pause();
        }}
    """)

    # Wait for render
    await page.wait_for_timeout(2000)

    # Screenshot
    await page.screenshot(path=str(output_path), full_page=False)

    exists = output_path.exists()
    size = output_path.stat().st_size if exists else 0

    return {
        "timestamp": ts,
        "frame_name": frame_name,
        "path": str(output_path),
        "exists": exists,
        "size": size,
        "status": "OK" if (exists and size >= MIN_FRAME_SIZE) else "FAIL",
    }


async def capture_review_frames(
    html_path: str,
    output_dir: str,
    timestamps: list[float] | None = None,
) -> dict[str, Any]:
    """Capture review frames from combined/index.html at specified timestamps.

    Uses Playwright to open the HTML, seek to each timestamp using
    window.__timelines["combined"].seek(ts), and capture a screenshot.

    Returns a dict with capture results for each timestamp and overall status.
    """
    if timestamps is None:
        timestamps = TIMESTAMPS

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    frames = []

    try:
        async with asyncio.timeout(120):
            from playwright.async_api import async_playwright

            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                page = await browser.new_page(viewport={"width": 1080, "height": 1920})

                html_file = Path(html_path)
                if not html_file.exists():
                    return {
                        "status": "FAIL",
                        "error": f"HTML file not found: {html_path}",
                        "frames": [],
                    }

                await page.goto(
                    f"file://{html_file.absolute()}",
                    wait_until="domcontentloaded",
                    timeout=30000,
                )
                # Wait for GSAP to boot and register the combined timeline
                # The HTML uses network-heavy external fonts, so we poll for the JS variable
                await page.wait_for_timeout(5000)

                timeline_exists = await page.evaluate("""
                    () => !!(window.__timelines && window.__timelines["combined"])
                """)
                if not timeline_exists:
                    return {
                        "status": "FAIL",
                        "error": "window.__timelines['combined'] not found",
                        "frames": [],
                    }

                for ts in timestamps:
                    frame_result = await _capture_single_frame(page, ts, output_path)
                    frames.append(frame_result)

                await browser.close()

    except asyncio.TimeoutError:
        return {
            "status": "FAIL",
            "error": "Capture timed out after 120s",
            "frames": frames,
        }
    except Exception as e:
        return {
            "status": "FAIL",
            "error": str(e),
            "frames": frames,
        }

    # Evaluate overall status
    ok_frames = [f for f in frames if f["status"] == "OK"]
    all_ok = len(ok_frames) >= 7 and all(f["status"] == "OK" for f in frames)

    return {
        "status": "PASS" if all_ok else "FAIL",
        "frames": frames,
        "ok_count": len(ok_frames),
        "total_count": len(frames),
        "output_dir": str(output_path),
    }


def write_capture_results(
    result: dict[str, Any],
    output_dir: Path,
) -> None:
    """Write capture results JSON and a summary."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write detailed results
    result_file = output_dir / "capture_result.json"
    result_file.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Write summary markdown
    lines = [
        f"# Review Frame Capture Report",
        "",
        f"- Status: **{result['status']}**",
        f"- OK frames: {result.get('ok_count', 0)} / {result.get('total_count', 0)}",
        f"- Output: `{result.get('output_dir', '')}`",
        "",
    ]
    if result.get("error"):
        lines.extend(["", f"## Error", "", f"```\n{result['error']}\n```", ""])

    lines.extend(["", "## Frame Details", ""])
    for f in result.get("frames", []):
        status_icon = "✅" if f["status"] == "OK" else "❌"
        lines.append(
            f"- {status_icon} `{f['frame_name']}` — {f['timestamp']}s — {f['size']} bytes"
        )

    (output_dir / "capture_report.md").write_text("\n".join(lines), encoding="utf-8")


def validate_frames(output_dir: Path, min_size: int = 5000) -> dict[str, Any]:
    """Validate that all expected frames exist and are non-empty."""
    results = {}
    all_ok = True

    for ts in TIMESTAMPS:
        ts_int = int(ts * 1000)
        frame_name = f"frame_{ts_int:07d}.png"
        frame_path = output_dir / frame_name

        exists = frame_path.exists()
        size = frame_path.stat().st_size if exists else 0
        ok = exists and size >= min_size

        # Check for black/empty frames (size < 10KB is suspicious for 1080x1920)
        if exists and size < 10000:
            ok = False

        results[frame_name] = {
            "exists": exists,
            "size": size,
            "ok": ok,
        }
        if not ok:
            all_ok = False

    return {"all_ok": all_ok, "frames": results}