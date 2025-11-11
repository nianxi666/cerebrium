# ⚡ 快速重新部署

应用被删除？ **不用担心！** 只需一个命令就能重新部署。

## 🚀 最快方式（推荐）

### 使用快速部署脚本

```bash
# 1. 设置凭据 (只需做一次)
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-service-account-token"

# 2. 运行快速部署脚本
chmod +x quick_redeploy.sh
./quick_redeploy.sh
```

**就这样！** 脚本会自动处理所有事情：
- ✅ 验证凭据
- ✅ 安装 Cerebrium CLI
- ✅ 检查配置文件
- ✅ 执行部署
- ✅ 显示部署结果

预计时间: **5-8 分钟**

---

## 📝 一行命令部署

如果你喜欢直接命令：

```bash
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token" && \
cd cerebrium && \
pip install --upgrade cerebrium --break-system-packages -q && \
cerebrium deploy --disable-syntax-check -y
```

---

## 🔧 手动部署步骤

如果脚本不适用，按以下步骤手动部署：

```bash
# 1. 进入部署目录
cd /path/to/project/cerebrium

# 2. 设置认证
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"
# 或
export CEREBRIUM_API_KEY="your-api-key"

# 3. 安装 CLI
pip install --upgrade cerebrium --break-system-packages

# 4. 部署
cerebrium deploy
```

---

## ✅ 验证部署成功

部署完成后，你应该看到：

```
╭─────────────────────────  wan22-ti2v is now live!   ─────────────────────────╮
│ App Dashboard:                                                               │
│ https://dashboard.cerebrium.ai/projects/p-194bc83f/apps/p-194bc83f-wan22-ti2v│
│                                                                              │
│ Endpoints:                                                                   │
│ POST https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict │
╰──────────────────────────────────────────────────────────────────────────────╯
```

✅ 如果看到 "is now live!" → **部署成功！**

---

## 🆘 遇到问题?

### 问题: 找不到凭据

```
❌ 未找到认证凭据！
```

**解决**:
```bash
# 设置凭据
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-full-token"

# 验证已设置
echo $CEREBRIUM_SERVICE_ACCOUNT_TOKEN
```

### 问题: CLI 安装失败

```bash
# 手动安装
pip install --upgrade cerebrium --break-system-packages
```

### 问题: 部署超时

```bash
# 使用后台部署模式
cerebrium deploy --detach
```

---

## 📊 部署配置信息

| 配置项 | 值 |
|--------|-----|
| 应用名称 | wan22-ti2v |
| 项目 ID | p-194bc83f |
| GPU | ADA L40 (48 GB) |
| CPU | 11 cores |
| 内存 | 48 GB |
| Python | 3.11 |

---

## 🎯 部署后下一步

部署完成后，你可以：

1. **测试 API**
   ```bash
   python3 test_inference.py
   ```

2. **使用 Web UI**
   ```bash
   open index.html
   ```

3. **查看日志**
   ```bash
   cerebrium logs wan22-ti2v
   ```

4. **访问仪表板**
   https://dashboard.cerebrium.ai/projects/p-194bc83f

---

## 💡 Tips

### 保存凭据（可选）

如果你经常部署，可以将凭据保存到 `cerebrium/.env`:

```bash
# 创建 .env 文件
echo 'CEREBRIUM_SERVICE_ACCOUNT_TOKEN=your-token' > cerebrium/.env

# 然后直接运行脚本
./quick_redeploy.sh
```

### 创建快捷命令

在 `~/.bashrc` 或 `~/.zshrc` 中添加：

```bash
alias redeploy='cd ~/your/project && export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token" && ./quick_redeploy.sh'
```

然后直接运行：

```bash
redeploy
```

---

## 📚 更详细的信息

- 📖 完整重新部署指南: [REDEPLOY_GUIDE.md](REDEPLOY_GUIDE.md)
- 📖 快速开始: [QUICK_START.md](QUICK_START.md)
- 📖 API 文档: [API_USAGE_GUIDE.md](API_USAGE_GUIDE.md)

---

## ⏱️ 部署时间表

| 步骤 | 预计时间 |
|------|---------|
| 验证凭据 | 10 秒 |
| 安装 CLI | 1-2 分钟 |
| 上传代码 | 1 分钟 |
| 构建镜像 | 2-3 分钟 |
| 启动应用 | 1-2 分钟 |
| **总计** | **5-8 分钟** |

---

**准备好了吗？** 

### 现在就开始：

```bash
export CEREBRIUM_SERVICE_ACCOUNT_TOKEN="your-token"
./quick_redeploy.sh
```

或查看 [REDEPLOY_GUIDE.md](REDEPLOY_GUIDE.md) 了解更多选项。

---

祝部署顺利！🚀
