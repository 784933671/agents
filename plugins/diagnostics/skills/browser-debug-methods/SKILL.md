---
name: "browser-debug-methods"
description: 掌握基于浏览器 DevTools 的系统化调试方法：断点、网络分析、性能录制、存储与状态检查。适用于在浏览器中对前端问题进行证据驱动的复现与定位。
---

# 浏览器调试方法

基于 Chrome DevTools（及其它现代浏览器）的系统化前端调试方法集。核心是"用工具收集证据，而非用直觉猜测"。

## 何时使用本技能

- 在浏览器中复现并定位前端 bug
- 需要查看实际 DOM、网络请求、运行时状态
- 排查渲染、网络、存储相关的客户端问题
- 录制性能或交互用于分析

## 调试工具地图

| 面板 | 用途 | 典型场景 |
|------|------|---------|
| Elements | DOM 与样式 | 布局错位、样式不生效 |
| Console | 日志与求值 | 报错、临时验证、状态查看 |
| Sources | 断点与调用栈 | 逻辑错误、执行流程 |
| Network | 请求与响应 | 接口问题、加载失败 |
| Performance | 录制与分析 | 卡顿、长任务、渲染性能 |
| Application | 存储与状态 | Cookie/Storage/缓存问题 |

## 常用方法

### 断点调试（Sources）

不止用 `debugger`，善用条件断点：

```js
// 在某行右键 → Add conditional breakpoint
// 只在条件满足时断下，避免无限触发
user.id === 123 && order.status === 'pending'
```

- **DOM 断点**：Elements 中右键节点 → Break on → 子树修改/属性修改
- **事件监听断点**：Sources → Event Listener Breakpoints → 选 click/keydown 等
- **XHR 断点**：Sources → XHR/fetch Breakpoints → 按 URL 匹配

### 网络分析（Network）

排查接口问题：

- **筛选**：按 `fetch/xhr` 过滤接口请求
- **阶段**：点开 Timing 看 DNS/连接/等待/传输各阶段
- **重放**：右键 → Replay，或 Copy as fetch 在 Console 改参数重试
- **节流**：Throttling 模拟弱网，验证超时与重试逻辑

```js
// Console 里重放并修改请求
const r = await fetch('/api/order', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ /* 改这里 */ })
});
console.log(await r.json());
```

### DOM 与状态检查

```js
// Console 里直接访问选中元素（Elements 选中后）
// $0 是当前选中元素，$1 是上一个
$0.dataset            // 看 data-* 属性
getEventListeners($0) // 看绑了哪些事件（DevTools 专属）

// 查存储
localStorage          // 键值
document.cookie       // cookie
```

### 性能录制（Performance）

定位卡顿：

1. 点录制 → 操作 → 停止
2. 看主轨道的火焰图，找**长红块**（长任务）
3. 放大到该时段，看具体函数占用
4. 结合 Bottom-Up 按耗时排序找热点函数

指标关注：
- **长任务**（>50ms 的任务）会阻塞主线程
- **布局抖动**：频繁的紫色 Layout 块
- **强制同步布局**：JS 里读 offsetHeight 触发的回流

## 调试策略

### 二分定位法

不确定哪段代码出问题时，二分注释或加日志：

```js
// 在可疑区间两端加标记，缩小范围
console.log('A', state);        // 入口
// ... 可疑代码 ...
console.log('B', state);        // 出口
// A 对 B 错 → 问题在中间
```

### 假设-验证循环

```
观察现象 → 形成假设 → 设计实验 → 收集证据 → 确认/推翻
```

每个假设都要有"如果假设成立，应该看到 X"的预期，再验证。

## 常见问题速查

| 现象 | 第一步检查 |
|------|-----------|
| 样式不生效 | Elements 看计算样式，是否被覆盖（划线） |
| 点击无反应 | Console 看报错，Elements 看 event listeners |
| 数据不更新 | Network 看请求是否发出、返回是否正确 |
| 偶现卡顿 | Performance 录制，找长任务 |
| 登录态丢失 | Application 看 Cookie/Storage 是否被清 |

## 原则

- **证据优先**：每个判断有工具数据支撑
- **最小侵入**：调试代码用完即删，不留在生产
- **可复现**：记录能稳定复现的操作序列
- **分层排查**：先排除环境/缓存，再看代码逻辑
