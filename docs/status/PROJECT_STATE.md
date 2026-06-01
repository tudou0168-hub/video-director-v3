# video-director-v3 当前项目状态

## 2026-06-01 P3 产品方向更新

用户已明确新的最高优先级。以下内容覆盖旧版固定 40 秒、固定场景数和固定 HUD 预览假设：

```text
中文文案
  → 爆款结构化口播
  → 自然语速男声 TTS
  → 真实音频时长
  → 动态字幕 / 动态分镜 / 自然转场
  → HyperFrames Studio Native Preview
  → approval
  → render_mp4 + audio mux
  → final_video.mp4
```

新基线：
- 不再限制 40 秒；真实语音时长决定视频时长。
- 长文先提炼为短视频口播：目标 `<= 120s`，最长 `<= 150s`。
- 语音不加速。
- 默认沿用原有 HUD 科技风，不使用简化占位画面作为发布基线。
- 分镜数量不固定。
- 音频、字幕、画面和转场同步误差必须 `<= 1.0s`。
- 最终 MP4 必须包含音频流。
- 分阶段建设 50-60 个模板资产。

完整路线图：`docs/plans/V3_P3_VIRAL_VIDEO_ROADMAP.md`

当前阶段：`V3-P2.8 Repo Cleanup Apply（历史参考已归档、缓存已清理、D 类待确认）`
下一任务：`等待人工确认 cleanup-status 后，再决定是否处理 D 类文件`
当前工作：`仅做文档整理与仓库盘点，不删除、不 render`

## 项目目标

用户目标不是半自动内容包。
用户目标是：

**中文文案 → HyperFrames/HTML 动画预览 → 用户确认 → 自动生成 MP4 视频**

主线闭环：

```
script.md
  → hyperframes_preview
  → approval_required.json
  → render_mp4
  → final_video.mp4
```

## 用户做事原则

- 优先复用成熟项目、成熟能力、市场验证过的方案。
- 不优先自研。
- 不为了工程完整性造大系统。
- 先集成、复用、跑通、产出结果。
- 自媒体内容也是先参考爆款、复刻结构，再小幅创新。
- 系统规划不要一上来重构，不要把项目做成四不像。
- 创新只放在最后 10%-20%。

## 当前阶段状态

