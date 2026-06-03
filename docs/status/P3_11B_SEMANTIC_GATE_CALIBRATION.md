# P3.11B Semantic Quality Gate Calibration

## 1. 阶段目标

本阶段只做一件事：校准 `src/video_director_v3/qa/semantic_quality_gate.py`，让语义质量门更接近人工视觉语义审查。

重点不是改模板，也不是重跑预览，而是让 gate 更准确地区分：

- 工程通过
- 预览可审
- 发布候选可用

## 2. 校准结果

### 新增的分层判断

本阶段新增了以下语义判断结果：

- `gate_status`: `PASS / FAIL`
- `score_band`: `READY / REVIEW / FAIL`
- `publish_candidate_readiness`: `READY / REVIEW / NO_GO`

### 分数规则

- `semantic_quality_score` 已封顶 `100`
- `READY`: `90–100`
- `REVIEW`: `75–89`
- `FAIL`: `<75`

### 硬失败仍然保留

以下情况继续 hard fail，不弱化：

- `placeholder_count > 0`
- `raw_text_dependency_count > 0`
- required slot missing without fallback
- `cta_scene_count = 0`
- `proof_scene_count = 0`
- `fallback_count > 30%`
- Chinese dominance too low
- role/template contract mismatch
- contact sheet missing
- preview not READY

### 新增结构风险

本阶段把以下问题纳入结构风险分析：

- early CTA
- repeated CTA
- abstract proof
- repeated role/template
- weak hook

这些问题不一定 hard fail，但会拉低分数，并影响 `publish_candidate_readiness`。

## 3. 验证结果

本阶段已完成以下验证：

- `tests/test_semantic_quality_gate.py`
- `tests/test_scene_pack_contracts.py`
- `tests/test_preview_pipeline.py`
- `tests/test_tts_contract.py`
- `tests/test_render_gate.py`
- `compileall src tests`
- `git diff --check`

结果：

- 单测通过
- 语法检查通过
- 补丁检查通过

## 4. 结论

### 结论等级

本阶段通过。

### 对 P3.11 的影响

这次校准解决了一个核心问题：之前 `semantic_quality_score=106.0` 偏乐观，且没有充分暴露早 CTA、重复 CTA、抽象 proof、重复结构和弱 hook 这类发布前风险。

现在 gate 更偏向于：

- 识别结构性问题
- 把“工程通过”与“发布候选”分开
- 让 `worst_3_scenes` 更接近人工感受

### 下一步建议

进入 `P3.11C Worst 3 Scene Repair`。

原因：

- gate 已经能发现问题
- 下一步应该修内容本身，而不是继续放大评分规则
- `worst_3_scenes` 里的弱点现在已经足够明确，可以直接进入 scene 级修复

## 5. 本阶段未做事项

- 没有扩模板数量
- 没有修改 HyperFrames renderer
- 没有改 playback / seek / `audio.timeupdate` / `window.__hf`
- 没有回 `combined/index.html`
- 没有 render MP4
- 没有生成新的 preview
- 没有把 `narrative_compressor.py` 接入主线

