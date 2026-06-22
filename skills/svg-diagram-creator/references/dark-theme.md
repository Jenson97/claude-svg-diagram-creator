# 深色技术风主题（Dark Technical Theme）

来源：Cocoon-AI/architecture-diagram-generator (MIT License) 的视觉规范，适配进本 skill。

## 何时使用

**触发词**：用户说"深色"、"赛博风"、"technical aesthetic"、"dark theme"、"工程风格"、"研发风"、"架构图（不指定颜色时）"等

**适用类型**：T1/T2/T4/T5/T6（技术正式类），尤其是**架构图、网络拓扑、云基础设施、安全分组**等场景

**不适用**：S1-S4（场景化）、E1-E2（漫画类）—— 这些类型保留原有浅色/活泼风格

## 输出格式

深色主题**强制使用 HTML 包裹 SVG**，而不是纯 SVG。原因：
- 需要 JetBrains Mono 字体（Google Fonts 引入）
- 需要导出工具栏（复制/PNG/PDF）
- 需要底部信息卡片网格

使用 `templates/dark-html-shell.html` 作为外壳，把 SVG 主体粘进去。

## 设计系统

### 背景与画布

| 元素 | 颜色 |
|------|------|
| 页面背景 | `#020617` (slate-950) |
| 卡片/容器背景 | `rgba(15, 23, 42, 0.5)` |
| 容器边框 | `#1e293b` |
| 网格线 | `stroke="#1e293b" stroke-width="0.5"`，40px 间距 |

### 组件配色（按语义）

| 组件类型 | 填充 (rgba) | 描边 |
|---------|-------------|------|
| Frontend / 前端 | `rgba(8, 51, 68, 0.4)` | `#22d3ee` (cyan-400) |
| Backend / 后端 | `rgba(6, 78, 59, 0.4)` | `#34d399` (emerald-400) |
| Database / 存储 | `rgba(76, 29, 149, 0.4)` | `#a78bfa` (violet-400) |
| Cloud / 云服务 | `rgba(120, 53, 15, 0.3)` | `#fbbf24` (amber-400) |
| Security / 安全 | `rgba(136, 19, 55, 0.4)` | `#fb7185` (rose-400) |
| Message Bus / 消息队列 | `rgba(251, 146, 60, 0.3)` | `#fb923c` (orange-400) |
| External / 通用 | `rgba(30, 41, 59, 0.5)` | `#94a3b8` (slate-400) |

**国内场景映射建议**：
- Kafka/Pulsar/RocketMQ → orange（Message Bus）
- Flink/Spark/计算任务 → emerald（Backend）
- HBase/KV/Redis/ES → violet（Database）
- 埋点/数据源 → slate（External）
- 鉴权/网关/SSO → rose（Security）

### 字体

```html
<link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600;700&display=swap" rel="stylesheet">
```

body 用：`font-family: 'JetBrains Mono', 'Microsoft YaHei', 'PingFang SC', monospace;`
（保留中文回退，避免中文字符变方块）

**字号**：
| 用途 | 字号 |
|------|------|
| 组件主标签 | 11-12px |
| 组件副标签 | 9px |
| 注释/小标注 | 8px |
| 微型标签 | 7px |

### 边界与分组

| 元素 | 样式 |
|------|------|
| 组件矩形圆角 | `rx="6"` |
| 组件描边宽度 | `stroke-width="1.5"` |
| 安全组（虚线） | `stroke-dasharray="4,4"` + `fill="transparent"` + rose 色 |
| 区域/Region 边界 | `stroke-dasharray="8,4"` + `rx="12"` + amber 色 + 极淡填充 `rgba(251, 191, 36, 0.05)` |

### 箭头

```svg
<marker id="arrowhead" markerWidth="10" markerHeight="7" refX="9" refY="3.5" orient="auto">
  <polygon points="0 0, 10 3.5, 0 7" fill="#64748b"/>
</marker>
```

**箭头颜色**：跟随源/目标组件的语义色（cyan/emerald/violet/amber）
**鉴权流箭头**：`stroke="#fb7185" stroke-dasharray="5,5"`

## 三条关键 Z-Order/遮罩规则

### 1. 箭头先画

SVG 按文档顺序绘制。**先画箭头线条，再画组件矩形** → 箭头自然被组件挡住，更整洁。

### 2. 半透明组件下加遮罩

组件填充是 `rgba(..., 0.4)`，箭头会透过来。需要完全遮挡时，先画一层不透明背景：

```svg
<!-- 遮罩层 -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="#0f172a"/>
<!-- 真正的样式组件 -->
<rect x="X" y="Y" width="W" height="H" rx="6" fill="rgba(76, 29, 149, 0.4)" stroke="#a78bfa" stroke-width="1.5"/>
```

### 3. Legend 放到边界之外

