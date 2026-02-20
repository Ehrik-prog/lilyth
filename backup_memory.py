import os
import json
from datetime import datetime
from git import Repo

# Variables d'environnement
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_URL = "https://{}@github.com/<ton_nom_utilisateur>/lilyth-bot.git".format(GITHUB_TOKEN)
BRANCH = "main"
REPO_LOCAL = os.path.dirname(os.path.abspath(__file__))  # dossier du bot

MEMORY_FILE = "memory.json"

# Vérifie si memory.json existe
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({}, f)

def backup_memory():
    repo = Repo(REPO_LOCAL)
    repo.git.add(MEMORY_FILE)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    repo.index.commit(f"Backup memory.json {now}")
    origin = repo.remote(name="origin")
    origin.push()

if __name__ == "__main__":
    backup_memory()
