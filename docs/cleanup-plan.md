# V3-P2.8 Cleanup Plan

本文件只做盘点，不做删除。

## 目标

1. 让新用户和新 agent 一眼看懂唯一主线。
2. 把历史路线、临时脚本、调试产物、旧输出分桶。
3. 所有清理动作都要等人工确认后再执行。

## 唯一主线

```text
文案
→ script.json
→ 男声 TTS
→ 读取音频真实时长
→ caption_beats.json
→ director_timeline.json
→ visual_beats.json
→ transition_map.json
→ HyperFrames Studio 原生 HTML 预览
→ 人工审查
→ 用户确认后才 render MP4
```

## 扫描结论

- 当前仓库里，最明显的旧路线代码是 `src/video_director_v3/renderers/hyperframes/combined_html_builder.py`。
- 历史 debug JS 和一次性探针已大多归档到 `tests/manual_archive/`，不作为主线入口。
- `outputs/`、`test_outputs/`、`rendered/`、`review_frames/` 一类内容应视作生成物，不进入主线文档。

## A. 保留

当前主线必须保留，不动。

- `README.md`
- `AGENTS.md`
- `docs/agents/ANY_AGENT_START_HERE.md`
- `docs/preview-standard.md`
- `docs/runbooks/COMMANDS.md`
- `docs/status/PROJECT_STATE.md`
- `docs/status/NEXT_TASK.md`
- `docs/status/CURRENT_BUGS.md`
- `docs/status/LAST_KNOWN_GOOD.md`
- `src/video_director_v3/cli.py`
- `src/video_director_v3/pipeline/project_paths.py`
- `src/video_director_v3/pipeline/pipeline_runner.py`
- `src/video_director_v3/director/narration_planner.py`
- `src/video_director_v3/director/storyboard_builder.py`
- `src/video_director_v3/motion/caption_beat_generator.py`
- `src/video_director_v3/motion/semantic_transition_planner.py`
- `src/video_director_v3/motion/visual_beat_planner.py`
- `src/video_director_v3/renderers/hyperframes/studio_native_project_builder.py`
- `src/video_director_v3/renderers/hyperframes/publish_templates.py`
- `src/video_director_v3/renderers/browser/browser_mp4_renderer.py`
- `tests/test_preview_pipeline.py`
- `tests/test_tts_contract.py`
- `tests/test_render_gate.py`

## B. 归档

有历史价值，但不应出现在主线入口。

- `docs/decisions/V3_RETROSPECTIVE.md`
- `docs/status/V2_VISUAL_REUSE_INVENTORY.md`
- `docs/status/GITHUB_UPLOAD_SAFETY_REPORT.md`
- `docs/status/visual_capability_catalog.json`
- `docs/V3_CAPABILITY_INDEX.md`
- `docs/visual/HUD_TEMPLATE_EXTRACTION.md`
- `docs/visual/hud_template_catalog.json`
- `outputs/demo_v3_preview/`
- `outputs/acceptance_claude_code_20260526/`
- `outputs/obsidian_second_brain_p31_preview/`
- `outputs/publishable_viral_v2/`
- `tests/manual_archive/`

建议归档目录：

- `docs/archive/`
- `outputs/archive/`

## C. 可删除

明显临时文件、重复测试、debug 产物、无引用文件。

当前建议删除的是“生成物模式”，不是某个主线文件本身：

- `__pycache__/`
- `.pytest_cache/`
- `.ruff_cache/`
- `.mypy_cache/`
- `.coverage`
- `.coverage.*`
- `coverage.xml`
- `.playwright/`
- `playwright-report/`
- `test-results/`
- `.hypothesis/`
- `*.log`
- `*.tmp`
- `*.trace`
- `tmp/`
- `cache/`
- `render_tmp/`
- `hf_cache/`

## D. 需要人工确认

不确定是否还被使用，先不要动。

- `src/video_director_v3/renderers/hyperframes/combined_html_builder.py`
- `docs/architecture.md`
- `docs/migration-from-v2.md`
- `docs/testing.md`
- `docs/quickstart-preview-to-mp4.md`
- `docs/agents/CLAUDE_HANDOFF.md`

## 需要确认后再做的动作

1. 把 B 类内容搬进 archive。
2. 删除 C 类生成物和临时文件。
3. 保留 D 类，或在人工确认后再决定是归档还是删除。
4. 不在本阶段执行任何 MP4 渲染。

## 本阶段结论

清理计划已就位，等人工确认后再进入 `V3-P2.8-Repo-Cleanup-Apply`。

## 执行状态

已执行结果请见 `docs/cleanup-status.md`。
