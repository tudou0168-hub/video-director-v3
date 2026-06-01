# V3-P3 爆款短视频生成系统路线图

## 1. 产品目标

目标不是生成一段固定长度的 HUD 动画，而是建立一条可持续迭代的短视频生产主线：

```text
中文文案
  → 爆款结构化口播
  → 自然语速男声 TTS
  → 真实音频时间轴
  → 动态字幕 / 动态分镜 / 视觉节拍
  → 模板路由 / 自然转场
  → HyperFrames Studio Native Preview
  → 人工审批
  → MP4 render + audio mux
  → 音画字幕同步验收
```

产品面向抖音等短视频平台。优化方向是：停留、看完、收藏、点赞、评论和复看。平台算法权重不公开，因此系统不猜权重公式，不承诺“必爆”，而是把公开可见的优质内容原则工程化。

## 2. 新基线

### 2.1 Audio First

- 不再设置 40 秒硬限制。长文先提炼为短视频口播，目标 `<=120s`，硬上限 `<=150s`。
- 不再为了命中时长加速语音。
- 不再为了命中时长机械压缩文案。
- 男声 TTS 默认自然语速：`rate = +0%`。
- 不允许为了时长加速 TTS；超长时删减次要信息并重新生成。
- `ffprobe(voiceover.mp3)` 是视频总时长唯一权威。
- Studio 预览暂时无声可以接受，但原生项目必须包含音频轨道，最终 MP4 必须完成 audio mux。

### 2.2 动态分镜

- 分镜数量不固定为 6、7、8 或其他数字。
- 分镜由语义节拍决定：Hook、痛点、反转、解释、方法、证据、案例、金句、CTA。
- Hook 段建议每 1.5-3 秒有视觉反应。
- 主体段建议每 3-5 秒有视觉变化。
- 复杂内容允许更长口播，但必须控制视觉疲劳，安排呼吸段。

### 2.3 同步 Gate

最终 MP4 必须生成 `sync_report.json`：

| 检查项 | Gate |
|---|---|
| MP4 视频流 | 必须存在 |
| MP4 音频流 | 必须存在 |
| 音频源时长 | `ffprobe` 可读取 |
| MP4 时长与音频源时长偏差 | `<= 1.0s` |
| 最后一条字幕尾点与音频尾点偏差 | `<= 1.0s` |
| 最后一个分镜尾点与音频尾点偏差 | `<= 1.0s` |
| 黑帧检查 | 不允许出现非设计性黑帧 |

## 3. 爆款结构原则

### 3.1 内容结构

```text
0-3s    Hook：利益点 / 冲突 / 反常识 / 强问题
3-6s    Promise：告诉观众继续看能得到什么
Body    Value：框架、步骤、案例、证据、对比
Close   CTA：收藏理由 + 自然评论问题 + 可执行动作
```

### 3.2 互动设计

| 行为 | 内容触发器 |
|---|---|
| 收藏 | 清单、步骤、模板、框架、复盘价值 |
| 点赞 | 强共鸣、认知刷新、清晰结果 |
| 评论 | 真实分歧、经验询问、场景选择题 |
| 复看 | 信息密度、流程图、对比表、可截图卡片 |

### 3.3 视觉原则

- 9:16 竖屏，始终遵守 UI safe zone。
- sound-on 为主，但字幕必须保证静音可理解。
- 分镜之间使用自然语义转场，不允许生硬跳切。
- 默认沿用原有 HUD 科技风；HUD、动效和特效服务于信息表达，不做纯装饰堆叠。
- 前 6 秒必须具有最强视觉密度。
- 主体段安排节奏波：`high → medium → low → high → close`。

## 4. 工程架构

