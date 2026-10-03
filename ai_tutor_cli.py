import argparse
import sys
import yaml
from typing import List, Dict, Literal
from ollama import Client as OllamaClient # Ollama specific client
from openai import OpenAI # New import for OpenAI


# Define possible providers for type safety
LLMProvider = Literal['ollama', 'openai']

class LLMProviderInterface:
    """Abstract interface for LLM communication."""
    def chat(self, messages: List[Dict]) -> str:
        raise NotImplementedError

class OllamaProvider(LLMProviderInterface):
    def __init__(self, host: str, model: str):
        self.client = OllamaClient(host=host)
        self.model = model

    def chat(self, messages: List[Dict]) -> str:
        try:
            # Live LLM call for Ollama
            response = self.client.chat(
                model=self.model,
                messages=messages,
            )
            return response['message']['content']
        except Exception as e:
            return f"[ERROR] Ollama Connection Failed: {e}"

class OpenAIProvider(LLMProviderInterface):
    def __init__(self, api_key: str, model: str, api_base: str):
        # Initialize the OpenAI client using the custom API base
        # This makes it compatible with Unsloth or any proxy server.
        self.client = OpenAI(api_key=api_key, base_url=api_base)
        self.model = model

    def chat(self, messages: List[Dict]) -> str:
        try:
            # Live LLM call for OpenAI/Unsloth
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=messages
            )
            return completion.choices[0].message.content
        except Exception as e:
            # This will catch connection errors to Unsloth/OpenAI
            return f"[ERROR] OpenAI/Unsloth Connection Failed: {e}"

class ChatSession:
    """Manages the conversation state and uses a configured LLM provider."""
    def __init__(self, role: str, topic: str, provider: LLMProviderInterface):
        self.role = role
        self.topic = topic
        self.provider = provider
        self.history: List[Dict] = []
        self.set_system_prompt()
        
    def set_system_prompt(self):
        """Sets the system instruction for the AI roleplay."""
        system_prompt = f"You are an expert language tutor. Your role is to act as a {self.role} focused on the topic '{self.topic}'. You must guide the user through a conversation based on this theme. Your responses must be encouraging, detailed, and role-appropriate. Keep your responses under 150 words."
        self.history.append({"role": "system", "content": system_prompt})

    def chat(self, user_input: str) -> str:
        """Sends user input to the LLM provider and returns the AI's response."""
        self.history.append({"role": "user", "content": user_input})
        
        # Delegate the LLM call to the configured provider
        ai_response = self.provider.chat(self.history)
        
        # Update history with the AI's response
        self.history.append({"role": "assistant", "content": ai_response})
        return ai_response

def load_config(config_path: str = 'config.yaml') -> Dict:
    """Loads configuration from a YAML file."""
    try:
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    except FileNotFoundError:
        print(f"[CRITICAL] Configuration file '{config_path}' not found. Using defaults.")
        return {}
    except yaml.YAMLError as e:
        print(f"[CRITICAL] Error parsing YAML file: {e}")
        sys.exit(1)

def get_llm_provider(config: Dict, provider_type: Literal['ollama', 'openai']) -> LLMProviderInterface:
    """Instantiates the correct LLM provider based on config."""
    if provider_type == 'ollama':
        conf = config.get('ollama', {})
        return OllamaProvider(
            host=conf.get('host', 'http://localhost:11434'),
            model=conf.get('model', 'llama3')
        )
    elif provider_type == 'openai':
        conf = config.get('openai', {})
        return OpenAIProvider(
            api_key=conf.get('api_key', 'dummy_key'),
            model=conf.get('model', 'gpt-3.5-turbo'),
            api_base=conf.get('api_base', 'https://api.openai.com/v1') # Correctly pull api_base
        )
    else:
        raise ValueError(f"Unknown provider type: {provider_type}")

def run_language_tutor(mode: str, role: str, topic: str):
    """Core logic for the language tutor CLI.
    Loads config, initializes the session, and starts the interactive chat loop.
    """
    print("-" * 50)
    print("🤖 AI Language Tutor Initializing...")
    print("-" * 50)

    if mode not in ['roleplay', 'practice']:
        print(f"Error: Unknown mode '{mode}'. Please use 'roleplay' or 'practice'.")
        sys.exit(1)

    # Load configuration
    config = load_config()
    provider_type = config.get('llm_provider', 'ollama')

    try:
        # Instantiate the correct LLM provider
        llm_provider = get_llm_provider(config, provider_type)
    except Exception as e:
        print(f"[CRITICAL] Failed to initialize LLM Provider. Check config.yaml. Error: {e}")
        sys.exit(1)

    # Initialize and run the session
    session = ChatSession(role, topic, llm_provider)

    print(f"🌍 Mode: {mode.upper()}")
    print(f"🎭 Role: {role}")
    print(f"🗣️ Topic: {topic}")
    print("\n*** Chat Session Started. Type 'exit' or 'quit' to end. ***")

    while True:
        try:
            user_input = input("You > ")
            if user_input.lower() in ['exit', 'quit']: 
                print("\n👋 Goodbye! Happy learning!")
                break
            
            ai_response = session.chat(user_input)
            print(f"AI ({session.role}):\n{ai_response}")
        except EOFError: # Handle Ctrl+D
            print("\n👋 Goodbye! Happy learning!")
            break
        except KeyboardInterrupt: # Handle Ctrl+C
            print("\n👋 Goodbye! Happy learning!")
            break


def main():
    parser = argparse.ArgumentParser(
        description="AI Language Tutor CLI: Practice conversations with a personalized, open-source AI tutor."
    )
    parser.add_argument(
        '--mode',
        type=str,
        default='roleplay',
        choices=['roleplay', 'practice'],
        help='The mode of the session: \"roleplay\" for character interaction, \"practice\" for structured drills.'
    )
    parser.add_argument(
        '--role',
        type=str,
        default='a helpful tutor',
        help='The persona the AI should adopt (e.g., \"French barista\", \"patient teacher\").'
    )
    parser.add_argument(
        '--topic',
        type=str,
        required=True,
        help='The subject matter of the conversation (e.g., \"ordering a pastry\", \"discuting climate change\").'
    )

    args = parser.parse_args()

    run_language_tutor(args.mode, args.role, args.topic)

if __name__ == '__main__':
    main()
