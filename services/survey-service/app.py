from flask import Flask, jsonify, request  # 添加request導入
import mysql.connector
import json
import os

app = Flask(__name__)

app.json.ensure_ascii = False

# 資料庫連接
def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'example'),
        database=os.environ.get('DB_NAME', 'testdb'),
        charset='utf8mb4'  # 指定字符集為utf8mb4，支持完整的中文和表情符號
    )

# 獲取當前的問卷
@app.route('/questionnaire', methods=['GET'])
def get_current_questionnaire():
    category = 1 # 默认分類ID
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 插入一些中文測試數據（如果表是空的）
        cursor.execute("SELECT COUNT(*) as count FROM Questionnaires")
        count = cursor.fetchone()['count']

        # 如果有指定分类，则查询该分类的问卷
        cursor.execute("SELECT title FROM Questionnaires WHERE category_id = %s", (category,))
        questionnaires = cursor.fetchall()
        
        if not questionnaires:
            return jsonify({'error': '找不到问卷或任何题目'}), 404
          
        return jsonify({
            'status': 'success',
            "questionnaires": questionnaires
        }), 200
    
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

# 提交問卷
@app.route('/questionnaire/submit', methods=['POST'])
def submit_questionnaire():
    data = request.get_json()
    
    # 檢查必要欄位
    if not data or not data.get('score'):
        return jsonify({'error': '問卷缺少必要欄位'}), 400
    
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 準備問卷數據
        user_id = data.get('user_id')
        category_id = 1  # 默認分類ID
        score = data.get('score')
        
        # 根據分數查詢對應的茶型人格
        cursor.execute(
            "SELECT * FROM TeaPersonalityTypes WHERE min_score <= %s AND max_score >= %s",
            (score, score)
        )
        tea_type = cursor.fetchone()
        
        if not tea_type:
            return jsonify({'error': '無法確定茶型人格'}), 401
        
        tea_type_id = tea_type['tea_type_id']
        
        # 插入問卷數據到QuestionnaireResponses表
        cursor.execute(
            "INSERT INTO QuestionnaireResponses (user_id, category_id, tea_type_id, score) VALUES (%s, %s, %s, %s)",
            (user_id, category_id, tea_type_id, score)
        )
        conn.commit()
        
        # 返回茶型人格結果
        return jsonify({
            'message': '問卷提交成功',
            'survey_id': cursor.lastrowid,
            'tea_type': {
                'id': tea_type['tea_type_id'],
                'code': tea_type['code'],
                'name': tea_type['name'],
                'description': tea_type['description'],
                'image_url': tea_type['image_url']
            }
        }), 201
    
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    
    finally:
        cursor.close()
        conn.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)