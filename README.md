# Video Director V3

中文文案先进入 `script.json`、男声 TTS、真实音频时长、`caption_beats.json`、`director_timeline.json`、`visual_beats.json`、`transition_map.json`，再生成 HyperFrames Studio 原生项目预览。只有用户人眼确认后，才允许 `render_mp4` 输出最终 MP4。

## 项目定位

V3 唯一主线：
```
文案
→ script.json
→ 男声 TTS
→ 读取音频真实时长
→ caption_beats.json
→ director_timeline.json
→ visual_beats.json
→ transition_map.json
→ HyperFrames Studio 原生 HTML 预览
→ 人工审查
→ 用户确认后才 render MP4
```

**当前不是：**
- `combined/index.html` 静态预览系统
- `file://` 普通 HTML 验收
- Remotion 主流程
- CapCut 主流程
- 中间阶段 render MP4
- JS/GSAP 自定义页面作为主线
- 静态图 concat 视频

## 新用户和新 Agent 从哪里开始

1. 先读 `AGENTS.md`
2. 再读 `docs/agents/ANY_AGENT_START_HERE.md`
3. 然后读 `docs/status/PROJECT_STATE.md`、`docs/status/NEXT_TASK.md`、`docs/status/CURRENT_BUGS.md`
4. 如果是在做清理盘点，先看 `docs/cleanup-plan.md`
5. 如果是在做主线预览，直接跑下面的 `hyperframes_preview`

## 快速开始

### 安装依赖

```bash
cd <PROJECT_ROOT>
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```

### 运行 preview

```bash
python3 -m video_director_v3.cli \
  --script samples/scripts/minimal_obsidian_codex_hermes.md \
  --platform douyin \
  --target-duration 40 \
  --project-id demo_v3_preview \
  --output-mode hyperframes_preview \
  --tts-mode edge_tts \
  --tts-fallback system_say \
  --design-variance 7 \
  --motion-intensity 6 \
  --visual-density 8 \
  --no-allow-mock-audio
```

这只是示例预览命令，`--target-duration 40` 不是产品约束。

### 查看预览

**唯一预览路线**：HyperFrames Studio 原生项目预览。

1. 启动 HyperFrames Studio 本地服务（确保 `http://localhost:3002` 可访问）
2. 打开：`http://localhost:3002/#project/hyperframes_timeline`
3. 检查 `outputs/demo_v3_preview/review_frames/` 截图
4. 检查 `outputs/demo_v3_preview/approval_required.json`

Studio 审查标准：
- Studio 是否正常加载项目
- 是否有 scene / audio / caption / visual beats
- 1080×1920 是否正确
- 音频是否可播放
- 字幕是否全程覆盖
- visual beats 是否随时间切换
- 是否无黑屏
- 是否无内部调试词

### 审批后渲染 MP4

只有用户确认预览通过后，才允许执行。

```bash
python3 -m video_director_v3.cli \
  --project-id demo_v3_preview \
  --output-mode render_mp4 \
  --approved
```

找到最终视频：`outputs/demo_v3_preview/rendered/final_video.mp4`

## 目录结构

```
video-director-v3/
├── AGENTS.md
├── README.md
├── requirements.txt
├── pyproject.toml
├── package.json
├── .gitignore
├── docs/
│ ├── architecture.md
│ ├── quickstart-preview-to-mp4.md
│ ├── migration-from-v2.md
│ ├── design-system.md
│ ├── testing.md
│ ├── cleanup-plan.md
│ └── archive/
├── samples/scripts/
│ └── minimal_obsidian_codex_hermes.md
├── src/video_director_v3/
│ ├── cli.py
│ ├── config.py
│ ├── pipeline/
│ │ ├── pipeline_runner.py
│ │ ├── stages.py
│ │ └── project_paths.py
│ ├── director/
│ │ ├── script_semantic_extractor.py
│ │ ├── narration_planner.py
│ │ ├── input_relevance_evaluator.py
│ │ └── storyboard_builder.py
│ ├── design/
│ │ ├── design_dials.py
│ │ ├── design_profile_builder.py
│ │ ├── brandkit_adapter.py
│ │ └── stitch_design_adapter.py
│ ├── tts/
│ │ ├── tts_adapter.py
│ │ └── edge_tts_provider.py
│ ├── motion/
│ │ ├── caption_beat_generator.py
│ │ ├── visual_beat_planner.py
│ │ ├── motion_event_bindings.py
│ │ ├── component_registry.py
│ │ └── semantic_transition_planner.py
│ ├── renderers/
│ │ ├── hyperframes/
│ │ │ ├── html_renderer.py
│ │ │ ├── combined_html_builder.py (deprecated)
│ │ │ └── scene_layout_director.py
│ │ └── browser/
│ │ ├── review_frame_capturer.py
│ │ └── browser_mp4_renderer.py
│ ├── quality/
│ │ ├── quality_checker.py
│ │ ├── rendered_frame_inspector.py
│ │ └── report_builder.py
│ └── exporters/
│ └── approval_gate.py
├── scripts/
│ ├── run_preview.sh
│ ├── render_approved_mp4.sh
│ └── clean_test_outputs.sh
└── tests/
```

