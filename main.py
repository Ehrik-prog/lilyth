import os
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import openai

# Assure-toi que tes variables Railway sont bien partagées et accessibles
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

openai.api_key = OPENAI_API_KEY

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Lilyth est connectée et prête !")

async def ask_ai(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_text = " ".join(context.args)
    if not user_text:
        await update.message.reply_text("Envoie-moi une question après la commande.")
        return

    # Appel à OpenAI
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": user_text}],
        temperature=0.7
    )
    answer = response.choices[0].message.content
    await update.message.reply_text(answer)

async def main():
    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ask", ask_ai))

    print("🤖 Lilyth démarre sur Telegram...")
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # pour colab / environnements déjà asynchrones
    asyncio.run(main())
