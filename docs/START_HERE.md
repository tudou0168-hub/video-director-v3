# Start Here

This is the first human and AI handoff entrypoint for `video-director-v3`.

## What this project does

`video-director-v3` turns Chinese short-video scripts into HyperFrames Studio Native Preview projects, then renders MP4 only after user confirmation.

## Canonical mainline

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

## Required reading order

For human users:

1. `README.md`
2. `docs/START_HERE.md`
3. `docs/runbooks/COMMANDS.md`

For AI agents:

1. `AGENTS.md`
2. `CLAUDE.md` when using Claude Code
3. `.ai/repo-index.yml`
4. `.ai/code-index.json`
5. `docs/status/PROJECT_STATE.md`
6. `docs/pipeline/MAINLINE.md`
7. `docs/runbooks/COMMANDS.md`

## What this project is not

- Not a general all-in-one director platform.
- Not a new rendering engine.
- Not a replacement for HyperFrames Studio Native Preview.
- Not a custom GSAP preview mainline.
- Not a workflow where MP4 is rendered before user review.

## Review-first workflow

1. Generate `hyperframes_preview`.
2. Open the HyperFrames Studio native preview.
3. Review visual hierarchy, subtitles, audio, rhythm, and sync.
4. Render MP4 only after explicit user confirmation.

## Current state

Read `docs/status/PROJECT_STATE.md` for the current project phase and latest verified baseline.

## Commands

Read `docs/runbooks/COMMANDS.md`. Do not invent commands that are not grounded in repository files.
