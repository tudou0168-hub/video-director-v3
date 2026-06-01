# V3 Capability Index — 资产盘点 + V4 入口

**日期**：2026-06-01
**状态**：V3 路线图全 6 阶段 PASS，63 资产 / 110 测试 / 0.0s drift

## 0. V3 唯一产品主线

```
中文文案
  → AI 导演解析（narration_planner + classify_role）
  → 视觉设计规范（scene_protocol + 30 模板库）
  → HyperFrames Studio 原生项目（studio_native_project_builder）
  → 用户确认（浏览器人眼验收 hyperframes_timeline/index.html）
  → MP4 视频（render_mp4 + audio mux）
```

**这是 V3 唯一允许的主线。任何新需求、任何改造、任何"捷径"，都必须能落到这条主线的某一步上。**

## 1. 主线能力

### 1.1 输入
- 中文文案（Markdown / 纯文本）
- 长文自动提炼为短视频口播（目标 ≤120s，硬上限 ≤150s）
- Edge TTS 自然语速男声（+0%，不加速）

### 1.2 核心管线
```
script.md
  → viral_script_distiller (提炼到 12-15 句口播)
  → edge_tts (生成 voiceover.mp3)
  → real audio duration 权威 (ffprobe)
  → narration_planner + classify_role
  → storyboard_builder (dynamic clustering, 12 scene)
  → semantic_transitions (相邻语义 + 转场)
  → caption_beats (句级音频时间轴驱动)
  → visual_beats (角色驱动节拍)
  → studio_native_project_builder (HyperFrames timeline + 30 模板)
  → review_frames (7 帧)
  → viral_qa_evaluator (6 维评分 + A/B manifest)
  → approval_required.json (fail-closed gate)
  → native_mp4_renderer (FFmpeg + audio mux)
  → sync_report.json (drift / volume / 音视频流)
```

### 1.3 输出
- `hyperframes_timeline/index.html` — HyperFrames Studio Native Preview
- `viral_quality_report.json` — 6 维内容评分 + A/B 变体
- `rendered_smoke/final_video_smoke.mp4` — 5 秒有声 MP4
- `rendered/final_video.mp4` — 全时长 MP4（待 V4 接入）
- `sync_report.json` — 同步漂移 / 音量 / 音视频流

## 2. 资产清单（63 项）

### 2.1 场景框架（30）

#### P3.2 批 1（6 个，原始 seed）
| ID | render_template | 角色 |
|---|---|---|
| scene.hook.hero_center | hook_big_claim | hook |
| scene.input.dense_data_table | pain_card_stack | pain |
| scene.memory.proof_overlay | broken_chain | explain/proof |
| scene.retrieval.pipeline_nodes | tool_chain_three_cols | method |
| scene.compare.option_split_vertical | before_after_compare | evidence |
| scene.cta.checklist_board | checklist_cta | cta |

#### P3.3（6 个）
| ID | render_template | 角色 |
|---|---|---|
| scene.method.framework_quadrant | framework_quadrant | method |
| scene.method.decision_tree | decision_tree | method |
| scene.evidence.metric_dashboard | metric_dashboard | evidence |
| scene.evidence.case_study_card | case_study_card | evidence |
| scene.proof.section_board | section_board | proof |
| scene.proof.comment_question | comment_question | proof |

#### P3.4（8 个）
| ID | render_template | 角色 |
|---|---|---|
| scene.hook.countdown_strike | countdown_strike | hook |
| scene.hook.keyword_punchline | keyword_punchline | hook |
| scene.pain.data_dense_table | data_dense_table | pain |
| scene.method.step_ladder | step_ladder | method |
| scene.method.concept_layers | concept_layers | method |
| scene.evidence.progress_tracker | progress_tracker | evidence |
| scene.proof.knowledge_graph | knowledge_graph | proof |
| scene.cta.quote_close | quote_close | cta |

#### P3.5（10 个）
| ID | render_template | 角色 |
|---|---|---|
| scene.hook.myth_bust | myth_bust | hook |
| scene.hook.before_after_flash | before_after_flash | hook |
| scene.pain.timeline_pain | timeline_pain | pain |
| scene.method.timeline_path | timeline_path | method |
| scene.method.tool_stack | tool_stack | method |
| scene.evidence.case_study | case_study | evidence |
| scene.evidence.evidence_cards | evidence_cards | evidence |
| scene.proof.score_panel | score_panel | proof |
| scene.proof.next_step_board | next_step_board | proof |
| scene.cta.comment_invite | comment_invite | cta |

