# P3.12B + P3.12C MP4 Trial Plan

## 本阶段目标

基于 `outputs/v3_p311c_sales_repair_preview/` 做一次本地 MP4 trial，验证 sales 候选片是否具备进入发布前最终确认的质量。

## 候选片路径

- `outputs/v3_p311c_sales_repair_preview/`

## Render 前置条件

- `approval_required.json` 存在且为 `READY`
- `semantic_quality_report.json` 无 hard fail
- `scene_pack.json` 存在
- `hyperframes_timeline/index.html` 存在
- `hyperframes_timeline/data/director_timeline.json` 存在
- `hyperframes_timeline/assets/voiceover.mp3` 存在
- `review_frames/contact-sheet.jpg` 存在

## Render 命令

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id v3_p311c_sales_repair_preview \
  --output-mode render_mp4 \
  --approved \
  --fps 25
```

## MP4 QA 项

- 文件存在性
- 文件大小
- duration 是否接近真实 TTS / timeline
- 是否有音频流
- 是否黑屏
- 是否 9:16
- 是否有明显卡顿
- 字幕是否覆盖全程
- 字幕是否遮挡主体
- hook 前 3 秒是否可读
- CTA 是否完整
- contact sheet 与 MP4 是否一致

## 允许小修范围

- 仅允许针对 sales 候选片做轻量修正
- 可小改 `semantic_planner.py`
- 可小改 `publish_templates.py`
- 可补对应小测试
- 不扩模板，不改 renderer，不改主线协议

## 禁止事项

- 不提交任何 MP4
- 不提交 `outputs/` 或 `renders/`
- 不提交 `contact-sheet.jpg`
- 不提交 `final_video.mp4`
- 不改 HyperFrames renderer
- 不改 playback / seek / audio.timeupdate / window.__hf
- 不把 `narrative_compressor.py` 接入主线

## 验收标准

- sales MP4 本地生成成功
- MP4 有声音
- MP4 不黑屏
- 时长合理
- 字幕可接受
- 结尾 CTA 出现
- 没有 renderer 改写
- 没有模板大扩张
- 没有提交 outputs/renders/MP4
