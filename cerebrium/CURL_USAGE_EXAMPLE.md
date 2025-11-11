# LatentSync API - 完整 Curl 使用示例

## API 信息

- **端点**: `https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict`
- **方法**: POST
- **认证**: Bearer Token

## API Key

```bash
export CEREBRIUM_API_KEY="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJwcmluY2lwYWwiOiJzZXJ2aWNlYWNjb3VudC9zYS0zZDQzYzE5Zi1kNWE4LTRjMGUtOTdlYS04MThkMTFjMGM2M2QiLCJwcm9qZWN0SWQiOiJwLTlkZTU0MTA4In0.Hszxrlt_IgqWVj3Vpb0oh_XSiUt0f9JW6cSXovKEfnNqgfXDMgy9s0IVWn5IrReJa0pKI2eAK5GDr7ewEVT1S7MHXJnuc48tFLLQkYARA0vMDasGMvbDBwkOqxqxPKDi2gn_DI26Zs0FWcpZyjH550ESg8W346iI6cwL3z-cu90FGGcUydGPOdhgLm_7BT-vvPAZSc7yHqB3OgEk80dMhPNl7xRI9m6yD4ghTR3BtblkTNR7mgLikeqQfiUAwzDtLCt9H1SadcG-y1OvyVjR_hO6qHVAfMqKaSyW7DE9q5IjPBwae-6fjD8x-cIA1TEZFM6Swif3yMnm5OrD4WLQEQ"
```

## 完整使用流程

### 步骤 1: 生成请求 Payload

创建 `payload.json` 文件，包含 base64 编码的视频和音频：

```bash
python3 <<'EOF'
import base64
import json
import pathlib

# 读取本地文件（请替换为你的文件路径）
video_path = pathlib.Path("assets/demo1_video.mp4")
audio_path = pathlib.Path("assets/demo1_audio.wav")

# 生成 payload
payload = {
    "video_base64": base64.b64encode(video_path.read_bytes()).decode("utf-8"),
    "audio_base64": base64.b64encode(audio_path.read_bytes()).decode("utf-8"),
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
}

# 保存到文件
with open("payload.json", "w", encoding="utf-8") as f:
    json.dump(payload, f)

print("✅ payload.json 已生成")
EOF
```

### 步骤 2: 发送 Curl 请求

```bash
curl -X POST "https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict" \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d @payload.json \
  -o response.json

echo "✅ 响应已保存到 response.json"
```

### 步骤 3: 提取并保存视频

```bash
python3 <<'EOF'
import base64
import json
import pathlib

# 读取响应
data = json.loads(pathlib.Path("response.json").read_text())

# 提取 video_base64
video_b64 = data["result"]["video_base64"]

# 解码并保存
output_path = pathlib.Path("latentsync_output.mp4")
output_path.write_bytes(base64.b64decode(video_b64))

print(f"✅ 视频已保存: {output_path}")
print(f"   文件大小: {output_path.stat().st_size / 1024 / 1024:.2f} MB")
EOF
```

## 一键脚本

如果不想手动执行，可以直接运行项目提供的自动化脚本：

```bash
export CEREBRIUM_API_KEY="your_api_key_here"
./test_curl.sh
```

该脚本会自动：
1. 验证 API Key
2. 编码本地视频和音频文件
3. 发送请求到 API
4. 自动提取并保存输出视频
5. 显示详细的执行信息

## 响应格式

API 返回 JSON 格式，结构如下：

```json
{
  "run_id": "1274dbb5-5e94-993f-b796-f93b6ad60e30",
  "result": {
    "video_base64": "<base64编码的MP4视频数据>",
    "details": {
      "guidance_scale": 1.5,
      "inference_steps": 20,
      "seed": 1247
    }
  },
  "run_time_ms": 607913.81
}
```

**重要**: 视频内容在 `result.video_base64` 字段中，为 **Base64 编码的 MP4 数据**，需要解码后才能播放。

## 请求参数说明

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `video_url` | string | 否* | - | 视频 URL（二选一） |
| `video_base64` | string | 否* | - | Base64 编码的视频（二选一） |
| `audio_url` | string | 否* | - | 音频 URL（二选一） |
| `audio_base64` | string | 否* | - | Base64 编码的音频（二选一） |
| `guidance_scale` | float | 否 | 1.5 | 引导系数 (1.0-3.0) |
| `inference_steps` | int | 否 | 20 | 推理步数 (20-50) |
| `seed` | int | 否 | 1247 | 随机种子 |

*注: 必须提供视频和音频，可以通过 URL 或 base64 方式

## 使用 URL 方式（无需 base64 编码）

如果你的视频和音频文件已经托管在可访问的 URL 上：

```bash
curl -X POST "https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict" \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://your-domain.com/video.mp4",
    "audio_url": "https://your-domain.com/audio.wav",
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
  }' \
  -o response.json
```

## 性能指标

- **冷启动时间**: 约 25-46 秒（首次请求）
- **推理时间**: 约 30-60 秒（取决于视频长度）
- **总耗时**: 约 60-120 秒
- **输出视频大小**: 约 4-6 MB（取决于视频长度和质量）

## 测试结果示例

实际测试运行结果：

```
🚀 开始测试 LatentSync API...
✅ API Key 已设置
📡 发送请求到: https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict
🎬 使用演示视频: assets/demo1_video.mp4
🎵 使用演示音频: assets/demo1_audio.wav
⏳ 请稍候，正在处理视频同步（这可能需要几分钟）...
⏱️  用时: 617秒
📊 HTTP 状态码: 200
✅ 请求成功！
💾 响应已保存到: curl_test_response_20251024_054159.json
🎬 输出视频已保存到: output_20251024_054159.mp4
```

## 常见问题

### 1. 超时怎么办？

推理可能需要 10 分钟，请增加 curl 的超时时间：

```bash
curl --max-time 900 -X POST ...
```

### 2. 文件太大怎么办？

建议视频文件控制在 10MB 以内，时长不超过 10 秒，以获得最佳性能。

### 3. 如何验证视频是否成功？

```bash
# Linux/Mac
file latentsync_output.mp4

# 或检查文件大小
ls -lh latentsync_output.mp4
```

## 相关资源

- **Dashboard**: https://dashboard.cerebrium.ai/projects/p-9de54108/apps/p-9de54108-latentsync
- **详细文档**: 查看 `CURL_TEST_GUIDE.md`
- **自动化脚本**: 使用 `test_curl.sh`
