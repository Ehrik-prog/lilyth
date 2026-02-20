import os
import logging
import nest_asyncio
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters

# ✅ Appliquer nest_asyncio pour réutiliser l'event loop existant
nest_asyncio.apply()

# 🔹 Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔹 Récupérer le token depuis les variables d'environnement
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise RuntimeError("⚠️ TELEGRAM_TOKEN non trouvé dans les variables d'environnement")

# 🔹 Exemple de commandes
async def start(update, context):
    await update.message.reply_text("Salut ! Lilyth est prête 🤖")

async def echo(update, context):
    await update.message.reply_text(update.message.text)

# 🔹 Fonction principale
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    # Ajouter handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    logger.info("🤖 Lilyth démarre sur Telegram...")
    # run_polling avec close_loop=False pour ne pas fermer l'event loop existant
    await app.run_polling(close_loop=False)

# 🔹 Lancer main
import asyncio

try:
    # Si l'event loop est déjà actif (Railway / Colab), on utilise get_event_loop()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
except RuntimeError as e:
    # fallback si aucun loop existant
    logger.warning(f"Event loop déjà en cours : {e}")
    asyncio.run(main())
