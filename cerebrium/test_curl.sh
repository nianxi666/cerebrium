#!/bin/bash

# LatentSync Curl 测试脚本
# 
# 使用方法:
#   1. 设置环境变量: export CEREBRIUM_API_KEY="your_api_key"
#   2. 运行脚本: ./test_curl.sh

if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

echo "🚀 开始测试 LatentSync API..."
echo ""

# 检查 API Key
AUTH_TOKEN=${CEREBRIUM_SERVICE_ACCOUNT_TOKEN:-$CEREBRIUM_API_KEY}

if [ -z "$AUTH_TOKEN" ]; then
    echo "❌ 错误: 请先设置 CEREBRIUM_SERVICE_ACCOUNT_TOKEN 或 CEREBRIUM_API_KEY 环境变量"
    echo "   在 .env 文件中设置 CEREBRIUM_SERVICE_ACCOUNT_TOKEN=\"your_token\""
    exit 1
fi

echo "✅ 认证密钥已设置"
echo ""

# API 端点
API_ENDPOINT="https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict"

VIDEO_PATH="assets/demo1_video.mp4"
AUDIO_PATH="assets/demo1_audio.wav"

if [ ! -f "$VIDEO_PATH" ] || [ ! -f "$AUDIO_PATH" ]; then
    echo "❌ 错误: 未找到演示音视频文件"
    echo "   请确保 $VIDEO_PATH 和 $AUDIO_PATH 存在"
    exit 1
fi

echo "📡 发送请求到: $API_ENDPOINT"
echo "🎬 使用演示视频: $VIDEO_PATH"
echo "🎵 使用演示音频: $AUDIO_PATH"
echo ""

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

echo "🐍 使用 Python 命令: $PYTHON_CMD"
echo ""

# 生成临时 payload 文件
PAYLOAD_FILE=$(mktemp)
$PYTHON_CMD - "$PAYLOAD_FILE" <<'PY'
import base64
import json
import pathlib
import sys

payload_path = pathlib.Path(sys.argv[1])
video_path = pathlib.Path("assets/demo1_video.mp4")
audio_path = pathlib.Path("assets/demo1_audio.wav")

payload = {
    "video_base64": base64.b64encode(video_path.read_bytes()).decode("utf-8"),
    "audio_base64": base64.b64encode(audio_path.read_bytes()).decode("utf-8"),
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247,
}

payload_path.write_text(json.dumps(payload))
PY

# 检查 payload 文件是否成功生成
if [ ! -s "$PAYLOAD_FILE" ]; then
    echo "❌ 错误: Payload 文件生成失败"
    echo "   请确保 Python 和必要的库（json, base64）已安装"
    rm -f "$PAYLOAD_FILE"
    exit 1
fi

echo "✅ Payload 文件已生成"
echo ""

# 记录开始时间
START_TIME=$(date +%s)

# 发送请求
echo "⏳ 请稍候，正在处理视频同步（这可能需要几分钟）..."
echo ""

RESPONSE=$(curl -s -w "\n%{http_code}" -X POST "$API_ENDPOINT" \
  -H "Authorization: Bearer $AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d @"$PAYLOAD_FILE")

rm -f "$PAYLOAD_FILE"

# 提取 HTTP 状态码和响应体
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)
BODY=$(echo "$RESPONSE" | head -n-1)

# 记录结束时间
END_TIME=$(date +%s)
DURATION=$((END_TIME - START_TIME))

echo "⏱️  用时: ${DURATION}秒"
echo ""
echo "📊 HTTP 状态码: $HTTP_CODE"
echo ""

if [ "$HTTP_CODE" -eq 200 ]; then
    echo "✅ 请求成功！"
    echo ""
    
    # 保存响应到文件
    OUTPUT_FILE="curl_test_response_$(date +%Y%m%d_%H%M%S).json"
    echo "$BODY" > "$OUTPUT_FILE"
    echo "💾 响应已保存到: $OUTPUT_FILE"
    echo ""
    
    # 提取并保存视频
    VIDEO_BASE64=$(echo "$BODY" | $PYTHON_CMD -c "import json, sys; data=json.load(sys.stdin); print(data.get('result', {}).get('video_base64', ''))" 2>/dev/null)
    
    if [ -n "$VIDEO_BASE64" ]; then
        OUTPUT_VIDEO="output_$(date +%Y%m%d_%H%M%S).mp4"
        echo "$VIDEO_BASE64" | base64 -d > "$OUTPUT_VIDEO"
        echo "🎬 输出视频已保存到: $OUTPUT_VIDEO"
        echo ""
        
        # 显示响应的详细信息（不包含视频base64）
        echo "📝 响应详情:"
        echo "$BODY" | $PYTHON_CMD -c "import json, sys; data=json.load(sys.stdin); result=data.get('result',{}); details=result.get('details',{}); print(json.dumps({'run_id': data.get('run_id'), 'run_time_ms': data.get('run_time_ms'), 'details': details}, indent=2))" 2>/dev/null || echo "$BODY"
    else
        echo "📝 响应内容:"
        echo "$BODY" | $PYTHON_CMD -m json.tool 2>/dev/null || echo "$BODY"
    fi
else
    echo "❌ 请求失败"
    echo ""
    echo "📝 错误信息:"
    echo "$BODY"
fi
