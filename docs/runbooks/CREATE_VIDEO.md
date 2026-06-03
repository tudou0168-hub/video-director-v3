# Create Video Runbook

## 目的

把中文文案跑成 HyperFrames 预览，确认后再进入本地 MP4 渲染。

## 唯一主线

```text
script
→ TTS
→ real audio duration
→ captions
→ scene_pack / director timeline
→ HyperFrames native preview
→ review frames / contact sheet
→ human review
→ confirmed MP4 render
```

## 标准命令

### 1. 生成 preview

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --script /absolute/path/to/script.md \
  --platform douyin \
  --target-duration 40 \
  --project-id your_project_id \
  --output-mode hyperframes_preview \
  --tts-mode edge_tts \
  --tts-fallback system_say \
  --design-variance 7 \
  --motion-intensity 6 \
  --visual-density 8 \
  --no-allow-mock-audio
```

### 2. 检查 preview 产物

重点看：

- `outputs/<project_id>/scene_pack.json`
- `outputs/<project_id>/semantic_quality_report.json`
- `outputs/<project_id>/approval_required.json`
- `outputs/<project_id>/review_frames/contact-sheet.jpg`
- `outputs/<project_id>/hyperframes_timeline/index.html`

### 3. 用户确认后再 render MP4

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id your_project_id \
  --output-mode render_mp4 \
  --approved \
  --fps 25
```

## 什么时候允许 render MP4

必须同时满足：

- `approval_required.json` 显示 `can_approve_preview = true`
- `review_frames` / contact sheet 已人工看过
- 没有 hard fail
- 用户明确确认可以合成

## 为什么 MP4 不进 GitHub

MP4 是本地产物，只用于最终交付或人工验收，不应该作为源码提交内容。

