# P4.1B-R4.1 Visual Scene Aggregation

## 阶段目的

把一条 40s smoke 的 24 个源 scene 聚合成更少、更可读的视觉章节，验证：

- `director_timeline.json` 是否从“逐句 scene”切换到“视觉 chapter”
- `caption beats` 是否仍保持完整
- `layout density gate` 是否能拦住过密/重复骨架
- `index.html` 是否仍然和 `director_timeline.json` 保持一致

## 输入脚本

- [samples/scripts/p4_batch_ai_toolflow.md](/Users/muzi/video-director-v3/samples/scripts/p4_batch_ai_toolflow.md)

## preview 输出

- [outputs/p4_1b_r4_1_visual_scene_aggregation_preview/](/Users/muzi/video-director-v3/outputs/p4_1b_r4_1_visual_scene_aggregation_preview)
- contact sheet: [review_frames/contact-sheet.jpg](/Users/muzi/video-director-v3/outputs/p4_1b_r4_1_visual_scene_aggregation_preview/review_frames/contact-sheet.jpg)
- HyperFrames 入口: [hyperframes_timeline/index.html](/Users/muzi/video-director-v3/outputs/p4_1b_r4_1_visual_scene_aggregation_preview/hyperframes_timeline/index.html)

## 聚合前后数量

| 指标 | 聚合前 | 聚合后 |
|---|---:|---:|
| source scene 数量 | 24 | 24 |
| visual chapter 数量 | 24 | 8 |
| caption beat 数量 | 39 | 39 |

## 时长

- 总时长：`113.226s`
- visual chapter 平均时长：`14.153s`
- 最短 visual chapter 时长：`12.446s`
- 最长 visual chapter 时长：`15.422s`

## 章节映射

| visual chapter | source_scene_ids | caption_ids | layout_family | duration |
|---|---|---|---|---:|
| `V01` | `S01,S02,S03` | `S01_C01,S01_C02,S01_C03,S02_C01,S03_C01,S03_C02` | `file_tree` | `14.500s` |
| `V02` | `S04,S05,S06,S07` | `S05_C01,S06_C01,S07_C01` | `tool_pipeline` | `14.951s` |
| `V03` | `S08,S09` | `S08_C02,S08_C03,S09_C01,S09_C02,S09_C03` | `framework_map` | `13.428s` |
| `V04` | `S10,S11,S12` | `S10_C02,S11_C01,S12_C01` | `config_panel` | `14.711s` |
| `V05` | `S13,S14,S15` | `S14_C01,S15_C01,S16_C01` | `framework_map` | `12.687s` |
| `V06` | `S16,S17,S18` | `S17_C02,S17_C03,S18_C01,S19_C01` | `framework_map` | `12.446s` |
| `V07` | `S19,S20` | `S20_C02,S21_C01,S21_C02,S21_C03` | `action_close` | `15.081s` |
| `V08` | `S21,S22,S23,S24` | `S23_C01,S24_C01,S24_C02,S25_C01` | `framework_map` | `15.422s` |

## 当前判断

这轮已经把 24 个源 scene 收敛成 8 个视觉章节，且 caption beat 没丢，平均视觉章节时长也明显上去了。

需要继续留意的点：

- `V01` 的视觉骨架仍偏 `file_tree`，和首章“工具栈”语义还有一点错位
- `framework_map` 在 `V03 / V05 / V06 / V08` 里仍然出现得较多，重复感比理想状态高一点
- 这条 40s smoke 本身没有 `hero_metric` 章节，所以这轮没法验证 hero 数字卡是否也被同样稳定聚合

## 验证

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
  - `93 passed`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
  - `PASS`
- `git diff --check`
  - `PASS`

## 下一步建议

先做一次小范围 follow-up fix，优先看：

1. 章节代表 scene 的选择规则是否还能再压一轮重复感
2. `framework_map` 的重复是否可以更均匀地拆到其他语义骨架
3. 再用一条不同类型文案验证泛化能力

