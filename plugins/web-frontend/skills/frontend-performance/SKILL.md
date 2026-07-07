---
name: "frontend-performance"
description: 掌握前端性能优化的关键路径：首屏渲染、打包拆分、渲染开销与资源加载策略。适用于定位页面卡顿、首屏慢或打包体积过大的问题。
---

# 前端性能

以前端用户体感为目标的性能优化指南，聚焦首屏、运行时与资源三个维度，给出可测量、可落地的改进路径。

## 何时使用本技能

- 页面首屏加载慢、FCP/LCP 不达标
- 交互卡顿、滚动掉帧、输入延迟
- 打包体积过大、构建产物冗余
- 制定性能预算或建立监控基线

## 性能模型

理解三个关键阶段：

```
加载性能      首字节 → 首次内容绘制 → 最大内容绘制 → 可交互
  关注: 关键路径、阻塞资源、体积
运行时性能    交互响应、动画帧率、滚动流畅度
  关注: 主线程占用、重渲染、布局抖动
资源性能      字体、图片、脚本的网络开销
  关注: 缓存、预加载、按需加载
```

## 首屏优化

### 关键渲染路径

1. **减少阻塞**：CSS 放头部、JS 异步化（`async`/`defer`）
2. **内联关键 CSS**：首屏样式内联，其余异步加载
3. **预连接关键域**：`<link rel="preconnect">` 提前建连

```html
<link rel="preconnect" href="https://cdn.example.com">
<link rel="preload" as="image" href="/hero.webp">
```

### 路由级代码分割

按路由拆包，首屏只加载所需：

```jsx
const Page = React.lazy(() => import("./Page"));
```

## 运行时优化

### 减少重渲染

```jsx
// ❌ 每次渲染都创建新对象，子组件 memo 失效
<Child config={{ theme: "dark" }} />

// ✅ 提到组件外或 useMemo
const config = useMemo(() => ({ theme: "dark" }), []);
<Child config={config} />
```

### 长列表虚拟化

超过 ~100 项的列表用虚拟滚动，只渲染可见区：

```jsx
import { FixedSizeList } from "react-window";
<FixedSizeList itemSize={48} itemCount={10000}>
  {({ index, style }) => <div style={style}>...</div>}
</FixedSizeList>
```

### 防布局抖动

读写分离，避免强制同步布局：

```js
// ❌ 交替读写触发反复回流
for (const el of items) {
  el.style.height = `${el.offsetHeight + 10}px`;
}

// ✅ 先读后写
const heights = items.map((el) => el.offsetHeight + 10);
items.forEach((el, i) => (el.style.height = `${heights[i]}px`));
```

## 资源优化

| 资源 | 策略 |
|------|------|
| 图片 | 用 WebP/AVIF、响应式 `srcset`、懒加载 `loading="lazy"` |
| 字体 | `font-display: swap`、子集化、`preload` 关键字体 |
| 脚本 | 路由分割、tree-shaking、按需 polyfill |
| 第三方 | 延迟加载、用 Partytown 移出主线程 |

## 测量优先

任何优化前先建立基线：

- 实验室：Lighthouse、Chrome DevTools Performance
- 真实用户：Web Vitals（LCP/CLS/INP）
- 构建：`bundle analyzer` 看体积构成

性能优化的铁律：**先测，再改，复测确认收益**。不做无测量的"直觉优化"。
