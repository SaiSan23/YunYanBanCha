from flask import Flask, jsonify
import mysql.connector

app = Flask(__name__)

@app.route('/time')
def get_time():
    # 連接資料庫
    conn = mysql.connector.connect(
        host='db',    # 使用服務名稱作為主機名
        user='root',
        password='example',
        database='testdb'
    )
    cursor = conn.cursor()
    cursor.execute("SELECT NOW()")    # 執行SQL查詢當前時間
    current_time = cursor.fetchone()[0]
    cursor.close()
    conn.close()
    return jsonify({'time': str(current_time)})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)