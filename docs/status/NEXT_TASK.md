# NEXT TASK

## 当前任务

**V3-P3.11E Reference-Style Template Polish** — 已生成 preview，待人工验收。

新 preview 路径：`outputs/v3_p311e_reference_matched_visual_correction_preview/`
- `hyperframes_timeline/index.html`（21 scenes）
- 无 MP4
- 无 window.__hf
- 无 sentinel

## 本轮改动

### 重写了 4 个模板函数（按参考风格）

| 模板 | 原来 | 现在 |
|------|------|------|
| **tool_stack** | 3 张卡片飘在中区 | 3 层流水线：L1 左移、L2 中置、L3 右移，层间 flow 线 + 箭头，左侧 4px 发光竖条，底部 amber 结果卡 |
| **keyword_punchline** | 大词+一句话+底部文字 | 大词 top:300 + glow block + 2 张 glass 解释卡（1 创作调用 / 2 素材系统）+ 底部 green INSIGHT 卡 |
| **myth_bust** | 上下两个框+中间按钮 | 4 段式：MYTH 卡（✕ icon）→ MYTH→TRUTH 过渡条 → TRUTH 卡（✓ icon）→ 底部结论卡 |
| **progress_tracker** | 3 条孤立进度条 | 3 个评分卡（左名称+描述 / 中 W1→W8 进度条 / 右大分数+状态标签 READY/STABLE/GROWING）+ 底部结果卡 |

### 新增共享 CSS（studio_native_project_builder.py）

.hf-page-anchor / .hf-result-card / .hf-flow-line / .hf-mini-badge / .hf-glow-divider

### 模板函数覆盖

- `_template_tool_stack` — 重写
- `_template_keyword_punchline` — 重写
- `_template_myth_bust` — 重写
- `_template_progress_tracker` — 重写

其余 6 个模板（broken_chain、before_after_compare、framework_quadrant、concept_layers、knowledge_graph、case_study_card）已在 P3.11C/D 中完成统一，本次未改。

## 验证

| Check | Result |
|-------|--------|
| 36 tests | ✅ PASS |
| compileall | ✅ PASS |
| git diff --check | ✅ clean |
| window.__hf | ✅ 0 |
| sentinel | ✅ clean |
| 21 scenes | ✅ |
| Contact sheet | ✅ 457K |

## 交付物

- **preview:** `outputs/v3_p311e_reference_matched_visual_correction_preview/hyperframes_timeline/index.html`
- **contact sheet:** `review_frames/contact-sheet.jpg`
- **21-scene thumbnails:** `review_frames/frame-XX-at-XXXs.png`（21 frames）
- **contact grid:** `review_frames/contact-sheet-1..3.jpg`（3 张拼接图）

## Studio 验证

请在 Studio 中打开验证：
`http://localhost:3002/#project/v3_p311e_reference_matched_visual_correction_preview/hyperframes_timeline`

---
最后更新：2026-06-02