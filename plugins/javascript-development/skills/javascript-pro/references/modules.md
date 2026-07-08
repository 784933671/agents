# 模块系统

## ES Modules（ESM）

```javascript
// 命名导出
export const PI = 3.14159;
export function add(a, b) {
  return a + b;
}

export class Calculator {
  multiply(a, b) {
    return a * b;
  }
}

// 默认导出
export default class Database {
  async connect() {
    // 实现逻辑
  }
}

// 重新导出
export { add, multiply } from './math.js';
export * from './utils.js';
export * as helpers from './helpers.js';
```

## 导入模式

```javascript
// 命名导入
import { add, multiply } from './math.js';
import { add as addition } from './math.js';

// 默认导入
import Database from './database.js';

// 命名空间导入
import * as math from './math.js';
math.add(1, 2);

// 混合导入
import Database, { connect, disconnect } from './database.js';

// 仅导入副作用
import './polyfills.js';

// 仅类型导入（用于文档）
/** @typedef {import('./types.js').User} User */
```

## 动态导入

```javascript
// 基础动态导入
const module = await import('./module.js');
module.default();

// 条件加载
const loadFeature = async (feature) => {
  if (feature === 'advanced') {
    const { AdvancedFeature } = await import('./advanced.js');
    return new AdvancedFeature();
  }
  const { BasicFeature } = await import('./basic.js');
  return new BasicFeature();
};

// 按路由拆分代码
const router = {
  '/home': () => import('./pages/home.js'),
  '/about': () => import('./pages/about.js'),
  '/profile': () => import('./pages/profile.js')
};

const loadPage = async (route) => {
  const module = await router[route]();
  return module.default;
};

// 带缓存的懒加载
const moduleCache = new Map();

const importWithCache = async (path) => {
  if (moduleCache.has(path)) {
    return moduleCache.get(path);
  }
  const module = await import(path);
  moduleCache.set(path, module);
  return module;
};
```

## Package.json 配置

```json
{
  "name": "my-package",
  "version": "1.0.0",
  "type": "module",
  "main": "./dist/index.cjs",
  "module": "./dist/index.mjs",
  "exports": {
    ".": {
      "import": "./dist/index.mjs",
      "require": "./dist/index.cjs",
      "types": "./dist/index.d.ts"
    },
    "./utils": {
      "import": "./dist/utils.mjs",
      "require": "./dist/utils.cjs"
    },
    "./package.json": "./package.json"
  },
  "imports": {
    "#utils": "./src/utils/index.js",
    "#constants": "./src/constants.js"
  }
}
```

## 条件导出

```javascript
// 使用条件导出的 package.json
{
  "exports": {
    ".": {
      "node": "./dist/node.js",
      "browser": "./dist/browser.js",
      "default": "./dist/index.js"
    },
    "./feature": {
      "development": "./src/feature.dev.js",
      "production": "./dist/feature.prod.js"
    }
  }
}

// 在代码中使用
import api from 'my-package'; // 根据环境解析
import feature from 'my-package/feature'; // 根据 NODE_ENV 条件解析
```

## Import Maps（浏览器）

```html
<!-- 在 HTML 中 -->
<script type="importmap">
{
  "imports": {
    "lodash": "/node_modules/lodash-es/lodash.js",
    "react": "https://esm.sh/react@18",
    "utils/": "/src/utils/"
  }
}
</script>

<script type="module">
import _ from 'lodash';
import React from 'react';
import { helper } from 'utils/helper.js';
</script>
```

## CommonJS 兼容性

```javascript
// ESM 使用 CommonJS
import cjsModule from './commonjs-module.cjs';
import { named } from './commonjs-module.cjs'; // 可能不可用

// 在 ESM 中使用 createRequire 加载 CommonJS
import { createRequire } from 'module';
const require = createRequire(import.meta.url);
const cjsModule = require('./commonjs-module.cjs');

// 在 ESM 中访问 CommonJS 元数据
import { fileURLToPath } from 'url';
import { dirname } from 'path';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);
```

