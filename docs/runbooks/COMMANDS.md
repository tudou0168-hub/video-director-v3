# COMMANDS

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

## Smoke Render

```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved \
  --render-smoke-seconds 5 \
  --fps 25
```

## Full Render

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
cat outputs/demo_v3_preview/rendered/full_render_probe.json
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

---

最后更新：2026-05-30