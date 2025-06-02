from flask import Flask, jsonify, request
import mysql.connector
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})  # ✅ 加這行
app.json.ensure_ascii = False

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'example'),
        database=os.environ.get('DB_NAME', 'testdb'),
        charset='utf8mb4'
    )

@app.route('/questionnaire', methods=['GET'])
def get_current_questionnaire():
    category = 1
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        # 如果有指定分类，则查询该分类的问卷
        cursor.execute("SELECT title FROM Questionnaires WHERE category_id = %s", (category,))
        questions = cursor.fetchall()
        if not questions:
            return jsonify({'error': '找不到問卷'}), 404
        return jsonify({'status': 'success', 'questionnaires': questions}), 200
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/questionnaire/submit', methods=['POST'])
def submit_questionnaire():
    data = request.get_json()
    if not data or not data.get('score') or not data.get('user_id'):
        return jsonify({'error': '缺少必要資料'}), 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        user_id = data['user_id']
        score = data['score']
        category_id = 1

        cursor.execute("SELECT * FROM TeaPersonalityTypes WHERE min_score <= %s AND max_score >= %s", (score, score))
        tea_type = cursor.fetchone()
        if not tea_type:
            return jsonify({'error': '無法配對茶型'}), 404

        tea_type_id = tea_type['tea_type_id']

        cursor.execute("INSERT INTO QuestionnaireResponses (user_id, category_id, tea_type_id, score) VALUES (%s, %s, %s, %s)",
                       (user_id, category_id, tea_type_id, score))
        conn.commit()

        return jsonify({
            'message': '問卷提交成功',
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

@app.route('/questionnaire/personality/<int:user_id>', methods=['GET'])
def get_user_personality(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT T.tea_type_id, T.name, T.description, T.image_url
            FROM QuestionnaireResponses Q
            JOIN TeaPersonalityTypes T ON Q.tea_type_id = T.tea_type_id
            WHERE Q.user_id = %s
            ORDER BY Q.submitted_at DESC
            LIMIT 1
        """, (user_id,))
        result = cursor.fetchone()
        if not result:
            return jsonify({'error': '查無結果'}), 404
        return jsonify({'tea_type': result})
    except mysql.connector.Error as e:
        return jsonify({'error': str(e)}), 500
    finally:
        cursor.close()
        conn.close()

# ✅ 只留一個 port: 5002
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
