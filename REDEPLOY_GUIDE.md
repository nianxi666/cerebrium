# 🔄 重新部署指南

## 快速重新部署 (一键部署)

如果不小心删除了应用，你可以快速重新部署。

### ⚡ 最快方式 (1 分钟)

```bash
# 进入部署目录
cd /home/engine/project/cerebrium

# 设置 API Token (选一个)
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"
# 或者
export CEREBRIUM_API_KEY="your-api-key"

# 一键部署
cerebrium deploy --disable-syntax-check -y
```

**就这样！** 应用会在 3-5 分钟内重新部署完成。

---

## 详细步骤

### 步骤 1: 准备凭据

```bash
# 选项 A: 使用 Service Account Token (推荐)
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9..."

# 选项 B: 使用 API Key
export CEREBRIUM_API_KEY="your-api-key"

# 选项 C: 创建 .env 文件
cat > cerebrium/.env << EOF
CEREBRIUM_SERVICE_ACCOUNT_TOKEN=your-token
EOF
```

### 步骤 2: 安装 Cerebrium CLI (如果需要)

```bash
pip install --upgrade cerebrium --break-system-packages
```

### 步骤 3: 执行部署

```bash
cd /home/engine/project/cerebrium

# 标准部署
cerebrium deploy

# 或使用自动确认 (推荐快速部署)
cerebrium deploy -y --disable-syntax-check

# 完整选项
cerebrium deploy \
  --disable-syntax-check \     # 跳过语法检查
  -y \                         # 自动确认
  --disable-animation          # 隐藏动画
```

### 步骤 4: 验证部署

部署完成后，你会看到类似的输出：

```
╭─────────────────────────  wan22-ti2v is now live!   ─────────────────────────╮
│ App Dashboard:                                                               │
│ https://dashboard.cerebrium.ai/projects/p-194bc83f/apps/p-194bc83f-wan22-ti2 │
│ v                                                                            │
│                                                                              │
│ Endpoints:                                                                   │
│ POST                                                                         │
│ https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/{function_na │
│ me}                                                                          │
╰──────────────────────────────────────────────────────────────────────────────╯
```

✅ **部署成功！**

---

## 脚本一键部署

我已经为你创建了自动化脚本。使用它进行快速部署：

### 使用 deploy.sh

```bash
# 方式 1: 使用已有的 deploy.sh 脚本
cd /home/engine/project/cerebrium
./deploy.sh
```

### deploy.sh 脚本内容

```bash
#!/bin/bash

# 从 .env 文件加载变量 (如果存在)
if [ -f .env ]; then
  set -a
  source .env
  set +a
fi

# 检查凭据
if [ -z "${CEREBRIUM_SERVICE_ACCOUNT_TOKEN}" ] && [ -z "${CEREBRIUM_API_KEY}" ]; then
  echo "Error: CEREBRIUM_SERVICE_ACCOUNT_TOKEN or CEREBRIUM_API_KEY is not set." >&2
  echo "Please create a .env file with your CEREBRIUM_SERVICE_ACCOUNT_TOKEN or export it." >&2
  exit 1
fi

# 安装 CLI (如果需要)
if ! command -v cerebrium &> /dev/null; then
  echo "Installing Cerebrium CLI..."
  pip install --upgrade cerebrium
fi

# 执行部署
echo "Deploying LatentSync to Cerebrium..."
cerebrium deploy
```

---

## 完全自动化部署 (创建自己的脚本)

创建一个快速部署脚本 `quick_redeploy.sh`:

```bash
#!/bin/bash

set -e  # 遇到错误立即退出

echo "🚀 快速重新部署脚本"
echo "===================="

# 检查凭据
if [ -z "$CEREBRIUM_SERVICE_ACCOUNT_TOKEN" ] && [ -z "$CEREBRIUM_API_KEY" ]; then
    echo "❌ 错误: 未设置认证凭据"
    echo "请设置: export CEREBRIUM_SERVICE_ACCOUNT_TOKEN='your-token'"
    exit 1
fi

# 进入项目目录
cd "$(dirname "$0")/cerebrium"

# 安装 CLI
echo "📦 安装 Cerebrium CLI..."
pip install --upgrade cerebrium --break-system-packages -q

# 执行部署
echo "🚀 开始部署..."
cerebrium deploy --disable-syntax-check -y

echo "✅ 部署完成！"
echo "📊 应用信息:"
echo "   名称: wan22-ti2v"
echo "   状态: Live"
echo "   API: https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v"
```

使用:

```bash
# 保存为 quick_redeploy.sh
chmod +x quick_redeploy.sh

# 运行
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"
./quick_redeploy.sh
```

