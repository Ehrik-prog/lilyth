import os
import nest_asyncio
import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)
from openai import OpenAI

# ─── LOGGING ──────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─── VARIABLES D'ENVIRONNEMENT ───────────────────────────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN manquant dans les variables d'environnement !")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY manquant dans les variables d'environnement !")

# ─── CLIENT OPENAI ───────────────────────────────────────
client = OpenAI(api_key=OPENAI_API_KEY)

# ─── PATCH ASYNCIO (pour pb loop sur certains environnements) ───
nest_asyncio.apply()

# ─── HANDLERS TELEGRAM ───────────────────────────────────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Lilyth est prête à discuter 🤖")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commandes disponibles:\n"
        "/start - Démarre le bot\n"
        "/help - Affiche ce message\n"
        "Tu peux aussi envoyer un message et Lilyth te répondra via OpenAI !"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Répond à tout message texte via OpenAI GPT."""
    user_message = update.message.text
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}],
            max_tokens=300
        )
        reply = response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur OpenAI: {e}")
        reply = "Désolé, je n'ai pas pu générer de réponse."
    await update.message.reply_text(reply)

# ─── APPLICATION TELEGRAM ───────────────────────────────
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("help", help_command))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

# ─── MAIN ───────────────────────────────────────────────
if __name__ == "__main__":
    logger.info("💾 Mémoire chargée")
    logger.info("🤖 Lilyth est connectée à Telegram et prête !")
    app.run_polling(close_loop=False)