| 阶段 | 状态 | 备注 |
|------|------|------|
| V3-A 项目结构 | PASS | 目录规范、输出分离 |
| V3-B 可复用模块迁移 | PASS | 从 V2 迁移核心模块 |
| V3-C1 hyperframes_preview | PASS | hyperframes_timeline/ 生成 |
| V3-C1.1 review_frames | PASS | 7/7 帧捕获成功 |
| V3-D1 smoke render_mp4 | PASS | 5s smoke MP4 生成 |
| V3-D2 full render_mp4 | PASS | MP4 生成正常，音频验证通过 |
| V3-D2.1 clean render | PASS | 隐藏调试控件，修复字幕容器宽度 |
| V3-D2.2 productionize clean render | PASS | clean_mode 固化进 pipeline |
| **V3-P2.1 Remotion Minimal Publishable** | **PASS** | Remotion 模板渲染 82.5s 视频，6 个关键帧验证 |
| **V3-P2.2 Remotion Visual Upgrade** | **PASS** | 6 个 scene 全部增强动画和视觉密度 |
| **V3-P3.1 Audio-First** | **PASS** | 81.10s 提炼口播、自然语速 TTS、HUD Native Preview、显式 audio mux、`sync_report.json` |
| **V3-P3.2 Dynamic Storyboard（批次 1）** | **PASS** | 修复 compile 阻塞、preview gate fail-closed、接通 audio timeline 驱动、12 scene / 11 transition / 26 captions、5s smoke `PASS` |
| **V3-P3.2 Dynamic Storyboard（批次 2）** | **PASS** | 细化语义角色判定，`demo_v3_preview` 调整为 `hook → pain → method/explain → evidence → proof → cta`，preview / smoke 继续 `PASS` |
| **V3-P3.2 Template Semantic Data Refinement（批次 3）** | **PASS** | `director_timeline.json` 持久化 Builder 实际使用的语义 scene config；`pain_card_stack` / `broken_chain` / `tool_chain_three_cols` / `before_after_compare` / `checklist_cta` 根据句子语义生成具体字段；preview / smoke 继续 `PASS` |
| **V3-P3.2 Visual Differentiation（批次 4）** | **PASS** | `tool_chain_three_cols` 新增 `three_col_row / source_ingest / knowledge_triangle / vertical_flow` 四种语义布局；`S05/S06/S07` 视觉骨架已分开；preview / smoke 继续 `PASS` |
| **V3-P3.2 Explain / Evidence / Proof 路由融合（批次 5）** | **PASS** | 复用现有 HUD 卡片/对比骨架，为 `broken_chain` 增加 `responsibility_split / binary_choice_split`，为 `before_after_compare` 增加 `dashboard_mobile / symptom_panel`；真实产物中 `S04/S08/S09/S11` 已按句子语义切换布局；preview / smoke 继续 `PASS` |
| **V3-P3.2 Hook / Method / Explain 视觉差异化（批次 6）** | **PASS** | `hook_big_claim` 增加 `quote_punch / big_number_left`；`tool_chain_three_cols` 增加 `intro_offset`；`broken_chain` 继续拉开责任分工与二选一场景；`S01/S03/S04` 从同一类居中双卡改成封面式 / 导语式 / 对撞式；preview / smoke 继续 `PASS` |
| **V3-P3.2 CTA 路由融合 + GSAP 评估（批次 7）** | **PASS** | `checklist_cta` 新增 `button_banner / end_score_goodbye / scorecard` 三个复用型变体；按 narration 关键词自动路由；GSAP 动效层评估为"接入但未触发"状态，保留 `get_scene_gsap` 接口但不再注入 Native Preview，以保护 0.0s 同步漂移基线；preview / smoke / 47 个测试全部 `PASS` |
| **V3-P3.3 Template Registry MVP（批次 8）** | **PASS** | 12 个 seed 模板（6 旧 + 6 新）：`framework_quadrant / decision_tree / metric_dashboard / case_study_card / section_board / comment_question`；按 narration 关键词自动路由（含 explain 角色 fallback）；56 个测试基线 `PASS`；preview / smoke 继续 PASS，同步漂移 `0.0s`；端到端 P3.3 demo 命中 4 种新 seed |
| **V3-P3.4 Template Library Expansion（批次 9）** | **PASS** | 20 个 seed 模板（+8：`countdown_strike / keyword_punchline / data_dense_table / step_ladder / concept_layers / progress_tracker / knowledge_graph / quote_close`）+ 9 动效预设 + 13 语义转场协议；`classify_role` 扩展 keyword 覆盖；73 个测试基线 `PASS`；demo 真实路径 S06 命中 `knowledge_graph`；preview / smoke 继续 PASS，同步漂移 `0.0s` |
| **V3-P3.5 Template Library Complete（批次 10）** | **PASS** | 30 个 seed 模板（+10：`myth_bust / before_after_flash / timeline_pain / timeline_path / tool_stack / case_study / evidence_cards / score_panel / next_step_board / comment_invite`）+ 14 动效 + 13 转场协议（达成路线图 56 资产目标，总 57）；85 个测试基线 `PASS`；preview / smoke 继续 PASS，同步漂移 `0.0s` |
| **V3-P3.6 Viral QA Loop（批次 11）** | **PASS** | `viral_qa_evaluator.py` 实现 6 维内容结构评分（hook / promise / saveable_value / comment_trigger / visual_rhythm / sync_reliability）+ A/B 变体 manifest；pipeline_runner 自动生成 `viral_quality_report.json`；评分基于公开可见的内容质量原则，**不冒充平台算法**；110 个测试基线 `PASS`；demo preview viral score=26/60 FAIL 是评分机制正确识别内容缺点的体现；sync_reliability=10/10（max_drift=0.0s） |
| **V3 Retrospective + Cleanup（批次 12）** | **PASS** | 112 调试 JS 归档到 `tests/manual_archive/` + gitignore 隔离；129 untracked 文件全部分类（9 个 add，120 个 gitignore）；新增 9 个正式资产（`viral_script_distiller` / `native_mp4_renderer` / HUD 提炼文档 / 路线图 / 2 demo 脚本 / `test_native_sync_report.py`）；新增 `docs/decisions/V3_RETROSPECTIVE.md`（6 阶段判断/教训/统计/V4 建议）；新增 `docs/V3_CAPABILITY_INDEX.md`（63 资产盘点 + 110 测试 + 0.0s drift 基线）；`scripts/` 未用目录删除；110 测试基线 `PASS`；preview / smoke 继续 PASS |

