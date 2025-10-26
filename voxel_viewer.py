import os
import base64
import logging
import threading
import webbrowser
import requests
import argparse
import json
import datetime
import tempfile
import zipfile
from urllib.parse import urlparse
from flask import Flask, jsonify, Response, request, render_template_string, send_file

# --- 配置 ---
PORT = 5000
INPUT_DIR = "input"
CACHE_DIR = "cache"
SAVE_DIR = "saves"  # 存档目录
API_KEY_FROM_FILE = None # 用于存储从 key.txt 读取的密钥
API_KEY_VALIDATED = False # 标记来自文件的密钥是否已验证成功
DOWNLOADED_MODEL_PATH = None # 用于存储从URL下载的模型路径

# 全局变量保存AI聊天记录和状态
CHAT_HISTORY = []
AGENT_STATE = {
    "is_running": False,
    "is_paused": False,
    "current_part_index": 0,
    "overall_analysis": "",
    "model_name": "gemini-2.5-flash"
}
INITIAL_SAVE_DATA = None # 用于存储从 --input_data 加载的存档


# --- 日志设置 ---
# 配置日志记录，所有日志将输出到终端
logging.basicConfig(level=logging.INFO, format='%(asctime)s - [SERVER] - %(levelname)s - %(message)s')

# --- Flask 应用初始化 ---
app = Flask(__name__)
# 禁用 Flask 的默认启动信息，以保持终端输出整洁
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# --- 后端核心功能 ---

def find_first_file(directory, extensions):
    """在指定目录中查找第一个具有给定扩展名的文件。"""
    if not os.path.isdir(directory):
        logging.warning(f"目录 '{directory}' 不存在。")
        return None
    logging.info(f"正在扫描目录 '{directory}'，查找文件类型: {extensions}")
    # 对文件进行排序以确保每次运行结果一致
    for filename in sorted(os.listdir(directory)):
        if any(filename.lower().endswith(ext) for ext in extensions):
            path = os.path.join(directory, filename)
            logging.info(f"找到文件: {path}")
            return path
    logging.warning(f"在 '{directory}' 中未找到类型为 {extensions} 的文件。")
    return None

def read_file_as_base64(filepath):
    """读取文件并将其内容作为 Base64 编码的字符串返回。"""
    if not filepath or not os.path.exists(filepath):
        return None
    try:
        with open(filepath, "rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"无法读取文件 {filepath}: {e}")
        return None

# --- 存档功能 ---

def create_save_data(voxel_data=None, chat_history=None, agent_state=None):
    """创建存档数据结构"""
    save_data = {
        "version": "1.0",
        "timestamp": datetime.datetime.now().isoformat(),
        "voxel_data": voxel_data or {},
        "chat_history": chat_history or [],
        "agent_state": agent_state or {
            "is_running": False,
            "is_paused": False,
            "current_part_index": 0,
            "overall_analysis": "",
            "model_name": "gemini-2.5-flash"
        }
    }
    return save_data

def export_save_file(save_data):
    """导出存档文件为zip格式"""
    temp_dir = tempfile.mkdtemp()
    try:
        # 创建存档数据JSON文件
        save_json_path = os.path.join(temp_dir, "save_data.json")
        with open(save_json_path, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        # 创建zip文件
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        zip_filename = f"mine_builder_save_{timestamp}.zip"
        zip_path = os.path.join(SAVE_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(save_json_path, "save_data.json")
        
        return zip_path
    finally:
        # 清理临时目录
        if os.path.exists(temp_dir):
            import shutil
            shutil.rmtree(temp_dir)

def import_save_file(zip_path_or_url):
    """导入存档文件"""
    try:
        # 如果是URL，先下载
        if zip_path_or_url.startswith(('http://', 'https://')):
            import requests
            response = requests.get(zip_path_or_url)
            response.raise_for_status()
            
            # 保存到临时文件
            temp_zip = tempfile.NamedTemporaryFile(delete=False, suffix='.zip')
            temp_zip.write(response.content)
            temp_zip.close()
            zip_path = temp_zip.name
        else:
            zip_path = zip_path_or_url
        
        # 解压并读取存档数据
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            with zipf.open('save_data.json') as f:
                save_data = json.load(f)
        
        # 如果是临时文件，清理
        if zip_path_or_url.startswith(('http://', 'https://')):
            os.unlink(zip_path)
        
        return save_data
    except Exception as e:
        logging.error(f"导入存档失败: {e}")
        return None

# --- HTML/JavaScript 前端内容（续）---
