from flask import Flask, jsonify, request
import mysql.connector
import os
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  


app.json.ensure_ascii = False

def get_db_connection():
    return mysql.connector.connect(
        host=os.environ.get('DB_HOST', 'db'),
        user=os.environ.get('DB_USER', 'root'),
        password=os.environ.get('DB_PASSWORD', 'example'),
        database=os.environ.get('DB_NAME', 'testdb'),
        charset='utf8mb4',
        buffered=True  # ⭐ 加這個
    )

@app.route('/missions/recommend/<int:user_id>', methods=['GET'])
def recommend_missions(user_id):
    conn = get_db_connection()
    try:
        with conn.cursor(dictionary=True) as cursor1:
            cursor1.execute("""
                SELECT tea_type_id FROM QuestionnaireResponses
                WHERE user_id = %s
                ORDER BY submitted_at DESC LIMIT 1
            """, (user_id,))
            result = cursor1.fetchone()

        if not result:
            return jsonify({'error': '無人格紀錄'}), 404

        tea_type_id = result['tea_type_id']

        with conn.cursor(dictionary=True) as cursor2:
            cursor2.execute("""
                SELECT M.mission_id, M.title, M.type
                FROM Missions M
                WHERE M.tea_type_id = %s
            """, (tea_type_id,))
            missions = cursor2.fetchall()

        mission_list = []
        for mission in missions:
            mission_id = mission['mission_id']

            with conn.cursor(dictionary=True) as cursor3:
                cursor3.execute("""
                    SELECT user_mission_id FROM UserMissions
                    WHERE user_id = %s AND mission_id = %s
                """, (user_id, mission_id))
                is_completed = cursor3.fetchone() is not None

            with conn.cursor(dictionary=True) as cursor4:
                cursor4.execute("""
                    SELECT C.code, C.description
                    FROM MissionCoupons MC
                    JOIN Coupons C ON MC.coupon_id = C.coupon_id
                    WHERE MC.mission_id = %s AND MC.trigger_condition = 'on_complete'
                """, (mission_id,))
                coupon = cursor4.fetchone()

            mission_list.append({
                'mission_id': mission_id,
                'title': mission['title'],
                'type': mission['type'],
                'is_completed': is_completed,
                'coupon': coupon
            })

        return jsonify({
            'tea_type_id': tea_type_id,
            'missions': mission_list
        })

    except mysql.connector.Error as e:
        print("🔥 MySQL 錯誤：", e)
        return jsonify({'error': '資料庫錯誤', 'detail': str(e)}), 500
    finally:
        conn.close()



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5003)

