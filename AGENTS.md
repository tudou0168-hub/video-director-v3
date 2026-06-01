# V3 AI Agent 行为规范

## 2026-06-01 P3 产品基线覆盖

以下规则覆盖本文后续仍保留的旧版固定 40 秒 P0 Gate：

- 不再限制视频为 38-43 秒。
- 长文先提炼为短视频口播：目标 `<= 120s`，硬上限 `<= 150s`。
- 不允许为了命中时长加速 TTS；超长时必须删减次要信息并重新生成。
- 使用自然语速男声，真实音频时长决定视频总时长。
- 默认视觉基线复用原有 HUD 科技风：深色网格、扫描线、HUD 边框、数据卡、流程节点、对比卡和 CTA 清单。
- 分镜数由内容动态决定，不固定为 6、7、8。
- 字幕、分镜、转场与最终 MP4 音频同步误差必须 `<= 1.0s`。
- 最终 MP4 必须通过 `ffprobe` 验证音频流。
- 分阶段建设 50-60 个模板资产。

完整路线图：`docs/plans/V3_P3_VIRAL_VIDEO_ROADMAP.md`

## Agent 接手须知

**所有智能体接手本项目，必须先读以下文件：**

1. `docs/status/PROJECT_STATE.md`
2. `docs/status/NEXT_TASK.md`
3. `docs/status/CURRENT_BUGS.md`
4. `docs/status/LAST_KNOWN_GOOD.md`
5. `docs/runbooks/COMMANDS.md`
6. `docs/decisions/DECISION_LOG.md`

**如果这些文件和聊天记录冲突，以这些文件为准。**

禁止：
- 不允许直接相信旧会话记忆
- 不允许只看 README 就开始改
- 不允许没有读 NEXT_TASK 就做功能
- 不允许跳过验收标准

---

## 唯一产品主线

```
中文文案 → hyperframes_preview → approval → render_mp4 → final_video.mp4
```

- `script.md` 是输入
- `hyperframes_timeline/` 是预览权威产物（HyperFrames Studio 原生项目）
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
- 从 HyperFrames Studio 原生预览通过的项目渲染
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
- `ffprobe` 可读取真实 audio duration
- hyperframes_timeline/ 有 audio
- scene body inserted
- S01 headline visible 且 >=72px
- caption beats 覆盖完整口播，尾点与音频尾点偏差 `<= 1.0s`
- scenes 覆盖完整口播，尾点与音频尾点偏差 `<= 1.0s`
- semantic_transitions 存在
- preview_report 存在
- approval_required.json 存在

render_mp4 必须有 `--approved` 才允许渲染，并验证最终 MP4 含视频流、音频流，时长偏差 `<= 1.0s`。

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
