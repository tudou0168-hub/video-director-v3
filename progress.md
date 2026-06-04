# Progress

## 2026-06-01

### 已完成

- 读取项目强制状态文档与决策日志。
- 读取 `planning-with-files-zh`、`hyperframes-director` 和 `hyperframes` 工作流。
- 盘点旧 TTS、口播规划、字幕节拍、分镜、转场、模板注册和 MP4 mux 实现。
- 建立新的持久化规划文件。
- 核对平台公开资料，形成不猜算法权重的爆款 QA 原则。
- 创建 `docs/plans/V3_P3_VIRAL_VIDEO_ROADMAP.md`。
- 更新 `AGENTS.md`、项目状态、下一任务、当前问题、决策日志和命令迁移提示。
- 将 `AGENTS.md` 的旧 `38-43s` Gate 替换为 Audio-First 同步 Gate。
- 运行 `git diff --check`：通过。
- 关闭上一轮遗留的本地 HyperFrames Studio 服务。
- 完成 `P3.1 Audio-First`：自然语速 Edge TTS、真实音频时长权威、Native Preview Builder、Native MP4 renderer、显式 FFmpeg audio mux、`sync_report.json`。
- 修复 Markdown YAML frontmatter 进入口播的问题。
- 根据用户反馈新增短视频口播提炼器：目标 `<=120s`、硬上限 `<=150s`，不允许加速 TTS。
- 用指定文案 `2026-05-27-Obsidian打造第二大脑AI记住一切.md` 将 76 句长文提炼为 12 句、419 字口播。
- 复用原有 HUD 科技风模板族升级 Native Preview：深色网格、扫描线、卡片堆栈、链路节点、对比卡、CTA 清单。
- 将字幕改为句级音频时间轴驱动：21 条字幕覆盖完整提炼口播。
- 用指定文案生成 Native Preview：音频 `81.10s`、`speaking_rate=+0%`、Native lint `0 errors`。
- 用指定文案生成 5 秒有声 smoke：`h264 + aac`、音量已检测、最大同步漂移 `0.0s`。
- 运行完整测试集：`28 passed`。

### 当前阶段

- `P3.1 Audio-First 主线修复`：已完成。

### 下一步

- 启动 `P3.2 Dynamic Storyboard`。
- 将固定 8 场景、每场景固定 2 条字幕和固定转场替换为语义节拍驱动。

### P3.2 接手审计

- 读取强制状态文档、路线图、现有规划文件、核心 pipeline、TTS、storyboard、caption、transition、visual beat、Native Builder、Native renderer 和测试文件。
- 确认 P3.1 既有产物证据仍可作为基线：81.1s Native Preview、5s 有声 smoke、同步报告 PASS。
- 运行 `git diff --check`：通过。
- 运行 `compileall`：失败。`src/video_director_v3/director/storyboard_builder.py:201` 存在未闭合字符串。
- 运行完整测试集：`36 passed in 120.68s`。随后确认这是误导性绿灯：storyboard 导入失败后 pipeline 回退到固定 7 场景，approval 仍 READY。
- 识别 P3.2 主阻塞：动态 storyboard 草稿未接入 pipeline，固定转场、固定视觉 beat 和 Native Builder 索引模板仍未替换。
- 识别 approval fail-open：必需阶段失败未阻止 `can_approve_preview=true`。
- 识别模板协议接线问题：seed registry 未在 pipeline 初始化，协议 ID 与发布渲染键不一致。
- 识别文档漂移：`docs/status/project_state.json` 与 `docs/testing.md` 仍保留旧 D2 / `38-43s` 信息。
- 识别提交卫生问题：未跟踪调试 JS 共 107 个，应与 P3.2 产品提交隔离处理。

### P3.2 批次推进

