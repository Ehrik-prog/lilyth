import os
import json
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")

# -------- MEMOIRE --------
MEMORY_FILE = "memory.json"

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        return {}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=4)

memory = load_memory()

# -------- HANDLER --------
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.message.from_user.id)
        text = update.message.text

        # Sauvegarde mémoire simple
        memory[user_id] = text
        save_memory(memory)

        await update.message.reply_text(f"Lilyth V1 active 🖤\nTu as dit : {text}")

    except Exception as e:
        print("Erreur :", e)
        await update.message.reply_text("⚠️ Une erreur est survenue.")

# -------- MAIN --------
if __name__ == "__main__":
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Lilyth V1 connectée")
    app.run_polling()