## 模块解析

```javascript
// ESM 要求显式文件扩展名
import utils from './utils.js'; // 正确
import utils from './utils';    // 在 ESM 中错误

// 目录导入需要 index.js
import api from './api/index.js';

// 使用 import.meta
console.log(import.meta.url); // file:///path/to/module.js
console.log(import.meta.resolve('./other.js')); // 解析相对路径

// 检测模块是否为入口
if (import.meta.url === `file://${process.argv[1]}`) {
  // 当前模块被直接运行
  main();
}
```

## 循环依赖

```javascript
// moduleA.js
import { b } from './moduleB.js';
export const a = 'A';
export function useB() {
  return b;
}

// moduleB.js
import { a } from './moduleA.js';
export const b = 'B';
export function useA() {
  return a; // 可用，因为 a 被提升
}

// 最佳实践：避免循环依赖，改用依赖注入
// factory.js
export function createA(dependencies) {
  return {
    name: 'A',
    useB: () => dependencies.b
  };
}

export function createB(dependencies) {
  return {
    name: 'B',
    useA: () => dependencies.a
  };
}

// index.js
const a = createA({});
const b = createB({});
a.dependencies = { b };
b.dependencies = { a };
```

## Tree Shaking 优化

```javascript
// 编写无副作用代码以支持 tree shaking
// utils.js：良好示例，纯函数
export const add = (a, b) => a + b;
export const multiply = (a, b) => a * b;
export const divide = (a, b) => a / b;

// 只有被使用的函数会被打包
import { add } from './utils.js'; // 仅打包 add

// 错误示例：副作用会阻止 tree shaking
console.log('Module loaded'); // 副作用
export const add = (a, b) => a + b;

// 在 package.json 中标记为无副作用
{
  "sideEffects": false,
  // 或指定有副作用的文件
  "sideEffects": ["*.css", "polyfills.js"]
}
```

## 模块模式

```javascript
// 单例模式
// database.js
class Database {
  #connection = null;

  async connect() {
    if (!this.#connection) {
      this.#connection = await createConnection();
    }
    return this.#connection;
  }
}

export default new Database();

// 工厂模式
// loggerFactory.js
export function createLogger(level = 'info') {
  return {
    info: (msg) => level !== 'silent' && console.log(msg),
    error: (msg) => console.error(msg)
  };
}

// 外观模式
// api.js
import { get, post, put, del } from './httpClient.js';
import { auth } from './auth.js';
import { cache } from './cache.js';

export const api = {
  async getUser(id) {
    const cached = cache.get(`user:${id}`);
    if (cached) return cached;

    const token = await auth.getToken();
    const user = await get(`/users/${id}`, { token });
    cache.set(`user:${id}`, user);
    return user;
  }
};
```

## Node.js ESM 特性

```javascript
// package.json
{
  "type": "module" // 所有 .js 文件都是 ESM
}

// 当 type: "module" 时，CommonJS 文件使用 .cjs
// 当 type: "commonjs"（默认）时，ESM 文件使用 .mjs

// 在 ESM 中加载 JSON
import data from './data.json' assert { type: 'json' };

// 或使用 fs
import { readFile } from 'fs/promises';
const data = JSON.parse(
  await readFile('./data.json', 'utf-8')
);

// Node.js ESM 中的顶层 await
const config = await fetch('/api/config').then(r => r.json());
export default config;
```

## 快速参考

| 特性 | ESM | CommonJS |
|---------|-----|----------|
| 语法 | `import`/`export` | `require()`/`module.exports` |
| 加载 | 异步 | 同步 |
| Tree shaking | 支持 | 不支持 |
| 顶层 await | 支持 | 不支持 |
| 动态导入 | `await import()` | `require()` |
| 文件扩展名 | 必需 | 可选 |
| `__dirname` | 使用 `import.meta.url` | 内置 |
| 浏览器支持 | 原生支持 | 需要打包器 |
| 默认模式 | `"type": "module"` | 无 type 字段 |
