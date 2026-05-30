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
| V3-C1 hyperframes_preview | PASS | combined/index.html 生成 |
| V3-C1.1 review_frames | PASS | 7/7 帧捕获成功 |
| V3-D1 smoke render_mp4 | PASS | 5s smoke MP4 生成 |
| V3-D2 full render_mp4 | **TECH PASS / PRODUCT FAIL** | MP4 生成但音频疑似异常 |

**V3-D2 技术层面**：final_video.mp4 存在 video+audio stream，时长 40.92s，文件 1.1MB。
**V3-D2 产品层面**：用户反馈播放无声音，音频 mux 需诊断。

## 当前最高优先级

### P0（暂停，跳过）
修复 final_video.mp4 无声音问题。**已暂停，优先建立记忆系统。**

### P1
Clean Render Mode：
- 隐藏 Play/Pause/Reset 调试控件
- 隐藏时间调试框（S01 · hook / 0.0s / 40.9s）
- 隐藏 scene label
- 隐藏进度条
- 修复字幕裁切（底部字幕只露出右侧）
- 逐帧缓存默认删除，只保留 final review frames

### P2
Motion Validation：
- 检测重复帧
- 检测静态视频
- 检测调试 UI
- 检测字幕裁切

## 当前不要做

- 不要重构 HyperFrames Studio native。
- 不要接 CapCut。
- 不要做 content_pack 主线。
- 不要接素材库。
- 不要新增复杂视觉组件。
- 不要优化视觉风格，直到音频 mux 和 clean render 修完。
- 不要把 smoke video 当 final video。
- 不要把有 video/audio stream 当作最终产品成功，必须实际播放有声音、画面可看。
- **不要修复视频无声音问题**（本阶段目标）。
- 不要做 D2.1。

## 当前关键路径

当前阶段：**建立持久化记忆系统和交接文档**

下一步（音频问题修复阶段）：
V3-D2.0-A Fix Final MP4 Audio Mux

然后才做：
V3-D2.1 Clean Render Mode + Motion Validation

## 关键产物路径

| 产物 | 路径 |
|------|------|
| 唯一预览权威 | `outputs/demo_v3_preview/combined/index.html` |
| TTS 音频 | `outputs/demo_v3_preview/audio/voiceover.mp3` (40.92s) |
| 最终视频 | `outputs/demo_v3_preview/rendered/final_video.mp4` |
| 审批 gate | `outputs/demo_v3_preview/approval_required.json` |
| 质量报告 | `outputs/demo_v3_preview/quality_report.json` |

## 项目约束

- **输出目录**：仅 `outputs/<project_id>/` 和 `test_outputs/<project_id>/`
- **禁止**写入 `src/outputs/` 或散落临时目录
- **禁止** hyperframes_preview 模式生成 final_video.mp4
- **禁止** render_mp4 无 --approved 就渲染
- **禁止** mock final_video 冒充真实视频

## 测试状态

24 个测试全部通过（最近运行：2026-05-30）

---

最后更新：2026-05-30