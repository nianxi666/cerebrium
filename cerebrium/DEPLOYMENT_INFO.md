# LatentSync 部署成功！

## 🎉 部署信息

**状态**: ✅ 部署成功

**应用名称**: latentsync

**项目ID**: p-9de54108

## 📊 配置详情

- **GPU**: AMPERE_A10 (24GB)
- **CPU**: 8核
- **内存**: 32GB
- **Python版本**: 3.11
- **镜像大小**: 3.40 GB
- **构建时间**: 3分20秒
- **初始化时间**: 46秒

## 🔗 访问地址

### 应用面板
https://dashboard.cerebrium.ai/projects/p-9de54108/apps/p-9de54108-latentsync

### API端点
```
POST https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict
```

## 💡 使用方法

### 发送请求示例

```bash
curl -X POST https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict \
  -H "Authorization: Bearer $CEREBRIUM_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "video_url": "https://github.com/anotherjesse/LatentSync/raw/main/assets/yuxin.mp4",
    "audio_url": "https://github.com/anotherjesse/LatentSync/raw/main/assets/audio_yuxin.wav",
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
  }'
```

### Python调用示例

```python
import requests
import os

CEREBRIUM_API_KEY = os.environ.get("CEREBRIUM_API_KEY")

response = requests.post(
    "https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict",
    headers={
        "Authorization": f"Bearer {CEREBRIUM_API_KEY}",
        "Content-Type": "application/json"
    },
    json={
        "video_url": "https://github.com/anotherjesse/LatentSync/raw/main/assets/yuxin.mp4",
        "audio_url": "https://github.com/anotherjesse/LatentSync/raw/main/assets/audio_yuxin.wav",
        "guidance_scale": 1.5,
        "inference_steps": 20,
        "seed": 1247
    }
)

result = response.json()
print(result)
```

## 📝 输入参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `video_url` | string | 否* | - | 视频URL |
| `video_base64` | string | 否* | - | Base64编码的视频 |
| `audio_url` | string | 否* | - | 音频URL |
| `audio_base64` | string | 否* | - | Base64编码的音频 |
| `guidance_scale` | float | 否 | 1.5 | 引导系数 (1.0-3.0) |
| `inference_steps` | int | 否 | 20 | 推理步数 (20-50) |
| `seed` | int | 否 | 1247 | 随机种子 |

*注：必须提供 `video_url` 或 `video_base64` 之一，以及 `audio_url` 或 `audio_base64` 之一

## 📤 输出格式

```json
{
  "video_base64": "<base64编码的视频>",
  "details": {
    "guidance_scale": 1.5,
    "inference_steps": 20,
    "seed": 1247
  }
}
```

## ⚠️ 重要说明

1. **硬件限制**: 由于账户计划限制，使用了 AMPERE_A10 (24GB) GPU，而不是原计划的 A100 80GB
2. **显存要求**: LatentSync 1.6 (512x512) 需要约18GB显存，A10的24GB应该足够
3. **并发限制**: 当前为免费计划，最多3个应用，最小副本数为0（按需启动）
4. **冷启动**: 首次请求可能需要额外的启动时间（约46秒）

## 🔧 已调整的依赖

部署过程中进行了以下版本调整：
- `deepCache`: 0.1.9 → 0.1.1 (pypi没有0.1.9版本)
- `face-alignment`: 1.4.2 → 1.4.1 (pypi没有1.4.2版本)

## 📞 支持

如有问题，请查看：
- 应用面板: https://dashboard.cerebrium.ai/projects/p-9de54108/apps/p-9de54108-latentsync
- Cerebrium文档: https://docs.cerebrium.ai
