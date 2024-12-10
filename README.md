# reTerminal-PhotoFrame
A minimalist digital photo frame application built with Flask for reTerminal, supporting photo slideshow, touch control and remote upload.

## Features
- Full-screen photo display with smooth transitions
- Touch-based navigation (swipe left/right)
- Automatic slideshow with configurable interval
- Web-based admin interface for photo management
- Support for JPG, PNG, and GIF formats
- Natural file name sorting
- Responsive design optimized for reTerminal display

## 功能特点
- 全屏照片展示，支持自动轮播
- 触控操作：左右滑动切换照片
- 自动适配屏幕尺寸
- 平滑过渡动画效果
- 支持远程管理：上传、删除照片
- 实时更新：配置修改和照片变更立即生效
- 支持常见图片格式（JPG/PNG/GIF）

## Installation
1. 克隆仓库：
```bash
git clone https://github.com/yourusername/reTerminal-PhotoFrame.git
cd reTerminal-PhotoFrame
```

2. 安装依赖：
```bash
pip install -r requirements.txt
pip install gunicorn  # 用于生产环境部署
```

3. 设置开机自启：
```bash
# 复制服务文件到系统目录
sudo cp photoframe.service /etc/systemd/system/
# 重载服务配置
sudo systemctl daemon-reload
# 启用服务
sudo systemctl enable photoframe
```

## Usage
1. Start the application:
```bash
python app.py
```

2. Access the interfaces:
- Photo Frame Display: `http://localhost:5000`
- Admin Interface: `http://localhost:5000/admin`

## 使用方法

### 控制命令
使用 `control.sh` 脚本控制相册：
```bash
./control.sh start   # 启动相册
./control.sh stop    # 停止相册
./control.sh restart # 重启相册
./control.sh status  # 查看状态
```

### 访问地址
- 照片展示界面：`http://localhost:5000`
- 管理界面：`http://localhost:5000/admin`
- 局域网访问：将 localhost 替换为树莓派IP地址

## Configuration
- Default slideshow interval: 5 seconds
- Slideshow state: Enabled by default
- All configurations can be changed through the admin interface

## 配置说明
- 轮播间隔：默认5秒，可在管理界面调整
- 轮播状态：默认开启，可在管理界面控制
- 支持格式：JPG、PNG、GIF
- 照片排序：按文件名自然排序

## Directory Structure
```
reTerminal-PhotoFrame/
├── app.py              # Main application file
├── requirements.txt    # Python dependencies
├── start.sh           # 启动脚本
├── control.sh         # 控制脚本
├── photoframe.service # 系统服务配置
├── static/
│   └── photos/        # Photo storage directory
└── templates/
    ├── index.html     # Photo frame display template
    └── admin.html     # Admin interface template

```

## 注意事项
1. 确保photos目录具有正确的读写权限
2. 建议使用Chrome/Chromium浏览器获得最佳体验
3. 上传大量照片时可能需要等待较长时间
4. 建议照片分辨率不超过4K以获得最佳性能