---

## 部署配置速查表

### 应用配置 (cerebrium/cerebrium.toml)

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
diffusers = "0.33.1"
transformers = "4.48.2"
```

### 项目 ID
- **项目 ID**: p-194bc83f
- **应用名**: wan22-ti2v

---

## 常见重新部署问题

### Q: 部署失败了，怎么办？

**A**: 查看错误日志，常见原因：

```bash
# 检查 API Key
echo $CEREBRIUM_SERVICE_ACCOUNT_TOKEN
echo $CEREBRIUM_API_KEY

# 确认 CLI 已安装
cerebrium --version

# 尝试手动安装
pip install --upgrade cerebrium --break-system-packages
```

### Q: 部署超时了？

**A**: 增加超时时间或使用分离模式：

```bash
# 分离模式部署 (后台运行)
cerebrium deploy --detach

# 然后查看状态
cerebrium status
```

### Q: 旧应用的数据会丢失吗？

**A**: 不会。部署新应用时：
- ✅ 使用相同的应用名 → 替换旧版本
- ✅ 仪表板历史保留
- ❌ 本地生成的视频不会自动备份 → 需要手动备份

---

## 预防措施

### 1. 备份重要数据

```bash
# 备份配置
cp cerebrium/cerebrium.toml cerebrium/cerebrium.toml.backup

# 备份部署文件
cp -r cerebrium cerebrium.backup
```

### 2. 保存凭据安全

```bash
# 永久保存 Token (在 ~/.bashrc 或 ~/.zshrc)
echo 'export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"' >> ~/.bashrc
source ~/.bashrc
```

### 3. 使用版本控制

```bash
# 所有更改都已在 Git 中
git log --oneline | head -5

# 可以随时回到之前的版本
git checkout <commit-hash>
```

---

## 监控部署状态

### 查看应用状态

```bash
# 访问仪表板
open https://dashboard.cerebrium.ai/projects/p-194bc83f

# 或通过 CLI
cerebrium logs wan22-ti2v
```

### 验证 API 连接

```bash
# 测试 API
curl -X POST \
  https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict \
  -H "Authorization: Bearer YOUR_KEY" \
  -H "Content-Type: application/json" \
  -d '{"prompt":"test"}'
```

---

## 部署时间表

| 步骤 | 时间 |
|------|------|
| CLI 安装 | 1-2 分钟 |
| 代码上传 | 1 分钟 |
| 镜像构建 | 2-3 分钟 |
| 应用启动 | 1-2 分钟 |
| **总计** | **5-8 分钟** |

---

## 一键部署命令速查

### 最快 (复制粘贴)

```bash
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token" && \
cd /home/engine/project/cerebrium && \
pip install --upgrade cerebrium --break-system-packages -q && \
cerebrium deploy --disable-syntax-check -y
```

### 标准方式

```bash
# 1. 设置凭据
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"

# 2. 安装 CLI
pip install --upgrade cerebrium --break-system-packages

# 3. 部署
cd /home/engine/project/cerebrium
cerebrium deploy
```

### 使用脚本

```bash
# 1. 创建脚本
cat > redeploy.sh << 'EOF'
#!/bin/bash
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"
cd /home/engine/project/cerebrium
cerebrium deploy --disable-syntax-check -y
EOF

# 2. 执行
chmod +x redeploy.sh
./redeploy.sh
```

---

## 部署后检查清单

- ✅ 应用显示为 "Live"
- ✅ 可以访问仪表板
- ✅ API 返回 200 状态码
- ✅ 生成的视频正常
- ✅ 日志中没有错误

---

## 需要帮助？

### 查看完整文档

- 📚 [START_HERE.txt](START_HERE.txt) - 快速入门
- 📚 [QUICK_START.md](QUICK_START.md) - 快速开始
- 📚 [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md) - API 参考
- 📚 [DEPLOYMENT_SUCCESS.md](DEPLOYMENT_SUCCESS.md) - 部署信息

### 测试部署

```bash
# 使用 Python 脚本测试
python3 /home/engine/project/test_inference.py

# 使用 Web UI 测试
open /home/engine/project/index.html
```

---

## 总结

**最快重新部署方式:**

```bash
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"
cd /home/engine/project/cerebrium
pip install --upgrade cerebrium --break-system-packages -q
cerebrium deploy --disable-syntax-check -y
```

**等待 5-8 分钟，应用将重新上线！** ✅

---

**记住**: 所有配置和代码都保存在 Git 中，可以随时重新部署！

最后更新: 2024-11-11
