# Quickstart: Preview to MP4

## Prerequisites

```bash
cd <PROJECT_ROOT>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

## Step 1: Run Preview

```bash
python3 -m video_director_v3.cli \
  --script samples/scripts/minimal_obsidian_codex_hermes.md \
  --platform douyin \
  --target-duration 40 \
  --project-id demo_v3_preview \
  --output-mode hyperframes_preview \
  --tts-mode edge_tts \
  --tts-fallback system_say \
  --design-variance 7 \
  --motion-intensity 6 \
  --visual-density 8 \
  --no-allow-mock-audio
```

## Step 2: Inspect Preview

1. Open `outputs/demo_v3_preview/combined/index.html` in browser
2. Check `outputs/demo_v3_preview/review_frames/` for screenshots
3. Review `outputs/demo_v3_preview/approval_required.json`

## Step 3: Approve and Render

```bash
python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved
```

## Step 4: Find Final Video

```
outputs/demo_v3_preview/rendered/final_video.mp4
```