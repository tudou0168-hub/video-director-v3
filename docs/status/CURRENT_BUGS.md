# CURRENT BUGS

## P0 — final_video.mp4 无声音（已暂停）

**状态**：本阶段暂停，不修复

**用户反馈**：
单独 voiceover.mp3 播放正常，但 final_video.mp4 播放无声音。

**技术观察**：
- `render_report.json` 报告 `final_video_has_audio_stream: true`
- `ffprobe` 显示 audio stream 存在：codec=aac, 24000Hz, mono, 40.92s
- `ffmpeg volumedetect` 显示 mean_volume=-24.5dB, max_volume=-2.5dB（音量极低但非零）
- 从 final_video.mp4 抽取的 audio 文件 duration=36.92s（视频 40.92s，不一致）
- 抽取后文件大小 453KB，时长 36.92s

**怀疑原因**（未确诊）：
1. final_video.mp4 被 silent_video.mp4 覆盖
2. ffmpeg mux 命令 map 错误导致 audio stream 无效
3. audio stream 存在但编码损坏
4. 抽取出的 audio 文件和最终 mux 的 audio 不是同一个
5. 渲染管线某处丢失了正确的 audio reference

**诊断命令**（供下一阶段使用）：

```bash
# 检查 final_video 音频 stream 详情
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,bit_rate,duration -of default=noprint_wrappers=1 <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4

# 抽取音频到独立文件验证
ffmpeg -i <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4 -map 0:a:0 -c copy /tmp/final_audio_check.aac

# 检查音频内容（应有声）
ffmpeg -i /tmp/final_audio_check.aac -af "volumedetect" -f null /dev/null

# 对比 voiceover.mp3 和 final_video 音频
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 <PROJECT_ROOT>/outputs/demo_v3_preview/audio/voiceover.mp3
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 /tmp/final_audio_check.aac

# 检查 silent_video.mp4 和 final_video.mp4 文件时间戳
ls -la <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/silent_video.mp4
ls -la <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4

# 检查 render_report 中记录的 audio source
cat <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/render_report.json
```

---

## P1 — 调试控件被录入视频

**问题**：0.0s / 40.9s 时间、HUD、S01 · hook、Play/Pause/Reset 按钮、进度条 被录入 final_video.mp4

**涉及元素**：
- `#combined-hud` — 左上角 scene label
- `#combined-time` — 右上角时间显示
- `#combined-progress` — 底部进度条
- `#combined-controls` — Play/Pause/Reset 按钮

**修复方向**：
- 在 browser_mp4_renderer 渲染前隐藏这些元素
- 或在 combined_html_builder 中添加 `data-render-mode="clean"` 属性

---

## P1 — 字幕被裁切

**问题**：底部字幕只露出右侧部分，`.caption-beat` 宽度或位置不正确

**涉及元素**：
- `#combined-captions` 固定在 bottom: 76px, left: 50%, transform: translateX(-50%)
- `.caption-beat` 宽度 860px，最小高度 80px

**修复方向**：
- 检查 `#combined-captions` 容器宽度是否正确
- 检查 `.caption-beat` 是否超出 #stage 边界

---

## P1 — 逐帧缓存污染输出目录

**问题**：full render 生成 1023 张图片在 `rendered/frames/`，不应作为正式输出

**文件路径**：`outputs/demo_v3_preview/rendered/frames/frame_000000.png` ~ `frame_1023000.png`

**修复方向**：
- 渲染完成后自动删除 frames/ 目录
- 或在 pipeline_runner 中添加 `--cleanup-frames` 选项
- 只保留 final_review_frames/

---

## P2 — 画面变化弱

**问题**：连续帧几乎无变化，motion storyboard 动效不足

**涉及**：
- GSAP entrance 动画只做了一次（from offscreen），后续无 motion
- 同一个 scene 内多帧内容相同

**修复方向**：
- 添加 per-beat 动效
- 添加 scene 内部 motion 循环
- 添加 motion validation 检测

---

最后更新：2026-05-30