# 🚀 快速开始指南

## 部署状态

✅ **应用已成功部署！**

- **应用名称**: wan22-ti2v
- **状态**: 🟢 Live
- **GPU**: ADA L40 (48 GB)
- **API 端点**: https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict
- **仪表板**: https://dashboard.cerebrium.ai/projects/p-194bc83f/apps/p-194bc83f-wan22-ti2v

---

## 📋 三种使用方式

### 方式 1️⃣: Web 界面（推荐）

最简单的方式，无需编码。

1. 打开 `index.html` 在浏览器中
2. 输入您的 API Key（首次使用）
3. 选择生成模式（T2V 或 TI2V）
4. 填入参数
5. 点击"生成视频"

**优点**: 直观、友好、无需编程知识

---

### 方式 2️⃣: Python 脚本

适合批量处理和自动化。

```bash
# 安装依赖
pip install requests

# 设置 API Key
export CEREBRIUM_API_KEY="your-api-key"

# 运行测试脚本
python3 test_inference.py
```

**脚本位置**: `/home/engine/project/test_inference.py`

**特性**:
- ✅ 自动下载生成的视频
- ✅ 支持 T2V 和 TI2V
- ✅ 详细的日志输出
- ✅ 错误处理

---

### 方式 3️⃣: cURL 命令

适合快速测试和脚本集成。

**Text-to-Video 示例**:

```bash
curl -X POST \
  https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over a calm ocean with birds flying in formation",
    "negative_prompt": "low quality, blurry",
    "num_frames": 121,
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "seed": 42
  }' \
  -o response.json
```

**Text-Image-to-Video 示例**:

```bash
curl -X POST \
  https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A person dancing gracefully",
    "image_url": "https://example.com/image.jpg",
    "num_frames": 121,
    "num_inference_steps": 30,
    "guidance_scale": 7.5
  }' \
  -o response.json
```

**提取视频**:

```bash
# 从 JSON 响应中提取 base64 并保存
cat response.json | jq -r '.video_base64' | base64 -d > output.mp4
```

---

## 🎨 提示词示例

### 高质量提示

```
"A cinematic scene of a girl walking through a misty forest at dawn, 
with golden sunlight filtering through tall trees, birds chirping, 
ultra high quality, 4K, cinematic lighting"
```

### 反向提示

```
"low quality, blurry, distorted, artifact, watermark, 
frame rate drop, static, freeze frame"
```

---

## ⚙️ 推荐参数

### 快速生成 (2-3 分钟)
```json
{
  "num_frames": 25,
  "num_inference_steps": 20,
  "guidance_scale": 5.0
}
```

### 均衡 (3-5 分钟)
```json
{
  "num_frames": 121,
  "num_inference_steps": 30,
  "guidance_scale": 7.5
}
```

### 高质量 (8-12 分钟)
```json
{
  "num_frames": 121,
  "num_inference_steps": 50,
  "guidance_scale": 10.0
}
```

---

## 📊 性能数据

| GPU | VRAM | T2V 性能 | TI2V 性能 |
|-----|------|---------|----------|
| ADA L40 | 48GB | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| A10 | 24GB | ⭐⭐⭐ | ⭐⭐⭐ |

---

## 🔧 故障排除

### 问题: "401 Unauthorized"
**解决**: 检查 API Key 是否正确设置
```bash
echo $CEREBRIUM_API_KEY
```

### 问题: "Timeout"
**解决**: 减少推理步数或帧数
```json
{
  "num_frames": 25,
  "num_inference_steps": 20
}
```

### 问题: "400 Invalid payload"
**解决**: 检查 num_frames 是否符合 4n+1 格式（25, 29, ..., 121）

### 问题: 视频质量不好
**解决**: 增加推理步数和指导尺度
```json
{
  "num_inference_steps": 50,
  "guidance_scale": 10.0
}
```

---

## 📚 详细文档

- **完整 API 文档**: 见 `API_USAGE_GUIDE.md`
- **部署信息**: 见 `DEPLOYMENT_SUCCESS.md`
- **源代码**: 位于 `cerebrium/` 目录

---

## 📈 API 端点对照

| 功能 | 方法 | 端点 |
|------|------|------|
| 生成视频 | POST | `/predict` |
| 获取状态 | GET | `/status` |
| 获取模型信息 | GET | `/info` |

---

## 💡 高级用法

### 批量生成

```python
prompts = [
    "A cat dancing on stage",
    "A sunset over mountains",
    "Ocean waves crashing on rocks"
]

for i, prompt in enumerate(prompts):
    payload = {
        "prompt": prompt,
        "seed": i  # 不同的 seed 产生不同的变化
    }
    # 发送请求...
```

### 使用种子复现结果

```python
# 第一次
result1 = generate_video(prompt, seed=42)

# 第二次会产生完全相同的结果
result2 = generate_video(prompt, seed=42)
```

### 参考图像优化

对于 TI2V，最佳结果的图像特性：
- ✅ 清晰、高分辨率
- ✅ 与提示词相关
- ✅ 良好的光线和对比度
- ❌ 避免低分辨率或模糊图像

---

## 🆘 获取帮助

1. **查看完整文档**: `API_USAGE_GUIDE.md`
2. **查看部署状态**: `DEPLOYMENT_SUCCESS.md`
3. **运行测试脚本**: `python3 test_inference.py`
4. **访问仪表板**: https://dashboard.cerebrium.ai/projects/p-194bc83f

---

## 📝 示例输出

### 请求
```json
{
  "prompt": "A butterfly landing on a flower",
  "num_frames": 121,
  "num_inference_steps": 30
}
```

### 响应
```json
{
  "video_base64": "AAAAAIGZ...[长的base64字符串]...==",
  "details": {
    "prompt": "A butterfly landing on a flower",
    "height": 704,
    "width": 1280,
    "num_frames": 121,
    "num_inference_steps": 30,
    "guidance_scale": 7.5,
    "fps": 24
  }
}
```

---

## 🎯 下一步

1. ✅ 获取 API Key
2. ✅ 尝试 Web 界面 (`index.html`)
3. ✅ 运行 Python 脚本 (`test_inference.py`)
4. ✅ 集成到您的应用
5. ✅ 探索高级功能

---

**准备好了吗？选择上面的方式之一开始吧！** 🚀

---

**最后更新**: 2024-11-11  
**模型**: Wan2.2 TI2V 5B  
**GPU**: ADA L40 (48GB)  
**状态**: ✅ 已部署并运行
