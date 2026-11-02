# Agente de Estudos

Agente inteligente construído com o **Google ADK** (Agent Development Kit) em Python, movido a skills, que monta planos de estudo personalizados com base na metodologia de estudo baseada em evidências (revisão espaçada, recuperação ativa, checkpoints semanais e exportação para o Google Agenda).

## Estrutura do Projeto

- `app/agent.py`: Definição do agente raiz (`root_agent`), ferramentas de arquivo filtradas (`FerramentasDeArquivo`) e conjunto de skills (`SkillToolset`).
- `app/skills/plano-de-estudos/`: Skill de planejamento de estudos com regras de ativação (gating) e documentação L3.
- `planos/`: Diretório onde o agente grava os arquivos `plano-de-estudos.csv`.

## Execução Local

```bash
cd agente-estudos
uv sync
uv run adk web --allow_origins="*"
```