## 输出目录规则

- **正式输出**: `outputs/<project_id>/`
- **测试输出**: `test_outputs/<project_id>/`

禁止写入 `src/outputs/` 或临时散落目录。

## V3 两个模式

### hyperframes_preview

生成 HTML 动画预览，包含：
- `hyperframes_timeline/` 原生项目目录
- review_frames/
- approval_required.json
- quality_report.json

**禁止**生成 final_video.mp4，也禁止在中间阶段渲染 MP4。

### render_mp4

必须有 `--approved` flag。从 HyperFrames Studio 原生预览通过的项目渲染 MP4。

**不允许**在 preview 之后、用户确认之前直接进入 MP4 渲染。

## 常见问题

### 黑屏
检查 hyperframes_timeline 项目是否正确加载，scene-layer divs 是否有 data-composition-id。

### 没音频
确认 audio/voiceover.mp3 存在，检查 TTS provider 是否正常。

### 字幕重叠
检查 caption_beats.json 中是否有 overlap，调整 beat 数量。

### render_mp4 被拒绝，因为未 approve
必须先运行 hyperframes_preview，再加 --approved 运行 render_mp4。

### Studio 原生预览
V3 使用 HyperFrames Studio 原生项目预览作为唯一审查路线。

## 已废弃路线

以下路线只应出现在历史记录、废弃说明或清理清单中，不应作为当前主线入口：

- `combined/index.html`
- `file://`
- fallback
- 普通静态 HTML 预览
- Remotion 主线
- CapCut 主流程
- 中间阶段 render MP4
- R9 / R16 历史调试路线
- JS / GSAP 自定义页面作为主线
- mute-blocker / patch `HTMLMediaElement.prototype`
- 固定 18 秒 smoke
- 静态图 concat 视频

## 接手说明

如果你是新 agent：

1. 先读 `AGENTS.md`
2. 再读 `docs/agents/ANY_AGENT_START_HERE.md`
3. 再读 `docs/cleanup-plan.md`
4. 然后按 `docs/runbooks/COMMANDS.md` 跑主线命令
5. 不要在用户确认前执行 `render_mp4`

## 设计技能融合

V3 接入以下技能作为 Design Profile 层：

- **stitch-skill**: 生成 DESIGN.md（视频视觉设计规范）
- **brandkit**: 生成 brandkit.json（统一颜色、字体、组件风格）
- **imagegen-frontend-***: 可选视觉参考图，不阻塞 preview
- **三个设计旋钮**:
  - DESIGN_VARIANCE (1-10): 控制版式变化度
  - MOTION_INTENSITY (1-10): 控制动效强度
  - VISUAL_DENSITY (1-10): 控制信息密度

## Agent Handoff / Persistent Memory

Claude Code 重启后不会自动记住项目历史。
本项目使用 `docs/status` + `docs/agents` 作为持久化项目记忆。

**任何智能体接手必须先读：**
- `AGENTS.md` — 行为规范和接手要求
- `docs/agents/ANY_AGENT_START_HERE.md` — 通用接手步骤
- `docs/status/PROJECT_STATE.md` — 项目当前状态
- `docs/status/NEXT_TASK.md` — 当前任务和禁止事项
- `docs/cleanup-plan.md` — 清理盘点与后续执行边界

**启动新会话前运行：**
```bash
bash scripts/memory/start_agent_session.sh
```

## 系统要求

- Python 3.10+
- ffmpeg / ffprobe
- Node/npm（可选）
- Playwright Chromium

## 安装命令

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m playwright install chromium
```
