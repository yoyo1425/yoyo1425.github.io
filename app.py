from flask import Flask, request, jsonify, send_from_directory
import sqlite3
import time
from datetime import datetime

app = Flask(__name__, static_folder='static')

# ---------- 初始化数据库 ----------
def init_db():
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp INTEGER NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# ---------- API 接口 ----------
@app.route('/api/messages', methods=['GET'])
def get_messages():
    """获取所有留言（按时间倒序）"""
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('SELECT name, content, timestamp FROM messages ORDER BY timestamp DESC')
    rows = c.fetchall()
    conn.close()
    messages = [{'name': row[0], 'content': row[1], 'timestamp': row[2]} for row in rows]
    return jsonify(messages)

@app.route('/api/messages', methods=['POST'])
def add_message():
    """添加一条留言"""
    data = request.get_json()
    if not data or 'content' not in data:
        return jsonify({'error': 'Missing content'}), 400
    
    name = data.get('name', '匿名').strip()[:20] or '匿名'
    content = data.get('content', '').strip()[:200]
    if not content:
        return jsonify({'error': 'Content cannot be empty'}), 400
    
    timestamp = int(time.time() * 1000)  # 毫秒级时间戳
    
    conn = sqlite3.connect('messages.db')
    c = conn.cursor()
    c.execute('INSERT INTO messages (name, content, timestamp) VALUES (?, ?, ?)',
              (name, content, timestamp))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': '留言已添加'}), 201

# ---------- 提供前端页面（可选） ----------
@app.route('/')
def index():
    return send_from_directory('static', 'index.html')

# ---------- 启动服务 ----------
if __name__ == '__main__':
    # 本地开发用固定端口，Railway 会自动注入 PORT 环境变量
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
