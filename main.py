import os
import json
import logging
import nest_asyncio
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)
from openai import OpenAI

# ─── LOGGING ───────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── PATCH ASYNCIO POUR ENVIRONNEMENTS SPAWN THREAD ─────
nest_asyncio.apply()

# ─── VARIABLES D'ENVIRONNEMENT ─────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MEMORY_FILE = "memory.json"

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN manquant dans les variables d'environnement !")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY manquant dans les variables d'environnement !")

# ─── CLIENT OPENAI ─────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ─── CHARGEMENT DE LA MÉMOIRE ─────────────
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = {}

# ─── FONCTIONS ───────────────────────────
async def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Je suis Lilyth 🤖. Prête à discuter.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start - Démarrer le bot\n"
        "/help - Afficher ce message\n"
        "/reset - Réinitialiser la mémoire de conversation\n"
        "Tu peux aussi m'envoyer un message et je te répondrai !"
    )

async def reset(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    if user_id in memory:
        memory[user_id] = []
        await save_memory()
    await update.message.reply_text("Mémoire réinitialisée ✅")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    user_message = update.message.text

    # Ajouter à la mémoire
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append({"role": "user", "content": user_message})

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=memory[user_id],
            max_tokens=300
        )
        reply = response.choices[0].message.content
        memory[user_id].append({"role": "assistant", "content": reply})
        await save_memory()
    except Exception as e:
        logger.error(f"Erreur OpenAI: {e}")
        reply = "Désolé, je n'ai pas pu générer de réponse."
    await update.message.reply_text(reply)

# ─── APPLICATION TELEGRAM ───────────────
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(CommandHandler("reset", reset))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

# ─── LANCEMENT ─────────────────────────
if __name__ == "__main__":
    logger.info("💾 Mémoire chargée")
    logger.info("🤖 Lilyth est connectée à Telegram et prête !")
    app.run_polling(close_loop=False)
