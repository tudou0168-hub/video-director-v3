# P3.11C + P3.12A Worst Scene Repair and Publish Candidate Pre-Selection Plan

## 1. 本阶段目标

基于 P3.11B 的新 semantic quality gate，修复 P3.10 三条 preview 里最影响发布的结构问题，并判断是否至少有 1 条可以进入 P3.12 Publish Candidate Selection。

本阶段分两层：

- P3.11C：修 worst scenes / 结构问题
- P3.12A：做候选片预选判断

## 2. 允许修改范围

允许修改：

- `src/video_director_v3/director/semantic_planner.py`
- `src/video_director_v3/director/template_contracts.py`
- `src/video_director_v3/qa/semantic_quality_gate.py`
- `src/video_director_v3/renderers/hyperframes/publish_templates.py`
- 相关测试文件
- `docs/status/P3_11C_WORST_SCENE_REPAIR_REPORT.md`
- `docs/status/P3_12A_PUBLISH_CANDIDATE_PRESELECTION.md`
- `docs/status/P3_11C_P3_12A_REPAIR_AND_CANDIDATE_PLAN.md`

## 3. 禁止事项

- 不要重写 HyperFrames renderer
- 不要改 playback / seek / `audio.timeupdate` / `window.__hf`
- 不要回 `combined/index.html`
- 不要默认 render MP4
- 不要提交 `outputs/` 或 `renders/`
- 不要提交 `contact-sheet.jpg`
- 不要提交 `final_video.mp4`
- 不要把 `narrative_compressor.py` 接入主线
- 不要大规模扩模板数量
- 不要为了好看弱化 hard fail
- 不要把 `approval READY` 直接等同于 publish candidate READY

## 4. 准备优先修的结构问题

1. 早 CTA
   - 前 30% 不能出现 final_cta
   - 中前段若需要行动引导，优先使用 `result_summary` / `offer` / `method`

2. 重复 CTA
   - 13–15 scenes 的视频里，final_cta 应集中在后段
   - 中段不要反复催收口

3. proof 偏抽象
   - proof slots 需要更具体的 evidence / situation / action / result / lesson
   - 不造假数字，只用真实可承载信息

4. weak hook
   - 开头要有冲突、反差、问题感
   - 避免“开始流程 / 方法 / 总结 / 第一步”式弱开头

5. 前段重复 problem_conflict
   - 不要连续 2–3 个 problem_conflict
   - 前段要形成 `hook -> problem -> reframe/method`

6. result_summary 薄弱
   - 末段 summary 要像收束
   - 要明确“看完你拿到了什么”

## 5. 重新跑哪些 preview

保留旧基线，不覆盖原目录，重跑到新目录：

1. `outputs/v3_p311c_knowledge_repair_preview`
2. `outputs/v3_p311c_sales_repair_preview`
3. `outputs/v3_p311c_toolflow_repair_preview`

要求：

- 只跑 `hyperframes_preview`
- 不跑 `render_mp4`
- 每条都要生成 `scene_pack.json`、`semantic_quality_report.json`、`approval_required.json`、`preview_report.md`、`review_frames/contact-sheet.jpg`、`hyperframes_timeline/index.html`、`hyperframes_timeline/data/director_timeline.json`

## 6. publish candidate 判断标准

只有同时满足以下条件，才可以推荐进入 P3.12：

- `gate_status = PASS`
- `score_band = READY`，或接近 READY 且问题可控
- `publish_candidate_readiness = READY` 或 `REVIEW` 但明确可修
- `hard_fail_reasons = []`
- `fallback_count = 0`
- `raw_text_dependency_count = 0`
- `placeholder_count = 0`
- `role_template_mismatch_count = 0`
- `cta_distribution_risk != high`
- `proof_strength_risk != high`
- `hook_strength_risk != high`
- `contact_sheet_exists = True`
- 人眼审查可读、可信、主信息清楚

## 7. 测试命令

必须运行：

```bash
PYTHONPATH=src .venv/bin/python3 -m pytest \
  tests/test_semantic_quality_gate.py \
  tests/test_scene_pack_contracts.py \
  tests/test_preview_pipeline.py \
  tests/test_tts_contract.py \
  tests/test_render_gate.py -q

PYTHONPATH=src .venv/bin/python3 -m compileall src tests

git diff --check
```

## 8. 验收标准

- 三条新版 preview 成功生成
- 新 gate 字段齐全
- early CTA / repeated CTA 明显下降
- proof_strength 至少有一条改善
- hook_strength 至少有一条改善
- worst_3_scenes 能反映真实结构风险
- 没有 hard fail
- 没有 renderer 改写
- 没有模板大扩张
- 没有 render MP4
- 没有提交 outputs/renders
- GitHub commit 可查

