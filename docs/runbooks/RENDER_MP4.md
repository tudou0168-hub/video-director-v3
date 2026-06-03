# Render MP4 Runbook

## 前置条件

只在以下条件都满足时运行：

- preview 已完成
- `approval_required.json` 允许审批
- contact sheet 已人工确认
- 用户明确说可以合成

## 标准命令

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id your_project_id \
  --output-mode render_mp4 \
  --approved \
  --fps 25
```

## 结果检查

运行后确认：

- `rendered/final_video.mp4` 存在
- 音频流存在
- 视频流存在
- `sync_status = PASS`

## 不要做的事

- 不要在 `hyperframes_preview` 阶段生成 MP4
- 不要把 `final_video.mp4` 提交到 GitHub
- 不要跳过人眼确认

