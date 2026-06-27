"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import sys
from dotenv import load_dotenv
from langchain import hub
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header

load_dotenv()

def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """Valida a estrutura do prompt antes do push."""
    errors = []
    
    required_fields = ["description", "system_prompt", "version"]
    for field in required_fields:
        if field not in prompt_data:
            errors.append(f"Campo obrigatório faltando: {field}")

    system_prompt = prompt_data.get("system_prompt", "").strip()
    if not system_prompt:
        errors.append("system_prompt está vazio")
    if "TODO" in system_prompt:
        errors.append("system_prompt ainda contém TODOs")

    techniques = prompt_data.get("techniques_applied", [])
    if len(techniques) < 2:
        errors.append(f"Mínimo de 2 técnicas, encontradas: {len(techniques)}")

    return (len(errors) == 0, errors)

def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """Faz push do prompt para o LangSmith Hub (público)."""
    try:
        system_prompt = prompt_data["system_prompt"]

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
        ])

        print(f"Publicando '{prompt_name}' no Hub...")

        # is_public=True deixa o prompt visível publicamente (exigência
        # da entrega). hub.push resolve o owner pela API key autenticada.
        url = hub.push(
            prompt_name,
            prompt,
            new_repo_is_public=True,
            new_repo_description=prompt_data.get("description", ""),
            tags=prompt_data.get("tags", []),
        )

        print(f"Publicado com sucesso!")
        print(f"URL: {url}")
        return True

    except Exception as e:
        print(f"Erro ao publicar: {e}")
        return False

def main():
    """Função principal."""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS PARA O HUB")

    if not check_env_vars(["LANGSMITH_API_KEY"]):
        return 1

    yaml_path = "prompts/bug_to_user_story_v2.yml"
    prompt_data = load_yaml(yaml_path)
    if prompt_data is None:
        print(f"Não foi possível carregar {yaml_path}")
        return 1

    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("Prompt inválido:")
        for err in errors:
            print(f"- {err}")
        return 1
    print("Validação passou")

    prompt_name = "bug_to_user_story_v2"
    success = push_prompt_to_langsmith(prompt_name, prompt_data)

    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
