# Language Learning Machine

## Project Overview

This project is an AI Language Tutor CLI, built to solve a real, personal problem for my girlfriend, fitting the Hacktoberfest 'Build for a Friend' challenge.
My girlfriend always had problem learning languages so I created this tutor to help her.

It provides a private, personalized, and stateful conversational practice partner powered by an open-source LLM.

This application is designed to be highly flexible, allowing you to switch between local (Ollama) and private (OpenAI compatible) LLM backends by modifying a configuration file.

## Setup & Installation

### 1. Prerequisites
*   **Python 3.x:** Ensure you have a modern Python environment.
*   **Dependencies:** All necessary libraries are listed in `requirements.txt`.

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configuration

Create a file named `config.yaml` in the root directory. This file controls which LLM provider is used and where it connects.

**Use the provided template and choose one provider:**

```yaml
llm_provider: ollama  # Options: ollama, openai

# --- Ollama Configuration ---
ollama:
  model: llama3
  host: http://localhost:11434

# --- OpenAI Configuration ---
openai:
  api_key: "YOUR_API_KEY"
  model: gpt-3.5-turbo
  api_base: "http://localhost:8000/v1"
```

## Running the Application

To start the tutor, run the main CLI file, specifying the persona and topic:

```bash
python ai_tutor_cli.py --mode roleplay --role "French barista" --topic "ordering a pastry"
```

## Project Features

*   **Personalized Tutoring:** Tailors the conversation based on a custom `role` and `topic`.
*   **Stateful Conversation:** Uses a `ChatSession` to maintain conversation history, allowing for coherent, multi-turn dialogue.
*   **Provider Agnostic:** Seamlessly switches between **Ollama** (private, local) and **OpenAI/Unsloth** (private, custom API base).

---

*Built for the Hacktoberfest Weekend Challenge: Build for a Friend*
