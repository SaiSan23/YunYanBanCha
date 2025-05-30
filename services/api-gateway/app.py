from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # 啟用跨域資源共享

# 服務地址
OTHER_SERVICE_URL = 'http://other-service:5000'
AUTH_SERVICE_URL = 'http://auth-service:5000'
SURVEY_SERVICE_URL = 'http://survey-service:5002'

# 時間服務路由
@app.route('/api/time')
def get_time():
    # 轉發請求到時間服務
    response = requests.get(f'{OTHER_SERVICE_URL}/time')
    return jsonify(response.json())

# 註冊路由
@app.route('/api/auth/register', methods=['POST'])
def register():
    # 轉發請求到認證服務
    response = requests.post(f'{AUTH_SERVICE_URL}/register', json=request.get_json())
    return jsonify(response.json()), response.status_code

# 登入路由
@app.route('/api/auth/login', methods=['POST'])
def login():
    # 轉發請求到認證服務
    response = requests.post(f'{AUTH_SERVICE_URL}/login', json=request.get_json())
    return jsonify(response.json()), response.status_code

# 驗證令牌路由
@app.route('/api/auth/verify-token', methods=['POST'])
def verify_token():
    # 轉發請求到認證服務
    response = requests.post(f'{AUTH_SERVICE_URL}/verify-token', json=request.get_json())
    return jsonify(response.json()), response.status_code

# 獲取問卷題目路由
@app.route('/api/questionnaire', methods=['GET'])
def get_current_questionnaire():
    # 轉發請求到問卷服務
    response = requests.get(f'{SURVEY_SERVICE_URL}/questionnaire')
    return jsonify(response.json())

# 問卷提交路由
@app.route('/api/questionnaire/submit', methods=['POST'])
def submit_survey():
    # 獲取授權令牌
    auth_header = request.headers.get('Authorization')
    token = None
    user_info = None
    
    # 如果有授權令牌，驗證用戶身份
    if auth_header and auth_header.startswith('Bearer '):
        token = auth_header.split(' ')[1]
        # 驗證令牌
        verify_response = requests.post(
            f'{AUTH_SERVICE_URL}/verify-token',  # 修正這裡的URL變數
            json={'token': token}
        )
        
        if verify_response.status_code == 200:
            user_info = verify_response.json()
    
    # 獲取問卷數據
    survey_data = request.get_json()
    
    # 如果用戶已登入，將用戶信息添加到問卷數據中
    if user_info and user_info.get('valid'):
        survey_data['user_id'] = user_info.get('user_id')
        survey_data['username'] = user_info.get('username')
    
    # 轉發請求到問卷服務
    response = requests.post(
        f'{SURVEY_SERVICE_URL}/questionnaire/submit',
        json=survey_data
    )
    
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)