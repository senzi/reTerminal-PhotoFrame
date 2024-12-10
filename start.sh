#!/bin/bash

# 检查并杀死已存在的进程
pkill -f gunicorn
pkill -f chromium

# 切换到项目目录
cd /home/pi/Git_Project/reTerminal-PhotoFrame

# 定义可能的gunicorn路径
GUNICORN_PATHS=(
    "/home/pi/.local/bin/gunicorn"  # pip install --user 安装的路径
    "/usr/local/bin/gunicorn"       # pip install 安装的标准路径
    "/usr/bin/gunicorn"             # 系统包管理器安装的路径
)

# 查找可用的gunicorn
GUNICORN_PATH=""
for path in "${GUNICORN_PATHS[@]}"; do
    if [ -x "$path" ]; then
        GUNICORN_PATH="$path"
        break
    fi
done

# 如果没有找到gunicorn，尝试使用PATH中的gunicorn
if [ -z "$GUNICORN_PATH" ]; then
    if command -v gunicorn >/dev/null 2>&1; then
        GUNICORN_PATH="gunicorn"
    else
        echo "Error: gunicorn not found"
        exit 1
    fi
fi

# 启动gunicorn
$GUNICORN_PATH -w 4 -b 0.0.0.0:5000 app:app -D

# 等待gunicorn启动
sleep 2

# 启动浏览器
DISPLAY=:0 chromium-browser --start-fullscreen --app=http://localhost:5000