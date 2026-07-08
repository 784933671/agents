# 现代 JavaScript 语法（ES2023+）

## 可选链与空值合并

```javascript
// 可选链：安全访问属性
const userName = user?.profile?.name;
const firstItem = items?.[0];
const result = api?.fetchData?.();

// 空值合并：仅在 null/undefined 时使用默认值
const port = config.port ?? 3000;
const name = user.name ?? 'Anonymous';

// 组合两种模式
const displayName = user?.profile?.name ?? user?.email ?? 'Guest';

// delete 搭配可选链
delete user?.temporaryData?.cache;
```

## 类私有字段

```javascript
class BankAccount {
  // 私有字段
  #balance = 0;
  #accountNumber;

  // 私有方法
  #validateAmount(amount) {
    if (amount <= 0) throw new Error('Invalid amount');
  }

  constructor(accountNumber, initialBalance = 0) {
    this.#accountNumber = accountNumber;
    this.#balance = initialBalance;
  }

  deposit(amount) {
    this.#validateAmount(amount);
    this.#balance += amount;
    return this.#balance;
  }

  getBalance() {
    return this.#balance;
  }
}

// 静态私有字段
class Config {
  static #apiKey = process.env.API_KEY;

  static getApiKey() {
    return this.#apiKey;
  }
}
```

## 顶层 Await

```javascript
// 不需要 async IIFE 包装
const data = await fetch('/api/config').then(r => r.json());
const db = await connectDatabase(data.dbUrl);

// await 搭配动态导入
const module = await import(`./modules/${moduleName}.js`);

// 顶层错误处理
try {
  const config = await loadConfig();
  startServer(config);
} catch (error) {
  console.error('Failed to start:', error);
  process.exit(1);
}
```

## 现代数组方法

```javascript
// at()：负数索引
const last = items.at(-1);
const secondLast = items.at(-2);

// findLast() 与 findLastIndex()
const lastEven = numbers.findLast(n => n % 2 === 0);
const lastIndex = numbers.findLastIndex(n => n > 10);

// toSorted()、toReversed()、toSpliced()：非变异方法
const sorted = items.toSorted((a, b) => a - b);
const reversed = items.toReversed();
const spliced = items.toSpliced(1, 2, 'new');

// with()：替换指定索引的值
const updated = items.with(2, 'newValue');

// flatMap()：转换并扁平化
const nestedResults = users.flatMap(user => user.posts);
```

## 对象与字符串增强

```javascript
// Object.groupBy()：数组元素分组
const groupedByAge = Object.groupBy(users, user => user.age);
const groupedByStatus = Object.groupBy(orders, o => o.status);

// Object.hasOwn()：更安全的 hasOwnProperty 替代方案
if (Object.hasOwn(obj, 'key')) {
  // 比 obj.hasOwnProperty("key") 更安全
}

// String.prototype.at()
const firstChar = str.at(0);
const lastChar = str.at(-1);

// replaceAll()
const cleaned = text.replaceAll('old', 'new');
const sanitized = input.replaceAll(/[<>]/g, '');
```

## WeakRef 与 FinalizationRegistry

```javascript
// WeakRef：持有对象弱引用
class Cache {
  #cache = new Map();

  set(key, value) {
    this.#cache.set(key, new WeakRef(value));
  }

  get(key) {
    const ref = this.#cache.get(key);
    return ref?.deref(); // GC 后为 undefined
  }
}

// FinalizationRegistry：清理回调
const registry = new FinalizationRegistry((heldValue) => {
  console.log(`Cleanup: ${heldValue}`);
  // 释放资源
});

class Resource {
  constructor(id) {
    this.id = id;
    registry.register(this, id, this);
  }

  dispose() {
    registry.unregister(this);
  }
}
```

## 逻辑赋值运算符

```javascript
// ||=：值为 falsy 时赋值
config.timeout ||= 5000;
user.name ||= 'Anonymous';

// &&=：值为 truthy 时赋值
user.profile &&= sanitize(user.profile);

// ??=：值为 nullish 时赋值
options.port ??= 3000;
settings.theme ??= 'dark';
```

## 数字分隔符与 BigInt

```javascript
// 使用数字分隔符提升可读性
const billion = 1_000_000_000;
const bytes = 0xFF_EC_DE_5E;
const trillion = 1_000_000_000_000n;

// BigInt 用于大整数
const hugeNumber = 9007199254740991n;
const result = hugeNumber + 1n;
const mixed = BigInt(123) + 456n;

// BigInt 运算
const divided = 10n / 3n; // 3n（截断）
const power = 2n ** 64n;
```

## 模式匹配（Stage 3 提案）

```javascript
// 使用 switch 模拟增强模式（可用时）
function processValue(value) {
  switch (true) {
    case typeof value === 'string':
      return value.toUpperCase();
    case typeof value === 'number':
      return value * 2;
    case Array.isArray(value):
      return value.length;
    default:
      return null;
  }
}

// 对象解构模式
function handleResponse({ status, data, error }) {
  if (error) throw error;
  if (status === 200) return data;
  return null;
}
```

## 迭代器辅助方法（Stage 3）

```javascript
// 可用时：链式迭代器操作
const result = [1, 2, 3, 4, 5]
  .values()
  .map(x => x * 2)
  .filter(x => x > 5)
  .toArray();

// 自定义迭代器
const range = {
  *[Symbol.iterator]() {
    for (let i = 0; i < 10; i++) {
      yield i;
    }
  }
};

for (const num of range) {
  console.log(num);
}
```

## Temporal API（Stage 3）

```javascript
// 现代日期/时间处理（可用时）
import { Temporal } from '@js-temporal/polyfill';

const now = Temporal.Now.instant();
const date = Temporal.PlainDate.from('2024-01-15');
const time = Temporal.PlainTime.from('14:30:00');

// 时长计算
const duration = Temporal.Duration.from({ hours: 2, minutes: 30 });
const later = now.add(duration);

// 时区处理
const zonedTime = now.toZonedDateTimeISO('America/New_York');
```

## 快速参考

| 特性 | ES 版本 | 语法 |
|---------|-----------|--------|
| 可选链 | ES2020 | `obj?.prop` |
| 空值合并 | ES2020 | `value ?? default` |
| 私有字段 | ES2022 | `#fieldName` |
| 顶层 await | ES2022 | `await import()` |
| 逻辑赋值 | ES2021 | `x ??= y` |
| Array.at() | ES2022 | `arr.at(-1)` |
| Object.hasOwn() | ES2022 | `Object.hasOwn(obj, 'key')` |
| Array.findLast() | ES2023 | `arr.findLast(fn)` |
| toSorted() | ES2023 | `arr.toSorted()` |
