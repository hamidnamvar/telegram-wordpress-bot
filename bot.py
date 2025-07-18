import requests
import time

TELEGRAM_TOKEN = '7602351049:AAHSHa1X8RgycROFqnEcxaUJBSTwDt4qcfg'
CHANNEL_USERNAME = '@sorenbam_post'
WORDPRESS_API = 'https://sorenbam.ir/wp-json/wp/v2/posts'

sent_post_ids = set()

def get_latest_posts():
    try:
        response = requests.get(WORDPRESS_API)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error fetching posts: {e}")
        return []

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

def main():
    global sent_post_ids
    while True:
        posts = get_latest_posts()
        for post in reversed(posts):  # ارسال به ترتیب انتشار
            post_id = post['id']
            if post_id not in sent_post_ids:
                title = post['title']['rendered']
                link = post['link']
                
                # استخراج خلاصه مطلب و حذف تگ‌های HTML اضافی
                import re
                raw_excerpt = post.get('excerpt', {}).get('rendered', '')
                # حذف تگ‌های HTML از خلاصه
                clean_excerpt = re.sub('<[^<]+?>', '', raw_excerpt).strip()
                
                # ساخت پیام با فرمت HTML و خلاصه
                message = f"📢 <b>{title}</b>\n\n{clean_excerpt}\n\n<a href='{link}'>📖 مشاهده مطلب در سایت</a>"
                
                send_to_telegram(message)
                sent_post_ids.add(post_id)
        time.sleep(60)  # هر ۶۰ ثانیه چک کن

