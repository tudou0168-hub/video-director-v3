# V3-P2.6-HF HyperFrames-first 编排报告

## 1. 能力盘点

| 能力 | 是否存在 | 如何调用 | 本项目用途 |
| -- | ---- | ---- | ----- |
| `/hyperframes` | ✅ 符号链接存在 | `npx hyperframes preview <path>` | 视觉预览 / 渲染 / snapshot |
| `hyperframes-video-workflow` | ✅ SKILL.md 完整 | 读取 `~/.claude/skills/hyperframes-video-workflow/SKILL.md` | 工作流规范参考 |
| `hyperframes` CLI | ✅ 在 `~/.agents/skills/hyperframes/` | `npx hyperframes <cmd>` | render / snapshot / tts / transcribe |
| `hyperframes-registry` | ✅ | `npx hyperframes catalog` | 浏览转场/特效注册表 |
| `hyperframes-media` | ✅ | `npx hyperframes remove-background` | 视频去背景 |
| `remotion-to-hyperframes` | ✅ 符号链接 | 转换 Remotion 项目为 HyperFrames | Remotion → HyperFrames 迁移路径 |
| `frontend-design` | ✅ | `Skill: frontend-design` | 生成 HUD 风格 HTML 组件 |
| `design-html` | ✅ | `Skill: design-html` | 生成 HTML 视觉分镜 |
| `gsap-*` 系列 | ✅ 7 个子技能 | `gsap-core`, `gsap-timeline`, `gsap-react` 等 | 强化 GSAP 动画细节 |
| `superdesign-integration` | ✅ | `Skill: superdesign-integration` | UI mockup / 组件生成 |
| `taste-skill` | ✅ | `Skill: taste-skill` | 审美评审 |
| `design-review` | ✅ | `Skill: design-review` | 设计问题诊断 |
| `awesome-claude-design` | ✅ | `Skill: awesome-claude-design` | 9 种美学风格参考 |
| `Remotion` | ✅ 已集成 | 直接修改 TSX | 仅承接渲染，不做视觉设计 |
| `website-to-hyperframes` | ✅ 符号链接 | 转换网页为 HyperFrames | 可将参考视频截图转为 HTML 资产 |

---

## 2. 当前方向修正

### 为什么不继续手搓 Remotion HUD

当前 Remotion 版本（P2.6-S2）的核心问题：

1. **背景太空** — GlowBackground 只有简单 radial gradient + 模糊 UI 层，缺少"内容生产驾驶舱"的空间密度
2. **HUD 组件风格扁平** — HudPrimitives 的 GlassPanel / StatusBadge / BigMetric 是通用组件池，不是针对本项目内容的专业 HUD 设计
3. **信息密度不够** — 参考视频有截图、表格、进度条、状态徽章、评分条交织，本项目只有列表 + 大字体
4. **字体系统薄弱** — 系统字体 + text-shadow，缺少专业 HUD 等宽字体、数据字体层级
5. **动效系统感不足** — spring 动画太机械，缺少 scan/glitch/数据涌入/光效脉冲

**本质问题：Remotion 不是为电影感 HUD 包装设计的工具**，它是时间轴 + 渲染引擎。手写 TSX 组件永远无法达到参考视频那种"截图 + 数据叠层 + 暗色调 + 局部光效"的视觉密度。

### 为什么优先 HyperFrames

HyperFrames 的核心优势：

- **HTML 是真相来源** — AI 最擅长的领域，丰富的 CSS/GSAP 生态
- **视觉密度无上限** — 可以嵌入真实截图、数据表格、进度条、评分卡，任何 HTML/CSS 都能叠
- **GSAP 时间轴精度** — 逐帧 seek 精确渲染，支持确定性动画
- **已有 `remotion-to-hyperframes` 迁移路径** — Remotion smoke 可以作为 HyperFrames 的 track-0 视频层
- **本机已有完整工具链** — hyperframes CLI、GSAP 系列技能、design-html、frontend-design 全部可用

### Remotion 后续只负责什么

1. **时间轴** — 18s smoke duration + 场景切换时间点
2. **音频承接** — TTS 音频轨道 + 字幕时间轴
3. **track-0 视频层** — 如果用 HyperFrames 替代 Remotion 做视觉，Remotion 只负责最终 MP4 输出
4. **不做视觉设计** — 禁止继续在 Remotion TSX 里研发新 HUD 组件

**推荐架构：HyperFrames 做视觉导演（合成 + 动画），Remotion 做最终渲染承接（如果还需要）。**

---

## 3. 推荐技能编排链路

