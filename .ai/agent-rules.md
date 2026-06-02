# AI Agent Rules

This project is optimized for practical short-video generation. Agents should preserve the existing production path and avoid broad redesign.

## Highest principle

Use mature existing capabilities and the current V3 pipeline. Avoid rebuilding the director, renderer, timeline, or preview system from scratch.

## Required reading order

1. `AGENTS.md`
2. `CLAUDE.md` when using Claude Code
3. `docs/START_HERE.md`
4. `.ai/repo-index.yml`
5. `.ai/code-index.json`
6. `docs/status/PROJECT_STATE.md`
7. `docs/pipeline/MAINLINE.md`
8. `docs/runbooks/COMMANDS.md`

## Mainline discipline

All changes must fit this mainline:

中文文案 -> 爆款结构化口播/AI 导演解析 -> 自然语速男声 TTS -> 真实音频时长 -> 动态字幕/动态分镜/自然转场 -> HyperFrames Studio Native Preview -> 用户确认 -> render_mp4 + audio mux -> final_video.mp4

## Preferred behavior

- Keep tasks small and reviewable.
- Reuse existing modules before adding new ones.
- Update docs when project behavior changes.
- Use real project commands from `docs/runbooks/COMMANDS.md`.
- Keep Chinese content and Chinese visual hierarchy primary.
- Treat real audio duration as the master timing source.
- Use review frames and HTML/Studio preview for intermediate review.

## Protected constraints

- Keep one production pipeline.
- Keep HyperFrames Studio Native Preview as the review path.
- Keep MP4 rendering behind explicit user confirmation.
- Keep generated output directories out of source control.
- Keep output path conventions stable.
- Keep quality scoring framed as internal review, not platform-algorithm certainty.

## Final report requirement

Every agent task should end with:

1. What changed
2. Files changed
3. Commands run
4. Verification result
5. Risks or open TODOs
6. Recommended next step
