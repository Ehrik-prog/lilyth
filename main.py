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

HF_MODEL = "OpenAssistant/release-10-13b"

def query_model(prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"

    headers = {
        "Authorization": f"Bearer {os.getenv('OPENROUTER_API_KEY')}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are Lilyth, an intelligent and conversational AI."},
            {"role": "user", "content": prompt}
        ]
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code != 200:
        return f"Erreur OpenRouter {response.status_code}: {response.text}"

    result = response.json()
    return result["choices"][0]["message"]["content"]


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
        print("ERREUR:", e)
        await update.message.reply_text("Erreur : " + str(e))

if __name__ == "__main__":
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("Lilyth V1 active")
    app.run_polling()