**V3-P2 视觉渲染技术栈**：Remotion → HTML/CSS/React 动画 → MP4

## 当前最高优先级

### P1
- V3-P3.2 CTA 路由融合 + GSAP 可选动效层评估
- V3-P3.3 至 P3.5 模板库扩展到 50-60 个资产
- V3-P3.6 爆款 QA 与 A/B 变体

## 当前不要做

- 不要继续强化固定 40 秒契约
- 不要为了时长加速语音
- 不要把公众号长文原样朗读；先提炼到 120 秒目标、150 秒硬上限
- 不要用简化占位画面替代原 HUD 科技风
- 不要固定生成 6、7、8 个分镜
- 不要继续扩展 `combined/index.html`
- 不要一次性堆叠 50-60 个重复模板
- 不要承诺破解或命中平台算法

## 关键产物路径

| 产物 | 路径 |
|------|------|
| Remotion 模板 | `remotion_templates/hud_explainer/` |
| smoke props | `outputs/publishable_viral_v2/remotion_smoke_props.json` |
| full props | `outputs/publishable_viral_v2/remotion_props.json` |
| smoke 视频 | `outputs/publishable_viral_v2/remotion_smoke_v2/final_video.mp4` |
| smoke 帧 | `outputs/publishable_viral_v2/remotion_smoke_v2/frames/` |
| P3.1 正式文案 Native Preview | `outputs/obsidian_second_brain_p31_preview/hyperframes_timeline/` |
| P3.1 正式文案有声 smoke | `outputs/obsidian_second_brain_p31_preview/rendered_smoke/final_video_smoke.mp4` |
| P3.1 同步报告 | `outputs/obsidian_second_brain_p31_preview/rendered_smoke/sync_report.json` |
| P3.2 动态 preview | `outputs/demo_v3_preview/hyperframes_timeline/` |
| P3.2 动态 smoke | `outputs/demo_v3_preview/rendered_smoke/final_video_smoke.mp4` |
| P3.2 动态同步报告 | `outputs/demo_v3_preview/rendered_smoke/sync_report.json` |

## 当前视觉风格

AI 科技解释型 HUD 风格：
- 深色渐变背景 (#050814)
- 细网格 + 柔光光斑
- 半透明玻璃卡片
- 青蓝/橙红/荧光绿强调色
- Spring / ease-out 动效
- 数据卡、流程节点、前后对比、CTA 清单

## 测试状态

110 个测试基线保持通过（`tests/test_template_protocol.py` 46 个 + `tests/test_preview_pipeline.py` 27 个 + `tests/test_viral_qa.py` 25 个 + `tests/test_tts_contract.py` + 其他）；V3 Retrospective 批次 12 后，cleanup 0 回归；真实 preview `READY`、5 秒 smoke render `PASS`、`sync_report.json` `max_drift=0.0s`、`viral_quality_report.json` 自动生成（最近运行：2026-06-01）

---

最后更新：2026-06-01

---
最后更新：2026-06-01
