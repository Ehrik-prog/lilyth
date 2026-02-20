# main.py
import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI

# ───── CONFIG LOG ─────
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ───── VARIABLES D'ENVIRONNEMENT ─────
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN manquant dans les variables d'environnement !")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY manquant dans les variables d'environnement !")

# ───── CLIENT OPENAI ─────
client = OpenAI(api_key=OPENAI_API_KEY)

# ───── COMMANDES DE BASE ─────
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("💾 Lilyth est connectée et prête !")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Envoyez un message et Lilyth vous répondra via OpenAI.")

# ───── GESTION DES MESSAGES ─────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text

    # Génération de réponse via OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": user_message}]
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        logger.error(f"Erreur OpenAI: {e}")
        reply_text = "❌ Une erreur est survenue lors de la génération de la réponse."

    await update.message.reply_text(reply_text)

# ───── APPLICATION TELEGRAM ─────
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Commandes
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("🤖 Lilyth démarre sur Telegram...")
    await app.run_polling()

if __name__ == "__main__":
    # asyncio.run pour gérer l'event loop correctement
    asyncio.run(main())
