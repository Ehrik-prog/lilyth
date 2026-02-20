import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
import openai

# ----------------------
# CONFIG LOGGING
# ----------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ----------------------
# CONFIG TOKENS
# ----------------------
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("Le token Telegram n'est pas défini !")
if not OPENAI_API_KEY:
    raise ValueError("La clé OpenAI n'est pas définie !")

openai.api_key = OPENAI_API_KEY

# ----------------------
# HANDLERS
# ----------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Lilyth est en ligne ! Envoyez-moi un message.")

async def chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Tu es Lilyth, une assistante IA."},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=500
        )
        reply_text = response['choices'][0]['message']['content'].strip()
    except Exception as e:
        logger.error("Erreur OpenAI : %s", e)
        reply_text = "😵‍💫 Oups, erreur côté OpenAI !"

    await update.message.reply_text(reply_text)

# ----------------------
# MAIN BOT
# ----------------------
def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Commandes
    app.add_handler(CommandHandler("start", start))

    # Messages libres
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, chat))

    logger.info("🤖 Lilyth démarre sur Telegram...")
    # run_polling avec close_loop=False pour éviter les erreurs de loop
    app.run_polling(close_loop=False)

if __name__ == "__main__":
    main()
