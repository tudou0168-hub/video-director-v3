# P3.11B Semantic Quality Gate Calibration Plan

## 1. 本阶段目标

校准 `src/video_director_v3/qa/semantic_quality_gate.py`，让 QA gate 更接近人工视觉语义审查结果。

目标不是修具体 scene 内容，也不是扩模板，而是让 gate 更能识别：
- 早 CTA
- 重复 CTA
- proof 偏抽象
- 前段问题堆叠
- hook 力度不足

## 2. P3.11 审查发现的问题

- `semantic_quality_score=106.0` 明显偏乐观
- 三条 preview 虽然 `approval READY`，但都不适合进入 `P3.12`
- `worst_3_scenes` 有参考价值，但没有充分暴露：
  - 早 CTA
  - 重复 CTA
  - proof 偏抽象
  - 前段问题堆叠
  - hook 力度不足
- `approval_required` 对“工程通过”和“发布候选”区分不够
- 当前 gate 能挡住明显技术垃圾，但挡不住“看起来像成品，实际不够发布”的内容

## 3. 本阶段允许改的文件

- `src/video_director_v3/qa/semantic_quality_gate.py`
- `tests/test_semantic_quality_gate.py`
- `docs/status/P3_11B_SEMANTIC_GATE_CALIBRATION_PLAN.md`
- `docs/status/P3_11B_SEMANTIC_GATE_CALIBRATION.md`

## 4. 本阶段禁止事项

- 不要扩模板数量
- 不要修改 HyperFrames renderer
- 不要修改 playback / seek / `audio.timeupdate` / `window.__hf`
- 不要回 `combined/index.html`
- 不要 render MP4
- 不要提交 `outputs/` 或 `renders/`
- 不要提交 `archive_later` 文件
- 不要把 `narrative_compressor.py` 接入主线
- 不要修具体 scene 内容
- 不要改 semantic_planner 生成策略，除非测试证明 gate 无法单独完成
- 不要为了让分数好看而调低 hard fail

## 5. 评分校准方案

### 分数上限

- `semantic_quality_score` 必须封顶 `100`

### 分数带

- `READY`: `90–100`
- `REVIEW`: `75–89`
- `FAIL`: `<75`

### 结果语义

- `gate_status`: `PASS / FAIL`
- `score_band`: `READY / REVIEW / FAIL`
- `publish_candidate_readiness`: `READY / REVIEW / NO_GO`

### 评判原则

- 工程通过不等于发布候选 ready
- `approval READY` 仍然只是“预览可人工审查”，不等于 publish candidate ready
- `publish_candidate_readiness` 需要更严格地结合 CTA 分布、proof 强度、重复结构和 hook 强度

## 6. 新增 hard / warn 规则

### Hard fail

以下情况仍然必须 hard fail，不弱化：

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

### Warn / structural risk

以下情况不一定 hard fail，但会拉低分数、影响 `publish_candidate_readiness`：

- early CTA
- repeated CTA
- abstract proof
- repeated role/template
- weak hook

## 7. 测试计划

新增 `tests/test_semantic_quality_gate.py`，覆盖：

- score never exceeds 100
- score band READY / REVIEW / FAIL
- hard fail 时 `publish_candidate_readiness = NO_GO`
- early CTA detection
- repeated CTA detection
- CTA 过多时 risk = high
- abstract proof detection
- repeated role/template detection
- weak hook detection
- `worst_3_scenes` 包含 structural_risks
- 缺 proof fail
- 缺 CTA fail
- contact sheet missing fail

## 8. 验收标准

- `semantic_quality_score <= 100`
- `score_band` 存在且正确
- `publish_candidate_readiness` 存在且正确
- early CTA / repeated CTA / abstract proof / repeated role-template / weak hook 可检测
- `worst_3_scenes` 包含 structural_risks
- hard fail 未弱化
- 测试通过
- 不改 renderer
- 不扩模板
- 不 render MP4
