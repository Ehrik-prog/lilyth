import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from openai import OpenAI

# --- Vérification des tokens ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN manquant dans les variables d'environnement !")

# Fichier mémoire
MEMORY_FILE = "memory.json"

# Chargement mémoire
if os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        memory = json.load(f)
else:
    memory = {}

def save_memory():
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, ensure_ascii=False, indent=2)

# --- Handlers Telegram ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salut ! Je suis Lilyth, ton assistant.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    message_text = update.message.text

    # Sauvegarde du message
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append(message_text)
    save_memory()

    # --- Lecture clé OpenAI au moment du message ---
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    if not OPENAI_API_KEY:
        await update.message.reply_text("⚠️ OpenAI API key manquante !")
        return

    client = OpenAI(api_key=OPENAI_API_KEY)

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

# --- Création de l'application ---
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

# Handlers
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# --- Lancement ---
if __name__ == "__main__":
    print("💾 Mémoire chargée")
    print("🤖 Lilyth est connectée à Telegram et prête !")
    app.run_polling(close_loop=False)
