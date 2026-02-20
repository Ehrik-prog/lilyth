import os
import json
import asyncio
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters
from openai import OpenAI, OpenAIError

# -----------------------------
# Vérification des variables d'environnement
# -----------------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN manquant dans les variables d'environnement !")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY manquant dans les variables d'environnement !")

# -----------------------------
# Initialisation OpenAI
# -----------------------------
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except OpenAIError as e:
    raise RuntimeError(f"Erreur OpenAI : {e}")

# -----------------------------
# Mémoire persistante
# -----------------------------
MEMORY_FILE = "memory.json"
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = {}

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# -----------------------------
# Commandes Telegram
# -----------------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_html(
        rf"Salut {user.mention_html()} ! Je suis Lilyth, ton assistant IA.",
        reply_markup=ForceReply(selective=True),
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message_text = update.message.text

    # Sauvegarde du message dans la mémoire
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append(message_text)
    save_memory()

    # Appel OpenAI pour réponse
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es Lilyth, assistant Telegram de Eric."},
                {"role": "user", "content": message_text}
            ]
        )
        reply_text = response.choices[0].message.content
    except Exception as e:
        reply_text = f"⚠️ Erreur OpenAI : {e}"

    await update.message.reply_text(reply_text)

# -----------------------------
# Application Telegram
# -----------------------------
async def main():
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("💾 Mémoire chargée")
    print("🤖 Lilyth est connectée à Telegram et prête !")

    await app.run_polling()

# -----------------------------
# Lancement
# -----------------------------
if __name__ == "__main__":
    asyncio.run(main())
