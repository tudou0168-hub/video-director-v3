# P4.1B-R4 Real Follow-up: Preview Load Fix + Unified Visual Layout Rules

## 结论

- 本轮目标：修复 HyperFrames Studio 预览加载错误，并把通用构图规则做成稳定的中轴布局容器。
- 预览加载根因：Studio 之前挂在旧的 `p4_1b_r4_followup_visual_rules_preview` 项目目录上，导致当前页面显示成 `0:00 / 0:00` 的空项目态；已经清掉旧 server，并用正确的 `outputs/p4_1b_r4_real_followup_visual_layout_preview/hyperframes_timeline` 重新启动 `http://localhost:3002`。
- 本轮已经把通用视觉容器接进渲染层：`vf-visual-stage`、`vf-skeleton-main`、`vf-visual-center-band`、`vf-support-layer`、`vf-caption-zone`、`vf-glass-anchor-card`。
- 本轮没有 render MP4，没有提交 `outputs/` / `renders/` / `contact-sheet.jpg`。

## 事实核验

- 正确 branch：`main`
- 当前工作区最新远端 commit：`a422f6b3d2b310e505fefa60fe958f13adaf3f96`
- GitHub URL：[a422f6b3d2b310e505fefa60fe958f13adaf3f96](https://github.com/tudou0168-hub/video-director-v3/commit/a422f6b3d2b310e505fefa60fe958f13adaf3f96)
- preview 输出目录：`/Users/muzi/video-director-v3/outputs/p4_1b_r4_real_followup_visual_layout_preview/`
- Studio preview：已恢复到正确项目目录
- preview 是否重新生成：`yes`
- preview 输出路径：`/Users/muzi/video-director-v3/outputs/p4_1b_r4_real_followup_visual_layout_preview/`
- contact sheet 路径：`/Users/muzi/video-director-v3/outputs/p4_1b_r4_real_followup_visual_layout_preview/review_frames/contact-sheet.jpg`
- 是否生成 MP4：`no`
- 是否提交 outputs/renders/contact-sheet：`no`

## 根因

1. `localhost:3002` 当时跑的是旧 project directory，而不是这次新的 `p4_1b_r4_real_followup_visual_layout_preview`。
2. 新 preview 目录里的 `hyperframes_timeline/index.html` 和 `data/*.json` 本身是完整的，问题不在产物缺失，而在 Studio 启动的项目路径。
3. 杀掉旧 preview server 后，用正确目录重启后，HyperFrames Studio 才挂到当前输出目录。

## 通用视觉规则

### 1) 中轴布局

- `hero_metric`、`tool_pipeline`、`framework_map / proof_matrix`、`action_close / checklist_close` 都改成统一的视觉 stage / skeleton / support 结构。
- 主视觉不再一股脑压在顶部，而是进入 `--vf-main-top` 定义的中段。
- 支持层（glass card / result card）退到右侧或下方，承担解释与锚点作用，不再压住主体。

### 2) 字幕统一

- 所有 caption 走同一个 foundation：相同底层样式、相同安全区、相同底部位置、相同最大宽度。
- `caption_mode` 只保留轻微差异，不再像两套系统。
- 第 5 张旧字幕风格的问题，通过统一底座和去掉特殊左对齐 / 偏离式样式来修正。

### 3) 玻璃卡语义承托

- 玻璃卡保留，但只做语义承托层。
- `hero_metric`：数字 + 单位 + 标题 + 右侧 anchor card。
- `tool_pipeline`：节点链路 + 结果卡。
- `framework_map / proof_matrix`：结构图 + 右侧 insight card。
- `action_close / checklist_close`：主结论 + CTA / checklist + save reason。

### 4) fallback 文案门

- 任何 `这一帧需要补充` / `需要补充语义内容` / `TODO` / `PLACEHOLDER` / `placeholder` 进入 scene / caption / index.html / report 都应继续 hard fail 或 NO-GO。

## 测试

- `PYTHONPATH=src .venv/bin/python3 -m pytest tests/test_visual_strategy_pack.py tests/test_semantic_quality_gate.py tests/test_scene_pack_contracts.py tests/test_preview_pipeline.py tests/test_tts_contract.py tests/test_render_gate.py tests/test_offer_proof_cta_contracts.py -q`
  - `91 passed`
- `PYTHONPATH=src .venv/bin/python3 -m compileall src tests`
  - `PASS`
- `git diff --check`
  - `PASS`

## 下一步建议

- 建议继续：`P4.1B-R4 Follow-up Fix`
- 说明：当前结构容器和 preview load 问题已修复，但在没有进一步人眼确认 contact sheet 的前提下，不建议直接跳到 R5。