- 批次 1：修复 `storyboard_builder.py` 编译错误；preview approval 改为 fail-closed；接通 `audio_timeline -> dynamic storyboard`；真实产物变为 12 scene / 11 transition / 26 caption。
- 批次 2：细化 `classify_role()`；将第二句重新归到 `pain`，把“以前/现在/30 秒”类结果句归到 `evidence`，把“你才能/把记住交给第二大脑”类总结句归到 `proof`。
- 批次 3：在 Native Builder 中按句子语义生成更具体的 template data，并把实际渲染使用的 scene config 持久化到 `outputs/<project_id>/hyperframes_timeline/data/director_timeline.json`。

### 本轮验证

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_preview_pipeline.py tests/test_tts_contract.py -q`：`14 passed`
- `PYTHONPATH=src .venv/bin/python3 -m compileall -q src tests`：通过
- `git diff --check`：通过
- 真实 preview：`demo_v3_preview` 继续 `READY`
- 真实 smoke render：`outputs/demo_v3_preview/rendered_smoke/final_video_smoke.mp4` 继续 `PASS`
- `outputs/demo_v3_preview/rendered_smoke/sync_report.json`：`has_video_stream=true`、`has_audio_stream=true`、三类漂移 `0.0s`

### P3.2 视觉差异化

- 为 `tool_chain_three_cols` 增加语义驱动的布局变体：
  - `three_col_row`
  - `source_ingest`
  - `knowledge_triangle`
  - `vertical_flow`
- 让 `studio_native_project_builder.py` 根据句子语义写入 `layout_variant`。
- 让 `director_timeline.json` 持久化这些布局变体，便于后续排查和接手。
- 实际产物中：
  - `S03=three_col_row`
  - `S05=source_ingest`
  - `S06=knowledge_triangle`
  - `S07=vertical_flow`
- 最新 review frame 已证明 `S05` 与 `S06` 的视觉骨架明显分开。

### 外部参考图库提炼

- 新增任务：结合系统原有模板与 `/Users/muzi/Windows共享文件/视频效果分析` 的 79 张截图，抽取 HUD 样式、布局骨架、图表框架、动效语法，并和文案场景建立映射。
- 已确认参考目录图片总数：`79`
- 已生成本地批次 HTML 联系表到 `outputs/reference_analysis/html/`
- 已完成批次 1（前 12 张）人工提炼，识别出：
  - `hero_big_number_left`
  - `comparison_progress_bars`
  - `money_ladder_with_evidence`
  - `top_carousel_examples`
  - `feature_cards_row`
  - `step_tabs_or_paths`
  - `dual_curve_growth`
  - `relationship_triangle_or_bridge`
  - `checklist_claim_left`
  - `keyword_punchline`
- 已完成后续批次抽样，确认中后段大多是前述模板家族的主题变体，并补出这些独立骨架：
  - `comment_quote_hook`
  - `binary_choice_split`
  - `dashboard_mobile`
  - `section_board`
  - `matrix_glossary_wall`
  - `parallel_lanes`
  - `symptom_panel`
  - `end_score_goodbye`
- 已新增后续可直接接入 P3.3 的资产：
  - `docs/visual/HUD_TEMPLATE_EXTRACTION.md`
  - `docs/visual/hud_template_catalog.json`
- 已结合 `/Users/muzi/LLM_Knowledge2.0/wiki` 的内容结构，把模板骨架和高频文案场景建立初版路由映射。

### P3.2 Explain / Evidence / Proof 路由融合

- 延续“整合、编排、融合、复用”原则，没有新造独立动画系统，而是复用当前 `publish_templates.py + studio_native_project_builder.py + HyperFrames HUD 基线`。
- 参考已安装技能与能力边界后，明确当前实现策略：
  - 大场景编排继续以 HyperFrames Native timeline 为主；
  - 主要场景骨架继续复用现有 HUD 面板、边框、网格、卡片；
  - 大块时序编排优先 GSAP 语义，但 Native Preview 当前仍以稳定 HTML 布局为主；
  - CSS 只保留给轻量装饰性扫描线、网格漂移和柔光，不另造新框架。
- 为 `broken_chain` 增加两种复用型布局变体：
  - `responsibility_split`
  - `binary_choice_split`
- 为 `before_after_compare` 增加两种复用型布局变体：
  - `dashboard_mobile`
  - `symptom_panel`
- 让 Native Builder 根据真实句子语义自动路由：
  - `S04=responsibility_split`
  - `S08=dashboard_mobile`
  - `S09=binary_choice_split`
  - `S11=symptom_panel`
- 已补定向 snapshot 审查，确认 Explain / Evidence / Proof 四段的视觉骨架明显分开。
- 本轮验证：
  - `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_preview_pipeline.py tests/test_tts_contract.py -q`：`14 passed`
  - `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`：通过
  - `git diff --check`：通过
  - 真实 preview：`READY`
  - 真实 5 秒 smoke render：`PASS`
  - `outputs/demo_v3_preview/rendered_smoke/sync_report.json`：`PASS`，视频流 / 音频流存在，漂移 `0.0s`

### P3.2 Hook / Method 视觉差异化

- 针对用户指出的 `S01 / S03 / S04` 视觉重复问题，进一步把首段、导语段和解释段拆成不同语法，而不是继续在同类双卡上堆文案。
- `hook_big_claim` 新增两种复用型布局：
  - `quote_punch`
  - `big_number_left`
- `tool_chain_three_cols` 新增导语型布局：
  - `intro_offset`
- 真实 preview 中已路由为：
  - `S01=quote_punch`
  - `S03=intro_offset`
  - `S04=responsibility_split`
- 定向 snapshot 已确认三段不再是同一套居中卡片：
  - `S01` 变成封面式引言海报
  - `S03` 变成偏置式导语流程板
  - `S04` 变成左右对撞式职责分工板
- 本轮验证：
  - `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_preview_pipeline.py tests/test_tts_contract.py -q`：`14 passed`
  - `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`：通过
  - `git diff --check`：通过
  - 真实 preview：`READY`
  - 真实 5 秒 smoke render：`PASS`
  - `outputs/demo_v3_preview/rendered_smoke/sync_report.json`：`PASS`，视频流 / 音频流存在，漂移 `0.0s`

### P3.2 CTA 路由融合（批次 7）

- 为 `checklist_cta` 复用现有 HUD 卡片骨架扩展为 4 个 layout_variant：
  - `checklist_steps`（默认 3-step action）
  - `button_banner`（大按钮式行动号召）
  - `end_score_goodbye`（大分数收束 + 下期预告）
  - `scorecard`（3 项指标得分卡）
- `_cta_layout_variant_from_narration()` 按 narration 关键词自动路由：
  - 完结 / 下期 / 系列 → `end_score_goodbye`
  - 得分 / 状态 / 指标 → `scorecard`
  - 立即 / 现在 / 下一步 → `button_banner`
  - 其他 → `checklist_steps`
- 让 `get_scene_body` 在 `_template_checklist_cta` 入口按 `layout_variant` dispatch 到 4 个 render 函数。
- 新增 3 个 GSAP 适配器（`_gsap_cta_button_banner / _gsap_cta_end_score_goodbye / _gsap_cta_scorecard`）保持与现有 GSAP 调度风格一致。

### P3.2 GSAP 动效层评估（批次 7）

- 调研结论：`get_scene_gsap` 当前只被已废弃的 `combined_html_builder.py` 消费，Native Preview 主线（`studio_native_project_builder`）不消费 GSAP。
- 按用户"如破坏稳定性就停止扩大范围"原则，**不**将 GSAP timeline 注入到 Native Preview HTML。`get_scene_gsap` 函数体与 seed GSAP 字符串保留作为未来扩展点。
- 评估理由：当前 `sync_report.json` `max_drift=0.0s` 是 native data-attribute driven 的稳定基线；注入 GSAP 后时间偏移会引入额外漂移。

### 本轮验证（批次 7）

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -q`：`47 passed in 124.13s`
- `PYTHONPATH=src .venv/bin/python3 -m compileall -q src tests`：通过
- `git diff --check`：通过
- 真实 preview：`demo_v3_preview` 继续 `READY`（`can_approve_preview=true`）
- 真实 smoke render：`outputs/demo_v3_preview/rendered_smoke/final_video_smoke.mp4` `PASS`，`duration=5.00s`，视频流 / 音频流存在
- `outputs/demo_v3_preview/rendered_smoke/sync_report.json`：`status=PASS`，`max_drift=0.0s`
- CTA 路由验证：构造 4 类 narration 触发 4 种 layout_variant，单元测试 + 真实路径双重确认

