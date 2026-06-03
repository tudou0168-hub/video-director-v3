# NEXT TASK

## 当前任务

**P3.13A Offer-Proof-CTA System** — 正在把成交结构独立成显式契约层，补齐 offer / proof / CTA 资产与 QA gate，保持主线不变、不 render MP4。

当前重点：

- `samples/offers/default_ai_content_system.yaml`
- `samples/proofs/default_ai_content_system.yaml`
- `samples/cta/default_value_first.yaml`
- `src/video_director_v3/director/offer_profile.py`
- `src/video_director_v3/director/proof_asset.py`
- `src/video_director_v3/director/cta_policy.py`
- `src/video_director_v3/director/semantic_planner.py`
- `src/video_director_v3/qa/semantic_quality_gate.py`
- `tests/test_offer_proof_cta_contracts.py`

## 本轮改动

### P3.13A

- 新增 offer / proof / CTA contract assets
- 让 `scene_pack` 持有 offer / proof / CTA refs 与 stage/strength 扩展字段
- 让 semantic planner 为 sales-like 场景注入更稳的承诺与证据资产
- 让 QA gate 拦截早 CTA、重复 CTA、伪造 proof metric、低质 CTA phrase

## 验证

待完成：

- `pytest tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
- `python -m compileall src tests`
- `git diff --check`

## 交付物

- `docs/status/P3_13A_OFFER_PROOF_CTA_SYSTEM.md`
- `docs/status/P3_13A_IMPLEMENTATION_REPORT.md`

## 注意

- 不 render MP4
- 不提交 outputs/
- 不提交 renders/
- 不把 `narrative_compressor.py` 接入主线

---
最后更新：2026-06-03
