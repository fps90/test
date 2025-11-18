import asyncio
import random
import string
import re
import os
import threading
from telethon import TelegramClient, events
from telethon.tl.functions.contacts import ResolveUsernameRequest
from telethon.errors import UsernameNotOccupiedError, UsernameInvalidError
from flask import Flask

# --- إعدادات الخادم والبوت ---
API_ID = 26372231
API_HASH = "22bb44b8bd17877fc9ac062532a0d26e"
BOT_TOKEN = "8234331423:AAHztPNXzTSP8VcqAj2xaydcMras3IEjBvQ"

# --- إعداد خادم Flask لفحص الصحة ---
app = Flask(__name__)

@app.route('/')
def health_check():
    """هذه هي نقطة النهاية التي سترد على فحص الصحة."""
    return "Bot is alive and running!", 200

def run_flask_app():
    """تشغيل خادم Flask في خيط منفصل."""
    # الحصول على المنفذ من متغيرات البيئة، مع قيمة افتراضية 8000
    port = int(os.environ.get("PORT", 8000))
    # الاستماع على 0.0.0.0 ليكون متاحًا من خارج الحاوية
    app.run(host='0.0.0.0', port=port)

# --- إعداد بوت تليجرام ---
tele_client = TelegramClient("botyee", API_ID, API_HASH)
user_states = {}

# --- دوال البوت (تبقى كما هي) ---
@tele_client.on(events.NewMessage(pattern=r'^/start$'))
async def start_handler(event):
    await event.reply("أهلًا بك في بوت فحص وتوليد اليوزرات\n\n-  الأمر /generation لتوليد يوزرات .\n- الأمر /check لفحص اليوزر .")
    
def generate_username_by_pattern(pattern):
    letters = string.ascii_lowercase
    digits = string.digits
    all_chars = letters + digits
    result = ""
    char_map = {}

    for i, char in enumerate(pattern):
        if char == '_':
            result += '_'
            continue
        if char not in char_map:
            if i == 0:
                char_map[char] = random.choice(letters)
            else:
                char_map[char] = random.choice(all_chars)
        result += char_map[char]

    return '@' + result

def generate_usernames_by_pattern(pattern, count):
    usernames = set()
    while len(usernames) < count:
        usernames.add(generate_username_by_pattern(pattern))
    return list(usernames)

@tele_client.on(events.NewMessage(pattern=r'^/generation'))
async def handle_generation(event):
    raw_text = event.raw_text
    parts = raw_text.split()
    if len(parts) != 2 or not re.match(r"^@[\w_]{3,}$", parts[1]):
        await event.reply("أرسل الأمر بهذا الشكل:\n/generation @a_7_k أو @vvcvv")
        return
    username_pattern = parts[1][1:] 
    user_states[event.sender_id] = username_pattern
    await event.reply("شكد عدد اليوزرات اللي تريد توليدها؟")

@tele_client.on(events.NewMessage(pattern=r'^\d+$'))
async def handle_count(event):
    user_id = event.sender_id
    pattern = user_states.get(user_id)
    if pattern:
        try:
            count = int(event.raw_text)
            if count > 100:
                await event.reply("الحد الأقصى للتوليد هو 100.")
                return
            usernames = generate_usernames_by_pattern(pattern, count)
            await event.reply("\n".join(usernames))
        except ValueError:
            await event.reply("أرسل رقم فقط.")
        user_states.pop(user_id, None)

@tele_client.on(events.NewMessage(pattern=r'^/check'))
async def check_handler(event):
    raw_text = event.raw_text
    usernames = re.findall(r'@[\w_]{3,}', raw_text)
    if not usernames:
        await event.reply("أرسل الأمر بهذا الشكل:\n/check @username\nأو أرسل قائمة يوزرات بعد الأمر.")
        return

    results = []
    for username in usernames:
        uname = username.replace('@', '')
        try:
            result = await tele_client(ResolveUsernameRequest(uname))
            peer = result.users[0] if result.users else result.chats[0]
            if hasattr(peer, 'first_name'):
                status = "ربط حساب"
            elif hasattr(peer, 'title'):
                if peer.broadcast:
                    status = "ربط قناة"
                else:
                    status = "ربط كروب"
            else:
                status = "مربوط - نوع غير معروف"
        except UsernameNotOccupiedError:
            status = "متاح"
        except UsernameInvalidError:
            status = "مبند(منصة)"
        except Exception as e:
            status = f"خطأ: {str(e)}"

        results.append(f"- {username} - ➤ {status}")
        await asyncio.sleep(3)  

    await event.reply("\n".join(results[:50]))

# --- الدالة الرئيسية المعدلة ---
async def main():
    """الدالة الرئيسية التي تشغل البوت."""
    await tele_client.start(bot_token=BOT_TOKEN)
    print("Bot has started successfully!")
    await tele_client.run_until_disconnected()

if __name__ == "__main__":
    # 1. تشغيل خادم Flask في خيط منفصل
    print("Starting Flask server for health checks...")
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True  # يسمح للبرنامج بالخروج حتى لو كان الخيط يعمل
    flask_thread.start()

    # 2. تشغيل بوت Telethon في الخيط الرئيسي
    print("Starting Telethon bot...")
    # يستخدم loop موجود بالفعل إذا كان متوفرًا
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())

async def main():
    await tele_client.start(bot_token=BOT_TOKEN)
    await tele_client.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
