---
name: "responsive-layout"
description: 掌握响应式与流式布局的实用方法：断点策略、容器查询、Fluid 排版与栅格系统。适用于设计多端适配的页面布局或排查断点错位问题。
---

# 响应式布局

以"内容优先、断点辅助"为指导的响应式布局实践，覆盖断点选取、流式单位、容器查询与栅格组织。

## 何时使用本技能

- 设计需要适配多端（手机/平板/桌面）的页面或组件
- 排查特定断点下的布局错位、溢出或留白异常
- 评估是否用容器查询替代媒体查询
- 制定团队统一的断点与间距规范

## 移动优先策略

默认样式服务最小视口，用 `min-width` 媒体查询逐步增强：

```css
/* 基础：移动端单列 */
.grid { display: grid; gap: 1rem; }

/* 平板：两列 */
@media (min-width: 48rem) {
  .grid { grid-template-columns: 1fr 1fr; }
}

/* 桌面：三列 */
@media (min-width: 64rem) {
  .grid { grid-template-columns: repeat(3, 1fr); }
}
```

## 断点选取

| 名称 | 宽度 | 典型设备 |
|------|------|---------|
| sm | ≥640px | 大手机竖屏 |
| md | ≥768px | 平板竖屏 |
| lg | ≥1024px | 平板横屏 / 小笔记本 |
| xl | ≥1280px | 桌面 |

断点应根据**内容断点**而非设备断点定——当布局"不舒服"时就加断点，不要硬绑设备型号。

## 容器查询（组件级响应式）

媒体查询基于视口，容器查询基于组件自身尺寸，更利于复用：

```css
.card {
  display: grid;
  gap: 1rem;
}
.card__media { display: none; }

@container (min-width: 30rem) {
  .card { grid-template-columns: auto 1fr; }
  .card__media { display: block; }
}

/* 父容器需声明容器上下文 */
.sidebar { container-type: inline-size; }
```

适用场景：组件在不同位置宽度不同（侧栏窄、主区宽），同一组件代码自适应。

## Fluid 排版

用 `clamp()` 让字号在区间内流畅变化，无需多个断点：

```css
h1 {
  font-size: clamp(1.5rem, 1.2rem + 2vw, 2.5rem);
}
```

公式：`clamp(最小值, 首选值, 最大值)`，首选值通常用 `基准 + vw 偏移`。

## 栅格组织

优先 CSS Grid 处理二维布局，Flexbox 处理一维排列：

```css
/* 经典 12 列栅格，按需跨越 */
.layout {
  display: grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 1.5rem;
}
.layout__main { grid-column: span 8; }
.layout__side { grid-column: span 4; }

@media (max-width: 48rem) {
  .layout__main, .layout__side { grid-column: span 12; }
}
```

## 常见问题排查

| 现象 | 可能原因 | 对策 |
|------|---------|------|
| 内容横向溢出 | 固定宽度元素或图片未限宽 | `max-width: 100%`、`overflow-wrap` |
| 断点跳动突兀 | 缺少过渡断点 | 增加中间断点或改用流式 |
| 组件在侧栏挤压 | 用了视口媒体查询 | 改用容器查询 |
| 移动端字太小 | 桌面尺寸硬编码 | 用 clamp 流式排版 |
