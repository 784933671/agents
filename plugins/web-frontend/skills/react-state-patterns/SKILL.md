---
name: "react-state-patterns"
description: 掌握 React 状态管理的实用模式：本地状态、状态提升、派生状态、Context、请求竞态与过期状态处理。适用于设计组件状态、排查渲染异常或选择状态方案时。
---

# React 状态模式

面向实际工程的 React 状态管理指南，覆盖本地状态组织、派生数据处理、服务端状态同步与常见陷阱。

## 何时使用本技能

- 设计一个组件或一组组件的状态结构
- 排查渲染异常（频繁重渲染、stale state、闭包陷阱）
- 在 props 传递过深时决定是否引入 Context
- 处理异步请求的竞态、取消与乐观更新

## 核心原则

1. **状态最小化**：能推导的不存储，能局部的不上提
2. **单一数据源**：同一数据只存一处，其余派生
3. **显式优于隐式**：副作用顺序与依赖要可读

## 状态分层

```
组件本地状态      ← UI 折叠、输入焦点、临时 hover
  ↓ 必要时提升
共享 UI 状态      ← Context（同树内多组件共享）
  ↓ 跨树/持久化
服务端状态        ← 数据获取库或自管缓存（带失效策略）
```

## 常用模式

### 派生状态优于镜像状态

```jsx
// ❌ 镜像 props 到 state，易过期
const [count, setCount] = useState(props.count);
useEffect(() => setCount(props.count), [props.count]);

// ✅ 直接派生，单一来源
const count = props.count;
```

### 受控与非受控兼容

```jsx
function Input({ value, defaultValue, onChange }) {
  // 受控模式
  if (value !== undefined) {
    return <input value={value} onChange={onChange} />;
  }
  // 非受控模式
  const [inner, setInner] = useState(defaultValue);
  return <input value={inner} onChange={(e) => { setInner(e.target.value); onChange?.(e); }} />;
}
```

### 请求竞态防护

```jsx
useEffect(() => {
  let cancelled = false;
  fetchData(id).then((data) => {
    if (!cancelled) setResult(data);
  });
  return () => { cancelled = true; };
}, [id]);
```

## 常见陷阱

| 陷阱 | 现象 | 对策 |
|------|------|------|
| Stale closure | setState 后读到旧值 | 用函数式更新 `setX(prev => ...)` |
| 依赖漏写 | useEffect 不触发或读到旧依赖 | 完整声明依赖，必要时用 useCallback |
| 过度 Context | 任意 state 变化触发整树重渲染 | 拆分 Context 或下沉状态 |
| 镜像 props | state 与 props 不同步 | 改用派生值或 key 重置组件 |

## 选择状态方案的决策

- 仅本组件用 → `useState` / `useReducer`
- 父子共享 → 提升到最近共同祖先
- 跨层级共享但低频变化 → Context
- 高频变化且影响范围大 → 状态库或按域拆 Context
- 来自服务端、需缓存失效 → 数据获取库
