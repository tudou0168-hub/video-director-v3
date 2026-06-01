# V3-P2.6-HF HUD 风格简要规范

> 本文档定义 HyperFrames 视觉生成的 HUD 风格约束。
> 基于参考视频分析和 Remotion P2.6-S2 经验总结。

---

## 视觉目标

**参考视频核心风格：**
- 电影感暗背景（非纯黑，有色调和层次）
- 内容生产驾驶舱感（数据面板 + 软件界面 + 截图空间）
- 半透明 HUD 面板（非实心卡片）
- 真实/模拟工作台空间（模糊浏览器、代码编辑器、文档堆叠）
- 大标题压迫感
- 数据表格 / 进度条 / 评分条交织
- 局部光效（glow / scan / 脉冲）

**本项目目标：**
- 甩掉"深色网格 PPT"标签
- 达到"电影感内容生产驾驶舱"视觉密度
- 信息层次清晰（HUD 标签 / 大数字 / 正文 / 结论条）

---

## 色彩系统

### 主色

| 用途 | 色值 | 说明 |
| --- | ---- | ---- |
| 背景 | `#050812` | 近黑带蓝调 |
| 面板底 | `rgba(8,12,22,0.82)` | 玻璃面板背景 |
| HUD 蓝 | `#25D8FF` | 标签 / 进度条 |
| 成功绿 | `#28F57A` | 完成 / 通过 |
| 警告黄 | `#F6B84A` | 警告 / 注意 |
| 危险红 | `#FF4757` | 警报 / 失败 |
| 强调紫 | `#B45CFF` | 工具 / 流程 |
| 文字白 | `#F4F7FF` | 主要文字 |
| 文字灰 | `#9AA4B2` | 次要文字 |

### 光效色（带透明度）

| 用途 | 示例 |
| --- | ---- |
| Glow 主色 | `radial-gradient(circle, ${color}18 0%, transparent 70%)` |
| Glow 叠加 | `radial-gradient(circle, ${color}10 0%, transparent 70%)` |
| 边框 | `${color}50` (50% opacity) |
| 填充 | `${color}12` (12% opacity) |

---

## 字体层级

### 数字

- BigMetric: `136px / weight 900 / letter-spacing: -3`
- 对比数字（BeforeAfter）: `120px / weight 900`
- 节点标签: `38px / weight 800`

### 标题

- 主标题: `64px / weight 900 / line-height: 1.15`
- 场景标签: `28px / weight 700`
- HUD 标签: `16px / weight 800 / letter-spacing: 0.24em / uppercase`

### 正文

- 表格行: `22px / weight 600`
- 列表项: `22px / weight 600`
- 结论条: `28px / weight 800`

### 小字

- 子标签: `18px / weight 400`
- 表格头: `13px / weight 800 / letter-spacing: 0.18em / uppercase`

---

## 组件规范

### StatusBadge

```css
padding: 8px 18px;
border-radius: 22px;
background: ${color}22;
border: 1.5px solid ${color}70;
box-shadow: 0 0 12px ${color}30;
font-size: 14px;
font-weight: 800;
letter-spacing: 0.18em;
text-transform: uppercase;
```

### BigMetric

```css
font-size: 136px;
font-weight: 900;
text-shadow: 0 0 40px ${color}80, 0 0 80px ${color}50, 0 0 120px ${color}30;
line-height: 1;
letter-spacing: -3;
```

### GlassPanel

```css
background: rgba(8,12,22,0.82);
border: 1.5px solid ${color}50;
border-radius: 16px;
backdrop-filter: blur(16px);
box-shadow: 0 0 32px ${color}20, inset 0 0 24px ${color}08, 0 8px 32px rgba(0,0,0,0.4);
```

### ConclusionBar

```css
background: rgba(8,12,22,0.80);
border: 1.5px solid ${color}55;
border-left: 5px solid ${color};
border-radius: 14px;
box-shadow: 0 0 32px ${color}25, 0 8px 24px rgba(0,0,0,0.4);
backdrop-filter: blur(12px);
font-size: 28px;
font-weight: 800;
```

### HudHeader

```css
/* 标签线 */
width: 5px;
background: ${color};
box-shadow: 0 0 16px ${color}, 0 0 32px ${color}40;
border-radius: 2px;

/* 标签 */
font-size: 16px;
font-weight: 800;
letter-spacing: 0.24em;
color: ${color};
text-transform: uppercase;
text-shadow: 0 0 12px ${color}60;

/* 中文标题 */
font-size: 28px;
font-weight: 700;
color: #F4F7FF;
letter-spacing: 0.04em;
```

---

## 背景层叠顺序（从底到顶）

```
1. 纯色底 #050812
2. radial-gradient 色调层（蓝/绿/紫，5-8% opacity）
3. 模拟工作台 UI 层（模糊浏览器 / 代码 / 文档，30-40% opacity）
4. 72px 网格线（3-5% opacity）
5. 多层 radial glow（15-18% opacity，圆形，位置错开）
6. 扫描线（repeating-linear-gradient，2px 间隔，0.5% opacity）
7. vignette（radial-gradient，中心透明，边缘 70% 黑）
8. HUD 内容层
9. 结论条层（底部 96px）
```

---

## 动效规范

### GSAP 时间轴格式

```js
// ✅ 正确
tl.fromTo("#element",
  { y: 50, opacity: 0 },
  { y: 0, opacity: 1, duration: 0.7, ease: "expo.out" },
  0.3  // position
);

// ❌ 禁止
tl.from("#element", { y: 50, opacity: 0, duration: 0.7 }); // no position
tl.to("#element", { opacity: 0 }); // 禁止场景内退场
```

### 缓动函数选择

| 场景 | 缓动 | 时长 |
| --- | --- | --- |
| 数字跳变 | `power4.out` | 1.0s |
| 标题滑入 | `expo.out` | 0.7s |
| 列表涌入 | `power2.out` | 0.4s |
| 徽章弹入 | `back.out(2.5)` | 0.3s |
| 脉冲 | `sine.inOut` | 1.5s repeat |
| Ambient glow | `sine.inOut` | 3s repeat |

---

## 禁止模式

| 禁止 | 替代 |
| --- | --- |
| 白色背景 | #050812 + 多层 glow |
| 居中对称布局 | 左重右轻 or 右重左轻 |
| 纯文字海报 | 数字 + 面板 + 列表 + 状态徽章交织 |
| 无 glow 无脉动 | radial glow + 脉冲动画 |
| 机械 spring 动画 | 多样缓动 + stagger |
| system-ui 默认字体 | PingFang SC + font-weight 控制 |
| 等高等宽节点 | 断点节点加 FAIL badge + shake + glow |
| 无色区分 | Before=red / After=green |