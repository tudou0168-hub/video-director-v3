# LAST KNOWN GOOD

## V3-P3.8 Preview Visual Quality Upgrade — 当前 preview 质量升级可用版本

| Item | Status | Notes |
|------|--------|-------|
| Preview project | PASS | `outputs/v3_p38_visual_upgrade_preview/hyperframes_timeline/` |
| Distilled voiceover | PASS | 21 句场景，total 116.21s |
| HUD review frames | PASS | `outputs/v3_p38_visual_upgrade_preview/review_frames/` (含 `contact-sheet.jpg`) |
| Visual template diversity | PASS | 21 scenes / 15 distinct visual_template（2026-05-26 run 是 20/8） |
| Anti-repetition (Layer 1 + Layer 2) | PASS | 连续 scene 不撞 `visual_template` |
| Source/footer metadata filter | PASS | narration / caption / on-screen text 零 metadata 词（情报来源 / 资料来源 / 本视频 / 数据来源 / 本文参考 / 本文根据 / anthropics/claude-code 2026-05-24 / 个人使用经验） |
| Last-scene CTA = finish board | PASS | S21 `role=cta / template=checklist_cta / variant=end_score_goodbye / score=100` |
| data↔HTML consistency | PASS | 21/21 scenes: `director_timeline.json.visual_template` 与 `<section data-visual-template="…">` 一致 |
| Native lint | PASS | `0 errors` |
| Test baseline | PASS | 115 测试通过（110 baseline + 5 新：T1 metadata / T2 pool rotation / T3 Layer 2 + data↔HTML / T4 last CTA / T5 既有 render gate 覆盖） |
| Main line | UNCHANGED | 仍然是 `script → hyperframes_preview → approval → render_mp4 → final_video.mp4`；preview-only，无 render_mp4 |
| NO MP4 generated | PASS | `find outputs/v3_p38_visual_upgrade_preview -name "*.mp4"` 返回 0 个文件 |

### V3-P3.8R1 — Engineering Contract Fix (覆盖在 V3-P3.8 之上)

| Contract | Status | Notes |
|----------|--------|-------|
| `design_variance` 单一旋钮 | PASS | `scene_protocol.should_enable_v3_p38_features(d_v)` 统一 3 个特性开关；`pipeline_runner.py:128` 把 `args.design_variance` 真正传到 `build_motion_storyboard` |
| `design_variance < 5` → 老 deterministic | PASS | Layer 1 轮转关 / Layer 2 fallback 关 / 末帧 CTA 默认关；T6 + T14 锁定 |
| `design_variance >= 5` → 全特性开 | PASS | T7 + T15 锁定 |
| `motion_storyboard.json` 是 initial suggestion | PASS | docstring 锁 + T10 断言 |
| `director_timeline.json` + `index.html` 是 final source of truth | PASS | 21/21 data↔HTML 一致；T3 + T10 锁定 |
| Metadata 过滤不过度 | PASS | T11-T13 锁定行内 / 括注 / 触发词在正文中保留 |
| 测试基线 | PASS | 126 测试（110 baseline + 5 V3-P3.8 + 11 V3-P3.8R1） |
| Re-run preview | PASS | `outputs/v3_p38r1_contract_fix_preview/` 21 scenes / 15 templates / 0 MP4 / 0 metadata 泄漏 |
| NO MP4 generated | PASS | `find outputs/v3_p38r1_contract_fix_preview -name "*.mp4"` 返回 0 |

### V3-P3.9 — Cinematic HUD Overlay Visual Upgrade (覆盖在 V3-P3.8R1 之上)

| Visual property | Status | Notes |
|---|---|---|
| Shared CSS scaffold | PASS | `hf-bg-cinematic` + 6 role-tinted `hf-bg-{role}` gradients, `hf-vignette`, `hf-scan-beam`, `hf-hud-header` (en + accent bar + zh), `hf-glass-panel` + 4 color variants, `hf-big-title` (clamp 120-200px), `hf-big-number` (clamp 180-360px), `hf-step-number`, `hf-metric-card`, `hf-status-stamp` + 5 status colors, `hf-safe-zone` (220px bottom), `hf-caption` with blur+glow |
| 7 keyframes | PASS | `hf-scale-in`, `hf-count-up`, `hf-stagger-in`, `hf-progress-fill`, `hf-stamp-pop`, `hf-beam`, `hf-pulse` (CSS only, no JS) |
| 9 enhanced templates | PASS | Hero Poster (`hook_big_claim`), Metric Dashboard (`metric_dashboard`), Card Wall (`case_study_card`), Knowledge Overlay (`framework_quadrant` / `concept_layers` / `knowledge_graph`), Step Panel (`tool_chain_three_cols` / `step_ladder`), Final Score Board (`checklist_cta` end_score_goodbye). 15 untouched templates keep their previous look. |
| Real preview | PASS | `outputs/v3_p39_cinematic_hud_overlay_preview/` 21 scenes; 0 MP4; no metadata leak |
| Tests / static | PASS | 35 tests pass (no new tests added); compileall clean; git diff --check clean |
| Main line / contract | UNCHANGED | V3-P3.8R1 design_variance contract, motion/director/html relationship, metadata filter — all preserved |

