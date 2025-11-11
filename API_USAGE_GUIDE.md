# 🎬 Wan2.2 TI2V API 使用指南

## 快速开始

### 1. 环境配置

```bash
# 设置 API Key
export CEREBRIUM_API_KEY="your-api-key-here"
```

### 2. Python 推理脚本

运行测试脚本：

```bash
cd /home/engine/project
python3 test_inference.py
```

### 3. Web 界面

打开浏览器访问 `index.html`：

```bash
# 简单的方式：用浏览器打开文件
open index.html

# 或使用 Python 简易服务器
python3 -m http.server 8000
# 然后访问 http://localhost:8000
```

---

## API 详细说明

### 基础信息

- **API 基础 URL**: `https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v`
- **项目 ID**: `p-194bc83f`
- **应用名称**: `wan22-ti2v`
- **GPU**: ADA L40 (48 GB VRAM)

### 认证

所有请求需要在 Header 中包含 API Key：

```
Authorization: Bearer YOUR_API_KEY
Content-Type: application/json
```

---

## 文本到视频 (T2V)

### 请求格式

```bash
curl -X POST https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over a calm ocean",
    "negative_prompt": "low quality, blurry",
    "height": 704,
    "width": 1280,
    "num_frames": 121,
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "fps": 24,
    "seed": 42
  }'
```

### 参数说明

| 参数 | 类型 | 默认值 | 范围 | 说明 |
|------|------|--------|------|------|
| `prompt` | string | 必需 | - | 视频描述文本 |
| `negative_prompt` | string | 空 | - | 反向提示，描述不想要的内容 |
| `height` | int | 704 | 32-2048 | 视频高度 |
| `width` | int | 1280 | 32-2048 | 视频宽度 |
| `num_frames` | int | 121 | 25-121 | 帧数（必须是 4n+1 格式） |
| `num_inference_steps` | int | 50 | 1-100 | 扩散步数，越多质量越好但耗时越长 |
| `guidance_scale` | float | 5.0 | 1.0-20.0 | 分类器自由引导强度 |
| `fps` | int | 24 | 1-60 | 输出视频帧率 |
| `seed` | int | null | - | 随机种子，设置可重复结果 |

### 响应示例

```json
{
  "video_base64": "AAAAAIGZ...",
  "details": {
    "prompt": "A beautiful sunset over a calm ocean",
    "negative_prompt": "low quality, blurry",
    "height": 704,
    "width": 1280,
    "num_frames": 121,
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "fps": 24,
    "seed": 42
  }
}
```

---

## 文本+图像到视频 (TI2V)

### 请求格式

```bash
curl -X POST https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A person dancing gracefully",
    "image_url": "https://example.com/image.jpg",
    "negative_prompt": "low quality",
    "height": 704,
    "width": 1280,
    "num_frames": 121,
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "fps": 24
  }'
```

### 额外参数

| 参数 | 类型 | 说明 |
|------|------|------|
| `image_url` | string | 参考图像的 URL（必需） |
| `image_base64` | string | 或提供 base64 编码的图像 |

---

## Python 使用示例

### 基础例子

```python
import requests
import base64
from pathlib import Path

API_KEY = "your-api-key"
API_URL = "https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict"

def generate_video(prompt, api_key=API_KEY):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "prompt": prompt,
        "negative_prompt": "low quality, blurry",
        "num_frames": 121,
        "num_inference_steps": 30,
        "guidance_scale": 7.5,
        "seed": 42
    }
    
    response = requests.post(API_URL, json=payload, headers=headers)
    
    if response.status_code == 200:
        result = response.json()
        video_bytes = base64.b64decode(result["video_base64"])
        Path("output.mp4").write_bytes(video_bytes)
        print("✅ Video saved to output.mp4")
    else:
        print(f"❌ Error: {response.text}")

# 使用
generate_video("A cat dancing on a stage")
```

### 保存视频

```python
import base64
from pathlib import Path

video_base64 = result["video_base64"]
video_bytes = base64.b64decode(video_base64)
Path("generated_video.mp4").write_bytes(video_bytes)
```

---

## JavaScript 使用示例

```javascript
const API_KEY = "your-api-key";
const API_URL = "https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict";

async function generateVideo(prompt) {
    const payload = {
        prompt: prompt,
        negative_prompt: "low quality, blurry",
        num_frames: 121,
        num_inference_steps: 30,
        guidance_scale: 7.5
    };

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Authorization": `Bearer ${API_KEY}`,
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        const result = await response.json();
        
        // 将 base64 转换为 blob
        const byteCharacters = atob(result.video_base64);
        const byteNumbers = new Array(byteCharacters.length);
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: "video/mp4" });
        
        // 播放或下载
        const videoUrl = URL.createObjectURL(blob);
        const videoElement = document.getElementById("video");
        videoElement.src = videoUrl;
    } catch (error) {
        console.error("Error:", error);
    }
}

// 使用
generateVideo("A beautiful sunset over ocean");
```

---

## 推理时间估计

| 推理步数 | 文件大小 | 估计时间* |
|---------|---------|----------|
| 20 | ~150 MB | 2-3 分钟 |
| 30 | ~150 MB | 3-4 分钟 |
| 50 | ~150 MB | 5-7 分钟 |
| 100 | ~150 MB | 10-15 分钟 |

*时间基于 ADA L40 GPU，实际时间可能因系统负载而异

---

## 常见问题

### Q: 如何获取更高质量的视频？
**A**: 增加 `num_inference_steps`（例如从 30 增加到 50），但这会增加生成时间。

### Q: 支持的最大分辨率是多少？
**A**: 理论上可达 2048x2048，但建议保持 1280×704（720p）以平衡质量和速度。

### Q: 帧数有什么限制？
**A**: 最多 121 帧（约 5 秒 @24fps）。帧数必须遵循 4n+1 格式（25, 29, 33, ..., 121）。

### Q: 可以使用 Base64 图像吗？
**A**: 可以，TI2V 模式支持 `image_base64` 参数代替 `image_url`。

### Q: 如何获取可重复的结果？
**A**: 设置 `seed` 参数为固定值。

---

## 错误处理

### 常见错误

```
HTTP 400: Invalid payload
-> 检查参数格式和类型

HTTP 401: Unauthorized
-> 检查 API Key 是否正确

HTTP 500: Internal server error
-> 服务器问题，稍后重试

Timeout
-> 请求超过 10 分钟，模型可能需要更多时间
```

---

## 最佳实践

1. **使用适当的 Seed**: 调试时使用固定 seed，生产环境使用随机 seed
2. **优化 Prompts**: 详细且具体的描述会产生更好的结果
3. **合理设置步数**: 30 步是质量和速度的很好平衡
4. **监控 API 使用**: 跟踪请求数量以管理成本

---

## 支持

- 📧 API 文档: https://cerebrium.ai/docs
- 🐛 问题报告: 通过 API Key 关联的账户
- 💬 社区论坛: https://cerebrium.ai/community

---

## 部署配置

```toml
[cerebrium.deployment]
name = "wan22-ti2v"
python_version = "3.11"

[cerebrium.hardware]
compute = "ADA_L40"
cpu = 11
memory = 48.0

[cerebrium.dependencies.pip]
torch = "2.3.1"
torchvision = "0.18.1"
diffusers = "0.33.1"
transformers = "4.48.2"
```

---

**最后更新**: 2024-11-11
**API 版本**: v4
**模型**: Wan2.2 TI2V 5B
