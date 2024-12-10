import os
from flask import Flask, render_template, request, jsonify, send_from_directory, url_for
from werkzeug.utils import secure_filename
from natsort import natsorted
import json
from PIL import Image
import hashlib
import time

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/photos')
app.config['THUMBNAIL_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static/thumbnails')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.config['THUMBNAIL_SIZE'] = (200, 200)  # 缩略图尺寸

# 确保上传和缩略图文件夹存在
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['THUMBNAIL_FOLDER'], exist_ok=True)

# 默认配置
CONFIG_FILE = 'config.json'
DEFAULT_CONFIG = {
    'slideshow_interval': 5,
    'slideshow_enabled': True
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return DEFAULT_CONFIG.copy()

def save_config(config):
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f)

def generate_thumbnail(image_path, filename):
    """生成缩略图并返回缩略图路径"""
    # 使用文件内容的hash作为缩略图名称，这样即使文件名相同，内容不同也会生成新的缩略图
    with open(image_path, 'rb') as f:
        file_hash = hashlib.md5(f.read()).hexdigest()
    
    thumbnail_filename = f"{file_hash}.jpg"
    thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], thumbnail_filename)
    
    # 如果缩略图已存在且原图未修改，直接返回
    if os.path.exists(thumbnail_path):
        if os.path.getmtime(thumbnail_path) >= os.path.getmtime(image_path):
            return thumbnail_filename
    
    try:
        with Image.open(image_path) as img:
            # 如果是动图，取第一帧
            if hasattr(img, 'is_animated') and img.is_animated:
                img.seek(0)
            
            # 创建缩略图
            img.thumbnail(app.config['THUMBNAIL_SIZE'], Image.Resampling.LANCZOS)
            
            # 创建白色背景
            bg = Image.new('RGB', app.config['THUMBNAIL_SIZE'], (255, 255, 255))
            
            # 将图片粘贴到中心位置
            offset = ((app.config['THUMBNAIL_SIZE'][0] - img.size[0]) // 2,
                     (app.config['THUMBNAIL_SIZE'][1] - img.size[1]) // 2)
            bg.paste(img, offset)
            
            # 保存缩略图
            bg.save(thumbnail_path, 'JPEG', quality=85)
            return thumbnail_filename
    except Exception as e:
        print(f"Error generating thumbnail for {filename}: {e}")
        return None

def get_photo_info(filename):
    """获取照片信息，包括缩略图路径"""
    photo_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    thumbnail = generate_thumbnail(photo_path, filename)
    return {
        'filename': filename,
        'thumbnail': thumbnail if thumbnail else filename,
        'timestamp': os.path.getmtime(photo_path)
    }

def get_photos():
    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        return []
    allowed_extensions = {'.jpg', '.jpeg', '.png', '.gif'}
    photos = [f for f in os.listdir(app.config['UPLOAD_FOLDER'])
             if os.path.splitext(f)[1].lower() in allowed_extensions]
    return natsorted(photos)

@app.route('/')
def index():
    config = load_config()
    return render_template('index.html', config=config)

@app.route('/admin')
def admin():
    config = load_config()
    photos = get_photos()
    return render_template('admin.html', photos=photos, config=config)

@app.route('/api/photos')
def list_photos():
    """获取照片列表"""
    photos = get_photos()
    return jsonify([{
        'filename': photo,
        'url': url_for('serve_photo', filename=photo, _external=True)
    } for photo in photos])

@app.route('/api/upload', methods=['POST'])
def upload_photo():
    if 'photos' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    files = request.files.getlist('photos')
    if not files or all(not file.filename for file in files):
        return jsonify({'error': 'No selected files'}), 400

    uploaded_files = []
    errors = []
    
    for file in files:
        if file and file.filename:
            try:
                filename = secure_filename(file.filename)
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(file_path)
                
                # 生成缩略图
                thumbnail = generate_thumbnail(file_path, filename)
                if thumbnail:
                    uploaded_files.append({
                        'filename': filename,
                        'thumbnail': thumbnail
                    })
                else:
                    errors.append(f"Error generating thumbnail for {filename}")
            except Exception as e:
                errors.append(f"Error uploading {file.filename}: {str(e)}")
    
    if errors:
        return jsonify({
            'message': f'Uploaded {len(uploaded_files)} files with {len(errors)} errors',
            'files': uploaded_files,
            'errors': errors
        }), 207  # 207 Multi-Status
    
    return jsonify({
        'message': f'Successfully uploaded {len(uploaded_files)} files',
        'files': uploaded_files
    })

@app.route('/api/delete/<filename>', methods=['DELETE'])
def delete_photo(filename):
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(filename))
    if os.path.exists(file_path):
        # 删除原图
        os.remove(file_path)
        
        # 尝试删除对应的缩略图
        try:
            with open(file_path, 'rb') as f:
                file_hash = hashlib.md5(f.read()).hexdigest()
            thumbnail_path = os.path.join(app.config['THUMBNAIL_FOLDER'], f"{file_hash}.jpg")
            if os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
        except:
            pass  # 如果缩略图删除失败，不影响主流程
            
        return jsonify({'message': 'File deleted successfully'})
    return jsonify({'error': 'File not found'}), 404

@app.route('/api/config', methods=['GET', 'PUT'])
def handle_config():
    if request.method == 'GET':
        return jsonify(load_config())
    
    config = load_config()
    new_config = request.json
    
    if 'slideshow_interval' in new_config:
        config['slideshow_interval'] = int(new_config['slideshow_interval'])
    if 'slideshow_enabled' in new_config:
        config['slideshow_enabled'] = bool(new_config['slideshow_enabled'])
    
    save_config(config)
    return jsonify(config)

@app.route('/static/photos/<path:filename>')
def serve_photo(filename):
    """提供照片文件"""
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/static/thumbnails/<path:filename>')
def serve_thumbnail(filename):
    """提供缩略图文件"""
    return send_from_directory(app.config['THUMBNAIL_FOLDER'], filename)

if __name__ == '__main__':
    # Initialize config file if it doesn't exist
    if not os.path.exists(CONFIG_FILE):
        save_config(DEFAULT_CONFIG)
    app.run(host='0.0.0.0', port=5000, debug=True)
