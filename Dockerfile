FROM python:3.10-slim

# نثبت المتطلبات
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# ننسخ الكود
COPY . /app

# <-- أضف هذا السطر هنا
# استبدل 8000 بالمنفذ الصحيح الذي يستخدمه تطبيقك
EXPOSE 8000

# الأمر اللي يشغّل البوت
CMD ["python", "main.py"]