```text
script.md
  ↓
viral_script_analyzer.py
  → narration_plan.json
  ↓
tts_adapter.py
  → audio/voiceover.mp3
  → audio_timeline.json
  ↓
dynamic_storyboard_builder.py
  → director_timeline.json
  → visual_beats.json
  ↓
caption_beat_generator.py
  → caption_beats.json
  ↓
semantic_transition_planner.py
  → transition_map.json
  ↓
template_registry.py + template_router.py
  → selected_templates.json
  ↓
studio_native_project_builder.py
  → hyperframes_timeline/
  ↓
approval_required.json
  ↓
render_mp4 --approved
  → rendered/final_video.mp4
  → rendered/sync_report.json
```

## 5. 分阶段落实

### P3.0 产品基线冻结

目标：让后续 Agent 不再沿用固定时长、固定分镜和旧 combined 路线。

交付：
- 本路线图。
- 更新状态文档、决策日志和 Agent 说明。
- 明确 P3.1 是唯一下一任务。

### P3.1 Audio-First 主线修复

目标：先完成一条可以真实交付的最小闭环。

改动范围：
- 删除 `38-43s` Gate。
- 删除 `target_duration` 对文案压缩和场景数量的控制；保留时长作为可选观察值，不作为硬约束。
- Edge TTS 使用自然语速 `+0%`。
- 生成音频后立即 `ffprobe`。
- 所有时间轴根据真实音频重新计算。
- 最终渲染读取 Studio Native 项目，不再读取 `combined/index.html`。
- 复用现有 FFmpeg mux 能力。
- 新增 `sync_report.json` 和 `volumedetect` 检查。

验收：
- 使用一篇真实长文生成自然语速男声。
- 输出 Studio Native Preview。
- 人工审批后生成 `final_video.mp4`。
- `ffprobe` 验证视频流和音频流存在。
- 同步误差 `<= 1.0s`。

### P3.2 Dynamic Storyboard

目标：从“固定场景播放器”升级为“内容驱动导演”。

改动范围：
- 文案分析输出：Hook、Promise、Pain、Insight、Method、Evidence、Example、CTA。
- 按语义段落和真实音频时间轴聚类分镜。
- 分镜数量动态生成。
- 字幕按可读短语拆分，绑定音频句级时间轴。
- 相邻分镜动态生成语义转场。
- 生成 `director_timeline.json`、`visual_beats.json`、`transition_map.json`。

验收：
- 30 秒、60 秒、90 秒三种文案均可生成。
- 三个样例场景数不同。
- 字幕、分镜和音频尾点偏差均 `<= 1.0s`。
- 每对相邻分镜都有转场策略。

### P3.3 Template Registry MVP

目标：先建立模板协议，再实现首批 12 个高频资产。

模板协议字段：

```json
{
  "id": "scene.hook.conflict_hero",
  "kind": "scene_framework",
  "semantic_roles": ["hook", "pain"],
  "content_shapes": ["question", "contrast", "single_metric"],
  "density": "high",
  "variables": ["headline", "subline", "accent", "metric"],
  "motion_preset": "motion.kinetic_title_burst",
  "compatible_transitions": ["transition.scan_reveal", "transition.glow_crossfade"],
  "preview_fixture": "fixtures/hook_conflict_hero.json"
}
```

首批资产：

| 类型 | 数量 | 内容 |
|---|---:|---|
| 场景框架 | 6 | Hook Hero、问题卡堆、流程链路、数据表格、前后对比、CTA 清单 |
| 动效预设 | 3 | 标题爆发、卡片 stagger、数字 count-up |
| 语义转场 | 3 | glow crossfade、scan reveal、cards-to-flow |

验收：
- 每个资产都有注册信息、变量协议、适用语义和截图 fixture。
- 路由器能根据文案 beat 选择资产。
- 同一文案可生成至少 2 个明显不同的视觉变体。

### P3.4 Template Library Expansion

目标：扩展至 36 个资产，覆盖常见知识型短视频。

累计资产：

| 类型 | 累计数量 |
|---|---:|
| 场景框架 | 20 |
| 动效预设 | 9 |
| 语义转场 | 7 |
| 合计 | 36 |

验收：
- 覆盖 AI 工具、职场效率、知识管理、自媒体方法、复盘清单五类内容。
- 每类至少 3 个可组合变体。
- 自动生成 contact sheet 做视觉回归。

