from flask import Flask, request, jsonify
from flask_cors import CORS
import mysql.connector
import bcrypt
import jwt
import datetime
import os
import json

app = Flask(__name__)
CORS(app)  # 啟用跨域資源共享

# JWT密鑰，實際應用中應該使用環境變量或配置文件
SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your_secret_key')

# 資料庫連接函數
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'example'),
        database=os.environ.get('DB_NAME', 'testdb')
    )

# 註冊路由
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    
    # 檢查必要欄位
    if not data or not data.get('username') or not data.get('password') or not data.get('email'):
        return jsonify({'error': '用戶名、密碼和電子郵件為必填項'}), 400
    
    username = data.get('username')
    password = data.get('password')
    email = data.get('email')
    
    # 密碼加密
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 檢查信箱是否已存在
        cursor.execute("SELECT user_id FROM Users WHERE email = %s", (email,))
        if cursor.fetchone():
            return jsonify({'error': '信箱已存在'}), 409
        
        # 插入新用戶
        cursor.execute(
            "INSERT INTO Users (name, password, email) VALUES (%s, %s, %s)",
            (username, hashed_password, email)
        )
        conn.commit()
        
        return jsonify({'message': '註冊成功'}), 201
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

# 登入路由
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    
    # 檢查必要欄位
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': '電子郵件和密碼為必填項'}), 400
    
    email = data.get('email')
    password = data.get('password')
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 查詢用戶
        cursor.execute("SELECT user_id, name, password FROM Users WHERE email = %s", (email,))
        user = cursor.fetchone()
        
        if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return jsonify({'error': '電子郵件或密碼錯誤'}), 401
        
        # 生成JWT令牌
        token = jwt.encode({
            'user_id': user['user_id'],
            'username': user['name'],
            'exp': datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=24)
        }, SECRET_KEY, algorithm='HS256')
        
        return jsonify({
            'message': '登入成功',
            'token': token,
            'username': user['name']
        }), 200
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

# 驗證令牌的路由
@app.route('/verify-token', methods=['POST'])
def verify_token():
    data = request.get_json()
    
    if not data or not data.get('token'):
        return jsonify({'error': '令牌為必填項'}), 400
    
    token = data.get('token')
    
    try:
        # 驗證令牌
        payload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        return jsonify({
            'valid': True,
            'user_id': payload['user_id'],
            'username': payload['username']
        }), 200
    
    except jwt.ExpiredSignatureError:
        return jsonify({'valid': False, 'error': '令牌已過期'}), 401
    
    except jwt.InvalidTokenError:
        return jsonify({'valid': False, 'error': '無效的令牌'}), 401

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)