### P3.3 Template Registry MVP（批次 8）

- 6 个新 seed 模板全部完成（独立 id + 独立 render_template）：
  - `scene.method.framework_quadrant` → `framework_quadrant`（2x2 四象限 + 中心 Hub）
  - `scene.method.decision_tree` → `decision_tree`（Y/N 决策树 + outcomes）
  - `scene.evidence.metric_dashboard` → `metric_dashboard`（4 指标 + delta）
  - `scene.evidence.case_study_card` → `case_study_card`（before/after + highlights）
  - `scene.proof.section_board` → `section_board`（4 维度板块）
  - `scene.proof.comment_question` → `comment_question`（评论卡 + 引导问题）
- 全部 6 个新模板在 `_TEMPLATES / _CSS_FUNCTIONS / _GSAP_FUNCTIONS` 三个 registry 全部注册。
- `ROLE_DEFAULT_TEMPLATE` 显式覆盖 6 个新角色：`framework / decision / metric / example / board / comment`。
- 新增 `ROLE_NARRATION_OVERRIDE` 路由表 + `_pick_seed_id` 函数：按 narration 关键词在 method/evidence/proof/explain 角色下路由到 6 个新 seed。
- 新增 12 个 helper 函数（`_framework_quadrant_data_from_narration` 等）为 6 个新模板生成 narrative-aware 数据。
- 端到端 P3.3 demo 验证：构造含"四象限/效率提升/三个维度/你愿意告诉我"关键词的短文案，6 个新 seed 全部命中。

### 本轮验证（批次 8）

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -q`：`56 passed in 119.99s`（从 47 → 56）
- `PYTHONPATH=src .venv/bin/python3 -m compileall -q src tests`：通过
- `git diff --check`：通过
- 真实 preview（`demo_v3_preview` 现有 demo 文案）：`READY`，`can_approve_preview=true`，12 scene 路由保持稳定
- 端到端 P3.3 demo 验证（`p33_demo_preview`）：6 句短文案命中 4 种新 seed（`framework_quadrant / metric_dashboard / decision_tree / checklist_cta`）
- 真实 5s smoke render：`outputs/demo_v3_preview/rendered_smoke/final_video_smoke.mp4` `PASS`，`duration=5.00s`
- `sync_report.json`：`status=PASS`，`max_drift=0.0s`

### P3.4 Template Library Expansion（批次 9）

- 8 个新 seed 模板全部完成（独立 id + 独立 render_template）：
  - `scene.hook.countdown_strike` → `countdown_strike`（3-2-1 倒数 + GO 按钮）
  - `scene.hook.keyword_punchline` → `keyword_punchline`（超大关键词 + 金句）
  - `scene.pain.data_dense_table` → `data_dense_table`（4 行状态表 + 状态色）
  - `scene.method.step_ladder` → `step_ladder`（4 步阶梯渐变 + 圆形编号）
  - `scene.method.concept_layers` → `concept_layers`（L1/L2/L3 概念分层 + 渐变宽度）
  - `scene.evidence.progress_tracker` → `progress_tracker`（3 条 8 周进度条 + delta %）
  - `scene.proof.knowledge_graph` → `knowledge_graph`（6 节点 + 7 边 + 中心节点）
  - `scene.cta.quote_close` → `quote_close`（金句大卡 + attribution + action）
- 全部 8 个新模板在 `_TEMPLATES / _CSS_FUNCTIONS / _GSAP_FUNCTIONS` 三个 registry 注册。
- 协议层补全：`MOTION_PRESETS` 9 个（`kinetic_title_burst / marker_sweep / card_stagger / count_up / flow_draw / table_stream / node_pulse / graph_rise / quote_reveal`）；`TRANSITIONS` 13 个（`glow_shift / fade_slide_bridge / scan_reveal / slide_bridge / soft_wipe / line_draw_bridge / panel_slide_bridge / final_hold_fade / cards_to_flow / flow_to_table / metric_to_compare / radial_focus_shift / zoom_through`）。
- `ROLE_DEFAULT_TEMPLATE` 显式覆盖 8 个新角色：`countdown / punchline / table / ladder / layers / progress / graph / close`。
- `ROLE_NARRATION_OVERRIDE` 扩展 8 个新 seed 的 keyword 路由表（含 hook / pain / method / evidence / proof / cta 全部家族）。
- `narration_planner.classify_role` keyword 扩展：HOOK/METHOD/EVIDENCE/PROOF/CTA 全部加新关键词，让 8 个新 seed 在真实脚本上可达。
- 新增 8 个 narrative-aware 数据生成 helper（`_countdown_steps_from_narration / _keyword_punchline_from_narration / _data_dense_rows_from_narration` 等）。
- 端到端 demo 验证：`demo_v3_preview` S06 "用双向链接组织笔记...形成知识网络" 命中 `scene.proof.knowledge_graph`（route 真实跑通）。

### 本轮验证（批次 9）

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -q`：`73 passed in 122.30s`（从 56 → 73，新增 17 个：routing 8 + render-distinct 1 + data-helper 1 + protocol 4 + classify_role 3）
- `PYTHONPATH=src .venv/bin/python3 -m compileall -q src tests`：通过
- `git diff --check`：通过
- 真实 preview（`demo_v3_preview`）：`READY`，`can_approve_preview=true`，12 scene 中 S06 已成功路由到 `knowledge_graph` 新 seed
- 真实 5s smoke render：`outputs/demo_v3_preview/rendered_smoke/final_video_smoke.mp4` `PASS`，`duration=5.00s`
- `sync_report.json`：`status=PASS`，`max_drift=0.0s`

### P3.5 Template Library Complete（批次 10）

- 10 个新 seed 模板全部完成（独立 id + 独立 render_template）：
  - `scene.hook.myth_bust` → `myth_bust`（迷思 + 真相 双卡）
  - `scene.hook.before_after_flash` → `before_after_flash`（前后指标大字号）
  - `scene.pain.timeline_pain` → `timeline_pain`（4 周时间线 + severity 颜色分级）
  - `scene.method.timeline_path` → `timeline_path`（4 里程碑时间线 + 渐变连线）
  - `scene.method.tool_stack` → `tool_stack`（3 层堆栈 + 渐变宽度）
  - `scene.evidence.case_study` → `case_study`（3 指标卡 + outcome）
  - `scene.evidence.evidence_cards` → `evidence_cards`（2x2 证据卡）
  - `scene.proof.score_panel` → `score_panel`（4 维度评分条 + verdict）
  - `scene.proof.next_step_board` → `next_step_board`（4 步行动板）
  - `scene.cta.comment_invite` → `comment_invite`（大引导问题 + 行动）
- 全部 10 个新模板在 `_TEMPLATES / _CSS_FUNCTIONS / _GSAP_FUNCTIONS` 三个 registry 注册。
- 协议层补全：`MOTION_PRESETS` 9 → 14（+5：`parallax_drift / scan_focus / depth_push / glow_breathe / check_pop`）。`TRANSITIONS` 维持 13（已达 12+ 目标）。
- 路线图资产目标达成：**30 seed + 14 motion + 13 transition = 57 资产**（超过 56 目标）。
- `ROLE_DEFAULT_TEMPLATE` 显式覆盖 10 个新角色；`ROLE_NARRATION_OVERRIDE` 扩展 10 个新 seed 的 keyword 路由（含 hook/pain/method/evidence/proof/cta 全部家族）。
- 新增 10 个 narrative-aware 数据生成 helper（`_myth_bust_pair_from_narration` 等）。

