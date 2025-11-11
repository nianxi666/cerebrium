# LatentSync Curl 测试指南

本指南说明如何使用 curl 测试已部署的 LatentSync 推理服务。

## 修复说明

### 问题 1: VGG16 模型下载失败

**错误信息:**
```
404 Client Error. Repository Not Found for url: https://huggingface.co/pytorch/vision/resolve/main/vgg16-397923af.pth
```

**原因:** 
原始代码尝试从 HuggingFace `pytorch/vision` 仓库下载 VGG16 权重文件，但该仓库不存在。

**解决方案:**
修改 `main.py` 中的 `_ensure_torch_hub_weights()` 函数，从 PyTorch 官方 CDN 下载：

```python
def _ensure_torch_hub_weights() -> None:
    if TORCH_HUB_CACHE.exists():
        return
    TORCH_HUB_CACHE.parent.mkdir(parents=True, exist_ok=True)
    urls = (
        "https://download.pytorch.org/models/vgg16-397923af.pth",
        "https://huggingface.co/pytorch/vision/resolve/main/vgg16-397923af.pth",
    )
    last_error: Optional[Exception] = None
    for url in urls:
        try:
            download_url_to_file(url, str(TORCH_HUB_CACHE), progress=False)
            return
        except Exception as exc:
            last_error = exc
            if TORCH_HUB_CACHE.exists():
                TORCH_HUB_CACHE.unlink()
    raise RuntimeError("Unable to download VGG16 weights for LatentSync.") from last_error
```

### 问题 2: 示例 URL 不可用

**错误信息:**
```
404 Client Error: Not Found for url: https://github.com/anotherjesse/LatentSync/raw/main/assets/yuxin.mp4
```

**原因:** 
文档中的示例 URL 指向不存在的 GitHub 仓库。

**解决方案:**
更新测试脚本使用本地文件，并通过 base64 编码上传：

```bash
# 使用本地文件
VIDEO_PATH="assets/demo1_video.mp4"
AUDIO_PATH="assets/demo1_audio.wav"

# 生成带 base64 编码的 payload
python3 <<EOF
import base64
import json
import pathlib

payload = {
    "video_base64": base64.b64encode(pathlib.Path("$VIDEO_PATH").read_bytes()).decode("utf-8"),
    "audio_base64": base64.b64encode(pathlib.Path("$AUDIO_PATH").read_bytes()).decode("utf-8"),
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247,
}

print(json.dumps(payload))
EOF
```

## 使用方法

### 1. 设置 API Key

```bash
export CEREBRIUM_API_KEY="your_service_account_token"
```

### 2. 运行测试脚本

```bash
./test_curl.sh
```

该脚本会：
- 验证 API Key 是否设置
- 检查本地演示文件是否存在
- 将视频和音频编码为 base64
- 发送请求到 Cerebrium API
- 保存响应和输出视频

### 3. 手动 Curl 请求（使用 URL）

如果您有可访问的 URL：

```bash
curl -X POST https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://your-domain.com/video.mp4",
    "audio_url": "https://your-domain.com/audio.wav",
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
  }'
```

### 4. 手动 Curl 请求（使用 base64）

如果使用本地文件：

```bash
# 生成 payload
python3 > payload.json <<'EOF'
import base64
import json
import pathlib

video_base64 = base64.b64encode(pathlib.Path("assets/demo1_video.mp4").read_bytes()).decode("utf-8")
audio_base64 = base64.b64encode(pathlib.Path("assets/demo1_audio.wav").read_bytes()).decode("utf-8")

payload = {
    "video_base64": video_base64,
    "audio_base64": audio_base64,
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
}

print(json.dumps(payload))
EOF

# 发送请求
curl -X POST https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d @payload.json
```

## API 参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `video_url` | string | 否* | - | 视频 URL |
| `video_base64` | string | 否* | - | Base64 编码的视频 |
| `audio_url` | string | 否* | - | 音频 URL |
| `audio_base64` | string | 否* | - | Base64 编码的音频 |
| `guidance_scale` | float | 否 | 1.5 | 引导系数 (1.0-3.0) |
| `inference_steps` | int | 否 | 20 | 推理步数 (20-50) |
| `seed` | int | 否 | 1247 | 随机种子 |

*注：必须提供 `video_url` 或 `video_base64` 之一，以及 `audio_url` 或 `audio_base64` 之一

## 输出格式

成功响应示例：

```json
{
  "run_id": "1cd00866-a12a-9b51-a76f-d00fb0f084be",
  "result": {
    "video_base64": "<base64编码的视频>",
    "details": {
      "guidance_scale": 1.5,
      "inference_steps": 20,
      "seed": 1247
    }
  },
  "run_time_ms": 28876.46
}
```

## 提取输出视频

从响应中提取视频：

```bash
# 使用 jq
cat response.json | jq -r '.result.video_base64' | base64 -d > output.mp4

# 使用 Python
python3 <<'EOF'
import json
import base64

with open('response.json') as f:
    data = json.load(f)

video_base64 = data['result']['video_base64']
with open('output.mp4', 'wb') as f:
    f.write(base64.b64decode(video_base64))
EOF
```

## 性能说明

- **冷启动时间**: 约 46 秒（首次请求）
- **推理时间**: 约 30-60 秒（取决于视频长度和参数）
- **GPU**: AMPERE_A10 (24GB)
- **显存需求**: 约 18GB

## 故障排查

### 1. 401 Unauthorized

检查 API Key 是否正确设置：

```bash
echo $CEREBRIUM_API_KEY
```

### 2. 404 Not Found

确保 URL 可以访问：

```bash
curl -I https://your-domain.com/video.mp4
```

### 3. 500 Internal Server Error

查看错误详情，可能是：
- 文件格式不支持
- 视频分辨率过大
- 显存不足

## 部署信息

- **项目 ID**: p-9de54108
- **应用名称**: latentsync
- **API 端点**: https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict
- **控制台**: https://dashboard.cerebrium.ai/projects/p-9de54108/apps/p-9de54108-latentsync

## 相关文件

- `test_curl.sh` - 自动化测试脚本
- `main.py` - 主要推理代码（已修复 VGG16 下载）
- `assets/` - 本地演示文件
- `DEPLOYMENT_INFO.md` - 详细部署信息
