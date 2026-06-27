"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import sys
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

def pull_prompts_from_langsmith():
    """Faz pull do prompt v1 do Hub e salva localmente em YAML."""
    prompt_name = "leonanluppi/bug_to_user_story_v1"
    output_path = "prompts/bug_to_user_story_v1.yml"

    print(f"Puxando prompt do Hub: {prompt_name}")

    prompt = hub.pull(prompt_name)

    messages = prompt.messages
    system_msg = next((m.prompt.template for m in messages if "System" in type(m).__name__), "")
    human_msg  = next((m.prompt.template for m in messages if "Human"  in type(m).__name__), "")

    prompt_data = {
        "bug_to_user_story_v1": {
            "description": "Prompt para converter relatos de bugs em User Stories",
            "system_prompt": system_msg,
            "user_prompt": human_msg,
            "version": "v1",
            "tags": ["bug-analysis", "user-story", "product-management"],
        }
    }

    print(f"Salvando prompt em: {output_path}")

    if save_yaml(prompt_data, output_path):
        print("Pull e salvamento concluídos com sucesso!")
        return True
    else:
        print("Falha ao salvar o prompt.")
        return False

def main():
    """Função principal."""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")
    
    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    try:
        success = pull_prompts_from_langsmith()
        return 0 if success else 1
    except Exception as e:
        print(f"Erro ao puxar prompts: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())