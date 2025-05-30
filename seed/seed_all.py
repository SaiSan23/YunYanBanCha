import pymysql
from datetime import date, datetime
import time

DB_CONFIG = dict(
    host='db',
    port=3306,
    user='root',
    password='example',
    database='testdb',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.Cursor
)

def get_conn(retries=20, delay=3):
    """重試連線直到 MySQL 可用，或超過次數報錯。"""
    for i in range(retries):
        try:
            conn = pymysql.connect(**DB_CONFIG)
            return conn
        except pymysql.MySQLError:
            print(f"⚠️ 連線失敗，{delay}秒後重試 ({i+1}/{retries})…")
            time.sleep(delay)
    raise RuntimeError("無法連線到 MySQL，請檢查 db 容器是否啟動")

def seed_users(cur):
    users = [
        ('alice@example.com','pwd1','Alice'),
        ('bob@example.com','pwd2','Bob'),
    ]
    cur.executemany(
        "INSERT INTO Users (email,password,name) VALUES (%s,%s,%s)",
        users
    )
    print("✅ Users seeded")

def seed_category(cur):
    cats = [
        ('SPR','Spring','春季活動',3,5),
        ('SUM','Summer','夏季活動',6,8),
        ('AUT','Autumn','秋季活動',9,11),
        ('WIN','Winter','冬季活動',12,2),
    ]
    cur.executemany(
        "INSERT INTO Category (code,name,description,start_month,end_month) VALUES (%s,%s,%s,%s,%s)",
        cats
    )
    print("✅ Category seeded")

def seed_shops(cur):
    shops = [('雲南茶舖',),('南投茶行',)]
    cur.executemany("INSERT INTO Shops (name) VALUES (%s)", shops)
    print("✅ Shops seeded")

def seed_tea_types(cur):
    pts = [
        ('GREEN','綠茶型','清新自然','/img/green.png',0,20),
        ('BLACK','紅茶型','熱情沉穩','/img/black.png',21,40),
    ]
    cur.executemany(
        "INSERT INTO TeaPersonalityTypes (code,name,description,image_url,min_score,max_score) "
        "VALUES (%s,%s,%s,%s,%s,%s)",
        pts
    )
    print("✅ TeaPersonalityTypes seeded")

def seed_questionnaires(cur):
    questions = []
    texts = {
        1: [
            '您喜歡在春季到茶園賞花嗎？',
            '您常在春季飲用綠茶嗎？',
            '您認為春茶香氣如何？',
            '春季您喜歡哪款茶點？'
        ],
        2: [
            '夏季您喜歡冰鎮茶還是熱茶？',
            '您在夏季嘗試過水果茶嗎？',
            '夏季到茶店消暑首選？',
            '您參加過夏季茶園活動嗎？'
        ],
        3: [
            '秋季您偏好哪種烏龍茶？',
            '您在秋季感受過茶香沉穩嗎？',
            '秋季賞茶時搭配何種小吃？',
            '秋茶與其他季茶有何不同？'
        ],
        4: [
            '冬季您喜歡哪種暖身茶？',
            '您常在冬季以茶取暖嗎？',
            '冬季喝茶：甜味還是微苦？',
            '您品味過普洱生熟茶嗎？'
        ]
    }
    for cid, arr in texts.items():
        for txt in arr:
            questions.append((cid, txt))
    cur.executemany(
        "INSERT INTO Questionnaires (category_id,title) VALUES (%s,%s)",
        questions
    )
    print("✅ Questionnaires seeded")

def seed_missions(cur):
    cur.execute("SELECT tea_type_id, name FROM TeaPersonalityTypes")
    tea_types = cur.fetchall()
    missions = []
    for tid, name in tea_types:
        for i in range(1, 4):
            missions.append((tid, f"拍照打卡：與{name}合影第{i}次", '拍照打卡'))
        for i in range(1, 3):
            missions.append((tid, f"餐飲體驗：品嚐{name}特色飲品第{i}款", '餐飲'))
    cur.executemany(
        "INSERT INTO Missions (tea_type_id,title,type) VALUES (%s,%s,%s)",
        missions
    )
    print(f"✅ Missions seeded ({len(missions)} rows)")

def seed_coupons(cur):
    coupons = [
        (1,'SPR10','折扣','春季優惠10%', date(2025,3,1), date(2025,5,31)),
        (2,'SUM15','折扣','夏季優惠15%', date(2025,6,1), date(2025,8,31)),
    ]
    cur.executemany(
        "INSERT INTO Coupons (shop_id,code,type,description,start_date,end_date) VALUES (%s,%s,%s,%s,%s,%s)",
        coupons
    )
    print("✅ Coupons seeded")

def seed_mission_coupons(cur):
    mc = []
    cur.execute("SELECT mission_id,type FROM Missions")
    for mid, t in cur.fetchall():
        if t == '餐飲':
            mc.append((mid,1,'on_complete'))
            mc.append((mid,2,'on_complete'))
    cur.executemany(
        "INSERT INTO MissionCoupons (mission_id,coupon_id,trigger_condition) VALUES (%s,%s,%s)",
        mc
    )
    print("✅ MissionCoupons seeded")

def seed_questionnaire_responses(cur):
    resp = [
        (1,1,1, 15),
        (2,2,2, 30),
    ]
    cur.executemany(
        "INSERT INTO QuestionnaireResponses (user_id,category_id,tea_type_id,score) VALUES (%s,%s,%s,%s)",
        resp
    )
    print("✅ QuestionnaireResponses seeded")

def seed_user_missions(cur):
    cur.execute("SELECT mission_id FROM Missions LIMIT 4")
    mids = [r[0] for r in cur.fetchall()]
    ums = [
        (1,mids[0],'scanned_qr', datetime.now()),
        (2,mids[1],'scanned_qr', datetime.now())
    ]
    cur.executemany(
        "INSERT INTO UserMissions (user_id,mission_id,trigger_event,trigger_time) VALUES (%s,%s,%s,%s)",
        ums
    )
    print("✅ UserMissions seeded")

def main():
    conn = get_conn()
    try:
        with conn.cursor() as cur:
            seed_users(cur)
            seed_category(cur)
            seed_shops(cur)
            seed_tea_types(cur)
            seed_questionnaires(cur)
            seed_missions(cur)
            seed_coupons(cur)
            seed_mission_coupons(cur)
            seed_questionnaire_responses(cur)
            seed_user_missions(cur)
        conn.commit()
    finally:
        conn.close()

if __name__ == '__main__':
    main()