```
文案脚本（已有）
  ↓
design-html / frontend-design
  → 生成 6 张 HTML styleframes（1080x1920）
  → 每次生成 1 张，快速迭代
  ↓
gsap-core / gsap-timeline
  → 为每张 styleframe 添加 GSAP 动画
  → scan / glitch / 数据涌入 / 光效脉冲
  ↓
taste-skill / design-review
  → 审美评审 6 张 styleframes
  → 选出 1-2 套接近参考样例的方案
  ↓
HyperFrames preview
  → 打开 HTML 验证动态效果
  → snapshot 截取 6 个关键帧
  ↓
Remotion 承接（可选）
  → 如果 HyperFrames smoke 渲染满意
  → 用 Remotion 做最终 MP4 输出
  → 或者直接用 HyperFrames render MP4
```

**本轮不做 Remotion TSX 修改。**

---

## 4. 6 个 HyperFrames 场景提示词

---

### Scene 1 — Hook / 痛点扫描

**visual objective:**
让用户 1 秒停住。制造"素材爆仓"的紧迫感和压迫感。

**layout:**
- 9:16 竖屏 (1080x1920)
- 全局暗色背景 + 多层 radial glow
- 顶部：系统状态栏（HUD 风格标签）
- 左侧中部：999+ 超大数字指标（红色 glow）
- 右侧：素材来源列表（微信收藏/浏览器书签/读书笔记/临时截图）
- 底部：主标题大字（2 行，"收藏越多，为什么越写不出来？"）
- 结论条：底部 96px 处

**HUD elements:**
- 系统状态标签：OVERLOAD (danger)
- 超大数字：999+ (red glow, 136px)
- 素材列表卡片：半透明玻璃面板，每行右侧状态徽章
- 进度指示线：红色，左侧竖向
- 模拟素材库截图区域：模糊卡片堆叠（右下角）

**motion:**
- 场景开始：scan line 从上到下扫过（0.3s）
- 999+ 数字：scale 0.85→1 + glow pulse (0.5s, back.out)
- 素材列表：从右滑入，每行 delay 0.1s
- 标题：从下滑入 (0.4s, expo.out)
- ambient: 背景 glow 缓慢脉动 (3s ease-in-out, repeat)

**text content:**
- HEADLINE: "收藏越多，为什么越写不出来？"
- METRIC: "999+"
- LABEL: "未归档素材"
- STATUS: "OVERLOAD"
- MATERIAL LIST: 微信收藏 999+ | 浏览器书签 500+ | 读书笔记 100本 | 临时截图 200+
- CONCLUSION: "素材越多，不等于更容易开写"

**forbidden:**
- 白色背景
- 纯文字海报风格
- 居中对称布局
- 无 glow 无脉动

**expected styleframe:**
暗色系 + 红色警报光 + 大标题压迫感 + 右侧素材爆仓列表 + 左下角超大 999+ 指标

---

### Scene 2 — Pain / 素材明细

**visual objective:**
展示"资料越多，越乱"的混乱全景。

**layout:**
- 顶部：系统状态 "SYSTEM ANALYZING" (danger)
- 左侧：超大数字 999+ 未归档素材 + MATERIALS STACKED sublabel
- 中下部：8 行数据表格（平台 / 数量 / 状态）
- 右侧：无（留给背景层）
- 底部：结论条

**HUD elements:**
- 状态徽章：SYSTEM ANALYZING (danger, animated pulse)
- BigMetric：999+ (red, 136px)
- DataTable：8 行，平台 | 数量 | 状态徽章
- 扫描条：顶部进度动画
- 背景：多层 radial glow（红色系）+ 扫描线
- 模糊素材卡：左下角背景层

**motion:**
- 场景开始：扫描线从上到下 (0.4s)
- BigMetric：数字从 0 跳到 999+ (1s, power4.out)
- 表格行：逐行淡入，每行 delay 0.08s (stagger)
- 状态徽章：脉冲动画 (持续)
- ambient: 红色 glow 缓慢脉动

**text content:**
- HEADER: "素材明细" / "未归档素材正在堆积"
- BIG METRIC: "999+" / "未归档素材" / "MATERIALS STACKED"
- TABLE ROWS:
  - 微信收藏 | 999+ 条 | WARNING
  - 浏览器书签 | 500+ 条 | WARNING
  - 读书笔记 | 100 本 | UNSTRUCTURED
  - 会议录音 | 找不到 | HIGH RISK
  - 临时截图 | 200+ | UNTAGGED
  - 公众号收藏 | 300+ | UNSORTED
  - 课程笔记 | 50+ | PENDING
  - 脑暴记录 | 80+ | CHAOS
- CONCLUSION: "资料越多，开写越慢"

