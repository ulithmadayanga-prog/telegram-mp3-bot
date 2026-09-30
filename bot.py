import os
import asyncio
import yt_dlp
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def start_health_server():
    port = int(os.environ.get("PORT", "10000"))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.environ.get("BOT_TOKEN")


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎵 YouTube link එක එවන්න.\n\n"
        "මම ඒක MP3 එකක් කරලා දෙන්නම්."
    )


async def download_mp3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()

    if not ("youtube.com/" in url or "youtu.be/" in url):
        await update.message.reply_text("❌ YouTube link එකක් එවන්න.")
        return

    msg = await update.message.reply_text("⏳ MP3 එක හදමින්...")

    filename = f"audio_{update.message.message_id}"

    options = {
        "format": "bestaudio/best",
        "outtmpl": f"{filename}.%(ext)s",
        "noplaylist": True,
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }

    try:
        def convert():
            with yt_dlp.YoutubeDL(options) as ydl:
                info = ydl.extract_info(url, download=True)
                return info.get("title", "Audio")

        title = await asyncio.to_thread(convert)
        mp3_file = f"{filename}.mp3"

        await update.message.reply_audio(
            audio=open(mp3_file, "rb"),
            title=title[:64]
        )

        os.remove(mp3_file)
        await msg.delete()

    except Exception as e:
        await msg.edit_text("❌ MP3 එක හදන්න බැරි වුණා.")
        print(e)


def main():
        threading.Thread(target=start_health_server, daemon=True).start()
    if not TOKEN:
        raise RuntimeError("BOT_TOKEN is missing")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, download_mp3)
    )

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
