---
name: javascript-pro
description: 编写、调试和重构现代 JavaScript 代码，覆盖 ES2023+、async/await、ESM 模块系统和 Node.js API。适用于构建原生 JavaScript 应用、实现 Promise 异步流程、优化浏览器或 Node.js 性能、使用 Web Workers 或 Fetch API，以及审查 .js/.mjs/.cjs 文件的正确性和最佳实践。
license: MIT
metadata:
  author: https://github.com/Jeffallan
  version: "1.1.0"
  domain: language
  triggers: JavaScript, ES2023, async await, Node.js, vanilla JavaScript, Web Workers, Fetch API, browser API, module system
  role: specialist
  scope: implementation
  output-format: code
  related-skills: fullstack-guardian
---

# JavaScript Pro

## 适用场景

- 构建原生 JavaScript 应用
- 实现 async/await 模式和 Promise 处理
- 使用现代模块系统（ESM/CJS）
- 优化浏览器性能和内存占用
- 开发 Node.js 后端服务
- 实现 Web Workers、Service Workers 或浏览器 API

## 核心流程

1. **分析需求**：检查 `package.json`、模块系统、Node 版本、浏览器目标；确认 `.js`/`.mjs`/`.cjs` 约定
2. **设计架构**：规划模块、异步流程和错误处理策略
3. **实现代码**：使用 ES2023+ 编写代码，遵循正确模式和性能优化原则
4. **验证质量**：优先运行项目已有 lint/format 命令；仅在项目惯例允许时使用 `eslint --fix`。如果校验失败，修复所有问题后重新运行。必要时使用 DevTools 或 `--inspect` 检查内存泄漏，并按项目要求验证 bundle 体积
5. **测试覆盖**：优先使用项目已有测试框架和覆盖率阈值（Jest、Vitest、Node test runner 等）；如项目没有阈值，补充覆盖核心异步、错误和边界路径的测试。确认没有未处理的 Promise rejection

## 参考指南

根据上下文加载对应的详细指南：

| 主题 | 参考文件 | 加载时机 |
|------|----------|----------|
| 现代语法 | `references/modern-syntax.md` | ES2023+ 特性、可选链、私有字段 |
| 异步模式 | `references/async-patterns.md` | Promises、async/await、错误处理、事件循环 |
| 模块系统 | `references/modules.md` | ESM vs CJS、动态导入、package.json exports |
| 浏览器 API | `references/browser-apis.md` | Fetch、Web Workers、Storage、IntersectionObserver |
| Node 基础 | `references/node-essentials.md` | fs/promises、streams、EventEmitter、worker threads |

## 约束

### 必须做到

- 优先使用 ES2023+ 特性
- 使用 `X | null` 或 `X | undefined` 模式表达可空值
- 使用可选链（`?.`）和空值合并（`??`）
- 所有异步操作优先使用 async/await
- 新项目使用 ESM（`import`/`export`）
- 使用 try/catch 做好错误处理
- 为复杂函数添加 JSDoc 注释
- 遵循函数式编程原则

### 禁止事项

- 不使用 `var`（始终使用 `const` 或 `let`）
- 不使用 callback 风格模式（优先使用 Promises）
- 不在同一模块中混用 CommonJS 和 ESM
- 不忽略内存泄漏或性能问题
- 不跳过异步函数的错误处理
- 不在 Node.js 中使用同步 I/O
- 不修改函数参数
- 不在浏览器中创建阻塞操作

## 关键模式与示例

### Async/Await 错误处理

```js
// 正确：始终显式处理异步错误
async function fetchUser(id) {
  try {
    const response = await fetch(`/api/users/${id}`);
    if (!response.ok) throw new Error(`HTTP ${response.status}`);
    return await response.json();
  } catch (err) {
    console.error("fetchUser failed:", err);
    return null;
  }
}

// 错误：未处理 rejection，也缺少 null 兜底
async function fetchUser(id) {
  const response = await fetch(`/api/users/${id}`);
  return response.json();
}
```

### 可选链与空值合并

```js
// 正确
const city = user?.address?.city ?? "Unknown";

// 错误：address 为 undefined 时会抛错
const city = user.address.city || "Unknown";
```

### ESM 模块结构

```js
// 正确：命名导出，库代码避免只提供 default export
// utils/math.mjs
export const add = (a, b) => a + b;
export const multiply = (a, b) => a * b;

// consumer.mjs
import { add } from "./utils/math.mjs";

// 错误：混用 require() 与 ESM
const { add } = require("./utils/math.mjs");
```

### 避免 var / 优先 const

```js
// 正确
const MAX_RETRIES = 3;
let attempts = 0;

// 错误
var MAX_RETRIES = 3;
var attempts = 0;
```

## 输出模板

实现 JavaScript 功能时，提供：

1. 导出清晰的模块文件
2. 覆盖充分的测试文件
3. 面向公共 API 的 JSDoc 文档
4. 简要说明使用的模式

[文档](https://jeffallan.github.io/claude-skills/skills/language/javascript-pro/)
