# video-director-v3 当前项目状态

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

**V3-P2 视觉渲染技术栈**：Remotion → HTML/CSS/React 动画 → MP4

## 当前最高优先级

### P0
V3-P2.3 Full Remotion Render — 用正确 18s smoke props 渲染 smoke，验证通过后 full render 82.5s。

### P1
- Remotion 完整 82.5s 渲染 + audio mux
- 最终视频质量人工验收

## 当前不要做

- 不要回到 Playwright 截帧路线
- 不要改 TTS / audio path
- 不要重构 V3 director layer
- 不要修 publish_templates.py
- 不要继续扩展 Remotion 组件库（当前 6 个 scene 已够用）

## 关键产物路径

| 产物 | 路径 |
|------|------|
| Remotion 模板 | `remotion_templates/hud_explainer/` |
| smoke props | `outputs/publishable_viral_v2/remotion_smoke_props.json` |
| full props | `outputs/publishable_viral_v2/remotion_props.json` |
| smoke 视频 | `outputs/publishable_viral_v2/remotion_smoke_v2/final_video.mp4` |
| smoke 帧 | `outputs/publishable_viral_v2/remotion_smoke_v2/frames/` |

## 当前视觉风格

AI 科技解释型 HUD 风格：
- 深色渐变背景 (#050814)
- 细网格 + 柔光光斑
- 半透明玻璃卡片
- 青蓝/橙红/荧光绿强调色
- Spring / ease-out 动效

## 测试状态

24 个测试全部通过（最近运行：2026-05-30）

---
最后更新：2026-05-31