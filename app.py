import os, threading, time
from flask import Flask, request, send_file, render_template_string
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp
from urllib.parse import quote, unquote

app = Flask(__name__)
BOT_TOKEN = '8098351153:AAHddeFz1_sdVQCo7s2zje4og16vHJYM4JI'
SITE_URL = 'https://download-videos-reels-shorts.in'

HTML = '''
<!DOCTYPE html><html><head><title>Fast Downloader</title><meta name="viewport" content="width=device-width">
<style>body{font-family:Arial;background:#1a1a2e;color:white;text-align:center;padding:50px;}
.btn{display:inline-block;padding:20px 40px;background:#ff4444;color:white;text-decoration:none;border-radius:25px;font-size:20px;margin:15px;box-shadow:0 5px 15px rgba(255,68,68,0.4);}
.btn-audio{background:#4CAF50;box-shadow:0 5px 15px rgba(76,175,80,0.4);}
h1{font-size:2.5em;color:#ff6b6b;margin:30px 0;}
.info{background:rgba(255,255,255,0.1);padding:20px;border-radius:15px;margin:20px 0;}
@media(max-width:600px){.btn{padding:15px 30px;font-size:18px;}}</style></head>
<body><div style="max-width:500px;margin:auto;">
<h1>🚀 {{title}}</h1><div class="info"><p>📱 Mobile Optimized • ⚡ Fast Download • 🎬 720p Quality</p></div>
<a href="/get?url={{url}}" class="btn">📹 VIDEO DOWNLOAD</a><a href="/audio?url={{url}}" class="btn btn-audio">🎵 MP3 AUDIO</a>
<p style="color:#aaa;margin-top:40px;">Powered by yt-dlp | download-videos-reels-shorts.in</p></div></body></html>
'''

@app.route('/')
def home():
    url = unquote(request.args.get('url', ''))
    if not url: return '<h1 style="color:#ff4444;font-size:3em;">🔗 Telegram Bot se link bhejo!</h1>'
    if not any(x in url.lower() for x in ['youtube.com','instagram.com','youtu.be']):
        return '<h1 style="color:#ff4444;font-size:2em;">❌ YouTube/Instagram sirf!</h1>'
    
    try:
        with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')[:50]
        return render_template_string(HTML, title=title, url=quote(url))
    except: return '<h1 style="color:#ff4444;font-size:2em;">❌ Link galat hai!</h1>'

@app.route('/get')
def get_video():
    url = unquote(request.args.get('url'))
    try:
        ydl_opts = {'format':'best[height<=720]','outtmpl':'/tmp/v.%(ext)s','quiet':True}
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = '/tmp/v.' + info['ext']
        return send_file(filename, as_attachment=True, download_name=f"{info.get('title', 'video')[:80]}.mp4")
    except: return '<h1 style="color:#ff4444;">Download fail!</h1>'
    finally: os.system('rm -f /tmp/v.*')

@app.route('/audio')
def get_audio():
    url = unquote(request.args.get('url'))
    try:
        ydl_opts = {
            'format':'bestaudio/best',
            'postprocessors': [{'key':'FFmpegExtractAudio','preferredcodec':'mp3','preferredquality':'192'}],
            'outtmpl':'/tmp/a.%(ext)s','quiet':True
        }
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = '/tmp/a.mp3'
        return send_file(filename, as_attachment=True, download_name=f"{info.get('title', 'audio')[:80]}.mp3")
    except: return '<h1 style="color:#ff4444;">Audio fail!</h1>'
    finally: os.system('rm -f /tmp/a.*')

async def start(update: Update, context):
    await update.message.reply_text('🎬 **Video Downloader**\n\n🔗 YouTube/Instagram link bhejo!\n⚡ Video + MP3 dono milega')

async def handle_link(update: Update, context):
    url = update.message.text.strip()
    await update.message.reply_text('⚡ Ready kar raha...')
    
    if not any(x in url.lower() for x in ['youtube.com','instagram.com','youtu.be']):
        await update.message.reply_text('❌ YouTube/Instagram link daal!')
        return
    
    try:
        with yt_dlp.YoutubeDL({'quiet':True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Video')[:40]
        
        v_url = f"{SITE_URL}?url={quote(url)}"
        a_url = f"{SITE_URL}/audio?url={quote(url)}"
        
        keyboard = [
            [InlineKeyboardButton("📹 VIDEO 720p", url=v_url)],
            [InlineKeyboardButton("🎵 MP3 AUDIO", url=a_url)]
        ]
        await update.message.reply_text(f'🎬 **{title}**\n\nChoose:', reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    except:
        await update.message.reply_text('❌ Invalid link ya private video!')

def run_bot():
    app_bot = Application.builder().token(BOT_TOKEN).build()
    app_bot.add_handler(CommandHandler('start', start))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link))
    app_bot.run_polling()

if __name__ == '__main__':
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    time.sleep(3)
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
