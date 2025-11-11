#!/bin/bash

################################################################################
#                                                                              #
#                    🚀 快速一键重新部署脚本                                   #
#                                                                              #
#  如果应用被意外删除，运行此脚本可以在 5-8 分钟内重新部署                    #
#                                                                              #
################################################################################

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 函数：打印带颜色的日志
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# 打印标题
clear
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                                                                ║"
echo "║              🚀 Wan2.2 TI2V 快速重新部署脚本                   ║"
echo "║                                                                ║"
echo "║  应用名称: wan22-ti2v                                         ║"
echo "║  项目 ID:  p-194bc83f                                         ║"
echo "║  GPU:      ADA L40 (48 GB)                                    ║"
echo "║                                                                ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# 检查凭据
log_info "检查部署凭据..."

if [ -z "$CEREBRIUM_SERVICE_ACCOUNT_TOKEN" ] && [ -z "$CEREBRIUM_API_KEY" ]; then
    log_error "未找到认证凭据！"
    echo ""
    echo "请设置以下其中一个环境变量:"
    echo ""
    echo "  选项 1: Service Account Token (推荐)"
    echo "    export CEREBRIUM_SERVICE_ACCOUNT_TOKEN='your-token'"
    echo ""
    echo "  选项 2: API Key"
    echo "    export CEREBRIUM_API_KEY='your-key'"
    echo ""
    echo "  选项 3: .env 文件"
    echo "    echo 'CEREBRIUM_SERVICE_ACCOUNT_TOKEN=your-token' > cerebrium/.env"
    echo ""
    exit 1
fi

if [ -n "$CEREBRIUM_SERVICE_ACCOUNT_TOKEN" ]; then
    log_success "找到 Service Account Token"
    TOKEN_TYPE="Service Account Token"
elif [ -n "$CEREBRIUM_API_KEY" ]; then
    log_success "找到 API Key"
    TOKEN_TYPE="API Key"
fi

echo ""

# 进入项目目录
log_info "进入项目目录..."
cd "$(dirname "$0")/cerebrium"
log_success "当前目录: $(pwd)"
echo ""

# 检查必要的文件
log_info "检查必要的文件..."
if [ ! -f "cerebrium.toml" ]; then
    log_error "找不到 cerebrium.toml 配置文件"
    exit 1
fi
log_success "配置文件存在"

if [ ! -f "main.py" ]; then
    log_error "找不到 main.py 入口文件"
    exit 1
fi
log_success "入口文件存在"
echo ""

# 安装 Cerebrium CLI
log_info "安装/更新 Cerebrium CLI..."
pip install --upgrade cerebrium --break-system-packages -q > /dev/null 2>&1
log_success "Cerebrium CLI 已就绪"
echo ""

# 验证 CLI
log_info "验证 Cerebrium CLI..."
if ! command -v cerebrium &> /dev/null; then
    log_error "Cerebrium CLI 安装失败"
    exit 1
fi
cli_version=$(cerebrium --version 2>/dev/null || echo "unknown")
log_success "CLI 版本: $cli_version"
echo ""

# 显示部署信息
echo "📊 部署信息:"
echo "  ├─ 应用名称: wan22-ti2v"
echo "  ├─ GPU: ADA L40 (48 GB)"
echo "  ├─ CPU: 11 cores"
echo "  ├─ Python: 3.11"
echo "  └─ 认证方式: $TOKEN_TYPE"
echo ""

# 确认部署
log_warning "将开始部署应用，这需要 5-8 分钟"
echo ""
read -p "确认继续部署? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    log_info "已取消"
    exit 0
fi

echo ""
log_info "开始部署..."
echo "═════════════════════════════════════════════════════════════"
echo ""

# 执行部署
start_time=$(date +%s)

if cerebrium deploy --disable-syntax-check -y; then
    end_time=$(date +%s)
    duration=$((end_time - start_time))
    
    echo ""
    echo "═════════════════════════════════════════════════════════════"
    echo ""
    
    log_success "部署成功！"
    echo ""
    
    # 显示部署信息
    echo "📊 部署完成信息:"
    echo "  ├─ 耗时: ${duration} 秒 (~$((duration / 60)) 分 $((duration % 60)) 秒)"
    echo "  ├─ 应用名: wan22-ti2v"
    echo "  ├─ 状态: 🟢 Live"
    echo "  └─ 项目 ID: p-194bc83f"
    echo ""
    
    # 显示 API 端点
    echo "🔌 API 端点:"
    echo "  https://api.aws.us-east-1.cerebrium.ai/v4/p-194bc83f/wan22-ti2v/predict"
    echo ""
    
    # 显示仪表板
    echo "📈 仪表板:"
    echo "  https://dashboard.cerebrium.ai/projects/p-194bc83f/apps/p-194bc83f-wan22-ti2v"
    echo ""
    
    # 下一步建议
    echo "💡 下一步:"
    echo "  1. 访问仪表板查看应用状态"
    echo "  2. 测试 API 端点"
    echo "  3. 使用 Web UI: open ../index.html"
    echo "  4. 使用 Python 脚本: python3 ../test_inference.py"
    echo ""
    
    log_success "重新部署完成！"
    exit 0
else
    echo ""
    echo "═════════════════════════════════════════════════════════════"
    echo ""
    log_error "部署失败！"
    echo ""
    echo "💡 故障排除:"
    echo "  1. 检查网络连接"
    echo "  2. 验证 API Key/Token"
    echo "  3. 查看日志输出以了解详细错误"
    echo ""
    exit 1
fi
