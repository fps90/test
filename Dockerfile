FROM python:3.10-slim

# نثبت المتطلبات
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ننسخ الكود
COPY . /app

# الأمر اللي يشغّل البوت
CMD ["python", "main.py"]