图例必须放在所有 boundary box（Region/Cluster/SG）的**外部**：
- 计算所有边界的 y + height
- Legend 至少在最低边界下方 20px
- viewBox 高度要扩展容纳

## 间距规范（防重叠）

| 元素 | 推荐值 |
|------|--------|
| 标准服务组件高度 | 60px |
| 较大组件高度 | 80-120px |
| 组件之间垂直最小间距 | 40px |
| Inline 连接器（如消息总线）位置 | 放在间距正中（如间距 40px → 连接器 20px 高，居中） |

**反例**：组件 B 起点 y=170，消息总线 y=160（会重叠）
**正例**：组件 A 终点 y=130，消息总线 y=140（高 20px），组件 B 起点 y=170

## 组件代码片段

### 标准服务卡片

```svg
<rect x="X" y="Y" width="W" height="60" rx="6"
      fill="rgba(6, 78, 59, 0.4)" stroke="#34d399" stroke-width="1.5"/>
<text x="CX" y="Y+24" fill="white" font-size="11" font-weight="600" text-anchor="middle">服务名</text>
<text x="CX" y="Y+42" fill="#94a3b8" font-size="9" text-anchor="middle">技术栈/端口</text>
```

### 多行组件（多桶/多 topic）

```svg
<rect x="X" y="Y" width="W" height="100" rx="6"
      fill="rgba(120, 53, 15, 0.3)" stroke="#fbbf24" stroke-width="1.5"/>
<text x="CX" y="Y+20" fill="white" font-size="11" font-weight="600" text-anchor="middle">组件标题</text>
<text x="CX" y="Y+40" fill="#94a3b8" font-size="8" text-anchor="middle">• 项 1</text>
<text x="CX" y="Y+54" fill="#94a3b8" font-size="8" text-anchor="middle">• 项 2</text>
<text x="CX" y="Y+68" fill="#94a3b8" font-size="8" text-anchor="middle">• 项 3</text>
<text x="CX" y="Y+86" fill="#fbbf24" font-size="7" text-anchor="middle">标记/属性</text>
```

### 区域边界

```svg
<rect x="X" y="Y" width="W" height="H" rx="12"
      fill="rgba(251, 191, 36, 0.05)" stroke="#fbbf24" stroke-width="1" stroke-dasharray="8,4"/>
<text x="X+12" y="Y+18" fill="#fbbf24" font-size="10" font-weight="600">Region: us-west-2</text>
```

### 安全组（虚线）

```svg
<rect x="X" y="Y" width="W" height="H" rx="8"
      fill="transparent" stroke="#fb7185" stroke-width="1" stroke-dasharray="4,4"/>
<text x="X+8" y="Y+14" fill="#fb7185" font-size="8">sg-name :port</text>
```

### 消息总线（细长条）

```svg
<rect x="X" y="Y" width="120" height="20" rx="4"
      fill="rgba(251, 146, 60, 0.3)" stroke="#fb923c" stroke-width="1"/>
<text x="CX" y="Y+14" fill="#fb923c" font-size="7" text-anchor="middle">Kafka / Pulsar</text>
```

### 鉴权弯曲流

```svg
<path d="M 80 140 L 80 200 Q 80 220 100 220 L 200 220 Q 220 220 220 240 L 220 278"
      fill="none" stroke="#fb7185" stroke-width="1.5" stroke-dasharray="5,5"/>
<text x="150" y="210" fill="#fb7185" font-size="8">JWT + PKCE</text>
```

## 工作流

1. 用户触发深色风格 → 用 `templates/dark-html-shell.html` 作为外壳
2. 把对应 T 类型（T1/T2/T4/T5/T6）的 SVG 主体粘到 `<svg viewBox=...>` 内
3. 颜色按语义重映射（不使用本文件第六节的浅色配色，使用本文件的深色配色）
4. 字号下调（深色背景上 11-12px 已经够清晰）
5. 检查间距、遮罩、图例位置
6. 输出 `.html` 文件，浏览器直接打开

## 与浅色主题的差异速查

| 维度 | 浅色（默认）| 深色（Cocoon 风）|
|------|------------|---------------|
| 背景 | `#F0F3F8` | `#020617` + 网格 |
| 主字体 | 微软雅黑/苹方 | JetBrains Mono（中文回退苹方） |
| 组件描边 | 实色 1.5-2px | 1.5px + 高亮色（cyan/emerald/violet…） |
| 组件填充 | 浅色实色（#E8F2FF 等） | 半透明 rgba 0.3-0.4 |
| 输出格式 | 纯 SVG | HTML 包裹 SVG + 导出工具栏 |
| 字号 | 主标题 17-19，卡片 12-13 | 主标签 11-12，副标签 9 |

## 归属

视觉设计来源：[Cocoon-AI/architecture-diagram-generator](https://github.com/Cocoon-AI/architecture-diagram-generator) (MIT License)，本 skill 中的 `templates/dark-html-shell.html` 派生自该项目的 `resources/template.html`。
