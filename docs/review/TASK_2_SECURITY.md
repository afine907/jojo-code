# Agent 2: 安全漏洞审查

## 审查范围

审查所有涉及安全风险的代码，包括文件操作、命令执行、用户输入等。

## 重点审查

### 1. 文件操作安全

审查文件:
- `src/nano_code/tools/file_tools.py`
- `src/nano_code/context/project.py`

检查项:
- [ ] 路径遍历漏洞 (Path Traversal)
- [ ] 符号链接攻击
- [ ] 文件权限检查
- [ ] 敏感文件访问控制

### 2. 命令执行安全

审查文件:
- `src/nano_code/tools/shell_tools.py`

检查项:
- [ ] 命令注入风险
- [ ] 参数转义
- [ ] 危险命令限制
- [ ] 超时处理

### 3. 用户输入验证

审查文件:
- `src/nano_code/server/rpc.py`
- `packages/cli/src/client/rpc.ts`

检查项:
- [ ] 输入长度限制
- [ ] 特殊字符处理
- [ ] JSON 注入
- [ ] Unicode 攻击

### 4. 敏感信息处理

审查文件:
- `src/nano_code/core/config.py`
- `packages/cli/src/cli/config_wizard.py`

检查项:
- [ ] API Key 存储
- [ ] 日志脱敏
- [ ] 错误信息泄露
- [ ] 环境变量暴露

### 5. 网络安全

审查文件:
- `src/nano_code/tools/web_tools.py`

检查项:
- [ ] SSRF 风险
- [ ] URL 验证
- [ ] HTTPS 强制
- [ ] 证书验证

## 输出格式

```markdown
## 安全审查报告

### 严重漏洞 (P0)
- **漏洞类型**: [类型]
- **风险等级**: [高/中/低]
- **影响范围**: [受影响功能]
- **漏洞位置**: [文件:行号]
- **攻击场景**: [描述]
- **修复方案**: [详细方案]

### 潜在风险 (P1)
- [同上格式]

### 安全建议 (P2)
- [建议内容]

### 安全检查清单
- [x] 已检查项
- [ ] 未检查项
```
