# Preview Standard — HyperFrames Studio Native Only

## 唯一主线

V3 预览唯一路线：**HyperFrames Studio 原生项目预览**。

```
文案/选题
  → script.json
  → 男声 TTS
  → 读取音频真实时长
  → caption_beats.json
  → director_timeline.json
  → visual_beats.json
  → transition_map.json
  → HyperFrames Studio 原生项目目录
  → HyperFrames Studio timeline HTML 预览
  → 人工审查
  → 最终确认后 render MP4
```

## 为什么不再使用 combined/index.html

1. `combined/index.html` 使用定制 GSAP 时间轴架构
2. 不支持 HyperFrames Studio 原生加载
3. 无法复用 Studio 的 playback control、scene graph、inspector 等能力
4. `file://` 协议打开的普通 HTML 不能作为产品验收物

## 为什么不允许 file:// 普通页面作为验收

1. `file://` 页面没有 Studio 的项目上下文
2. 无法验证 scene / audio / caption / visual beats 的 Studio 结构正确性
3. 无法保证输出产物是 HyperFrames Studio 可加载的原生项目
4. 违反"优先复用成熟稳定的 HyperFrames Studio 能力"原则

## 标准输出目录

```
outputs/<project_id>/hyperframes_timeline/
├── meta.json
├── index.html
├── assets/
│   └── voiceover.mp3
├── data/
│   ├── script.json
│   ├── tts_result.json
│   ├── caption_beats.json
│   ├── director_timeline.json
│   ├── visual_beats.json
│   └── transition_map.json
├── compositions/
└── report.md
```

## 标准预览 URL

```
http://localhost:3002/#project/hyperframes_timeline
```

或者实际项目名：
```
http://localhost:3002/#project/<project_id>
```

## 标准数据文件

| 文件 | 用途 |
|------|------|
| `meta.json` | 项目元信息 |
| `data/script.json` | 原始文案 |
| `data/tts_result.json` | TTS 结果 |
| `data/caption_beats.json` | 字幕时间轴 |
| `data/director_timeline.json` | 导演时间轴 |
| `data/visual_beats.json` | 视觉节奏 |
| `data/transition_map.json` | 转场映射 |
| `assets/voiceover.mp3` | 音频文件 |

## 人工审查标准

1. Studio 是否正常加载项目
2. 是否有 scene / audio / caption / visual beats
3. 1080×1920 是否正确
4. 音频是否可播放
5. 字幕是否全程覆盖
6. visual beats 是否随时间切换
7. 是否无黑屏
8. 是否无内部调试词

## QA 标准

| 检查项 | 要求 |
|--------|------|
| Studio 加载 | 项目正常打开，无"请先选择"黑屏 |
| 默认 scene | 打开即显示 scene01 |
| 音频 | voiceover.mp3 可播放，duration 正确 |
| 字幕 | 全程覆盖，无遗漏 |
| 视觉节奏 | visual beats 随时间切换 |
| 分辨率 | 1080×1920 |

## MP4 渲染前置条件

1. HyperFrames Studio 原生预览通过人工审查
2. `--approved` flag 已设置
3. 项目目录 `hyperframes_timeline/` 结构完整
4. 所有 data 文件存在

## 新 Claude 接手时必须遵守的预览路线

1. 预览只允许 HyperFrames Studio 原生项目预览
2. `file://` 普通 HTML 不是验收物
3. 不能用 autoplay / JS 强制 play 绕过 Studio
4. combined/index.html 不属于 V3 当前主线
5. 所有产物必须是可以被 HyperFrames Studio 加载的原生项目结构

## 废弃路线（不应再使用）

- ❌ `combined/index.html` — V3 早期实验性输出，已废弃
- ❌ `file://` 协议打开 HTML — 不是 Studio 原生项目
- ❌ 自定义 GSAP 时间轴架构作为主线
- ❌ 普通静态 HTML 页面作为验收物
- ❌ `open outputs/.../combined/index.html` 命令

---
最后更新：2026-05-31