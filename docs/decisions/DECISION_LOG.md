# DECISION LOG

## 决策记录

---

### 决策 1：建立 video-director-v3 新项目

**日期**：2026-05-29
**内容**：建立 video-director-v3 作为新项目，不沿用旧项目的混乱目录结构
**理由**：旧项目（video-director-v2）目录混乱，outputs 散落多个位置
**结果**：V3 固定输出目录为 `outputs/<project_id>/` 和 `test_outputs/<project_id>/`

---

### 决策 2：V3 主线是 preview → approval → MP4

**日期**：2026-05-29
**内容**：V3 唯一主线：`script.md → hyperframes_preview → approval_required.json → render_mp4 → final_video.mp4`
**理由**：用户明确不需要 talking-head overlay、CapCut draft、content_pack
**结果**：所有开发围绕这个主线

---

### 决策 3：不使用 content_pack 作为主线

**日期**：2026-05-29
**内容**：content_pack 不是 V3 方向
**理由**：用户明确要做的是视频生成管线，不是素材管理
**结果**：V3 专注 HTML 预览 + MP4 渲染

---

### 决策 4：不使用 combined/index.html 路线（已废弃）

**日期**：2026-05-29
**内容**：combined/index.html 使用定制 GSAP 时间轴架构，不支持 HyperFrames Studio native preview
**理由**：V3 早期决策，已被 V3-P2.7 决策覆盖
**结果**：❌ 已废弃。V3 唯一预览路线为 HyperFrames Studio 原生项目预览，不再使用 combined/index.html / file:// 路线

---

### 决策 5：使用 Playwright + FFmpeg + HyperFrames Studio Native Preview

**日期**：2026-05-29
**内容**：渲染方案使用 Playwright 捕获帧 + FFmpeg 编码；预览使用 HyperFrames Studio 原生项目
**理由**：成熟方案 + 复用 Studio 能力
**结果**：V3 主线为 Studio Native Preview → Approval → MP4 render

---

### 决策 6：输出目录固定为 outputs/ 和 test_outputs/

**日期**：2026-05-29
**内容**：禁止写入 `src/outputs/` 或散落临时目录
**理由**：保持项目整洁，避免混淆
**结果**：所有产物在 `outputs/<project_id>/`

---

### 决策 7：设计技能作为 Design Profile 层

**日期**：2026-05-29
**内容**：stitch-skill / brandkit / imagegen 作为 Design Profile 层，不替代 video pipeline
**理由**：设计技能提供风格指导，不直接参与视频生成
**结果**：V3 接入 design_dials（DESIGN_VARIANCE / MOTION_INTENSITY / VISUAL_DENSITY）

---

### 决策 8：所有长期记忆写入 docs/status

**日期**：2026-05-30
**内容**：不依赖 Claude 会话记忆，所有关键信息写入 `docs/status/*.md`
**理由**：智能体重启、换会话、换模型后需要可快速理解项目状态
**结果**：建立 docs/status/ 目录，包含 PROJECT_STATE / CURRENT_BUGS / LAST_KNOWN_GOOD / NEXT_TASK / TASK_LOG

---

### 决策 9：当前优先级：先修音频 mux，再修 clean render，再做视觉增强

**日期**：2026-05-30
**内容**：修复顺序：音频 mux (P0) → clean render (P1) → motion validation (P2) → 视觉增强
**理由**：音频是基础功能，clean render 影响产品观感，视觉增强是锦上添花
**结果**：NEXT_TASK.md 明确 V3-D2.0-A 为当前任务

---

### 决策 10：本阶段不做视频修复

**日期**：2026-05-30
**内容**：本阶段专注建立记忆系统和交接文档，不修复视频无声音问题
**理由**：用户明确要求先建立记忆系统
**结果**：视频无声音问题标记为 P0 但暂停，等待下一阶段

---

最后更新：2026-05-30

---

### 决策 11：视频时长改为 Audio-First

**日期**：2026-06-01
**内容**：取消 40 秒和 `38-43s` 硬约束。自然语速 TTS 的真实时长决定视频时长。
**理由**：用户明确要求根据文案长度灵活调整，不为了指标加速语音。
**结果**：P3.1 删除旧时长 Gate，新增同步探针。

---

### 决策 12：分镜数量改为内容驱动

**日期**：2026-06-01
**内容**：不再固定生成 6、7、8 个场景。根据语义节拍和真实音频动态生成分镜、字幕和转场。
**理由**：固定场景会削弱信息表达和短视频节奏。
**结果**：P3.2 实现 Dynamic Storyboard。

---

### 决策 13：建设 56 个模板资产

**日期**：2026-06-01
**内容**：分阶段建设 30 个场景框架、14 个动效预设、12 个语义转场，共 56 个资产。
**理由**：需要适配不同文案并形成视觉多样性，但不能一次性堆叠重复模板。
**结果**：P3.3 建协议和首批 12 个资产，P3.4 扩展到 36，P3.5 扩展到 56。

---

### 决策 14：爆款 QA 不冒充平台算法

**日期**：2026-06-01
**内容**：以 Hook、获得感、收藏价值、评论触发、视觉节奏和同步可靠性做发布前评分。
**理由**：平台推荐权重不公开，系统应优化可验证的内容质量指标。
**结果**：P3.6 建立 Viral QA 与 A/B 变体。

---

最后更新：2026-06-01

---

### 决策 15：长文先提炼，口播最长 2 分 30 秒

**日期**：2026-06-01
**内容**：公众号长文先提炼为短视频口播，目标 `<=120s`，硬上限 `<=150s`。TTS 保持自然语速 `+0%`，超长时删减次要信息并重新生成。
**理由**：用户明确要求短视频口播不要超过 2 分钟，最长不能超过 2 分 30 秒。
**结果**：新增 `viral_script_distiller.py` 与 TTS 150 秒硬 gate。指定 Obsidian 长文从 76 句提炼为 12 句、419 字，实际音频 `81.10s`。

---

### 决策 16：视觉基线沿用原 HUD 科技风

**日期**：2026-06-01
**内容**：正式 Native Preview 复用原有 HUD 科技风模板族：深色网格、扫描线、HUD 边框、卡片堆栈、链路节点、对比卡和 CTA 清单。
**理由**：用户明确要求分镜画面保持原来的 HUD 科技风。
**结果**：`studio_native_project_builder.py` 接入 `publish_templates.py`，简化占位画面不再作为发布基线。

---

最后更新：2026-06-01
