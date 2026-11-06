"""Montagem do dossiê final — o arquivo extenso que une e relaciona tudo."""

from __future__ import annotations

from pathlib import Path

from .config import Caso

# Nomes canônicos dos artefatos produzidos pelo pipeline.
ARQ_PROVA_ORAL = "01_prova_oral.md"
ARQ_MATERIALIDADE = "02_materialidade.md"
ARQ_ALEGACOES = "03_alegacoes_finais.md"
ARQ_CRITICA = "04_critica_advogado_do_diabo.md"
ARQ_REVISADAS = "05_alegacoes_revisadas.md"
ARQ_DOSSIE = "00_dossie_completo.md"


def _ler_se_existir(pasta: Path, nome: str) -> str | None:
    caminho = pasta / nome
    if caminho.exists():
        return caminho.read_text(encoding="utf-8")
    return None


def montar_dossie(caso: Caso) -> Path:
    """Une todos os artefatos existentes em um único documento navegável.

    O dossiê reúne, em ordem lógica, os relatórios de prova, a peça final (usando
    a versão revisada quando houver), a crítica adversarial e os metadados do
    caso — cumprindo o objetivo de "unir e relacionar todos os dados".
    """
    saida = caso.pasta_saida
    saida.mkdir(parents=True, exist_ok=True)

    prova_oral = _ler_se_existir(saida, ARQ_PROVA_ORAL)
    materialidade = _ler_se_existir(saida, ARQ_MATERIALIDADE)
    alegacoes = _ler_se_existir(saida, ARQ_ALEGACOES)
    critica = _ler_se_existir(saida, ARQ_CRITICA)
    revisadas = _ler_se_existir(saida, ARQ_REVISADAS)

    peca_final = revisadas or alegacoes
    rotulo_peca = "revisada" if revisadas else "original"

    partes: list[str] = []
    partes.append(f"# DOSSIÊ COMPLETO — {caso.nome}\n")
    partes.append("> Documento gerado automaticamente pelo pipeline Agentes de "
                  "Alegações. Revise antes de qualquer uso processual.\n")

    # Metadados
    partes.append("## Identificação do caso\n")
    partes.append(caso.cabecalho() + "\n")

    # Sumário
    partes.append("## Sumário\n")
    itens = []
    if prova_oral:
        itens.append("1. Relatório da Prova Oral (Agente 1)")
    if materialidade:
        itens.append("2. Relatório da Materialidade (Agente 2)")
    if peca_final:
        itens.append(f"3. Alegações Finais — versão {rotulo_peca} (Agente 3)")
    if critica:
        itens.append("4. Crítica do Advogado do Diabo (Agente 4)")
    partes.append("\n".join(itens) + "\n")

    def secao(titulo: str, conteudo: str | None) -> None:
        if not conteudo:
            return
        partes.append(f"\n---\n\n# {titulo}\n")
        partes.append(conteudo.strip() + "\n")

    secao("1. Relatório da Prova Oral (Agente 1)", prova_oral)
    secao("2. Relatório da Materialidade (Agente 2)", materialidade)
    secao(f"3. Alegações Finais — versão {rotulo_peca} (Agente 3)", peca_final)
    if revisadas and alegacoes:
        secao("3-A. Alegações Finais — versão original (antes da crítica)", alegacoes)
    secao("4. Crítica do Advogado do Diabo (Agente 4)", critica)

    destino = saida / ARQ_DOSSIE
    destino.write_text("\n".join(partes), encoding="utf-8")
    return destino
