---
name: frontend-debugging
description: 前端问题定位与修复流程。用于 Vue、Element Plus、Vant、浏览器、H5 真机、接口、跨域、Source Map、白屏、样式错位、移动端兼容、线上异常和性能卡顿的调试分析。
---

# Frontend Debugging

## 工作原则

- 先复现，再定位；先证据，再修改。
- 每次只改变一个变量，避免同时改接口、样式和状态逻辑。
- 优先使用浏览器 DevTools、Vue Devtools、Network、Console、Performance 的直接证据。
- 修复后必须回到原复现路径验证。

## 定位流程

1. 明确现象：页面、设备、账号、路由、操作步骤、期望结果、实际结果。
2. 缩小范围：判断是接口、状态、组件库、样式、路由、构建还是环境问题。
3. 找证据：查看 Console、Network、Vue 组件状态、DOM、Computed 样式。
4. 做最小修复：只改根因相关代码。
5. 回归验证：覆盖成功、失败、空数据、刷新、返回、重复操作。

## 接口问题

- Network 里确认 URL、method、params、payload、headers、status、response。
- 区分浏览器没发出、请求被拦截、服务端报错、前端解析错误。
- CORS 问题看预检请求、响应头和代理配置，不在业务代码里硬绕。
- 401/403 优先查 token、权限、路由守卫和请求拦截器。
- 接口失败时确认页面是否恢复 loading、保留输入并显示兜底错误。

## Vue 状态问题

- 用 Vue Devtools 查看 props、emits、refs、computed、Pinia store。
- 检查是否直接修改 props、替换 reactive 对象、watch 依赖写错。
- 检查列表 key 是否稳定，避免复用错误 DOM。
- 检查异步请求返回顺序，避免旧请求覆盖新状态。
- 路由参数变化时确认是否有 watch 或 beforeRouteUpdate 处理。

## Element Plus 问题

- 表单问题先查 `model`、`rules`、`prop` 是否一致。
- 弹窗残留通常来自打开时未重置表单或未清校验。
- 表格错位先查列宽、固定列、容器高度和数据 key。
- 下拉、日期、级联组件异常时确认绑定值类型和 options 结构。

## Vant H5 问题

- 真机问题优先用远程调试或抓包复现，不只看桌面模拟器。
- 输入框问题检查键盘类型、maxlength、formatter、readonly 和弹层遮挡。
- 安全区、底部按钮遮挡检查 `safe-area-inset-bottom` 和固定定位容器。
- 滚动穿透、弹层层级问题检查 popup、body 滚动锁定和 z-index。
- iOS 兼容问题优先验证真实 Safari/WebView。

## 样式和布局问题

- 先在 Elements 面板确认 DOM 结构和最终生效样式。
- 检查作用域样式、深度选择器、组件库覆盖顺序。
- 响应式问题检查断点、容器宽度、flex/grid 收缩和文本溢出。
- 不用全局强选择器粗暴覆盖组件库，优先收敛到当前组件或业务类名。

## 白屏和构建问题

- Console 查首个错误，不被后续连锁错误干扰。
- Network 查 JS/CSS 是否 404、MIME 错误、chunk 加载失败。
- 路由 base、静态资源 publicPath、环境变量和部署路径一起核对。
- Source Map 可用时定位源码；不可用时根据 chunk 和路由范围缩小问题。

## 完成检查

- 复现路径已记录。
- 根因有证据支撑。
- 修复范围最小。
- 原问题路径和相邻状态已验证。
