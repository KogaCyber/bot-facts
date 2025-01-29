# 🌟 Scientific AI Facts Bot - Quick Start Guide

## 🚀 Installation & Setup

1. **Clone the repository**:
    ```bash
    git clone https://github.com/KogaCyber/bot-facts
    cd scientific-facts-bot
    ```

2. **Create a virtual environment**:
    ```bash
    python3 -m venv venv
    ```

3. **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```

4. **Set up environment variables**:
    - Create `.env` file in the root directory with the following keys:
      ```
      TELEGRAM_BOT_TOKEN=<Your Telegram Bot Token>
      CHANNEL_ID=<Your Telegram Channel ID>
      PEXELS_API_KEY=<Your Pexels API Key>
      ANTHROPIC_API_KEY=<Your Anthropic API Key>
      ```

## 🎯 Running the Bot

1. **Start the bot**:
    ```bash
    python main.py
    ```

2. **Expected output**:
    - The bot will initialize, connect to Telegram, and begin sending scientific facts at scheduled intervals.
    - It will also display logs of its activity, including when it sends facts, checks for images, and tracks statistics.

## 📊 Monitoring

The bot will automatically:
- **Generate and send facts 4 times daily** at 9:00, 13:00, 17:00, and 21:00 (Tashkent time).
- **Track token usage and costs**, keeping you informed of usage details.
- **Save statistics** to `bot_stats.json`, which logs:
  - Number of facts sent
  - Token usage
  - Costs
- **Display warnings** when balance is low or token usage exceeds expected limits.

## ⚠️ Requirements

- Python 3.8+
- Active **Telegram Bot Token** (Create your bot via [BotFather](https://core.telegram.org/bots#botfather))
- **Pexels API Key** (Sign up and get an API key [here](https://www.pexels.com/api/))
- **Anthropic API Key** (Sign up for access to Claude API [here](https://www.anthropic.com/))
- **Channel Admin Rights** for the Telegram channel to send messages
