# test_curl.sh 修复说明

## 问题描述

原始的 `test_curl.sh` 脚本存在以下问题：

1. **Python3 命令未找到**: 脚本硬编码使用 `python3` 命令，但在某些环境中可能没有安装或命令名称为 `python`
2. **请求体缺失**: 当 Python 命令执行失败时，payload 文件不会被创建，导致 curl 请求发送空的请求体，服务器返回 "Missing request body" 错误

## 修复内容

### 1. 添加 Python 命令自动检测 (第 39-49 行)

```bash
# 检测可用的 Python 命令
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ 错误: 未找到 Python 命令"
    echo "   请安装 Python 3 (python3 或 python)"
    exit 1
fi
```

脚本现在会自动检测系统中可用的 Python 命令：
- 首先尝试 `python3`
- 如果不存在，尝试 `python`
- 如果都不存在，显示清晰的错误信息并退出

### 2. 添加 Payload 文件验证 (第 77-86 行)

```bash
# 检查 payload 文件是否成功生成
if [ ! -s "$PAYLOAD_FILE" ]; then
    echo "❌ 错误: Payload 文件生成失败"
    echo "   请确保 Python 和必要的库（json, base64）已安装"
    rm -f "$PAYLOAD_FILE"
    exit 1
fi

echo "✅ Payload 文件已生成"
```

添加了文件生成验证：
- 检查 payload 文件是否存在且非空
- 如果生成失败，显示错误信息并退出
- 确保在发送 curl 请求前 payload 文件已成功创建

### 3. 更新所有 Python 命令引用

将脚本中所有硬编码的 `python3` 替换为检测到的 `$PYTHON_CMD` 变量：
- 第 56 行：生成 payload 文件
- 第 126 行：提取视频 base64
- 第 136 行：格式化响应详情
- 第 139 行：格式化 JSON 输出

## 测试结果

修复后的脚本经过以下测试：
- ✅ 语法检查通过 (`bash -n test_curl.sh`)
- ✅ Python 命令检测功能正常
- ✅ Payload 文件成功生成（约 2MB）
- ✅ JSON 格式验证通过

## 使用说明

修复后的脚本使用方式不变：

```bash
# 1. 设置 API Key
export CEREBRIUM_API_KEY="your_api_key"

# 2. 运行脚本
./test_curl.sh
```

现在脚本会：
1. 自动检测并显示使用的 Python 命令
2. 验证 payload 文件生成是否成功
3. 在发送请求前确保所有条件满足
4. 提供更清晰的错误提示信息