### V3-P3.9R1 — Visual Readability / Contrast / Composition Fix (覆盖在 V3-P3.9 之上)

| Visual property | Status | Notes |
|---|---|---|
| Stronger semantic colors | PASS | Brighter base palette: cyan #38E1FF, amber #FFC83D, red #FF5577, green #2EE874, purple #C77DFF. Per-role backgrounds now use 0.28-0.32 alpha radial glows (was 0.10-0.18). |
| Higher text contrast | PASS | `--hf-text: #F8FAFC` (was #F4F7FF). Small text ≥ 0.62 opacity (was 0.55). Vignette softened from 0.55 to 0.32 so mid-canvas content stays readable. |
| Bigger hero typography | PASS | `.hf-big-title` clamp 72-108px (was 110-170px) — fits 3-4 clean lines with cyan/amber accents. `.hf-big-number` 320px (was 360px). |
| Thicker glass borders | PASS | Border 1.5px solid (was 1px). Corner brackets 22x22 @ 3px (was 18x18 @ 2px). Shadow glow 0 0 48px (was 0 0 36px). |
| Per-scene single visual anchor | PASS | S01: 170px title with cyan/amber accent. S04: red BEFORE 880px + green AFTER 480px. S08/S12: 280px hero number + 3 satellite cards. S14: 4 green step pills with vertical green connector. S18: 240px HUB with purple glow. S21: 380px green 100 + DONE/COMPLETE stamps. |
| Real preview | PASS | `outputs/v3_p39r1_visual_readability_fix_preview/` 21 scenes; 0 MP4; no metadata leak; 0 caption occlusion. |
| Tests / static | PASS | 35 tests pass (no new tests added); compileall clean; git diff --check clean. |
| Main line / contract | UNCHANGED | V3-P3.8R1 design_variance contract, motion/director/html relationship, metadata filter — all preserved. |

### V3-P3.8 关键产物路径

| 产物 | 路径 |
|------|------|
| Preview project root | `outputs/v3_p38_visual_upgrade_preview/` |
| HyperFrames index.html | `outputs/v3_p38_visual_upgrade_preview/hyperframes_timeline/index.html` |
| Director timeline | `outputs/v3_p38_visual_upgrade_preview/hyperframes_timeline/data/director_timeline.json` |
| Caption beats | `outputs/v3_p38_visual_upgrade_preview/hyperframes_timeline/data/caption_beats.json` |
| Narration plan | `outputs/v3_p38_visual_upgrade_preview/narration_plan.json` |
| Contact sheet | `outputs/v3_p38_visual_upgrade_preview/review_frames/contact-sheet.jpg` |
| Review frames (PNG) | `outputs/v3_p38_visual_upgrade_preview/review_frames/frame-00 … frame-06` |
| Voiceover MP3 | `outputs/v3_p38_visual_upgrade_preview/hyperframes_timeline/assets/voiceover.mp3` |

### V3-P3.8 修改文件清单

- `src/video_director_v3/director/narration_planner.py` — metadata 过滤 + CTA fallback
- `src/video_director_v3/director/storyboard_builder.py` — `_pick_keyword_seed_id` + Layer 1 池轮换
- `src/video_director_v3/templates/scene_protocol.py` — `RENDER_TEMPLATE_POOLS` + `pick_render_template_for_role`
- `src/video_director_v3/renderers/hyperframes/studio_native_project_builder.py` — Layer 2 fallback + 末帧 CTA 默认 + broken_chain 变体轮换
- `src/video_director_v3/renderers/hyperframes/publish_templates.py` — `_render_chain_vertical_flow_layout` + `_render_chain_knowledge_triangle_layout`
- `tests/test_preview_pipeline.py` — 5 个新测试 (T1-T5)

---

## V3-P3.1 HUD Audio-First Preview

| Item | Status | Notes |
|------|--------|-------|
| Preview project | PASS | `outputs/obsidian_second_brain_p31_preview/hyperframes_timeline/` |
| Distilled voiceover | PASS | 76 句提炼为 12 句、419 字，自然语速 `81.10s` |
| HUD review frames | PASS | `outputs/obsidian_second_brain_p31_preview/review_frames/` |
| Native lint | PASS | `0 errors` |
| Audio smoke | PASS | `outputs/obsidian_second_brain_p31_preview/rendered_smoke/final_video_smoke.mp4` |
| Sync report | PASS | 最大漂移 `0.0s`，`h264 + aac` |

---

## V3-P2.5 HUD Style System Upgrade

| 能力 | 状态 | 备注 |
|------|------|------|
| HudExplainerSmoke composition | PASS | 450 frames @ 25fps = 18s |
| HudPrimitives.tsx | PASS | 8 HUD 组件：HUD_COLORS, HudHeader, GlassPanel, BigMetric, StatusBadge, StepBadge, FlowLine, DataTable, ConclusionBar |
| HookScene HUD 风格 | SMOKE PASS | HudHeader + BigMetric + StatusBadge + ConclusionBar |
| PainCardStack HUD 风格 | SMOKE PASS | HudHeader + BigMetric + DataTable + ConclusionBar |
| ProcessChainScene HUD 风格 | SMOKE PASS | HudHeader + BigMetric(4 BREAKS) + StatusBadge + FlowLine |
| ToolWorkflowScene HUD 风格 | SMOKE PASS | HudHeader + StepBadge + ConclusionBar |
| BeforeAfterScene HUD 风格 | SMOKE PASS | HudHeader + BigMetric(5h→40m) + ConclusionBar |
| ChecklistScene HUD 风格 | SMOKE PASS | HudHeader + BigMetric(3/3) + StatusBadge + ConclusionBar |

## 历史能力（保持通过）

| 能力 | 状态 | 备注 |
|------|------|------|
| Remotion 项目编译 | PASS | npx remotion build 成功 |
| Remotion 场景组件 | PASS | 6 个 scene 全部可渲染 |
| Remotion full render | PASS | 2063 帧 (82.5s) 渲染完成，4.4MB |
| Remotion audio mux | PASS | ffmpeg 合成 video+audio 成功，82.52s |

## V3-P2.5 Smoke 测试产物

| 产物 | 路径 |
|------|------|
| smoke video | `outputs/demo_v3_p25_hud_style_smoke/smoke_18s.mp4` (1.8MB, 18.048s) |
| review frames | `outputs/demo_v3_p25_hud_style_smoke/review_frames/` |
| frame_1s.jpg | 110KB — HookScene, HUD 风格 |
| frame_4s.jpg | 90KB — PainCardStack, HUD DataTable |
| frame_7s.jpg | 94KB — ProcessChainScene, HUD 链路诊断 |
| frame_10s.jpg | 95KB — ToolWorkflowScene, HUD 三端协作 |
| frame_14s.jpg | 100KB — BeforeAfterScene, HUD 效率对比 |
| frame_18s.jpg | 91KB — ChecklistScene, HUD 行动清单 |

## Smoke 渲染命令

```bash
cd /Users/muzi/video-director-v3/remotion_templates/hud_explainer
npx remotion render src/Root.tsx "HudExplainerSmoke" \
  /Users/muzi/video-director-v3/outputs/demo_v3_p25_hud_style_smoke/smoke_18s.mp4 \
  --props /Users/muzi/video-director-v3/outputs/publishable_viral_v2/remotion_smoke_props.json
```

## 关键帧导出命令

```bash
cd /Users/muzi/video-director-v3
for t in 1 4 7 10 14; do
  ffmpeg -ss $t -i outputs/demo_v3_p25_hud_style_smoke/smoke_18s.mp4 \
    -frames:v 1 -q:v 2 outputs/demo_v3_p25_hud_style_smoke/review_frames/frame_${t}s.jpg -y
done
ffmpeg -ss 17.8 -i outputs/demo_v3_p25_hud_style_smoke/smoke_18s.mp4 \
  -frames:v 1 -q:v 2 outputs/demo_v3_p25_hud_style_smoke/review_frames/frame_18s.jpg -y
```

---
最后更新：2026-05-30
