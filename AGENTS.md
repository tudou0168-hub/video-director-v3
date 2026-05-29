# V3 AI Agent 行为规范

## 唯一产品主线

```
中文文案 → hyperframes_preview → approval → render_mp4 → final_video.mp4
```

- `script.md` 是输入
- `combined/index.html` 是预览权威产物
- `approval_required.json` 是审批 gate
- `final_video.mp4` 只能由 `render_mp4` 生成

## 两个输出模式

### hyperframes_preview
- 生成 HTML 动画预览
- 生成 review_frames 截图
- 生成 approval_required.json
- **禁止**生成 final_video.mp4

### render_mp4
- 必须有 `--approved` flag
- 从已有 `combined/index.html` 渲染
- 不重新跑完整 pipeline
- 输出 `rendered/final_video.mp4`

## 目录规则

V3 统一输出目录，不允许混乱：

- **正式输出**: `outputs/<project_id>/`
- **测试输出**: `test_outputs/<project_id>/`

**禁止**写入：
- `src/outputs/`
- 旧项目 outputs/
- 临时散落目录
- `/tmp` 作为最终产物目录

所有路径由 `src/video_director_v3/pipeline/project_paths.py` 统一管理。

## 修改原则

1. 先读代码，再动手
2. 小步修改，不重构无关模块
3. 不引入复杂依赖
4. 不删除旧项目
5. 不把旧 outputs 迁入 V3

## P0 Gate

hyperframes_preview 必须通过：

- `input_relevance_score >= 0.7`
- TTS ok
- audio duration 38-43s
- combined/index.html 有 audio
- scene body inserted
- S01 headline visible 且 >=72px
- caption_beats_count >= scene_count * 2
- semantic_transitions 存在
- preview_report 存在
- approval_required.json 存在

render_mp4 必须有 `--approved` 才允许渲染。

## 禁止事项

- mock final_video 冒充真实视频
- quality_score 替代人眼验收
- Studio native 不兼容就大重构
- 为了指标修改报告数字
- 新代码把产物写入 src/outputs
- hyperframes_preview 模式生成 final_video.mp4
- render_mp4 无 --approved 就渲染

## 辅助技能融合

V3 接入以下技能作为 Design Profile 层：

- stitch-skill / stitch-design-taste → 生成 DESIGN.md
- brandkit → 生成 brandkit.json
- imagegen-* → 可选视觉参考图
- DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY 三个设计旋钮

这些技能不替代 video pipeline。