### P3.5 Template Library Complete

目标：扩展至 56 个资产，达到可持续生产规模。

最终资产分布：

| 类型 | 数量 | 用途 |
|---|---:|---|
| 场景框架 | 30 | 负责内容表达结构 |
| 动效预设 | 14 | 负责动态多样性 |
| 语义转场 | 12 | 负责自然衔接 |
| 合计 | 56 | 落在用户要求的 50-60 区间 |

#### 30 个场景框架

| 类别 | 数量 | 模板 |
|---|---:|---|
| Hook | 8 | conflict_hero、question_hook、single_metric_alarm、myth_bust、before_after_flash、countdown、quote_slam、visual_mystery |
| 解释与方法 | 8 | process_chain、step_ladder、pipeline_nodes、framework_quadrant、concept_layers、timeline_path、tool_stack、decision_tree |
| 证据与价值 | 8 | data_table、metric_dashboard、case_study、comparison_split、score_panel、progress_tracker、evidence_cards、knowledge_graph |
| CTA 与收束 | 6 | checklist_close、saveable_summary、comment_question、action_plan、quote_close、next_step_board |

#### 14 个动效预设

`kinetic_title_burst`、`marker_sweep`、`card_stagger`、`count_up`、`flow_draw`、`node_pulse`、`table_stream`、`graph_rise`、`scan_focus`、`glow_breathe`、`depth_push`、`parallax_drift`、`check_pop`、`quote_reveal`

#### 12 个语义转场

`glow_crossfade`、`scan_reveal`、`cards_to_flow`、`flow_to_table`、`table_to_checklist`、`metric_to_compare`、`zoom_through`、`panel_slide_bridge`、`line_draw_bridge`、`radial_focus_shift`、`soft_wipe`、`final_hold_fade`

验收：
- 56 个资产全部注册。
- 不允许仅换颜色冒充新模板。
- 每个场景框架至少有一张 hero frame。
- 每个动效预设有确定性 timeline 测试。
- 每个转场预设有起点、终点和黑帧检查。

### P3.6 Viral QA Loop

目标：将爆款原则做成发布前质量门。

新增：
- `viral_quality_report.json`
- 结构评分：Hook、Promise、收藏价值、评论触发、视觉节奏、同步可靠性。
- A/B 输出：同一文案默认生成 2 个 Hook 版本和 2 个视觉版本。
- 发布复盘：手工录入或未来接入播放、完播、收藏、点赞、评论数据。

说明：
- 评分用于筛选和复盘，不冒充平台推荐算法。
- 数据反馈用于调整模板路由权重，不替代人工判断。

## 6. P3.1 实施顺序

1. 新增 Audio-First 契约测试。
2. 删除固定时长 Gate 和 TTS 加速。
3. 让 `ffprobe` 音频时长成为全局时间轴权威。
4. 将 Native Preview Builder 纳入正式 pipeline。
5. 将 MP4 render 切换到 Native Preview 项目。
6. 增加音频 mux、音频流、音量和同步探针。
7. 使用真实长文完成 preview → approval → MP4 smoke。
8. 人工听音并审查字幕、画面、分镜同步。

## 7. 当前不做

- 不一次性手写 56 个模板。
- 不继续扩展废弃的 `combined/index.html`。
- 不把预览静音误认为最终视频可以静音。
- 不为了时长加速语音或删减核心内容。
- 不承诺破解或命中平台算法。

## 8. 公开资料

- [抖音创作者中心](https://creator.douyin.com/creator-school?ug_source=seo_cjy)
- [新华网：2025 抖音创作者大会](https://www.news.cn/tech/20250924/187cfb6418bd4e8c94111c273cc2bbaf/c.html)
- [抖音精选：优质内容播放时长信息](https://jingxuan.douyin.com/m/video/7553160730091064628)
- [TikTok For Business: Creative best practices](https://ads.tiktok.com/help/article/creative-best-practices)
- [TikTok Creative Codes](https://ads.tiktok.com/business/de/creative-codes)
