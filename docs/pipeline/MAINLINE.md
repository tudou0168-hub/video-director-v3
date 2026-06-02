# Mainline Pipeline

This document defines the canonical production path for `video-director-v3`.

## Strict flow

```text
中文文案
  -> 爆款结构化口播 / AI 导演解析
  -> 自然语速男声 TTS
  -> 真实音频时长
  -> 动态字幕 / 动态分镜 / 自然转场
  -> HyperFrames Studio Native Preview
  -> 用户确认
  -> render_mp4 + audio mux
  -> final_video.mp4
```

## Command-level flow

```text
script.md
  -> hyperframes_preview
  -> hyperframes_timeline/
  -> approval_required.json
  -> user review
  -> render_mp4 --approved
  -> rendered/final_video.mp4
```

## Preview rule

The authoritative review artifact is the HyperFrames Studio Native Preview project.

The old combined HTML output may exist for history or debugging, but it is not the new production mainline.

## Audio rule

Natural-speed male TTS is the default. Real audio duration drives the timeline.

Do not speed up TTS to hit a fixed video duration.

## Duration rule

The product baseline is not fixed at 40 seconds.

Long source text should be distilled into a short-video spoken script:

- Target: `<= 120s`
- Hard limit: `<= 150s`

## Subtitle and sync rule

Captions, scenes, transitions, and final audio must remain synchronized. The accepted drift threshold is `<= 1.0s`.

## Render rule

Intermediate review should stop at preview and review artifacts. MP4 rendering requires explicit user confirmation and `--approved`.

## Agent rule

Every change must map to one step in this mainline. If a proposed change does not map to the mainline, pause and clarify before implementing it.
