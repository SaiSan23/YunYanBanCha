# 使用輕量版的 Python 環境作為基底映像
FROM python:3.8-slim

# 設定容器內部的工作目錄
WORKDIR /app

# 複製當前資料夾下所有檔案到容器內
COPY . .

# 安裝 Python 依賴套件
RUN pip install --no-cache-dir -r requirements.txt

# 開放 Flask 預設 port
EXPOSE 5000

# 啟動 Flask 應用
CMD ["python", "app.py"]
