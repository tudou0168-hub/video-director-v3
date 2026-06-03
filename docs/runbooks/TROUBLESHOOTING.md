# Troubleshooting Runbook

## 1. preview 失败

先看：

- `scene_pack.json`
- `semantic_quality_report.json`
- `approval_required.json`
- `error_report.json`

### 常见原因

- `template_contracts` fail
- `semantic_quality` fail
- `review_frames` 不足
- `contact-sheet.jpg` 缺失

## 2. CTA 太早或太多

检查：

- `cta_scene_count`
- `cta_policy_risk`
- `early_cta_count`
- `repeated_cta_count`

如果是 sales 场景，先看 `offer_profile_ref` 是否存在，再看 `cta_stage` 是否在 `final`。

## 3. proof 太空

检查：

- `proof_asset_ref`
- `metric_or_evidence`
- `fake_metric_count`
- `generic_proof_count`

## 4. MP4 不能渲染

确认：

- `--approved` 是否带了
- `approval_required.json` 是否 `READY`
- 是否已经人工确认 preview

## 5. 不要改的地方

- 不要改 HyperFrames renderer
- 不要回 `combined/index.html`
- 不要接入 `narrative_compressor.py`
- 不要把 outputs / renders 提交到 GitHub

