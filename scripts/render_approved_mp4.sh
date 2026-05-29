#!/bin/bash
# Render approved MP4

set -e

cd /Users/muzi/video-director-v3

python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved