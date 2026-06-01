# HUD Template Extraction

## Scope

来源分两部分：

1. 系统现有模板
   - `src/video_director_v3/renderers/hyperframes/publish_templates.py`
   - `remotion_templates/hud_explainer/src/components/HudPrimitives.tsx`
   - `remotion_templates/hud_explainer/src/scenes/*.tsx`
2. 外部参考截图
   - `/Users/muzi/Windows共享文件/视频效果分析`
   - 当前已抽取 79 张中的代表性批次，并确认后段主要是前段骨架的主题变体，而不是全新模板家族

本文件只提炼 HUD 样式、框架、布局、动效语法和文案场景关联，不讨论真人主体。

## 现有系统基线

- `hook_big_claim`
  - 大标题居中，关键词高亮
- `pain_card_stack`
  - 纵向信息卡堆叠
- `broken_chain`
  - 链路断裂/环节诊断
- `tool_chain_three_cols`
  - 三列流程；现已拆出 `three_col_row / source_ingest / knowledge_triangle / vertical_flow`
- `before_after_compare`
  - 左右对比
- `checklist_cta`
  - 纵向清单 CTA

当前系统长处：

- 颜色语义清晰：红=问题，绿=结果，蓝=解释，黄=收益
- 深色背景 + 玻璃卡片 + 发光边框，适合知识型口播
- 现有模板已经能覆盖 Hook / Pain / Method / Evidence / CTA 主链

当前系统缺口：

- 评论引用开场
- 大数字 + 小图表的结论先行
- 顶部案例卡轮播
- 收入阶梯 + 证据页卡
- 双曲线增长
- 二选一路径分流
- 术语课程化章节进度
- 看板/监控面板类 proof

## 提炼出的模板家族

### Hook

1. `hook.keyword_punchline`
- 大关键词冲击，单词或短语局部着色
- 适配：反常识开场、概念命名、方法名、痛点命名
- 动效：主词 0-6f 放大弹出，副词延迟淡入

2. `hook.comment_quote`
- 大号评论/质疑引用卡，形成冲突
- 适配：观众质疑、用户原话、真实评论切入
- 动效：评论框先入，关键词二次着色闪烁

3. `hook.big_number_claim`
- 左侧超大数字，右侧辅助图或短注释
- 适配：市场规模、效率提升、节省成本、爆款结果
- 动效：数字计数 / scale-up，图表延迟生长

### Pain / Contrast

4. `pain.progress_gap`
- 多条横向进度条，表达能力差距/普及率/市场错位
- 适配：认知差距、技能普及率、工具使用落差
- 动效：条形从左向右填充

5. `pain.abstract_to_plain`
- 左旧右新，复杂 -> 通俗，抽象 -> 易懂
- 适配：解释术语、纠偏、认知升级
- 动效：旧卡先显示，新卡带箭头切换

6. `pain.version_upgrade`
- AI 1.0 -> AI 2.0 一类版本迁移 + 风险提示条
- 适配：旧方法过时、新方法升级、粗糙到自然
- 动效：箭头推进，警告条从下方滑入

### Method

7. `method.step_tabs_paths`
- 多步骤或多路径，当前步骤高亮，其他灰化
- 适配：三条路径、流程分段、方法树
- 动效：当前步骤 glow，标签逐个点亮

8. `method.binary_choice_split`
- 左右双卡二选一，中间 `OR`
- 适配：两种做法、自己做 vs 对标、手动 vs 自动
- 动效：双卡对称入场，中间 `OR` 后跳出

9. `method.three_principles_cards`
- 3 张并列认知卡
- 适配：三件套、三原则、三要素
- 动效：卡片级联淡入

10. `method.vertical_flow`
- 纵向步骤流，适配已有 `tool_chain_three_cols.vertical_flow`
- 适配：执行步骤、Agent 流程、脚本到发布链路
- 动效：节点逐格落下，连接箭头后显

11. `method.knowledge_triangle`
- 三点关系图，适配已有 `knowledge_triangle`
- 适配：角色关系、观点/例子/方法互联、桥接逻辑
- 动效：节点先入，连接线再绘制

12. `method.matrix_glossary_wall`
- 6-10 个术语/卡片组成矩阵
- 适配：术语扫盲、模块一览、知识全景图
- 动效：卡片 stagger + 轻微摇摆

### Evidence / Proof

13. `evidence.money_ladder`
- 收入阶梯 / 路径升级，旁边挂证据页卡或截图
- 适配：变现路径、阶段式升级、商业模型拆解
- 动效：柱状图自下而上，证据图后入

14. `evidence.dual_curve_growth`
- 两条增长曲线，表达双轮增长
- 适配：流量与产品、效率与质量、播放与转化同步增长
- 动效：曲线描边动画

15. `evidence.dashboard_mobile`
- 手机长截图 + 左侧大标题/指标
- 适配：后台监控、数据看板、真实证据、产品实拍
- 动效：手机 mockup 侧滑入场

16. `evidence.scorecard_sheet`
- 左侧大分数/维度清单，右侧表格截图
- 适配：评测打分、审查结果、内容质检
- 动效：分数先弹出，表格 fade-in

17. `evidence.parallel_lanes`
- 多条并行条形 lane，表达多线程/多模块协同
- 适配：多 Agent 并行、四模块协作、流水线并发
- 动效：各条并发填充

18. `proof.section_board`
- 多板块看板，适合“5 个栏目 / 5 个板块 / 9 个维度”
- 适配：内容栏目设计、评估维度、功能模块
- 动效：板块按行/列分组进入

19. `proof.symptom_panel`
- 左侧术语编号，右侧症状/风险说明条
- 适配：AI 幻觉、错误诊断、问题清单
- 动效：编号固定，症状条逐条亮起

### CTA

20. `cta.button_banner`
- 大标题 + 单个按钮式行动条
- 适配：开始、继续、收藏、下一步
- 动效：按钮脉冲 / 边框发光

21. `cta.end_score_goodbye`
- 左侧完成分数，右侧下一集提示
- 适配：系列结尾、章节结尾、视频收束
- 动效：分数定格，下一集按钮稍后弹出

## 文案场景路由建议

基于 `LLM_Knowledge2.0/wiki` 的内容结构，建议把文案先归到这些场景，再匹配模板：

- `hook.question_conflict`
  - 参考：`金句七法` 的否定法、反常识表达
  - 首选模板：`hook.keyword_punchline` / `hook.comment_quote`

- `hook.number_result`
  - 参考：`抖音AI短视频全链路2026` 的单人日产量、月成本、时间压缩
  - 首选模板：`hook.big_number_claim`

- `pain.complexity_gap`
  - 参考：术语难懂、AI 味、抽象概念
  - 首选模板：`pain.abstract_to_plain` / `pain.progress_gap`

- `method.path_or_step`
  - 参考：`AI短视频自动化工作流` 的 5 步流程
  - 首选模板：`method.step_tabs_paths` / `method.vertical_flow`

- `method.choice`
  - 参考：不同执行方式、低成本路径 vs 标准路径
  - 首选模板：`method.binary_choice_split`

- `method.three_points`
  - 参考：`中文口语三件套`、三大原则、三大支柱
  - 首选模板：`method.three_principles_cards`

- `explain.term_glossary`
  - 参考：术语扫盲、课程型内容、10 大术语
  - 首选模板：`method.matrix_glossary_wall` / `proof.symptom_panel`

- `evidence.market_or_growth`
  - 参考：市场规模、CAGR、成本变化、双轮增长
  - 首选模板：`evidence.money_ladder` / `evidence.dual_curve_growth`

- `proof.dashboard_or_case`
  - 参考：真实后台、预测面板、监控、评分表
  - 首选模板：`evidence.dashboard_mobile` / `evidence.scorecard_sheet`

- `proof.parallel_system`
  - 参考：多 Agent、多模块并行
  - 首选模板：`evidence.parallel_lanes`

- `cta.start`
  - 首选模板：`cta.button_banner`

- `cta.series_end`
  - 首选模板：`cta.end_score_goodbye`

## 动效共识

这些参考图虽然是静帧，但明显共享一套动效语言：

- 标题：`scale + fade + light sweep`
- 卡片：`stagger fade-in`
- 图表：`bar grow / line draw / progress fill`
- 关系：`arrow draw / connector reveal`
- CTA：`pulse glow`
- 系列进度：`step dots / page count / n of m`

后续实现时，优先做“少量动效原语 + 多模板复用”，不要为每个模板单独发明一套动画系统。
