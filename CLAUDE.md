# CLAUDE.md

This file is the Claude Code handoff entrypoint for `video-director-v3`.

Claude Code should not redesign the project. Claude Code should execute scoped tasks against the current mainline and preserve the HyperFrames Studio Native Preview workflow.

## Required startup routine

Before changing code, read these files in order:

1. `AGENTS.md`
2. `docs/START_HERE.md`
3. `.ai/repo-index.yml`
4. `.ai/code-index.json`
5. `docs/status/PROJECT_STATE.md`
6. `docs/status/NEXT_TASK.md` if present
7. `docs/pipeline/MAINLINE.md`
8. `docs/runbooks/COMMANDS.md`

Then report:

- Current project phase
- Current strict mainline
- Intended task scope
- Files likely to change
- Files or mechanisms that must not be touched
- Verification commands or review artifacts

## Non-negotiable execution rules

- Do not create a parallel video pipeline.
- Do not replace HyperFrames Studio Native Preview with custom `combined/index.html`, `file://`, or GSAP-only preview.
- Do not use `window.__hf`, `audio.timeupdate`, custom seek loops, or scene-switching playback hacks as the mainline.
- Do not render MP4 during intermediate review unless the user explicitly confirms render.
- Do not introduce a new renderer, timeline engine, director engine, or all-in-one framework.
- Do not change male TTS requirements unless explicitly requested.
- Do not make English the primary visual hierarchy; Chinese content is primary.
- Do not mix cleanup, refactor, and feature development in one uncontrolled task.
- Do not commit generated outputs such as review frames, MP4s, screenshots, caches, or temporary artifacts.

## Preferred working style

- Make small, reviewable changes.
- Prefer reusing existing modules and mature tools.
- Read code before editing.
- Keep commands and paths grounded in the repository.
- Mark uncertain commands as `TODO: verify` instead of inventing them.
- Preserve existing project history and status docs unless the task explicitly updates them.

## Required final report format

After each task, report:

1. Summary
2. Files changed
3. Commands run
4. Verification result
5. Review artifacts, if generated
6. Risks or unresolved issues
7. Recommended next step
