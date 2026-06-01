# COMMANDS

## P3 迁移提示

P3.1 已完成。当前主线：
- 不要将 `--target-duration 40` 视为产品约束。
- 不要使用旧 `combined/index.html` 作为新预览或新渲染验收依据。
- 使用自然语速男声，真实音频时长驱动 timeline。
- 长文先提炼：目标 `<=120s`，硬上限 `<=150s`；禁止通过加速 TTS 命中时长。
- 视觉基线沿用原 HUD 科技风。
- `render_mp4 --approved` 从 HyperFrames Studio Native 项目渲染，并生成 `sync_report.json`。
- `render_mp4` 只能在用户确认后执行，不允许中间阶段渲染。
- 如果是在做 cleanup 盘点，先产出 `docs/cleanup-plan.md`，不要直接删除。

新路线图：`docs/plans/V3_P3_VIRAL_VIDEO_ROADMAP.md`

## 环境启动

```bash
cd <PROJECT_ROOT>
source .venv/bin/activate
```

## Preview

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
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

这条命令只负责生成 `hyperframes_preview`，不生成 final MP4。

## HyperFrames Studio Native Preview

标准预览入口：
```
http://localhost:3002/#project/hyperframes_timeline
```

或者实际项目名对应的 URL：
```
http://localhost:3002/#project/<project_id>
```

Studio 审查标准：
1. Studio 是否正常加载项目
2. 是否有 scene / audio / caption / visual beats
3. 1080×1920 是否正确
4. 音频是否可播放
5. 字幕是否全程覆盖
6. visual beats 是否随时间切换
7. 是否无黑屏
8. 是否无内部调试词
9. 是否没有在用户确认前进入 render 阶段

## Smoke Render

前置条件：HyperFrames Studio 原生预览通过，且用户已确认可以进入渲染。

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved \
  --render-smoke-seconds 5 \
  --fps 25
```

## Full Render

前置条件：HyperFrames Studio 原生预览通过，`--approved` 已确认，且用户已确认可以进入渲染。

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved \
  --fps 25
```

## Tests

```bash
PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -v
```

## ffprobe final video

```bash
# 检查视频和音频 stream
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4

ffprobe -v error -select_streams a -show_entries stream=codec_type,sample_rate,channels,duration -of json <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4

ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,bit_rate,duration -of default=noprint_wrappers=1 <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4
```

## Extract audio from final_video

```bash
ffmpeg -i <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4 -map 0:a:0 -c copy /tmp/final_audio_check.aac
```

## Check audio content

```bash
ffmpeg -i /tmp/final_audio_check.aac -af "volumedetect" -f null /dev/null

ffmpeg -i <PROJECT_ROOT>/outputs/demo_v3_preview/audio/voiceover.mp3 -af "volumedetect" -f null /dev/null
```

## Compare voiceover and final_video audio

```bash
# voiceover.mp3 duration
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 <PROJECT_ROOT>/outputs/demo_v3_preview/audio/voiceover.mp3

# extracted audio duration
ffprobe -v error -show_entries format=duration,size -of default=noprint_wrappers=1 /tmp/final_audio_check.aac
```

## Check file timestamps (suspect silent_video overwrite)

```bash
ls -la outputs/demo_v3_preview/rendered/silent_video.mp4
ls -la outputs/demo_v3_preview/rendered/final_video.mp4
```

## Check render report

```bash
cat outputs/demo_v3_preview/rendered/render_report.json
cat outputs/demo_v3_preview/rendered/sync_report.json
```

## Clean frame cache (after render)

```bash
rm -rf <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/frames/
```

## Git

```bash
cd <PROJECT_ROOT>

# Check status
git status

# Check diff
git diff --stat

# Commit all changes (if needed)
git add -A
git commit -m "description"

# Push
git push
```

## Cleanup Plan

如果当前工作是清理盘点：

1. 先写 `docs/cleanup-plan.md`
2. 先写 `docs/archive/README.md`
3. 先做 A/B/C/D 分类
4. 等人工确认后，再进入清理执行阶段

不要在这个阶段直接删除文件。

---

最后更新：2026-06-01
