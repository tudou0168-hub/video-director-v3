# Agent Handoff — Codex

## 你适合做什么

Codex 适合做：
- 小范围代码修复
- 测试编写和运行
- 重构检查
- 单个文件修改

## 你不适合做什么

Codex **不得**：
- 大范围重写 pipeline
- 重构 pipeline_runner.py 的管线结构
- 修改 combined_html_builder 的 HTML 生成逻辑
- 大幅修改 tts_adapter.py 的 TTS 逻辑

## 当前可接手任务

### 任务 1：音频真实性检查

文件：`src/video_director_v3/quality/rendered_frame_inspector.py` 或新建

添加音频真实性检查，不只是检查 stream 是否存在，要验证：
- audio duration >= video duration * 0.9
- volumedetect mean_volume > -40dB
- 抽取出的 audio 文件非空

### 任务 2：Frame cache cleanup

文件：`src/video_director_v3/renderers/browser/browser_mp4_renderer.py`

在 full render 完成后删除 `frames/` 目录，或移到单独的 temp 目录。

### 任务 3：修复测试

如果有测试失败，修复测试代码。不要修改被测试的功能逻辑。

### 任务 4：诊断音频 mux 问题

检查 `browser_mp4_renderer.py` 中的 ffmpeg 命令，确认：
- 使用的 audio source 是哪个文件
- map 参数是否正确
- 是否用了正确的 audio stream

## 接手前必须读

1. `docs/status/PROJECT_STATE.md`
2. `docs/status/NEXT_TASK.md`
3. `docs/status/CURRENT_BUGS.md`

## 完成后更新

- `docs/status/TASK_LOG.md`
- `docs/status/CURRENT_BUGS.md`（如果 bug 状态变化）

---

最后更新：2026-05-30