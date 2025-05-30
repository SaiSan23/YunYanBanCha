-- 使用者資料表
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    name VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 季節分類資料表
CREATE TABLE IF NOT EXISTS Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    description TEXT,
    start_month INT,
    end_month INT
);

-- 問卷資料表
CREATE TABLE IF NOT EXISTS Questionnaires (
    questionnaire_id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT,
    title VARCHAR(255) NOT NULL,
    FOREIGN KEY (category_id) REFERENCES Category(category_id)
);

-- 茶型人格類型資料表
CREATE TABLE IF NOT EXISTS TeaPersonalityTypes (
    tea_type_id INT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(50) NOT NULL,
    name VARCHAR(100),
    description TEXT,
    image_url TEXT,
    min_score INT,
    max_score INT
);

-- 問卷作答紀錄資料表
CREATE TABLE IF NOT EXISTS QuestionnaireResponses (
    response_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    category_id INT,
    tea_type_id INT,
    score INT,
    submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (category_id) REFERENCES Category(category_id),
    FOREIGN KEY (tea_type_id) REFERENCES TeaPersonalityTypes(tea_type_id)
);

-- 人格任務資料表
CREATE TABLE IF NOT EXISTS Missions (
    mission_id INT AUTO_INCREMENT PRIMARY KEY,
    tea_type_id INT,
    title VARCHAR(255),
    type VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (tea_type_id) REFERENCES TeaPersonalityTypes(tea_type_id)
);

-- 使用者任務紀錄資料表
CREATE TABLE IF NOT EXISTS UserMissions (
    user_mission_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    mission_id INT,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    trigger_event VARCHAR(50),
    trigger_time TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES Users(user_id),
    FOREIGN KEY (mission_id) REFERENCES Missions(mission_id)
);

-- 店家資料表
CREATE TABLE IF NOT EXISTS Shops (
    shop_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100)
);

-- 優惠券資料表
CREATE TABLE IF NOT EXISTS Coupons (
    coupon_id INT AUTO_INCREMENT PRIMARY KEY,
    shop_id INT,
    code VARCHAR(50) NOT NULL,
    type VARCHAR(50),
    description TEXT,
    start_date DATE,
    end_date DATE,
    FOREIGN KEY (shop_id) REFERENCES Shops(shop_id)
);

-- 任務與優惠券關聯資料表
CREATE TABLE IF NOT EXISTS MissionCoupons (
    mission_id INT,
    coupon_id INT,
    trigger_condition VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (mission_id, coupon_id),
    FOREIGN KEY (mission_id) REFERENCES Missions(mission_id),
    FOREIGN KEY (coupon_id) REFERENCES Coupons(coupon_id)
);