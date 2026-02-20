# main.py
import os
import json
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI, OpenAIError

# ─── Variables d'environnement ───
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN manquant dans les variables d'environnement !")

if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY manquant dans les variables d'environnement !")

# ─── Initialisation OpenAI ───
client = OpenAI(api_key=OPENAI_API_KEY)

# ─── Mémoire locale ───
MEMORY_FILE = "memory.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

memory = load_memory()

# ─── Handlers ───
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Lilyth est en ligne et prête !")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text

    # sauvegarde du message dans la mémoire
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append(text)
    save_memory(memory)

    await update.message.reply_text(f"Message enregistré : {text}")

async def ask_openai(prompt: str):
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content
    except OpenAIError as e:
        return f"Erreur OpenAI : {str(e)}"

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text

    reply = await ask_openai(text)

    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append(f"Bot: {reply}")
    save_memory(memory)

    await update.message.reply_text(reply)

# ─── Main ───
async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Commandes
    app.add_handler(CommandHandler("start", start))
    
    # Messages simples → echo + sauvegarde
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Messages avec AI → pour activer l’OpenAI chat, remplacer echo par chat si voulu
    # app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    print("💾 Lilyth v1 prête et en ligne...")
    await app.run_polling()

# ─── Lancement ───
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except RuntimeError:
        # si loop déjà en cours
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main())