### 本轮验证（批次 10）

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -q`：`85 passed in 127.22s`（从 73 → 85，新增 12 个：P3.5 routing 10 + protocol 1 + role-default 1 + render-distinct 0 + data-helper 0，P3.5 测试在 test_template_protocol 中展开；新增测试由 append 引入 11 个，原始 73 + 11 + 1 = 85）
- `PYTHONPATH=src .venv/bin/python3 -m compileall -q src tests`：通过
- `git diff --check`：通过
- 真实 preview（`demo_v3_preview`）：`READY`，12 scene 路由保持稳定（S06 命中 `knowledge_graph`）
- 真实 5s smoke render：`outputs/demo_v3_preview/rendered_smoke/final_video_smoke.mp4` `PASS`，`duration=5.00s`
- `sync_report.json`：`status=PASS`，`max_drift=0.0s`

### 资产清单（P3.5 完成）

- 30 场景框架
- 14 动效预设
- 13 语义转场
- 合计 57 资产
- 86 个测试基线
- sync drift 0.0s

### P3.6 Viral QA Loop（批次 11）

- 实现 `viral_qa_evaluator.py`（`src/video_director_v3/qa/`）：
  - 6 维评分（每维 0-10 分，总分 60，PASS 阈值 42 + 0 failed）
  - **hook**：首句长度 + 冲击词命中 + emphasis_words + hook visual 模板
  - **promise**：前 2-3 句的方法信号（我会 / 告诉你 / 步骤 / 怎么用 等）
  - **saveable_value**：可复用结构关键词（步骤 / 清单 / 复盘 / 框架 / 象限 等）
  - **comment_trigger**：自然评论引导（你愿意 / 评论区 / 告诉我 等）+ 惩罚机械诱导词（点赞 / 关注）
  - **visual_rhythm**：unique visual_templates / scenes 比例 + 30 模板库就绪 bonus
  - **sync_reliability**：从 `sync_report.json` max_drift 反向（0.0s=10 分，>1.0s=0 分）
- A/B 路由 manifest：`ab_variants` 给出当前 hook + 2 个候选 hook 变体 + method/evidence/cta 各 2 候选；不实际渲染两套 HTML（避免成本爆炸），只是选种清单
- 接入 `pipeline_runner`：每个 preview 流程自动写出 `viral_quality_report.json`
- 报告含 disclaimer 明确"不冒充平台推荐算法"
- 新增 25 项测试覆盖：6 维评分边界 + A/B manifest + 真实 demo 路径

### 本轮验证（批次 11）

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -q`：`110 passed in 120.85s`（从 85 → 110，新增 25 个 viral_qa 测试）
- `PYTHONPATH=src .venv/bin/python3 -m compileall -q src tests`：通过
- `git diff --check`：通过
- 真实 preview（`demo_v3_preview`）：`READY`，`viral_quality_report.json` 自动生成（status=FAIL, total=26/60）
- 真实 5s smoke render：`outputs/demo_v3_preview/rendered_smoke/final_video_smoke.mp4` `PASS`，`duration=5.00s`
- `sync_report.json`：`max_drift=0.0s`，`viral_quality_report.json` 中 `sync_reliability=10/10`
- 端到端 P3.6 真实路径验证：viral_qa evaluator 在真实 demo 文案上能区分强项（sync 满分）和弱点（hook/promise/comment 内容结构偏弱）

### V3 路线图完整状态（全部 6 阶段 PASS）

