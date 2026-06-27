"""
Testes automatizados para validação de prompts.
"""
import pytest
import yaml
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from utils import validate_prompt_structure

PROMPT_FILE = Path(__file__).parent.parent / "prompts" / "bug_to_user_story_v2.yml"


def load_prompts(file_path: str):
    """Carrega prompts do arquivo YAML."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


@pytest.fixture(scope="module")
def prompt_data():
    return load_prompts(PROMPT_FILE)


class TestPrompts:
    def test_prompt_has_system_prompt(self, prompt_data):
        """Verifica se o campo 'system_prompt' existe e não está vazio."""
        assert "system_prompt" in prompt_data, "Campo 'system_prompt' não encontrado no YAML"
        assert prompt_data["system_prompt"].strip(), "system_prompt está vazio"

    def test_prompt_has_role_definition(self, prompt_data):
        """Verifica se o prompt define uma persona (ex: "Você é um Product Manager")."""
        system_prompt = prompt_data.get("system_prompt", "")
        assert "Você é" in system_prompt, "Prompt não define uma persona com 'Você é'"

    def test_prompt_mentions_format(self, prompt_data):
        """Verifica se o prompt exige formato Markdown ou User Story padrão."""
        system_prompt = prompt_data.get("system_prompt", "")
        format_keywords = ["Como [", "User Story", "Critérios de Aceitação", "Dado que", "Então"]
        assert any(kw in system_prompt for kw in format_keywords), (
            "Prompt não menciona formato esperado (User Story / Dado-Quando-Então)"
        )

    def test_prompt_has_few_shot_examples(self, prompt_data):
        """Verifica se o prompt contém exemplos de entrada/saída (técnica Few-shot)."""
        techniques = prompt_data.get("techniques_applied", [])
        system_prompt = prompt_data.get("system_prompt", "")
        has_technique = "few_shot_learning" in techniques
        has_examples = "Relato de Bug:" in system_prompt and "User Story:" in system_prompt
        assert has_technique or has_examples, (
            "Prompt não declara few_shot_learning nas técnicas nem contém exemplos no texto"
        )

    def test_prompt_no_todos(self, prompt_data):
        """Garante que você não esqueceu nenhum `[TODO]` no texto."""
        system_prompt = prompt_data.get("system_prompt", "")
        assert "TODO" not in system_prompt, "system_prompt ainda contém TODOs"

    def test_minimum_techniques(self, prompt_data):
        """Verifica (através dos metadados do yaml) se pelo menos 2 técnicas foram listadas."""
        techniques = prompt_data.get("techniques_applied", [])
        assert len(techniques) >= 2, (
            f"Mínimo de 2 técnicas requeridas, encontradas: {len(techniques)}"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
