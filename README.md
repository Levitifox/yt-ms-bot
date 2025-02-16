# YouTube Music Inline Bot for Telegram

A Telegram inline bot that lets you search for and share tracks from YouTube Music directly within your chats. This bot uses the [YTMusicAPI](https://github.com/sigma67/ytmusicapi) to search for songs, [yt-dlp](https://github.com/yt-dlp/yt-dlp) to download and convert YouTube videos to MP3, and serves the audio via a temporary [Flask](https://flask.palletsprojects.com/) web server tunneled through [ngrok](https://ngrok.com/). It integrates seamlessly with Telegram’s inline mode, allowing users to search and send music without leaving their chat.

## Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [How It Works](#how-it-works)
- [Troubleshooting](#troubleshooting)
- [Contributing](#contributing)
- [Acknowledgments](#acknowledgments)

## Features

- **Inline Mode**: Search and share music directly within Telegram chats.
- **YouTube Music Search**: Leverages YouTube Music’s database to fetch song details.
- **Audio Downloading**: Downloads and converts YouTube videos to MP3 using yt-dlp.
- **Temporary File Hosting**: Serves audio files through a Flask server with automatic cleanup.
- **Ngrok Tunneling**: Exposes your local Flask server to the internet using ngrok.

## Prerequisites

- **Python 3.7+**  
- **FFmpeg**: Required by yt-dlp for audio extraction and conversion.  
  - [Download FFmpeg](https://ffmpeg.org/download.html) and ensure it’s available in your system’s PATH.
- **Telegram Bot Token**: Obtain one from [BotFather](https://t.me/BotFather) on Telegram.
- **Internet Connection**: For accessing YouTube Music, downloading audio, and tunneling via ngrok.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/levitifox/yt-ms-bot.git
   cd yt-ms-bot
   ```

2. **Create a virtual environment (optional but recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. **Set the Telegram Bot Token:**

   The bot reads the Telegram bot token from the environment variable `TELEGRAM_BOT_TOKEN`. You can set it in your terminal session as follows:

   ```bash
   export TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

   On Windows (Command Prompt):

   ```cmd
   set TELEGRAM_BOT_TOKEN=your_telegram_bot_token_here
   ```

2. **Ensure FFmpeg is installed** and accessible via your system’s PATH.

## Usage

To start the bot, simply run:

```bash
python yt_ms_bot.py
```

This will:

- Establish an ngrok tunnel exposing the Flask server on port 5000.
- Start the Flask server that handles audio file requests.
- Launch the Telegram bot that listens for inline queries.

Once running, you can use the bot inline by typing `@your_bot_username` in any Telegram chat and entering a track name.

## How It Works

1. **Inline Query Handling**:  
   When you type an inline query (e.g., `@your_bot_username song title`), the bot uses the YTMusicAPI to search for songs on YouTube Music and returns up to 5 results.

2. **Audio Downloading**:  
   When a user selects a track, the bot triggers the download process using yt-dlp. The video is converted to MP3 and saved temporarily.

3. **Serving the Audio File**:  
   The Flask server, exposed via an ngrok tunnel, serves the MP3 file through an endpoint (`/audio/<video_id>`). The bot sends this URL as an inline audio result.

4. **Automatic Cleanup**:  
   Downloaded audio files are scheduled for deletion 20 seconds after being served to ensure your system stays clean.

## Troubleshooting

- **Empty or Corrupt Downloads**:  
  If a downloaded file is empty or corrupted, check your FFmpeg installation and ensure it is in the PATH.

- **Ngrok Issues**:  
  If the ngrok tunnel does not start or you encounter connectivity issues, verify your internet connection and ngrok installation.

- **Logging**:  
  The bot logs its activity. Check the console output for detailed error messages and troubleshooting tips.

## Contributing

Contributions are welcome! Please fork the repository and submit pull requests with your improvements or bug fixes. For major changes, please open an issue first to discuss what you would like to change.

## Acknowledgments

- [YTMusicAPI](https://github.com/sigma67/ytmusicapi)
- [yt-dlp](https://github.com/yt-dlp/yt-dlp)
- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot)
- [Flask](https://flask.palletsprojects.com/)
- [ngrok](https://ngrok.com/)
