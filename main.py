import os
import json
import asyncio
import base64
import requests
from datetime import datetime
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv
from openai import OpenAI

# ==============================
# CONFIGURATION
# ==============================

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPO = "<ton_nom_utilisateur>/lilyth-bot"  # ⚠️ remplace par ton user

import os
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

MEMORY_FILE = "memory.json"

# ==============================
# GESTION MÉMOIRE
# ==============================

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=4, ensure_ascii=False)

memory = load_memory()

# ==============================
# BACKUP VIA API GITHUB
# ==============================

def backup_memory():
    try:
        if not GITHUB_TOKEN:
            return

        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            content = f.read()

        b64_content = base64.b64encode(content.encode()).decode()
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        headers = {
            "Authorization": f"token {GITHUB_TOKEN}"
        }

        # Vérifier si le fichier existe
        url_get = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{MEMORY_FILE}"
        r = requests.get(url_get, headers=headers)
        sha = r.json().get("sha") if r.status_code == 200 else None

        payload = {
            "message": f"Backup memory {now}",
            "content": b64_content,
            "branch": "main"
        }

        if sha:
            payload["sha"] = sha

        url_put = f"https://api.github.com/repos/{GITHUB_REPO}/contents/{MEMORY_FILE}"
        requests.put(url_put, headers=headers, json=payload)

        print("Backup GitHub OK")

    except Exception as e:
        print("Erreur backup:", e)


async def periodic_backup():
    while True:
        backup_memory()
        await asyncio.sleep(300)  # toutes les 5 minutes


# ==============================
# INTELLIGENCE LILYTH
# ==============================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_message = update.message.text

    if user_id not in memory:
        memory[user_id] = []

    memory[user_id].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=memory[user_id]
        )

        reply = response.choices[0].message.content

        memory[user_id].append({"role": "assistant", "content": reply})
        save_memory(memory)

        await update.message.reply_text(reply)

    except Exception as e:
        await update.message.reply_text("Erreur IA.")
        print("Erreur OpenAI:", e)


# ==============================
# MAIN
# ==============================

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Lilyth est en ligne...")

    asyncio.create_task(periodic_backup())

    await app.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
