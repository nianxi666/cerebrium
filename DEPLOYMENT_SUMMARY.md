# LatentSync 部署和测试总结

## 🎯 任务完成情况

✅ **已完成**: 部署 LatentSync 推理服务到 Cerebrium 并通过 curl 进行测试

## 📝 主要修复

### 1. VGG16 模型下载问题

**问题描述:**
- 原代码尝试从不存在的 HuggingFace `pytorch/vision` 仓库下载 VGG16 权重
- 导致推理初始化失败，错误：`404 Client Error: Not Found`

**解决方案:**
修改 `main.py` 中的 `_ensure_torch_hub_weights()` 函数，使用 PyTorch 官方 CDN：

```python
from torch.hub import download_url_to_file

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

### 2. 输出路径创建问题

**问题描述:**
- Pipeline 在生成输出视频时，输出目录不存在
- 导致 ffmpeg 无法写入文件：`[Errno 2] No such file or directory`

**解决方案:**
修改 `latentsync/pipelines/lipsync_pipeline.py`，确保输出目录存在：

```python
from pathlib import Path

# 在 ffmpeg 执行前创建输出目录
Path(video_out_path).parent.mkdir(parents=True, exist_ok=True)

# 添加错误检查
command = f"ffmpeg -y -loglevel error -nostdin -i {os.path.join(temp_dir, 'video.mp4')} -i {os.path.join(temp_dir, 'audio.wav')} -c:v libx264 -crf 18 -c:a aac -q:v 0 -q:a 0 {video_out_path}"
result = subprocess.run(command, shell=True, capture_output=True, text=True)

if result.returncode != 0:
    raise RuntimeError(f"ffmpeg failed with code {result.returncode}: {result.stderr}")

if not os.path.exists(video_out_path):
    raise FileNotFoundError(f"Output video was not created at {video_out_path}")
```

### 3. 测试 URL 不可用

**问题描述:**
- 文档中的示例 URL 不存在 (`https://github.com/anotherjesse/LatentSync/...`)

**解决方案:**
创建 `test_curl.sh` 脚本，使用本地 `assets/` 目录中的演示文件，并通过 base64 编码上传。

## 🚀 部署信息

### 服务端点
```
POST https://api.aws.us-east-1.cerebrium.ai/v4/p-9de54108/latentsync/predict
```

### 认证
```bash
Authorization: Bearer $CEREBRIUM_API_KEY
```

### 硬件配置
- **GPU**: AMPERE_A10 (24GB)
- **CPU**: 8 核
- **内存**: 32GB
- **镜像大小**: 3.40 GB

### 部署时间
- **构建时间**: 约 40 秒（重新部署）
- **初始化时间**: 约 25 秒

## 🧪 测试方法

### 使用测试脚本
```bash
export CEREBRIUM_API_KEY="your_service_account_token"
./test_curl.sh
```

### 手动 curl 测试（使用本地文件）
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

### 使用公开 URL
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

## 📊 性能指标

### 推理时间
- 首次请求（冷启动）: ~70 秒
- 后续请求（热启动）: ~30-40 秒（取决于视频长度）

### 处理阶段
1. 模型加载（仅冷启动）: ~25 秒
2. 人脸检测和变换: ~5-10 秒
3. AI 推理（多个批次）: ~20-30 秒
4. 视频恢复和合成: ~5-10 秒

## 📄 输出格式

成功响应示例：
```json
{
  "run_id": "uuid",
  "result": {
    "video_base64": "<base64编码的视频>",
    "details": {
      "guidance_scale": 1.5,
      "inference_steps": 20,
      "seed": 1247
    }
  },
  "run_time_ms": 35000.0
}
```

提取输出视频：
```bash
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

# 或使用 jq
cat response.json | jq -r '.result.video_base64' | base64 -d > output.mp4
```

## 📁 相关文件

- `main.py` - 主要推理代码（已修复 VGG16 下载）
- `latentsync/pipelines/lipsync_pipeline.py` - Pipeline 代码（已修复输出路径）
- `test_curl.sh` - 自动化测试脚本（使用本地文件）
- `assets/demo1_video.mp4` - 演示视频
- `assets/demo1_audio.wav` - 演示音频
- `CURL_TEST_GUIDE.md` - 详细的测试指南

## 🔗 有用链接

- **应用控制台**: https://dashboard.cerebrium.ai/projects/p-9de54108/apps/p-9de54108-latentsync
- **项目 ID**: p-9de54108
- **应用名称**: latentsync
- **区域**: AWS US-East-1

## ⚠️ 注意事项

1. **API Key 安全**: 
   - 不要在代码中硬编码 API Key
   - 使用环境变量 `CEREBRIUM_API_KEY`

2. **输入限制**:
   - 视频格式: MP4
   - 音频格式: WAV
   - 建议分辨率: 512x512

3. **显存要求**:
   - LatentSync 1.6 需要约 18GB 显存
   - AMPERE_A10 提供 24GB，应该足够

4. **并发限制**:
   - 当前计划最小副本数为 0（按需启动）
   - 冷启动时间约 25 秒

## 🎉 部署成功

LatentSync 推理服务已成功部署到 Cerebrium 并通过 curl 测试验证！

### 关键成就
✅ 修复 VGG16 模型下载问题  
✅ 修复输出文件路径问题  
✅ 创建自动化测试脚本  
✅ 部署成功（构建时间 40 秒，初始化 25 秒）  
✅ 编写详细文档和测试指南
