# NEXT TASK

## 当前任务

**P3.12 Publish Candidate Selection** — 已完成 P3.11C 修复与 P3.12A 预选，待人工确认首选候选片。

首选候选 preview：

- `outputs/v3_p311c_sales_repair_preview/`
- `hyperframes_timeline/index.html`（13 scenes）
- 无 MP4
- 无 window.__hf
- 无 sentinel

## 本轮改动

### P3.11C

- 通过 `semantic_planner.py` 轻量重排角色
- 把早 CTA 回收为 `result_summary` / `offer` / `verdict`
- 让 proof slots 变具体
- 降低 abstract proof / early CTA / repeated CTA 风险

### P3.12A

- 基于三条新 preview 做 publish candidate 预选
- 首选候选：`v3_p311c_sales_repair_preview`
- 其余两条作为备选，不作为首选进入 P3.12

## 验证

| Check | Result |
|-------|--------|
| 69 tests | ✅ PASS |
| compileall | ✅ PASS |
| git diff --check | ✅ clean |
| 3 new previews | ✅ PASS |
| contact sheets | ✅ PASS |

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
