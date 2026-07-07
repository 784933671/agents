---
name: "wcag-essentials"
description: 掌握 WCAG 2.x 的核心原则与 A/AA 级合规要点：可感知、可操作、可理解、健壮。适用于做无障碍审计、设计可访问组件或修复对比度/键盘/语义问题。
---

# WCAG 要点

WCAG（Web Content Accessibility Guidelines）是 Web 无障碍的国际标准。本技能聚焦 A/AA 级（多数法规的合规底线）的实际落地，而非逐条背诵。

## 何时使用本技能

- 设计或审计需要符合 WCAG A/AA 的界面
- 构建自定义组件（弹窗、标签页、菜单）的键盘交互
- 修复对比度、焦点、语义等无障碍问题
- 评估组件库的无障碍成熟度

## 四大原则（POUR）

```
可感知 Perceivable   信息必须能被用户感知（看不见也能用）
可操作 Operable      界面必须可操作（只用键盘也能完成）
可理解 Understandable 内容和操作必须可理解
健壮   Robust        必须能被各种用户代理（含辅助技术）正确解析
```

## 关键 A 级条款（必须满足）

### 1.1.1 非文本内容

所有图片要有 `alt`：

```html
<!-- 信息性图片 -->
<img src="chart.png" alt="2024 年 Q3 销售趋势图，环比增长 18%">

<!-- 装饰性图片 -->
<img src="spacer.gif" alt="">

<!-- 功能性图片（如按钮） -->
<img src="search.svg" alt="搜索">
```

### 2.1.1 键盘可访问

所有功能用键盘可完成。自定义交互必须实现键盘等价操作。

### 2.4.3 焦点顺序

Tab 顺序应符合阅读逻辑，不跳跃。

### 4.1.2 名称、角色、值

自定义控件要有正确的 `role`、`aria-label`、可设置状态：

```html
<!-- 自定义开关 -->
<button role="switch" aria-checked="false" aria-label="夜间模式">
  夜间模式
</button>
```

## 关键 AA 级条款（合规底线）

### 1.4.3 对比度（最低）

- 正文文字 ≥ **4.5:1**
- 大字（≥18pt 或 14pt 粗体）≥ **3:1**
- 组件边界与图形 ≥ **3:1**

### 1.4.11 非文本对比度

UI 组件边界、状态指示（focus、选中）也要达到 3:1。

### 2.4.7 焦点可见

焦点指示不能被 `outline: none` 抹掉：

```css
/* ❌ 抹掉焦点环 */
button { outline: none; }

/* ✅ 自定义但保持可见 */
button:focus-visible {
  outline: 2px solid currentColor;
  outline-offset: 2px;
}
```

### 1.4.1 不只靠颜色

状态不能只用颜色区分，要加图标或文字：

```html
<!-- ❌ 只有红色表示错误 -->
<span class="error">邮箱格式不正确</span>

<!-- ✅ 图标 + 颜色 + 文字 -->
<span class="error">
  <icon name="warning" aria-hidden="true" /> 邮箱格式不正确
</span>
```

## 自定义组件模式

### 弹窗（Dialog）

```html
<div role="dialog" aria-modal="true" aria-labelledby="title">
  <h2 id="title">确认删除</h2>
  <!-- 焦点要在对话框内、Esc 关闭、关闭后焦点回到触发元素 -->
</div>
```

要点：焦点陷阱、Esc 关闭、关闭后焦点恢复。

### 标签页

```html
<div role="tablist">
  <button role="tab" aria-selected="true" aria-controls="p1" id="t1">概览</button>
  <button role="tab" aria-selected="false" aria-controls="p2" id="t2">详情</button>
</div>
<div role="tabpanel" id="p1" aria-labelledby="t1">...</div>
```

要点：方向键切换、`aria-selected`、`aria-controls` 关联。

## 实操检查清单

- [ ] 所有图片有合适 alt
- [ ] 所有表单控件有 label
- [ ] 对比度达标（用工具测，不靠目测）
- [ ] 纯键盘能完成所有操作
- [ ] 焦点始终可见
- [ ] 标题层级不跳级
- [ ] 动态内容有 `aria-live` 通告
