<div align="right">
  🇺🇸 <strong>English</strong> | 🇧🇷 <a href="README.pt-BR.md">Português</a>
</div>

# 🎵 Discord Music Bot

A Discord music bot developed in Python, with support for audio playback, full playlists, queues, and text commands for playback control.

---

## 🚀 Features

- Audio playback via YouTube, YouTube Music, and URLs with extraction using `yt-dlp` and `FFmpeg`
- Music and playlist queue management (`play`, `skip`, `stop`, `jump`, `queue`, `pause`, `resume`)
- Modular structure using `discord.py` Cogs

---

## 🛠️ Prerequisites

- **Python 3.10+** (Recommended 3.10 on Ubuntu server or 3.14+ in local development environment)
- **FFmpeg** installed and added to the system `PATH`
- Bot token created in the [Discord Developer Portal](https://discord.com/developers/applications)

---

## 📦 Local Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/YourUsername/discord-music-bot.git
   ```

2. **Access the project root:**
   ```bash
   cd discord-music-bot
   ```

3. **Create and configure the `.env` file:**
   The `config/` folder comes with the repository. You need to create the file that will store your credentials inside it. 
   
   **On Linux / macOS (Terminal):**
   ```bash
   nano config/.env
   ```
   *(In nano, paste your token, save with `Ctrl + O`, `Enter`, and exit with `Ctrl + X`)*.

   **On Windows (PowerShell):**
   ```powershell
   New-Item config\.env -ItemType File
   notepad config\.env
   ```
   *(Or just right-click the `config` folder in PyCharm/VSCode and create the file).*

   Inside the file, add your bot token generated in the Discord Developer Portal:
   ```text
   DISCORD_TOKEN=paste_your_token_here
   ```

4. **Create and activate the virtual environment:**
   To keep dependencies isolated, create a virtual environment:
   
   **On Linux / macOS:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   
   **On Windows:**
   ```powershell
   python -m venv .venv
   .venv\Scripts\activate
   ```

5. **Install dependencies:**
   With the environment activated, update the installer and download the packages (same command for both):
   ```bash
   pip install --upgrade pip setuptools wheel
   pip install -r requirements.txt
   ```

6. **Configure YouTube Cookies (Required for yt-dlp):**
   To avoid YouTube blocks (Error 400), the bot needs an authentication file. Follow the tutorial in the **How to export the cookies.txt file** section below and save the generated file inside the `config/` folder.

7. **Start the bot:**
   ```bash
   python main.py
   ```

---

## 🍪 How to export the cookies.txt file

YouTube blocks automated requests from `yt-dlp` by default. To bypass this, the bot needs to simulate a real browser using your session cookies.

**Follow these steps:**

1. Install the **Get cookies.txt LOCALLY** extension in your browser ([Chrome/Edge](https://chromewebstore.google.com/detail/get-cookiestxt-locally/cclelndahbckbenkjhflpocjadpjheoe) or [Firefox](https://addons.mozilla.org/pt-BR/firefox/addon/cookies-txt/)).
2. Access [YouTube](https://www.youtube.com/) and log in.
   > ⚠️ **Security Warning:** It is highly recommended to create and use a secondary ("burner") Google account just for the bot. This prevents your main account from suffering YouTube restrictions.
3. With the YouTube tab open and logged in, click the extension icon at the top of the browser.
4. Click the **Export** button (or ensure you are exporting in *Netscape* format).
5. A text file will be downloaded. Rename it exactly to `cookies.txt`.
6. Move this file inside the **`config/`** folder in your project (becoming `config/cookies.txt`).

---

## ⚙️ Project Structure

```text
discord-music-bot/
├── .venv/               # Isolated virtual environment
├── cogs/                # Bot modules and commands (e.g., music.py)
├── config/              # Local configuration folder
│   ├── .gitkeep         # File to keep the folder in version control
│   ├── .env             # (Git ignored) Environment variables
│   └── cookies.txt      # (Git ignored) YouTube authentication
├── main.py              # Main initialization file
├── requirements.txt     # List of dependencies
└── README.md            # Project documentation
```