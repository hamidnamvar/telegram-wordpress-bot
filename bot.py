import requests
import time
import re
import os
from flask import Flask

# تنظیمات
TELEGRAM_TOKEN = '7602351049:AAHSHa1X8RgycROFqnEcxaUJBSTwDt4qcfg'
CHANNEL_USERNAME = '@sorenbam_post'
WORDPRESS_API = 'https://sorenbam.ir/wp-json/wp/v2/posts'
SENT_IDS_FILE = 'sent_ids.txt'

app = Flask(__name__)

# خواندن IDهای فرستاده‌شده
def load_sent_ids():
    if not os.path.exists(SENT_IDS_FILE):
        return set()
    with open(SENT_IDS_FILE, 'r') as file:
        return set(map(int, file.read().splitlines()))

# ذخیره ID جدید
def save_sent_id(post_id):
    with open(SENT_IDS_FILE, 'a') as file:
        file.write(f"{post_id}\n")

# گرفتن همه پست‌ها با صفحه‌بندی
def get_all_posts():
    all_posts = []
    page = 1
    while True:
        try:
            url = f"{WORDPRESS_API}?per_page=100&page={page}"
            response = requests.get(url)
            if response.status_code == 400:
                break
            response.raise_for_status()
            posts = response.json()
            if not posts:
                break
            all_posts.extend(posts)
            page += 1
        except Exception as e:
            print(f"خطا در صفحه {page}: {e}")
            break
    return all_posts

# ارسال پیام به تلگرام
def send_to_telegram(text):
    url = f'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage'
    payload = {
        'chat_id': CHANNEL_USERNAME,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': False
    }
    try:
        response = requests.post(url, data=payload)
        if response.status_code != 200:
            print(f"Telegram send error: {response.text}")
    except Exception as e:
        print(f"Error sending to Telegram: {e}")

# حلقه اصلی بات که پست‌ها رو می‌فرسته
def bot_loop():
    sent_post_ids = load_sent_ids()

    print("🔁 شروع بررسی پست‌های وردپرس...")

    while True:
        posts = get_all_posts()
        new_posts = [post for post in reversed(posts) if post['id'] not in sent_post_ids]

        for post in new_posts:
            title = post['title']['rendered']
            link = post['link']
            raw_excerpt = post.get('excerpt', {}).get('rendered', '')
            clean_excerpt = re.sub('<[^<]+?>', '', raw_excerpt).strip()
            message = f"📢 <b>{title}</b>\n\n{clean_excerpt}\n\n<a href='{link}'>📖 مشاهده مطلب در سایت</a>"

            send_to_telegram(message)
            sent_post_ids.add(post['id'])
            save_sent_id(post['id'])

            time.sleep(30)  # فاصله ارسال پست‌ها

        if not new_posts:
            time.sleep(60)  # اگر پست جدید نبود، صبر کن

# مسیر سلامت سرور
@app.route('/')
def home():
    return "بات سورن‌بام فعال است 🚀"

if __name__ == '__main__':
    import threading

    # اجرای بات در ترد جدا
    t = threading.Thread(target=bot_loop)
    t.daemon = True
    t.start()

    # اجرای سرور Flask روی پورت 8080
    app.run(host='0.0.0.0', port=8080)
