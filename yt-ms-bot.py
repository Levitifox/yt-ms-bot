import logging
import os
import tempfile
import time
from threading import Thread, Lock

from flask import Flask, abort, send_file
from yt_dlp import YoutubeDL
from ytmusicapi import YTMusic
from telegram import InlineQueryResultAudio, Update
from telegram.ext import Application, CommandHandler, InlineQueryHandler, ContextTypes
from dotenv import load_dotenv
from pyngrok import ngrok # type: ignore

load_dotenv()

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("No TELEGRAM_BOT_TOKEN provided in the environment!")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
ytmusic = YTMusic()
download_locks = {}
SERVER_URL = None

def download_audio(video_id: str) -> str:
    video_url = f"https://www.youtube.com/watch?v={video_id}"
    temp_dir = tempfile.gettempdir()
    mp3_file = os.path.join(temp_dir, f"{video_id}.mp3")
    if video_id in download_locks:
        logger.info(f"Waiting for another download to finish: {video_id}")
        while not os.path.exists(mp3_file) or os.path.getsize(mp3_file) == 0:
            time.sleep(0.5)
        return mp3_file
    download_locks[video_id] = Lock()
    download_locks[video_id].acquire()
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(temp_dir, f"{video_id}.%(ext)s"),
            'quiet': True,
            'user_agent': ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                           'AppleWebKit/537.36 (KHTML, like Gecko) '
                           'Chrome/102.0.5005.63 Safari/537.36'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            downloaded_file = ydl.prepare_filename(info)
        base, _ = os.path.splitext(downloaded_file)
        final_mp3 = base + '.mp3'
        if not os.path.exists(final_mp3) or os.path.getsize(final_mp3) == 0:
            logger.error(f"Downloaded file is empty: {final_mp3}")
            raise Exception("File was not downloaded correctly.")
        logger.info(f"Downloaded successfully: {final_mp3}")
        return final_mp3
    except Exception as e:
        logger.error(f"yt-dlp failed for {video_id}: {e}")
        raise
    finally:
        download_locks[video_id].release()
        del download_locks[video_id]

@app.route('/audio/<video_id>')
def audio_endpoint(video_id):
    try:
        file_path = download_audio(video_id)
        while not os.path.exists(file_path) or os.path.getsize(file_path) == 0:
            logger.info(f"Waiting for file to be ready: {file_path}")
            time.sleep(0.5)
        def delayed_remove():
            time.sleep(20)
            try:
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
            except Exception as e:
                logger.error(f"Error removing file {file_path}: {e}")
        Thread(target=delayed_remove, daemon=True).start()
        return send_file(file_path, mimetype='audio/mpeg', as_attachment=True, download_name=os.path.basename(file_path))
    except Exception as e:
        logger.error(f"Error retrieving audio for video_id {video_id}: {e}")
        return abort(500)

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello! I'm your YouTube Music inline bot.\nUse me inline in any chat: type @yt_ms_lf_bot followed by a track name.")

async def inlinequery(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.inline_query.query.strip()
    logger.info(f"Received inline query: '{query}'")
    if not query:
        return
    results = []
    try:
        search_results = ytmusic.search(query, filter='songs')
        if not search_results:
            logger.info("No search results found.")
            return
        for i, item in enumerate(search_results[:5]):
            video_id = item.get('videoId')
            if not video_id:
                continue
            title = item.get('title')
            artists = item.get('artists')
            artist_names = ", ".join(artist.get('name') for artist in artists) if artists else "Unknown"
            audio_url = f"{SERVER_URL}/audio/{video_id}"
            logger.info(f"Adding result: title='{title}', video_id='{video_id}'")
            result = InlineQueryResultAudio(id=str(i), audio_url=audio_url, title=title, performer=artist_names)
            results.append(result)
    except Exception as e:
        logger.error(f"Error processing inline query '{query}': {e}")
    await update.inline_query.answer(results, cache_time=0)

def main():
    global SERVER_URL
    SERVER_URL = ngrok.connect(5000).public_url
    logger.info("ngrok tunnel: %s", SERVER_URL)
    flask_thread = Thread(target=run_flask, daemon=True)
    flask_thread.start()
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(InlineQueryHandler(inlinequery))
    logger.info("Telegram bot started. Press Ctrl+C to stop.")
    application.run_polling()

if __name__ == '__main__':
    main()
