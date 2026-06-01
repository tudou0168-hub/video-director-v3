# V3-P2.8 Cleanup Status

This file records what was applied from `docs/cleanup-plan.md`.

## Applied

- B 类历史参考内容已归档到 `docs/archive/` 和 `outputs/archive/`
- `outputs/` 顶层历史项目已整体收进 `outputs/archive/`，顶层只保留 archive 容器
- 额外归档了几份明显的旧视觉规划文档，避免它们继续被误认为主线入口
- C 类缓存、临时文件、debug 产物已清理
- D 类文件未移动、未删除，仅保留为待确认
- `.gitignore` 已补充更细的生成物规则

## D 类仍待确认

- `src/video_director_v3/renderers/hyperframes/combined_html_builder.py`
- `docs/architecture.md`
- `docs/migration-from-v2.md`
- `docs/testing.md`
- `docs/quickstart-preview-to-mp4.md`
- `docs/agents/CLAUDE_HANDOFF.md`

## Notes

- 当前主线仍然是 `script.json -> TTS -> real audio duration -> caption_beats.json -> director_timeline.json -> visual_beats.json -> transition_map.json -> HyperFrames Studio native preview -> human review -> approved render_mp4`
- 未执行任何 MP4 渲染
- 未修 R9/R16
- 未修改业务源码
