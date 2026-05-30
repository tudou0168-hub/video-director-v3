# NEXT TASK

## 当前任务

**V3-D2.0-A Fix Final MP4 Audio Mux**

## 目标

修复 final_video.mp4 无声音问题。

用户反馈：
- 单独 voiceover.mp3 播放正常
- final_video.mp4 播放无声音
- render_report.json 报告 audio stream 存在，但实际播放异常

## 验收标准

修复完成后必须满足：

1. `ffprobe -select_streams a` 在 final_video.mp4 上有输出
2. 从 final_video.mp4 抽取的 audio 时长 >= 视频时长 * 0.9
3. `ffmpeg volumedetect` mean_volume > -40dB（非静音）
4. render_report.json 增加 `audio_truth_status: PASS`
5. 用户实际播放 final_video.mp4 能听到声音

## 当前禁止

- 不要做视觉优化
- 不要做 D2.1（clean render）
- 不要改 TTS
- 不要改字幕
- 不要重构 pipeline
- 不要新增视觉组件
- 不要做 motion validation
- 不要改变 approval gate 逻辑
- **不要改 browser_mp4_renderer 的 mux 逻辑以外的代码**（见约束）

## 约束

根据用户明确要求：
- 不修改 browser_mp4_renderer 的 mux 逻辑
- 不修改视频渲染逻辑
- 不修改 TTS

**仅允许**：
- 诊断问题根因
- 在 render_report 或 quality_report 中增加音频真实性检查
- 修改 mux 命令参数（如果问题是参数错误）
- 清理无效的 frame cache

## 下一步骤

1. 运行 CURRENT_BUGS.md 中的诊断命令
2. 确认 audio mux 问题根因
3. 修复后重新渲染
4. 验证音频真实性
5. 更新 PROJECT_STATE.md / CURRENT_BUGS.md / LAST_KNOWN_GOOD.md

---

最后更新：2026-05-30