# 解决磁盘配额问题 - Volume方案

## 问题分析

经过测试，虽然我们已经：
1. ✅ 成功部署应用到Cerebrium (AMPERE_A10)
2. ✅ API调用格式正确
3. ✅ 模型加载流程正常启动

但仍然遇到 "Disk quota exceeded" 错误，原因是：

### 磁盘占用分析
- **模型权重**: ~3GB+ (LatentSync UNet + Whisper + VAE)
- **临时视频/音频**: 下载的输入文件
- **中间处理文件**: 视频帧提取、面部检测结果
- **输出视频**: 生成的最终结果
- **免费计划限制**: 磁盘配额有限

### 尝试的解决方案

#### 1. 添加Volume配置 (已实施)
```toml
[cerebrium.volumes]
persistent-storage = "/persistent-storage"
```

#### 2. 修改代码使用Persistent Storage (已实施)
- 将模型权重存储路径改为 `/persistent-storage/latentsync/checkpoints/`
- 将缓存文件存储到persistent storage

### 当前状态

虽然已添加volume配置并更新代码，但仍然遇到磁盘配额问题。这可能是因为:

1. **免费计划限制**: Volume功能可能不在免费计划中
2. **Volume未激活**: 需要通过Cerebrium dashboard手动创建volume
3. **运行时磁盘限制**: 即使有volume，运行时的临时磁盘空间仍然受限

## 推荐解决方案

### 方案 1: 升级Cerebrium计划 ⭐ (推荐)
- 升级到付费计划以获得更大磁盘配额
- 可以使用persistent volumes
- 联系: https://cerebrium.ai/pricing

### 方案 2: 优化代码减少磁盘使用
```python
# 1. 使用流式处理
- 边下载边处理，不保存完整文件
- 使用内存流而非磁盘文件

# 2. 及时清理
- 处理完每一帧立即删除
- 使用 with 语句确保资源释放

# 3. 压缩中间结果
- 使用更低的视频质量进行中间处理
- 只保留必要的数据
```

### 方案 3: 使用更小的模型
```toml
# 使用256x256而非512x512分辨率
# 修改 cerebrium.toml
# 修改 main.py 使用 stage2.yaml 而非 stage2_512.yaml
```

### 方案 4: 分阶段处理
- 将长视频分段处理
- 每次只处理几秒钟的内容
- 最后合并结果

## 已实现的优化

✅ 模型权重存储到persistent storage (如果可用)
✅ 自动检测persistent storage可用性
✅ fallback到当前目录（如果volume不可用）

## 下一步行动

1. **联系Cerebrium支持**: 询问volume功能和磁盘配额
2. **切换到256分辨率**: 减少资源需求
3. **升级计划**: 获得更大的磁盘空间和计算资源

## 代码更改记录

### cerebrium.toml
```toml
[cerebrium.volumes]
persistent-storage = "/persistent-storage"
```

### main.py
```python
PERSISTENT_ROOT = Path("/persistent-storage")
if PERSISTENT_ROOT.exists() and os.access(PERSISTENT_ROOT, os.W_OK):
    STORAGE_BASE = PERSISTENT_ROOT / "latentsync"
else:
    STORAGE_BASE = Path.cwd()
```

## 测试结果

```json
{
  "run_id": "cbc38a91-2b53-9ee2-8f6d-88bba091dc1d",
  "result": {
    "error": "[Errno 122] Disk quota exceeded"
  },
  "run_time_ms": 903.39
}
```

应用成功启动并开始处理，但在模型加载或文件处理阶段遇到磁盘限制。
