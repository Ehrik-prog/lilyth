import os
import json
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ---- TOKENS ----
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

# ---- MEMOIRE ----
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

# ---- HUGGINGFACE CHAT API ----
HF_MODEL = "meta-llama/Llama-3.1-70B-Instruct"  # exemple de modèle puissant

def query_hf_api(messages):
    url = f"https://api-inference.huggingface.co/models/{HF_MODEL}"
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    data = {"inputs": messages, "options": {"wait_for_model": True}}
    response = requests.post(url, headers=headers, json=data)
    result = response.json()
    text = result[0]["generated_text"] if isinstance(result, list) else str(result)
    return text

# ---- HANDLER ----
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.message.from_user.id)
        user_input = update.message.text

        history = memory.get(user_id, [])
        history.append({"role": "user", "content": user_input})

        # Construire un prompt simple
        full_prompt = ""
        for msg in history[-10:]:
            role = msg["role"]
            content = msg["content"]
            full_prompt += f"{role}: {content}\n​"
​
"

        answer = query_hf_api(full_prompt)

        history.append({"role": "assistant", "content": answer})
        memory[user_id] = history
        save_memory(memory)

        await update.message.reply_text(answer)

    except Exception as e:
        print("Erreur:", e)
        await update.message.reply_text("⚠️ Une erreur est survenue.")

# ---- MAIN ----
if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Lilyth HF gratuite connectée")
    app.run_polling()
