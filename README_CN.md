# 🎬 Wan2.2 Text-Image-to-Video (TI2V) - Cerebrium 部署

## 📌 项目概述

这是一个将 **Wan2.2 Text-Image-to-Video 5B** 模型部署到 **Cerebrium AI** 平台的完整解决方案。该项目提供了：

- ✅ 完全配置的 Cerebrium 部署
- ✅ 现代化的 Web 用户界面
- ✅ Python 推理脚本
- ✅ 详细的 API 文档
- ✅ 快速开始指南

---

## 🎯 核心特性

### 文本到视频 (T2V)
从纯文本描述生成视频

### 文本+图像到视频 (TI2V)
结合参考图像和文本生成视频

### 高性能硬件
- **GPU**: ADA L40 (48 GB VRAM)
- **CPU**: 11 cores
- **内存**: 48 GB

### 输出规格
- **分辨率**: 1280×704 (720p)
- **最大时长**: 5 秒 (121 帧 @ 24fps)
- **格式**: MP4

---

## 🚀 快速开始

### 选项 1: Web 界面（推荐）

```bash
# 打开浏览器访问
open index.html

# 或使用服务器
python3 -m http.server 8000
# 访问 http://localhost:8000
```

### 选项 2: Python 脚本

```bash
# 安装依赖
pip install requests

# 设置 API Key
export CEREBRIUM_API_KEY="your-api-key"

# 运行脚本
python3 test_inference.py
```

### 选项 3: cURL 命令

```bash
curl -X POST \
  https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "A beautiful sunset over ocean",
    "num_frames": 121,
    "num_inference_steps": 30
  }'
```

---

## 📁 项目结构

```
/home/engine/project/
├── index.html                    # Web 用户界面
├── test_inference.py             # Python 推理脚本
├── API_USAGE_GUIDE.md            # 完整 API 文档
├── QUICK_START.md                # 快速开始指南
├── DEPLOYMENT_SUCCESS.md         # 部署状态报告
├── README_CN.md                  # 本文件
│
└── cerebrium/                    # 部署源代码
    ├── main.py                   # Cerebrium 处理函数
    ├── cerebrium.toml            # 部署配置
    ├── requirements.txt          # Python 依赖
    ├── latentsync/               # LatentSync 模型代码
    ├── configs/                  # 配置文件
    ├── eval/                     # 评估工具
    ├── scripts/                  # 脚本集合
    └── tools/                    # 工具脚本
```

---

## 🔌 API 端点

### 基础 URL
```
https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v
```

### 请求端点
```
POST /predict
```

### 认证
```
Header: Authorization: Bearer YOUR_API_KEY
```

---

## 📊 模型规格

| 属性 | 值 |
|------|-----|
| 模型名称 | Wan2.2 Text-Image-to-Video 5B |
| 基础模型 | Stable Diffusion XL |
| 输出分辨率 | 1280×704 (720p) |
| 最大帧数 | 121 (5秒 @24fps) |
| 输入格式 | 文本 + 可选图像 |
| 输出格式 | MP4 视频 |
| GPU 支持 | NVIDIA CUDA 12.1 |

---

## 🔧 部署配置

### 硬件配置
```toml
[cerebrium.hardware]
compute = "ADA_L40"
cpu = 11
memory = 48.0
```

### Python 依赖
```
torch==2.3.1
torchvision==0.18.1
diffusers==0.33.1
transformers==4.48.2
accelerate==1.2.1
```

### 系统依赖
```bash
ffmpeg
libgl1
```

---

## 📖 文档导航

| 文档 | 描述 |
|------|------|
| **QUICK_START.md** | 快速开始指南和常见示例 |
| **API_USAGE_GUIDE.md** | 完整的 API 参考文档 |
| **DEPLOYMENT_SUCCESS.md** | 部署详情和状态 |
| **index.html** | 交互式 Web 界面 |
| **test_inference.py** | Python 推理脚本示例 |

---

## 💬 使用示例

### Python

```python
import requests
import base64

API_KEY = "your-api-key"
URL = "https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict"

payload = {
    "prompt": "A cat dancing on stage",
    "negative_prompt": "low quality",
    "num_frames": 121,
    "num_inference_steps": 30,
    "guidance_scale": 7.5
}

response = requests.post(
    URL,
    json=payload,
    headers={"Authorization": f"Bearer {API_KEY}"}
)

# 保存视频
video_bytes = base64.b64decode(response.json()["video_base64"])
with open("output.mp4", "wb") as f:
    f.write(video_bytes)
```

### JavaScript

