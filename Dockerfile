# 使用官方 Python 3.13 作為基礎映像檔
FROM python:3.13-slim

# 設定工作目錄
WORKDIR /app

# 設定環境變數
# PYTHONDONTWRITEBYTECODE: 防止 Python 產生 .pyc 檔案
# PYTHONUNBUFFERED: 讓 Python 輸出直接顯示（不緩衝）
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# 複製 requirements.txt 並安裝相依套件
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 複製整個專案到容器中
COPY . /app/

# 暴露 8000 port（Django 預設 port）
EXPOSE 8000

# 進入 Django 專案目錄
WORKDIR /app/calendarTW

# 啟動 Django 開發伺服器
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
