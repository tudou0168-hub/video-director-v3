# V3-P2.6-HF 技能编排计划

## 目标

优先复用现有技能，通过 HyperFrames 视觉生成链路，快速产出 6 张高质量 styleframes，人工审查通过后决定 Remotion 承接策略。

## 编排链路

```
文案脚本（已有 TTS / caption_beats）
  ↓
Step 1: design-html / frontend-design
  → 生成 6 个独立 HTML scene 文件
  → 每次迭代 1 个场景，快速验证
  ↓
Step 2: gsap-timeline / gsap-core
  → 为每个 scene HTML 添加 GSAP 动画
  → 强化 scan / glitch / 数字跳变 / 列表涌入
  ↓
Step 3: taste-skill / design-review
  → 审美评审 6 张 styleframes
  → 选出最接近参考样例的 1-2 套方案
  ↓
Step 4: npx hyperframes preview + snapshot
  → 验证动态效果
  → 截取 6 个关键帧 PNG
  ↓
Step 5（决策点）:
  → A: HyperFrames 直接 render MP4（如果满意）
  → B: remotion-to-hyperframes 转换后 Remotion render
  → C: 保持 Remotion 只做 audio + smoke，最终视觉用 HyperFrames overlay
```

## Step 1 详细：design-html 生成流程

### 调用方式

通过 `Skill: design-html` 技能，每次生成 1 个 scene HTML。

### 输入模板（每 scene）

```
scene_id: S01
scene_name: Hook / 痛点扫描
output_file: /Users/muzi/video-director-v3/docs/visual/styleframes/scene-01-hook.html
dimensions: 1080x1920 (portrait 9:16)
style: cinematic HUD, dark background, red alarm glow
prompt: <从 HYPERFRAMES_SCENE_PROMPTS.md 复制对应 scene prompt>
```

### 输出产物

6 个 HTML 文件：
- `scene-01-hook.html` — 痛点扫描
- `scene-02-pain.html` — 素材明细
- `scene-03-process.html` — 链路诊断
- `scene-04-toolflow.html` — 三端协作
- `scene-05-beforeafter.html` — 效率对比
- `scene-06-checklist.html` — 今日执行

### 质量标准

每个 HTML 必须包含：
1. 完整的 `1080x1920` 布局
2. HUD 风格组件（StatusBadge / BigMetric / GlassPanel / ConclusionBar）
3. GSAP timeline 使用 `tl.fromTo()` 格式
4. `window.__timelines['scene-01'] = tl` 导出
5. `data-composition-id` 正确设置
6. 无 `Math.random()` / 无 `repeat: -1`
7. 背景：`#050812` + vignette + glow layers + scan lines

## Step 2 详细：GSAP 动画增强

### 可用技能

- `gsap-core` — GSAP 基础
- `gsap-timeline` — 时间轴编排
- `gsap-react` — React 中的 GSAP（不适用）
- `gsap-scrolltrigger` — 滚动触发（不适用）
- `gsap-plugins` — 插件使用
- `gsap-utils` — 工具函数
- `gsap-performance` — 性能优化

### 本项目需要的动画类型

| 动画类型 | GSAP 实现 | 适用场景 |
| ------- | -------- | -------- |
| 数字跳变 | `gsap.fromTo({val:0}, {val:999, onUpdate})` | BigMetric |
| 列表涌入 | `stagger: 0.1s, fromTo({x:80,opacity:0})` | Material list / DataTable rows |
| 标题滑入 | `fromTo({y:50,opacity:0}, {y:0,opacity:1})` | Headlines |
| 缩放弹入 | `back.out(2.5)` | Badge pop |
| 脉冲 | `repeat: -1, yoyo: true` | StatusBadge pulse |
| shake | `Math.sin(frame*0.3)*4` 或 GSAP | Broken nodes |
| glow 脉动 | `opacity: 0.6→0.9→0.6, repeat: -1` | Ambient background |

### 注意事项

- 所有场景必须用 `tl.fromTo()` 而非 `tl.from()`
- 时间轴末尾用 `tl.set({}, {}, TOTAL_DURATION)` 扩展到场景总时长
- 缓动函数多样化：每场景至少使用 3 种

## Step 3 详细：审美评审

### 调用 taste-skill

```bash
Skill: taste-skill
输入：6 个 HTML 文件路径 + 参考视频截图（如果有）
问题：请判断哪个 scene 最接近参考样例的"电影感 HUD 包装"风格
输出：每个 scene 的审美评分（1-10）+ 具体问题列表
```

### 评审维度

| 维度 | 权重 | 检查点 |
| --- | --- | ------ |
| 暗色背景 | 15% | 非纯黑，有 radial glow 层，有 vignette |
| HUD 组件 | 20% | StatusBadge / BigMetric / GlassPanel 样式到位 |
| 信息密度 | 20% | 有数据表/进度条/评分条交织，非纯文字海报 |
| 字体层级 | 15% | 数字够大(80-136px)，标题够大(28-64px) |
| 光效 | 15% | glow / scan / 脉冲至少有一种 |
| 动效 | 15% | GSAP 动画流畅，无机械感 |

## Step 4：验证流程

```bash
# 每次生成 1 个 HTML 后快速预览
npx hyperframes preview /path/to/scene-01-hook.html

# snapshot 截取关键帧（场景动画稳定在 1s 处）
npx hyperframes snapshot /path/to/scene-01-hook.html --at 1.0 --output /tmp/scene01_frame.png

# 检查截图
open /tmp/scene01_frame.png

# 6 个全部验证后，合并到 docs/visual/styleframes/
mkdir -p /Users/muzi/video-director-v3/docs/visual/styleframes/
```

## Step 5 决策矩阵

| 条件 | 选择 |
| --- | ----- |
| HyperFrames styleframes 质量 ≥ 8/10 | A: HyperFrames 直接 render |
| HyperFrames quality 5-7/10，需改 Remotion | B: remotion-to-hyperframes 转换 |
| Remotion TTS + 字幕已验证 OK | C: Remotion 只做最终 MP4 输出 |
| 时间紧迫，只需要 6 张关键帧 | 直接 snapshot 使用，不 render |

## 禁止事项

- ❌ 不要从零研发新的工程能力
- ❌ 不要修改 Remotion TSX
- ❌ 不要改 TTS / 男声
- ❌ 不要做 full render
- ❌ 不要改 Python pipeline
- ❌ 不要同时生成 6 个 HTML（逐个迭代）
- ❌ 不要跳过 taste-skill 审美评审

## 快速开始指令

```bash
# 1. 打开 taste-skill 评审参考视频截图
Skill: taste-skill

# 2. 开始生成第一个场景
Skill: design-html
# 输入 scene-01-hook.html 的 prompt

# 3. preview + snapshot
npx hyperframes preview docs/visual/styleframes/scene-01-hook.html
npx hyperframes snapshot docs/visual/styleframes/scene-01-hook.html --at 1.0 --output /tmp/scene01.png

# 4. 打开截图人工审查
open /tmp/scene01.png

# 5. 重复 2-4 直到 6 个全部完成
# 6. taste-skill 评审
Skill: taste-skill
# 输入：6 个 HTML 文件路径
# 问题：哪个最接近参考？具体改进建议？
```