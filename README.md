# Web Python 測試專案

## 備註（新增跟調整功能）
1. MySQL（調整為透過 init.sql 初始化）
2. Feature：
   - 問卷

## 啟動步驟 CMD 指令
### 進入資料夾 （自己調整位置會吧）
```bash
cd desktop/web-python-test-3
```
### 部署專案到 docker（也可以背景執行：<font color=#FF6600>-d</font>）
```bash
docker compose up
```
### 停止
```bash
CTRL ＋ C
control ＋ C
docker compose stop
```
### 移除
```bash
docker compose down
docker compose down -v # 移除資料庫
```
### 觀看網頁
<http://localhost:8080>

## 專案概述
這是一個基於微服務架構的網頁應用程式，提供用戶註冊、登入和時間服務功能。專案使用 Docker 容器化技術進行部署，包含前端網頁界面和後端 API 服務。

## 系統架構
專案採用微服務架構，包含以下組件：

- 前端網頁 (Web) : 使用 HTML、CSS 和 JavaScript 構建的用戶界面
- API 網關 (API Gateway) : 處理所有外部請求並轉發到相應的服務
- 認證服務 (Auth Service) : 處理用戶註冊、登入和令牌驗證
- 時間服務 (Time Service) : 提供時間相關功能
- 資料庫 (MySQL) : 存儲用戶資料和其他應用數據

 \*\*\*（Web -> API -> 找到指定 service -> return）\*\*\*

## 技術棧
### 前端
- HTML5
- CSS3
- JavaScript (原生)
### 後端
- Python 3.8
- Flask 框架
- Flask-CORS (跨域資源共享)
- JWT (JSON Web Token) 認證：目前用在 auth-service（登入、註冊）
### 資料庫
- MySQL 8 （arm64：Mac M1, M2）
## 功能特點
- （新）問卷服務
  - 可以登入或者匿名填寫問卷
  - 匿名填寫的問卷可以暫存問卷資料
  - 註冊登入後，導向問卷，且原資料會顯示
## 開發說明
### 環境變量
認證服務使用以下環境變量：

- DB_HOST : 資料庫主機名
- DB_USER : 資料庫用戶名
- DB_PASSWORD : 資料庫密碼
- DB_NAME : 資料庫名稱
- JWT_SECRET_KEY : JWT 簽名密鑰