"""Agente de Estudos - Google ADK.

Monta planos de estudo personalizados com revisão espaçada,
checkpoints de autoavaliação e exportação de agenda CSV para o Google Agenda.
"""

import datetime
import os
import pathlib
from dotenv import load_dotenv

try:
    from google.adk import Agent
except ImportError:
    from google.adk.agents import Agent

try:
    from google.adk.environment import LocalEnvironment
except ImportError:
    from google.adk.environments import LocalEnvironment

try:
    from google.adk.tools.environment import EnvironmentToolset
except ImportError:
    from google.adk.tools import EnvironmentToolset

try:
    from google.adk.skills import load_skill_from_dir
except ImportError:
    from google.adk.tools.skill_toolset import load_skill_from_dir

try:
    from google.adk.tools.skill_toolset import SkillToolset
except ImportError:
    from google.adk.skills import SkillToolset


# Caminhos absolutos calculados a partir deste arquivo
APP_DIR = pathlib.Path(__file__).resolve().parent
PROJECT_DIR = APP_DIR.parent
PLANOS_DIR = PROJECT_DIR / "planos"
SKILL_DIR = APP_DIR / "skills" / "plano-de-estudos"

# Garante que a pasta de planos existe
PLANOS_DIR.mkdir(parents=True, exist_ok=True)

# Carrega variáveis de ambiente do .env do projeto
load_dotenv(PROJECT_DIR / ".env")

MODEL = os.getenv("MODEL", "gemini-3.8-flash")

DIAS_DA_SEMANA = [
    "segunda-feira",
    "terça-feira",
    "quarta-feira",
    "quinta-feira",
    "sexta-feira",
    "sábado",
    "domingo",
]


class FerramentasDeArquivo(EnvironmentToolset):
    """Subclasse de EnvironmentToolset que restringe as ferramentas expostas a ReadFile e WriteFile."""

    async def get_tools(self, readonly_context=None):
        tools = await super().get_tools(readonly_context)
        return [t for t in tools if t.name in ("ReadFile", "WriteFile")]


def instruction_provider(readonly_context=None) -> str:
    """Injeta dinamicamente a data atual e a persona de mentor de estudos."""
    hoje = datetime.date.today()
    dia_semana = DIAS_DA_SEMANA[hoje.weekday()]
    data_formatada = hoje.strftime("%d/%m/%Y")

    return f"""Você é um mentor especialista em aprendizagem e organização de estudos.
Sua missão é ajudar o usuário a montar um plano de estudos personalizado, eficiente e executável.
Hoje é {data_formatada} ({dia_semana}). Use sempre esta data como ponto de referência para calcular datas relativas como "segunda que vem", "amanhã" ou datas sem o ano especificado.

Você tem à sua disposição a skill `plano-de-estudos`. Siga rigorosamente o fluxo e as diretrizes dessa skill:
1. Gating obrigatório: não avance para o planejamento e NÃO carregue nenhum recurso L3 (referências ou assets) até coletar as 4 informações obrigatórias (Objetivo, Prazo, Disponibilidade e Nível atual). Se faltar algo, faça uma única pergunta amigável e objetiva apenas sobre o que falta.
2. Quando todas as informações estiverem presentes, siga o fluxo de trabalho da skill, preencha o template completo e grave o arquivo CSV usando a ferramenta `WriteFile`.
3. Responda sempre em português do Brasil, em tom de mentor direto, encorajador e prático.
"""


# Carrega a skill do plano de estudos
skill_plano = load_skill_from_dir(SKILL_DIR)

# Configura o SkillToolset com a skill carregada
skill_toolset = SkillToolset(skills=[skill_plano])

# Configura o EnvironmentToolset filtrado, com working_dir restrito à pasta planos/
ferramentas_arquivo = FerramentasDeArquivo(
    environment=LocalEnvironment(working_dir=str(PLANOS_DIR))
)

# Agente raiz do ADK
root_agent = Agent(
    name="app",
    model=MODEL,
    instruction=instruction_provider,
    tools=[
        skill_toolset,
        ferramentas_arquivo,
    ],
)