**forbidden:**
- 表格无状态徽章
- 无 scan 动效
- 白色表格背景

---

### Scene 3 — Process / 链路诊断

**visual objective:**
展示从收藏到输出的 4 个断点，定位故障。

**layout:**
- 顶部：系统状态 DIAGNOSIS (danger)
- 顶部左侧：BigMetric "4 BREAKS" / "断点数量"
- 中央：4 个节点横向排列（输入→整理→回顾→输出）
- 每个节点下方：诊断标签（输入：没入口 / 整理：没结构 / 回顾：没复盘 / 输出：写不出）
- 节点之间：FlowLine 连接线（红色断裂）
- 断点节点：红色 glow + FAIL 徽章 + shake 动画
- 底部：结论条

**HUD elements:**
- 状态徽章：DIAGNOSIS (danger)
- BigMetric：4 BREAKS (red, 136px)
- 4 个节点卡片：240x150，半透明玻璃面板
- FlowLine：正常=绿色流动 / 断裂=红色 X
- FAIL 徽章：红色，absolute 定位在断点节点右上角
- 断裂光效：红色 radial glow，覆盖断点区域

**motion:**
- 节点：逐个从下往上 slide-in，每节点 delay 0.15s
- 连接线：正常节点连接线有流动动画
- 断点节点：持续 shake (sin wave, 0.3 freq)
- FAIL 徽章：pulse 动画
- 断裂光效：opacity pulse (0→1→0.5, 2s)
- 结论条：从下淡入

**text content:**
- HEADER: "链路诊断" / "检测收藏到输出的断点"
- METRIC: "4 BREAKS" / "断点数量"
- NODE LABELS: 输入 / 整理 / 回顾 / 输出
- NODE DESCRIPTIONS: 输入：没入口 | 整理：没结构 | 回顾：没复盘 | 输出：写不出
- NODE STATUS: FAIL (断点节点)
- CONCLUSION: "素材堆积，不等于内容产出"

**forbidden:**
- 4 个节点等高等宽无区分
- 无断裂线效果
- 无 shake 动画

---

### Scene 4 — Toolflow / 三端协作

**visual objective:**
展示 Obsidian → Codex → Hermes 三端协作流水线。

**layout:**
- 顶部：系统状态 "3/3 READY" (success)
- 顶部右侧：BigMetric "3/3" / "OUTPUT READY" (green)
- 中央：3 个阶段垂直排列（收素材→搭结构→定时复盘）
- 每个阶段：圆形编号 + 工具名 + 3 个 bullet points + 右侧状态徽章
- 阶段之间：向下箭头连接
- 底部：结论条

**HUD elements:**
- StepBadge：3/3 READY (green)
- BigMetric：3/3 OUTPUT READY (green)
- 3 个 StagePanel：圆形编号 (72px) + 工具名 + bullet 列表
- StatusBadge：INPUT READY / STRUCTURE ACTIVE / REVIEW DONE
- 连接箭头：圆形带向下箭头
- 背景：purple radial glows

**motion:**
- StagePanel 1：左侧 slide-in (0.3s, power2.out)
- StagePanel 2：左侧 slide-in (0.4s, delay 0.2s)
- StagePanel 3：左侧 slide-in (0.4s, delay 0.4s)
- 连接箭头：逐个 fade-in，每箭头 delay 0.15s
- ambient: purple glow pulse
- 结论条：从下淡入

**text content:**
- HEADER: "三端协作" / "让素材变成可改草稿"
- STAGE 01: "收素材" / "Obsidian" / ✓ 统一入口 ✓ 知识库 ✓ 标签整理
- STAGE 02: "搭结构" / "Codex" / ✓ 拆选题 ✓ 改文章 ✓ 生成脚本
- STAGE 03: "定时复盘" / "Hermes" / ✓ 采集评分 ✓ 定时提醒 ✓ 下次接写
- STATUS: "INPUT READY" / "STRUCTURE ACTIVE" / "REVIEW DONE"
- CONCLUSION: "先让流程跑起来，再优化风格"

**forbidden:**
- 横向三栏布局（竖屏空间不够）
- 无连接箭头
- 工具名不突出

---

### Scene 5 — BeforeAfter / 效率对比

**visual objective:**
用超大数字对比强化"效率提升"结果承诺。

**layout:**
- 顶部：状态徽章 "TIME SAVED: 83%" (success)
- 中央：大数字对比 "5小时" → "40分钟"
- 中间箭头："→" (绿色)
- 数字下方：以前 / 现在标签
- 中下部：两栏对比面板（Before = 红色 / After = 绿色）
- 每栏 4 个对比项
- 底部：结论条