| 阶段 | 状态 | 关键交付 |
|------|------|---------|
| P3.0 产品基线冻结 | PASS | 路线图 + 状态文档 + AGENTS 规范 |
| P3.1 Audio-First | PASS | 自然语速 TTS + 真实音频时长 + sync_report |
| P3.2 Dynamic Storyboard | PASS | 12 scene / 11 transition / 26 caption + 6 批次优化 |
| P3.3 Template Registry MVP | PASS | 12 seed templates（首批）|
| P3.4 Template Library Expansion | PASS | 20 seed templates（+8）|
| P3.5 Template Library Complete | PASS | 30 seed templates（+10）达成 57 资产 |
| P3.6 Viral QA Loop | PASS | 6 维评分 + A/B manifest + viral_quality_report |

### V3 Retrospective + Cleanup（批次 12）

- **清理 129 个 untracked 文件**：
  - 112 个调试 JS（`_check_audio*.js` / `_test_*.js` / `_screenshot*.js` 等）→ `tests/manual_archive/` + gitignore
  - 9 个正式资产 add 到 git：`viral_script_distiller.py` / `native_mp4_renderer.py` / `test_native_sync_report.py` / 2 demo 脚本 / HUD 提炼文档 / 路线图 / V2 视觉库存
  - 8 个旧路线文件（`scripts/build_v3_p28_clean_preview.py` / `scripts/v3_to_remotion.py` / `task_plan.md` / `findings.md` / `remotion_templates/` / `src/...egg-info/` / `.learnings/` / `_chatgpt_handoff/`）→ gitignore
- **V3_RETROSPECTIVE.md**（`docs/decisions/`）：6 阶段判断/教训/统计/V4 方向建议
  - 关键判断：复用优先 / 协议层分离 / 真实数据驱动 / 解释优先于绕过
  - V4 候选：V4.0 真实数据 / V4.1 跨平台 / V4.2 内容反向工程
- **V3_CAPABILITY_INDEX.md**（`docs/`）：63 资产盘点（30 场景 + 14 动效 + 13 转场 + 6 QA）+ 110 测试 + 0.0s drift 基线 + 文件入口

### 本轮验证（批次 12）

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/ -q`：`110 passed in 120.60s`（cleanup 0 回归）
- `PYTHONPATH=src .venv/bin/python3 -m compileall -q src tests`：通过
- `git diff --check`：通过
- 真实 preview（`demo_v3_preview`）：`READY`，viral_quality_report.json 自动生成
- 真实 5s smoke render：`PASS`，`duration=5.00s`
- `sync_report.json`：`max_drift=0.0s`

### 2026-06-04 P4.1B-R2 预审与规划

- 读取用户新请求全文，确认目标是先做规划，再做 debug cleanup + 成熟组件复用 smoke。
- 已更新 `task_plan.md`，新增 `P4.1B-R2 Debug Cleanup + Mature Visual Component Reuse Smoke` 阶段。
- 当前工作区检查结果：
  - `git status --short` 仅显示当前正式改动 + 既有历史/实验未跟踪项；
  - `patches/p4_1b_r2_debug_patch.diff` 在仓库中不存在，`git apply --check` 失败原因是 patch file missing。
- 当前代码审计发现仍残留：
  - `publish_templates.py` 的 strategy debug meta 可见；
  - `studio_native_project_builder.py` 内存在 `hf-beam` / `scan-sweep` 横线动画；
  - `caption_mode` 仍需要进一步拉开视觉差异；
  - 旧 HUD 成熟组件还没有在 smoke preview 里被明确复用。
- 下一步执行顺序已经明确：
  1. 手动等价实现 patch 意图；
  2. 去掉 debug meta 和扫描线；
  3. 强化 caption mode 差异；
  4. 让 2-3 个旧 HUD 组件在 `p4_batch_ai_toolflow.md` smoke preview 中真实复用；
  5. 生成 `P4_1B_R2_DEBUG_CLEANUP_AND_COMPONENT_REUSE_SMOKE.md` 报告；
  6. 跑测试、compileall、git diff --check，并准备提交。
