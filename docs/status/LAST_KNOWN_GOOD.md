# LAST KNOWN GOOD

## 可确认通过的能力

| 能力 | 状态 | 备注 |
|------|------|------|
| combined/index.html 生成 | PASS | 44KB，包含 GSAP timeline |
| TTS voiceover.mp3 | PASS | 40.92s，时长在 38-43s 合同范围内 |
| review_frames 7张 | PASS | 7/7 帧捕获成功 |
| approval_required.json | PASS | can_approve_preview=true |
| render_mp4 smoke | PASS | 5s smoke MP4 生成 |
| full render 生成 MP4 文件 | PASS | 40.92s MP4 文件存在 |
| hyperframes 预览播放 | PASS | HTML 可用 Play/Pause 控制 |
| 24 个单元测试 | PASS | 全部通过 |

## 不能算通过的

| 能力 | 状态 | 备注 |
|------|------|------|
| final_video.mp4 有声音 | **FAIL** | 用户反馈播放无声音，音频疑似损坏或 mux 错误 |
| clean render | FAIL | 调试控件、时间、HUD 被录入视频 |
| 字幕显示正确 | FAIL | 底部字幕被裁切 |
| frame cache 清理 | FAIL | 1023 张临时帧保留在输出目录 |

## 最近运行命令

### Preview
```bash
cd <PROJECT_ROOT>
source .venv/bin/activate
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

### Smoke Render
```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved \
  --render-smoke-seconds 5 \
  --fps 25
```

### Full Render
```bash
PYTHONPATH=src .venv/bin/python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved \
  --fps 25
```

### Tests
```bash
PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -v
```

### 诊断音频
```bash
ffprobe -v error -select_streams a:0 -show_entries stream=codec_name,sample_rate,channels,duration -of default=noprint_wrappers=1 <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4

ffmpeg -i <PROJECT_ROOT>/outputs/demo_v3_preview/rendered/final_video.mp4 -map 0:a:0 -c copy /tmp/final_audio_check.aac

ffmpeg -i /tmp/final_audio_check.aac -af "volumedetect" -f null /dev/null
```

## 最近 commit

| 时间 | Commit | 内容 |
|------|--------|------|
| 2026-05-29 | 05ae50d | Update .gitignore: add media file extensions |
| 2026-05-29 | 71f5386 | Initial commit: video-director-v3 project |
| 未 commit | — | 11 个文件 + 2 个新文件未提交 |

---

最后更新：2026-05-30