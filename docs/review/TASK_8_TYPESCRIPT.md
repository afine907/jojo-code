# Agent 8: TypeScript代码审查

## 审查范围

审查所有 TypeScript 代码的类型安全性和最佳实践。

## 审查文件

```
packages/cli/src/
├── index.tsx           # 主入口
├── client/
│   ├── rpc.ts          # RPC 客户端
│   └── types.ts        # 类型定义
├── components/
│   ├── ChatView.tsx
│   ├── InputBox.tsx
│   ├── Markdown.tsx
│   └── ...
└── hooks/
    └── useAgent.ts     # Agent Hook
```

## 审查要点

### 1. 类型安全

检查项:
- [ ] 是否使用 any 类型
- [ ] 是否有类型断言
- [ ] 类型定义是否完整
- [ ] 是否使用严格模式

```bash
# 检查 any 使用
grep -r ": any" src/
```

### 2. 空值处理

检查项:
- [ ] 是否使用可选链
- [ ] 是否使用空值合并
- [ ] 是否有 null 检查
- [ ] 是否有 undefined 检查

### 3. 异步处理

检查项:
- [ ] 是否正确处理 Promise
- [ ] 是否有 try-catch
- [ ] 是否有错误边界
- [ ] 是否有加载状态

### 4. React 最佳实践

检查项:
- [ ] 是否使用函数组件
- [ ] 是否正确使用 hooks
- [ ] 是否有依赖数组问题
- [ ] 是否有内存泄漏风险

### 5. 性能优化

检查项:
- [ ] 是否使用 useMemo
- [ ] 是否使用 useCallback
- [ ] 是否有不必要的重渲染
- [ ] 是否有懒加载

## 输出格式

```markdown
## TypeScript代码审查报告

### 类型安全问题 (P0)
| 文件 | 行号 | 问题 | 建议 |
|------|------|------|------|
| rpc.ts | 10 | 使用 any 类型 | 定义具体类型 |

### React 问题 (P1)
| 组件 | 问题 | 建议 |
|------|------|------|
| useAgent | 缺少 cleanup | 添加 useEffect cleanup |

### 最佳实践违反
| 位置 | 违反项 | 建议 |
|------|--------|------|
| xxx.tsx | 内联函数 | 提取为 useCallback |

### 代码质量评分
| 维度 | 评分 | 说明 |
|------|------|------|
| 类型安全 | 7/10 | |
| React最佳实践 | 8/10 | |
| 性能优化 | 6/10 | |
```