### 2.2 动效预设（14）
`kinetic_title_burst / marker_sweep / card_stagger / count_up / flow_draw / table_stream / node_pulse / graph_rise / quote_reveal / parallax_drift / scan_focus / depth_push / glow_breathe / check_pop`

### 2.3 语义转场（13）
`glow_shift / fade_slide_bridge / scan_reveal / slide_bridge / soft_wipe / line_draw_bridge / panel_slide_bridge / final_hold_fade / cards_to_flow / flow_to_table / metric_to_compare / radial_focus_shift / zoom_through`

### 2.4 Viral QA（6 维 + A/B manifest）
- **Hook** — 冲击词 + 长度 + emphasis
- **Promise** — 方法信号密度
- **Saveable value** — 可复用结构（步骤/清单/框架）
- **Comment trigger** — 自然评论引导（去机械诱导）
- **Visual rhythm** — unique visual_templates 比例
- **Sync reliability** — max_drift 反向
- **A/B manifest** — hook/method/evidence/cta 各 2 候选

## 3. CTA 变体（4 layout_variants of checklist_cta）
- `checklist_steps`（默认 3-step action）
- `button_banner`（大按钮式行动号召）
- `end_score_goodbye`（大分数收束 + 下期预告）
- `scorecard`（3 项指标得分卡）

## 4. Layout Variants（继承自 P3.2 批 4-6）
- `broken_chain`：responsibility_split / binary_choice_split
- `before_after_compare`：dashboard_mobile / parallel_lanes / symptom_panel
- `tool_chain_three_cols`：three_col_row / source_ingest / knowledge_triangle / vertical_flow / matrix_glossary_wall / intro_offset

## 5. 测试基线（110）

| 类别 | 数量 |
|------|----:|
| 协议层（seed/motion/transition/role mapping）| 18 |
| routing 关键词 | 30+ |
| 渲染 dispatch + data helper | 60+ |
| Viral QA | 25 |
| 真实 demo 端到端 | 1 |

## 6. 关键不变量

- `sync_report.json` 的 `max_drift_seconds = 0.0s` 持续保持
- 真实 TTS 自然语速 +0%（不加速）
- 分镜数动态（不固定 6/7/8）
- preview approval fail-closed（必需阶段失败 = 不可批准）
- 不引入 combined/index.html / file:// 路线
- 不冒充平台推荐算法

## 7. V4 入口

按 [`V3_RETROSPECTIVE.md`](decisions/V3_RETROSPECTIVE.md) 第 5 节"V4 方向建议"推进：
- **V4.0（1-2 周）**：接入真实播放数据 + 强化 4 个低分维度
- **V4.1（1 个月）**：跨平台分发 + A/B 真渲染 + 模板自动权重
- **V4.2（季度）**：Hero frame 视觉评测 + 内容反向工程 + 个人风格化

## 8. 文件入口

| 入口 | 路径 |
|------|------|
| 主线 CLI | `src/video_director_v3/cli.py` |
| 协议层 | `src/video_director_v3/templates/scene_protocol.py` |
| 模板 registry | `src/video_director_v3/renderers/hyperframes/publish_templates.py` |
| 路由 | `src/video_director_v3/director/storyboard_builder.py` |
| 角色分类 | `src/video_director_v3/director/narration_planner.py` |
| Native Builder | `src/video_director_v3/renderers/hyperframes/studio_native_project_builder.py` |
| TTS | `src/video_director_v3/tts/tts_adapter.py` |
| 字幕 | `src/video_director_v3/motion/caption_beat_generator.py` |
| 转场 | `src/video_director_v3/motion/semantic_transition_planner.py` |
| 视觉节拍 | `src/video_director_v3/motion/visual_beat_planner.py` |
| MP4 renderer | `src/video_director_v3/renderers/hyperframes/native_mp4_renderer.py` |
| Pipeline runner | `src/video_director_v3/pipeline/pipeline_runner.py` |
| **Viral QA** | `src/video_director_v3/qa/viral_qa_evaluator.py` |
| 测试集 | `tests/test_*.py`（共 7 个文件）|
| 路线图 | `docs/plans/V3_P3_VIRAL_VIDEO_ROADMAP.md` |
| 复盘 | `docs/decisions/V3_RETROSPECTIVE.md` |
| 能力清单 | 本文档 |
| 调试 JS 归档 | `tests/manual_archive/`（112 个，已 gitignore）|

V3 已是可持续生产系统。下一棒是 V4 — 接真实数据。
