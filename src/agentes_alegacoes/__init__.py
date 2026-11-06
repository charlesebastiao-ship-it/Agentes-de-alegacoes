"""Agentes de Alegações — pipeline de análise de processos penais com IA.

Quatro agentes especializados dividem o trabalho de ler um processo penal
bruto e produzir uma peça de alegações finais fundamentada:

1. Prova Oral      — cruza depoimentos da fase policial x judicial.
2. Materialidade   — atesta a prova técnica (laudos, ERBs, extratos).
3. Redator Sênior  — faz o cotejo analítico e redige a peça.
4. Advogado do Diabo — ataca a peça para revelar seus pontos fracos.

O controle é do operador (human-in-the-loop): os relatórios dos agentes 1 e 2
são salvos em Markdown editável antes de o agente 3 redigir a peça final.
"""

__version__ = "0.1.0"

MODELO_PADRAO = "claude-opus-4-8"
