import os

# Root folder
root = "dyslexia-ai-agent"

# Repo structure dictionary
repo_structure = {
    "backend": {
        "app.py": "# FastAPI entrypoint\n",
        "agents": {
            "text_simplifier.py": "# Text simplifier agent\n",
            "audio_agent.py": "# Audio TTS agent\n",
            "quiz_agent.py": "# Quiz generation agent\n",
            "hint_agent.py": "# Hint agent\n",
            "gamification_agent.py": "# Gamification agent\n",
            "orchestrator.py": "# Orchestrates all agents\n",
        },
        "models": {
            "local_llm.py": "# LLaMA/Phi-3 wrapper\n"
        },
        "utils": {
            "embeddings.py": "# Embedding + FAISS utilities\n",
            "audio.py": "# Coqui TTS helper functions\n",
            "speech_input.py": "# Whisper offline dictation helper\n"
        },
        "data": {
            "sample_texts": {}
        }
    },
    "frontend": {
        "public": {
            "index.html": "<!-- Main HTML file -->\n"
        },
        "src": {
            "App.jsx": "// Main React app\n",
            "components": {
                "TextSimplifier.jsx": "// Component\n",
                "AudioPlayer.jsx": "// Component\n",
                "QuizPanel.jsx": "// Component\n",
                "HintDisplay.jsx": "// Component\n",
                "GamificationUI.jsx": "// Component\n"
            },
            "utils": {
                "api.js": "// API helper functions\n"
            }
        },
        "package.json": "{\n  \"name\": \"frontend\",\n  \"version\": \"1.0.0\"\n}\n"
    },
    "requirements.txt": "# Python dependencies\nfastapi\nuvicorn\nllama.cpp\ncoqui-tts\nsentence-transformers\nfaiss-cpu\nwhisper\n",
    "README.md": "# Dyslexia AI Agent Hackathon Repo\n",
    "run.sh": "#!/bin/bash\n# Start backend + frontend\n"
}

# Function to create folders and files recursively
def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        if isinstance(content, dict):
            os.makedirs(path, exist_ok=True)
            create_structure(path, content)
        else:
            # It's a file
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, "w") as f:
                f.write(content)

# Create the repo
create_structure(".", repo_structure)
print(f"Repo structure created under ./{root}")