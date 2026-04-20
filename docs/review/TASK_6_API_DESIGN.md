# Agent 6: API设计审查

## 审查范围

审查所有公开API的设计一致性。

## 审查文件

### Python API
- `src/nano_code/server/rpc.py` - JSON-RPC API
- `src/nano_code/tools/*.py` - 工具API
- `src/nano_code/core/config.py` - 配置API

### TypeScript API
- `packages/cli/src/client/rpc.ts` - Client API
- `packages/cli/src/hooks/useAgent.ts` - Hook API

## 审查要点

### 1. JSON-RPC API

检查方法:
- `agent.stream`
- `tools.list`
- `tool.execute`
- `config.get`
- `config.set`

检查项:
- [ ] 方法命名一致性
- [ ] 参数命名一致性
- [ ] 返回值结构一致性
- [ ] 错误码一致性

### 2. 工具API

检查所有工具:
- [ ] 参数命名规范
- [ ] 返回值类型一致
- [ ] 错误处理一致
- [ ] 文档格式一致

### 3. TypeScript 类型定义

检查文件:
- `packages/cli/src/client/types.ts`

检查项:
- [ ] 类型定义完整性
- [ ] 可选字段标记
- [ ] 类型导出规范
- [ ] 类型命名规范

### 4. Hook API

检查 `useAgent` Hook:
- [ ] 返回值结构
- [ ] 状态命名
- [ ] 方法命名
- [ ] 类型定义

### 5. 向后兼容性

检查项:
- [ ] 是否有废弃API
- [ ] 版本管理策略
- [ ] 升级路径

## 输出格式

```markdown
## API设计审查报告

### API一致性问题 (P0)
| 方法 | 问题 | 建议 |
|------|------|------|
| tool.execute | 返回值结构与 tools.list 不一致 | 统一返回结构 |

### API文档缺失
| API | 缺失文档 |
|-----|---------|
| agent.stream | 缺少 mode 参数说明 |

### API设计评分
| 维度 | 评分 | 说明 |
|------|------|------|
| 一致性 | 7/10 | |
| 文档完整 | 6/10 | |
| 易用性 | 8/10 | |

### API建议改进
[详细建议]
```
