# 轻量维护优化设计

**日期**: 2026-07-08

## 背景

当前仓库是一个自托管 ZCode / Claude Code 插件市场，实际只维护两个本地插件包:

- `ui-ux-craft`: UI/UX 设计、走查、修复与无障碍审计
- `vue-development`: Vue 3 / Composition API / Pinia / Vue Router / Vite 开发辅助

仓库已有 `scripts/sync_agents_table.py` 用于校验 README 中的 agents 表格，但缺少一个统一的发布前校验入口。历史设计文档仍描述过往的四包方案和上游包共存方案，容易与当前实现状态混淆。

## 目标

做一轮低风险维护优化，提升文档一致性与发布可靠性。

## 非目标

- 不新增插件包
- 不修改 agent、command、skill 的语义内容
- 不调整 marketplace 对外结构
- 不引入第三方依赖
- 不做大规模目录重构

## 方案

采用轻量维护优化方案，范围限定在文档和校验工具。

### 1. 文档一致性

更新 `README.md`:

- 保留现有安装说明和插件包列表
- 增加本地校验说明
- 明确当前 marketplace 只包含 `ui-ux-craft` 与 `vue-development`

更新 `docs/superpowers/specs/2026-07-07-local-agents-packaging-design.md`:

- 标注该文档为历史设计
- 追加当前实现状态
- 明确当前仓库已精简为两个插件包

### 2. 统一校验入口

新增 `scripts/verify.py`:

- 校验 `.claude-plugin/marketplace.json` 是合法 JSON
- 校验 `plugins/*/.claude-plugin/plugin.json` 是合法 JSON
- 调用现有 `scripts/sync_agents_table.py check`
- 任一校验失败时返回非 0
- 成功时输出简洁的通过信息

该脚本只使用 Python 标准库。

### 3. CI 校验

新增 `.github/workflows/verify.yml`:

- 在 push 和 pull request 时运行
- 使用系统 Python 运行 `python3 scripts/verify.py`
- 不安装依赖

## 验证

本地执行:

```bash
python3 scripts/verify.py
```

预期输出:

```text
ok: json manifests are valid
ok: README agents table is in sync.
ok: repository verification passed
```

## 风险与边界

- CI 只验证仓库结构和文档表格同步，不验证 Claude/ZCode 客户端实际安装行为。
- 由于不修改插件语义内容，本次优化不会影响已安装插件的运行逻辑。
- 如果后续新增远程 `git-subdir` source，`scripts/sync_agents_table.py check` 可能需要网络或缓存；当前本地目录 source 不受影响。
