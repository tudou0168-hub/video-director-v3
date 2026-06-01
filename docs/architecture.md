# Architecture

## Overview

V3 唯一产品主线：
```
中文文案
  → AI 导演解析（narration_planner + classify_role）
  → 视觉设计规范（scene_protocol + 30 模板库）
  → HyperFrames Studio 原生项目（studio_native_project_builder）
  → 用户确认（浏览器人眼验收 hyperframes_timeline/index.html）
  → MP4 视频（render_mp4 + audio mux）
```

**这是 V3 唯一允许的主线。任何新需求、任何改造、任何"捷径"，都必须能落到这条主线的某一步上。**

管线命令视角：
```
script.md → hyperframes_preview → approval_required.json → render_mp4 → final_video.mp4
```

## Directory Structure

```
video-director-v3/
├── outputs/                    # Formal project outputs
│   └── <project_id>/
│       ├── hyperframes_timeline/index.html
│       ├── review_frames/
│       ├── rendered/
│       └── ...
├── test_outputs/               # Test outputs
│   └── <project_id>/
├── src/video_director_v3/
│   ├── cli.py                  # Entry point
│   ├── config.py               # Configuration
│   ├── pipeline/               # Pipeline orchestration
│   ├── director/                # AI Director modules
│   ├── design/                 # Design Profile modules
│   ├── tts/                    # TTS modules
│   ├── motion/                 # Motion planning modules
│   ├── renderers/              # HTML and browser renderers
│   ├── quality/                # Quality checking
│   └── exporters/               # Approval gate
└── samples/scripts/             # Sample inputs
```

## Key Design Principles

1. **Unified output directories**: outputs/ and test_outputs/ only
2. **No src/outputs**: All outputs go through project_paths.py
3. **Two modes**: hyperframes_preview and render_mp4
4. **Approval gate**: render_mp4 requires --approved flag
5. **Design Profile layer**: Skills integrate as design adapters, not pipeline replacements