"""Testes de integridade e validação do agente-estudos."""

import asyncio
import datetime
import os
import pathlib
import sys
import unittest
from unittest.mock import MagicMock

# Adiciona o diretório do projeto ao sys.path
BASE_DIR = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))


class TestAgenteEstudosEstrutura(unittest.TestCase):
    """Valida a estrutura de arquivos e diretórios da skill e do agente."""

    def test_skills_arquivos_obrigatorios(self):
        skill_dir = BASE_DIR / "app" / "skills" / "plano-de-estudos"
        self.assertTrue(skill_dir.exists(), f"Diretório da skill não encontrado: {skill_dir}")

        arquivos_esperados = [
            skill_dir / "SKILL.md",
            skill_dir / "references" / "workflow.md",
            skill_dir / "references" / "tecnicas.md",
            skill_dir / "references" / "salvar_agenda.md",
            skill_dir / "assets" / "plano_template.md",
            skill_dir / "assets" / "exemplo_plano.md",
        ]
        for arq in arquivos_esperados:
            self.assertTrue(arq.exists(), f"Arquivo essencial da skill faltando: {arq.name}")

    def test_planos_diretorio_existe(self):
        planos_dir = BASE_DIR / "planos"
        self.assertTrue(planos_dir.exists(), "Diretório planos/ deve existir.")

    def test_env_e_git_ignore(self):
        gitignore = BASE_DIR.parent / ".gitignore"
        self.assertTrue(gitignore.exists(), ".gitignore na raiz deve existir.")
        conteudo = gitignore.read_text(encoding="utf-8")
        self.assertIn(".env", conteudo)
        self.assertIn("planos/", conteudo)


class TestAgenteEstudosLogica(unittest.TestCase):
    """Valida a lógica do agent.py sem necessariamente invocar chamadas de rede da LLM."""

    def test_import_e_instrucao(self):
        from app.agent import instruction_provider, MODEL, root_agent, FerramentasDeArquivo

        # Verifica se o modelo padrão ou de ambiente é respeitado
        self.assertTrue(bool(MODEL))

        # Verifica injeção da data no instruction_provider
        hoje = datetime.date.today()
        data_formatada = hoje.strftime("%d/%m/%Y")
        instrucao = instruction_provider()

        self.assertIn(data_formatada, instrucao)
        self.assertIn("plano-de-estudos", instrucao)
        self.assertIn("Gating", instrucao)

        # Verifica o agente raiz
        self.assertEqual(root_agent.name, "app")
        self.assertEqual(root_agent.model, MODEL)

    def test_ferramentas_de_arquivo_filtro(self):
        from app.agent import FerramentasDeArquivo

        class MockTool:
            def __init__(self, name):
                self.name = name

        class MockEnvironmentToolset:
            async def get_tools(self, readonly_context=None):
                return [
                    MockTool("ReadFile"),
                    MockTool("WriteFile"),
                    MockTool("Execute"),
                    MockTool("EditFile"),
                ]

        class TestSubclass(FerramentasDeArquivo, MockEnvironmentToolset):
            pass

        ferramentas = TestSubclass(environment=MagicMock())
        tools = asyncio.run(ferramentas.get_tools())
        nomes = [t.name for t in tools]

        self.assertIn("ReadFile", nomes)
        self.assertIn("WriteFile", nomes)
        self.assertNotIn("Execute", nomes)
        self.assertNotIn("EditFile", nomes)


if __name__ == "__main__":
    unittest.main()
