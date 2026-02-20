import os
import json
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI, OpenAIError

# --- Variables d'environnement ---
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MEMORY_FILE = "memory.json"

if not TELEGRAM_TOKEN:
    raise ValueError("⚠️ TELEGRAM_TOKEN manquant dans les variables d'environnement !")
if not OPENAI_API_KEY:
    raise ValueError("⚠️ OPENAI_API_KEY manquant dans les variables d'environnement !")

# --- Initialisation OpenAI ---
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except OpenAIError as e:
    print("Erreur OpenAI:", e)
    raise e

# --- Gestion de la mémoire ---
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
    await update.message.reply_text("Bonjour ! Lilyth est connectée 🤖")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    text = update.message.text
    # Enregistre le message dans la mémoire
    if user_id not in memory:
        memory[user_id] = []
    memory[user_id].append(text)
    save_memory()

    # Appel OpenAI
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es Lilyth, une assistante IA."},
                {"role": "user", "content": text},
            ]
        )
        answer = response.choices[0].message.content
    except Exception as e:
        answer = "⚠️ Erreur OpenAI : " + str(e)

    await update.message.reply_text(answer)

# --- Création de l'application Telegram ---
app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))

# --- Correction event loop pour Python 3.14+ ---
try:
    loop = asyncio.get_event_loop()
except RuntimeError:
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

print("💾 Mémoire chargée")
print("🤖 Lilyth est connectée à Telegram et prête !")

# --- Démarrage du bot ---
app.run_polling(close_loop=False)
