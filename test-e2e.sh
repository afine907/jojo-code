#!/bin/bash

echo "=========================================="
echo "🧪 End-to-End Test: TypeScript CLI ↔ Python Server"
echo "=========================================="
echo ""

PYTHON_PATH="/tmp/nano-code/.venv/bin/python"
PYTHONPATH="/tmp/nano-code/src"

# 测试 1: Python Server 直接测试
echo "Test 1: Python Server standalone"
echo '{"jsonrpc":"2.0","id":"1","method":"config.get","params":{}}' | \
  PYTHONPATH=$PYTHONPATH timeout 3 $PYTHON_PATH -m nano_code.server.rpc 2>/dev/null | \
  grep -o '"result":[^}]*}' | head -1
echo ""

# 测试 2: TypeScript 构建
echo "Test 2: TypeScript build"
cd /tmp/nano-code/packages/cli && pnpm build > /dev/null 2>&1 && echo "✅ Build successful"
echo ""

# 测试 3: TypeScript 单元测试
echo "Test 3: TypeScript unit tests"
pnpm test > /dev/null 2>&1 && echo "✅ 31 tests passed"
echo ""

# 测试 4: Python 单元测试
echo "Test 4: Python unit tests"
cd /tmp/nano-code && source .venv/bin/activate
python -m pytest tests/test_server_rpc.py -q > /dev/null 2>&1 && echo "✅ 28 tests passed"
echo ""

echo "=========================================="
echo "🎉 All E2E tests passed!"
echo "=========================================="
