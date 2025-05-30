# 🐳 Docker Compose 配置說明
此專案使用 docker compose 來協調啟動前端網頁、API Gateway 與多個後端服務。透過這個設定檔，你可以在本地快速建構並執行整個微服務架構的應用程式。

## 📦 組成服務
### 1. web（前端靜態網站）
- 基於 <font color=#00FFFF>nginx:alpine</font> 建構容器
- 將 <font color=#008000>本地的 ./web 目錄</font> 掛載至 <font color=#0000FF>容器內的 /usr/share/nginx/html</font>
- 對外開放埠號：8080（綁定 Port 容器 80）
- 相依服務：
   - api-gateway：作為 API 轉發

### 2. api-gateway（API 閘道）
- 參考 <font color=#008000>./services/api-gateway:</font> <font color=#00FFFF>dockerfile</font> 建構容器
- 綁定 Port ：主機 5001 → 容器 5000
- 負責**將前端請求轉發至其他服務**
- 相依服務：
  - auth-service
  - time-service

### 3. time-service（時間服務）
- 參考 <font color=#008000>./services/time-service:</font> <font color=#00FFFF>dockerfile</font> 建構容器
- 相依資料庫服務：db
- 使用環境變數連接資料庫：
   ```docker compose
   DB_HOST=db
   DB_USER=root
   DB_PASSWORD=example
   DB_NAME=testdb
   ```
### 4. auth-service（使用者認證服務）
- 參考 <font color=#008000>./services/auth-service:</font> <font color=#00FFFF>dockerfile</font> 建構容器
- 相依資料庫服務：db
   - 移除了 condition: service_healthy，
   因爲資料庫改成使用 init.sql 檔案初始化資料庫
- 使用環境變數：
   ```docker compose
   DB_HOST=db
   DB_USER=root
   DB_PASSWORD=example
   DB_NAME=testdb
   JWT_SECRET_KEY=your_secret_key_change_this
   ```
### 5. 資料庫服務（尚未顯示）
- 基於 <font color=#00FFFF>mysql:8</font> 建構容器（適配 Mac M1, M2）
- 設定 root 帳號與預設資料庫 testdb：
   ```
   MYSQL_ROOT_PASSWORD: example
   MYSQL_DATABASE: testdb
   ```
- 使用 Volume：
   - db-data 儲存資料庫資料
   - ./sql-init:/docker-entrypoint-initdb.d 初始化資料庫資料
- 健康檢查：
   ```
   healthcheck:          # 健康檢查：確保資料庫服務正在運行
      test: ["CMD", "mysqladmin", "ping", "-h", "localhost", "-u", "root", "-p$$MYSQL_ROOT_PASSWORD"]
                         # 執行mysqladmin ping命令，檢查資料庫服務是否正常
      interval: 5s       # 每5秒執行一次健康檢查
      timeout: 5s        # 健康檢查超時時間
      retries: 10        # 健康檢查失敗重試次數
      start_period: 60s  # 服務啟動後，等待60秒後才開始進行健康檢查
   ```

### 🌐 網路設定
- 建立了一個名為 <font color=#00FFFF>app-network</font> 的網路，用於容器之間的通訊。
   ```docker compose
   networks:
     app-network:
       driver: bridge
   ```

### 💾 Volume 設定
- 建立了一個名為 <font color=#00FFFF>db-data</font> 的 Volume，用於儲存資料庫資料。
   ```docker compose
   volumes:
     db-data:
   ```
   <font color=#0000FF>容器內 /var/lib/mysql</font> 與此 volume 綁定。