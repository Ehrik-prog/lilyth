import os
import json
import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
HF_API_KEY = os.getenv("HUGGING_FACE_API_KEY")

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

HF_MODEL = "meta-llama/Llama-3.1-8B-Instruct"

def query_hf_api(prompt):
    url = "https://api-inference.huggingface.co/models/" + HF_MODEL
    headers = {
        "Authorization": "Bearer " + HF_API_KEY
    }
    payload = {
        "inputs": prompt,
        "options": {"wait_for_model": True}
    }
    response = requests.post(url, headers=headers, json=payload)
    result = response.json()

    if isinstance(result, list):
        return result[0]["generated_text"]
    else:
        return str(result)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = str(update.message.from_user.id)
        user_input = update.message.text

        history = memory.get(user_id, [])
        history.append({"role": "user", "content": user_input})

        full_prompt = ""
        for msg in history[-10:]:
            full_prompt += msg["role"] + ": " + msg["content"] + "\n"

        answer = query_hf_api(full_prompt)

        history.append({"role": "assistant", "content": answer})
        memory[user_id] = history
        save_memory(memory)

        await update.message.reply_text(answer)

    except Exception as e:
        print("Erreur:", e)
        await update.message.reply_text("⚠️ Une erreur est survenue.")

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Lilyth HF gratuite connectée")
    app.run_polling()
