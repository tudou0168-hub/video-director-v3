# V3 AI Agent 行为规范

## V3 项目定位（唯一产品主线）

```
文案
  → script.json
  → 男声 TTS
  → 读取音频真实时长
  → caption_beats.json
  → director_timeline.json
  → visual_beats.json
  → transition_map.json
  → HyperFrames Studio 原生项目（studio_native_project_builder）
  → 用户确认（浏览器人眼验收 hyperframes_timeline/index.html）
  → MP4 视频（render_mp4 + audio mux）
```

**这是 V3 唯一允许的主线。任何新需求、任何改造、任何"捷径"，都必须能落到这条主线的某一步上。**

如果新需求不能落进这条主线：
- 先回到这条主线的某一步
- 不要发明并列链路（不要"另一套管线"、"另一种渲染方式"）
- 不要绕过"用户确认"（未经用户人眼验收就生成 MP4 是禁止的）
- 不要在中间阶段 render MP4
- 不要把 `combined/index.html`、`file://`、Remotion 主线、CapCut 主流程、静态 HTML 预览、JS/GSAP 自定义页面当成当前主线

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
7. `docs/cleanup-plan.md`

**如果这些文件和聊天记录冲突，以这些文件为准。**

禁止：
- 不允许直接相信旧会话记忆
- 不允许只看 README 就开始改
- 不允许没有读 NEXT_TASK 就做功能
- 不允许跳过验收标准
- 不允许在用户确认前 render MP4
- 不允许把旧路线当成主线入口

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

## 客户交付流程（用户要求的工作方式）

**默认流程：先生成 HTML 预览 → 用户人眼确认 → 再合成 MP4。**

具体步骤：
1. 接到新文案时，**只跑 hyperframes_preview**（不跑 render_mp4）。
2. 在浏览器中打开 `outputs/<project_id>/hyperframes_timeline/index.html`（`open <path>` 或拖到浏览器）。
3. 等待用户人眼验收视觉、节奏、字幕。
4. **只有用户明确确认"OK / 合成 / render"后才能跑 render_mp4**。

**禁止**：
- 未经用户确认就跑 `render_mp4`
- 自动跑 smoke render / full render（即使 sync drift = 0.0s 也不行）
- 在用户没说"可以了"前提交任何 MP4 产物

例外（仅以下情况可自动 render_mp4）：
- 用户明确说"自动跑 / 直接生成 / 不需要确认"
- 用户脚本里带 `--no-confirm`（若未来加这个 flag）

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