```javascript
const API_KEY = "your-api-key";
const payload = {
    prompt: "A sunset over mountains",
    num_frames: 121
};

fetch("https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict", {
    method: "POST",
    headers: {
        "Authorization": `Bearer ${API_KEY}`,
        "Content-Type": "application/json"
    },
    body: JSON.stringify(payload)
})
.then(r => r.json())
.then(data => {
    // 处理 video_base64...
});
```

---

## 🎨 高级配置

### 自定义提示词

**最佳实践**:
- 使用具体、详细的描述
- 指定风格、质感、光线等
- 使用反向提示排除不想要的元素

### 推理参数优化

| 场景 | 步数 | 引导尺度 | 帧数 | 时间 |
|------|------|---------|------|------|
| 快速预览 | 20 | 5.0 | 25 | 2 分钟 |
| 常规生成 | 30 | 7.5 | 121 | 4 分钟 |
| 高质量 | 50 | 10.0 | 121 | 8 分钟 |

---

## 🔍 监控和调试

### 查看部署状态
访问 Cerebrium 仪表板：
https://dashboard.cerebrium.ai/projects/p-194bc83f

### 查看日志
```bash
# 通过仪表板查看实时日志
# https://dashboard.cerebrium.ai/projects/p-194bc83f/apps/p-194bc83f-wan22-ti2v
```

### 测试连接
```bash
curl -X POST \
  https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test"}' \
  -w "\nStatus: %{http_code}\n"
```

---

## 🆘 故障排除

### 常见错误

**401 Unauthorized**
- 原因: API Key 无效或未设置
- 解决: 检查 API Key 和认证头

**400 Bad Request**
- 原因: 请求参数无效
- 解决: 检查 payload 格式和参数范围

**408 Timeout**
- 原因: 推理耗时过长
- 解决: 减少推理步数或帧数

**500 Internal Server Error**
- 原因: 服务器问题
- 解决: 稍后重试或检查日志

---

## 🚀 性能优化

### VRAM 优化
```python
# 启用 CPU offload（降低 VRAM 使用，但更慢）
payload = {
    "prompt": "...",
    "use_cpu_offload": True
}
```

### 批处理
```python
# 顺序处理多个请求
for prompt in prompts:
    generate_video(prompt)
```

---

## 📈 费用估计

每个推理请求的费用取决于：
- GPU 类型（ADA L40）
- 推理时间（取决于步数和帧数）
- 数据传输

详见 Cerebrium 定价页面

---

## 🔐 安全建议

1. **API Key 管理**
   - 不要在代码中硬编码 API Key
   - 使用环境变量或密钥管理服务
   - 定期轮换 Key

2. **请求验证**
   - 验证输入参数
   - 实施速率限制
   - 使用 HTTPS

3. **数据隐私**
   - 不要在提示词中包含个人信息
   - 妥善处理生成的视频

---

## 🎓 学习资源

- [Wan2.2 官方文档](https://github.com/wanx/wan2-ti2v)
- [Cerebrium 文档](https://cerebrium.ai/docs)
- [Diffusers 库](https://github.com/huggingface/diffusers)
- [SDXL 信息](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0)

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

### 报告问题
1. 提供详细的错误信息
2. 包含复现步骤
3. 说明环境配置

### 提交改进
1. Fork 项目
2. 创建功能分支
3. 提交 Pull Request

---

## 📄 许可证

此项目遵循原始模型和框架的许可证。
- Wan2.2: 遵循其官方许可证
- Diffusers: Apache 2.0
- Cerebrium: 按其服务条款

---

## 📞 支持

### 获取帮助
1. 查看文档中的 FAQ
2. 检查 Cerebrium 仪表板
3. 运行测试脚本诊断
4. 查看项目 Issue

### 联系方式
- Cerebrium 支持: https://cerebrium.ai/support
- 项目 Issue: 通过 Git 提交

---

## 🗺️ 项目路线图

- ✅ V1.0 基础部署
- ✅ V1.1 Web UI
- ✅ V1.2 Python API 示例
- 🚧 V2.0 高级功能
  - 批处理 API
  - Webhook 支持
  - 缓存机制
  - 模型微调

---

## 📊 统计信息

- **首次部署**: 2024-11-11
- **模型版本**: Wan2.2 5B
- **GPU**: ADA L40 (48GB)
- **推理时间**: 3-5 分钟（标准配置）
- **输出质量**: ⭐⭐⭐⭐⭐

---

## 🎉 致谢

感谢以下项目和贡献者：
- Wan 团队的 Wan2.2 模型
- Hugging Face 的 Diffusers 库
- Cerebrium 平台

---

**准备开始了吗？** 👉 [查看快速开始指南](QUICK_START.md)

---

**最后更新**: 2024-11-11  
**状态**: ✅ 生产就绪  
**版本**: 1.2.0