**HUD elements:**
- 状态徽章：TIME SAVED: 83% (success)
- Big numbers：5小时 (red, 120px) → 40分钟 (green, 120px)
- Arrow：绿色 "→"
- GlassPanel x2：Before (red border) / After (green border)
- StatusBadge：BEFORE (danger) / AFTER (success)
- 对比项列表：✓/✗ 图标 + 文字

**motion:**
- 场景开始：两个 BigNumber 从 0 scale-up (0.6s, back.out)
- Before 数字：红色 glow pulse
- After 数字：绿色 glow pulse
- 箭头：从透明 fade-in + 向右位移 (0.3s)
- BeforePanel：从左 slide-in (0.4s)
- AfterPanel：从右 slide-in (0.4s, delay 0.2s)
- 对比项：逐个 stagger fade-in (0.05s each)
- 结论条：从下淡入

**text content:**
- HEADER: "效率对比" / "不是更努力，是流程变短了"
- METRIC: "TIME SAVED: 83%"
- BEFORE: "5小时" / "以前"
- AFTER: "40分钟" / "现在"
- BEFORE ITEMS: ✗ 手动整理 ✗ 找不到素材 ✗ 写作卡壳 ✗ 无复盘
- AFTER ITEMS: ✓ 自动归类 ✓ 随时查找 ✓ 提纲辅助 ✓ 定时回顾
- CONCLUSION: "不是更努力，是流程变短了"

**forbidden:**
- 数字太小（<80px）
- 无 TIME SAVED 徽章
- 无绿色成功氛围

---

### Scene 6 — ActionList / 今日执行

**visual objective:**
展示 3 个任务全部完成，给用户行动信心。

**layout:**
- 顶部：状态徽章 "SYSTEM COMPLETE" (success)
- 顶部左侧：BigMetric "3/3" / "TASKS COMPLETED" (green)
- 中部：3 个任务完成卡片（每行：圆形勾选 + 任务名 + DONE 徽章）
- 底部：结论条

**HUD elements:**
- 状态徽章：SYSTEM COMPLETE (success)
- BigMetric：3/3 TASKS COMPLETED (green)
- 3 个 TaskCard：圆形勾选 (48px, green glow) + 任务名 + DONE 徽章
- Progress bar：顶部进度指示（100%）
- 背景：多层 green radial glow

**motion:**
- 场景开始：进度条从 0% → 100% (0.6s)
- BigMetric：数字 scale-up (0.4s, back.out)
- TaskCard 1：从上 slide-in (0.3s)
- TaskCard 2：从上 slide-in (0.3s, delay 0.15s)
- TaskCard 3：从上 slide-in (0.3s, delay 0.3s)
- 每个勾选：pop 动画 (scale 0→1.2→1, 0.3s, back.out)
- ambient: green glow pulse
- 结论条：从下淡入

**text content:**
- HEADER: "今日执行" / "今天只跑通一次"
- METRIC: "3/3" / "TASKS COMPLETED"
- TASK 01: "任务 1 完成内容"
- TASK 02: "任务 2 完成内容"
- TASK 03: "任务 3 完成内容"
- STATUS: "SYSTEM COMPLETE" / "DONE" (per task)
- CONCLUSION: "先产出，再优化"

**forbidden:**
- 无勾选动画
- 无完成状态绿色氛围
- 无 progress 指示

---

## 5. 下一步建议

**先用 `design-html` + `frontend-design` 生成 6 张高质量 styleframes（HTML，1080x1920），不继续改 Remotion TSX。**

每张 styleframe 是一个独立 HTML 文件，包含：
- 该场景的完整视觉布局
- HUD 风格组件（系统徽章、数据面板、玻璃面板）
- GSAP 动画（入场动效）
- 暗色 cinematic 背景

生成后用 `npx hyperframes preview` 打开验证，snapshot 截取关键帧，人工审查是否接近参考样例。

**等 styleframes 人工审查通过后，再决定：**
1. 是否用 HyperFrames 直接 render MP4
2. 还是将 HyperFrames HTML 转为 Remotion 场景
3. 还是保持 Remotion 只做 audio + smoke render

---

## 6. 未做事项

以下事项本轮**未执行**，保持原样：

- ✅ 未改 Remotion scene TSX
- ✅ 未改 HudPrimitives.tsx
- ✅ 未改 GlowBackground.tsx
- ✅ 未改 TTS
- ✅ 未改男声
- ✅ 未改 Python pipeline
- ✅ 未 full render
- ✅ 未接 CapCut
- ✅ 未做素材库
- ✅ 未重构 V3 pipeline
- ✅ 未改 Root.tsx
- ✅ 未改 Video.tsx