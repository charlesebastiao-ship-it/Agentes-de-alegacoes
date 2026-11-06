"""Orquestração do pipeline com controle humano entre as etapas."""

from __future__ import annotations

from pathlib import Path

from . import agentes, relatorio
from .config import Caso
from .documentos import carregar_documentos
from .llm import ClienteLLM


def _salvar(caso: Caso, nome: str, conteudo: str) -> Path:
    caso.pasta_saida.mkdir(parents=True, exist_ok=True)
    destino = caso.pasta_saida / nome
    destino.write_text(conteudo, encoding="utf-8")
    return destino


def _titulo(texto: str) -> None:
    print(f"\n{'=' * 70}\n{texto}\n{'=' * 70}")


def etapa_analisar(cliente: ClienteLLM, caso: Caso, transmitir: bool = True) -> None:
    """Executa os Agentes 1 e 2 e salva os relatórios para revisão humana."""
    docs_orais = carregar_documentos(caso.pasta_prova_oral)
    docs_tecnicos = carregar_documentos(caso.pasta_prova_tecnica)

    if not docs_orais and not docs_tecnicos:
        raise SystemExit(
            "Nenhum documento encontrado. Coloque arquivos (.pdf/.txt/.md) em "
            f"{caso.pasta_prova_oral} e/ou {caso.pasta_prova_tecnica}."
        )

    _titulo(f"AGENTE 1 — Prova Oral  ({len(docs_orais)} documento(s))")
    if docs_orais:
        resp = agentes.executar_prova_oral(cliente, caso, docs_orais, transmitir)
        caminho = _salvar(caso, relatorio.ARQ_PROVA_ORAL, resp.texto)
        print(f"\n→ Salvo em: {caminho}")
    else:
        print("Sem provas orais; etapa pulada.")

    _titulo(f"AGENTE 2 — Materialidade  ({len(docs_tecnicos)} documento(s))")
    if docs_tecnicos:
        resp = agentes.executar_materialidade(cliente, caso, docs_tecnicos, transmitir)
        caminho = _salvar(caso, relatorio.ARQ_MATERIALIDADE, resp.texto)
        print(f"\n→ Salvo em: {caminho}")
    else:
        print("Sem provas técnicas; etapa pulada.")

    _titulo("CONTROLE HUMANO (human-in-the-loop)")
    print(
        "Revise e, se preciso, edite os relatórios salvos em:\n"
        f"  {caso.pasta_saida / relatorio.ARQ_PROVA_ORAL}\n"
        f"  {caso.pasta_saida / relatorio.ARQ_MATERIALIDADE}\n"
        "Depois rode a etapa de redação:  python -m agentes_alegacoes redigir --caso <pasta>"
    )
    print("\n" + cliente.uso.resumo())


def etapa_redigir(
    cliente: ClienteLLM, caso: Caso, revisar: bool = True, transmitir: bool = True
) -> None:
    """Executa o Agente 3 (redação), o Agente 4 (crítica) e a revisão."""
    ro = caso.pasta_saida / relatorio.ARQ_PROVA_ORAL
    rm = caso.pasta_saida / relatorio.ARQ_MATERIALIDADE
    if not ro.exists() and not rm.exists():
        raise SystemExit(
            "Relatórios dos Agentes 1/2 não encontrados. Rode antes: "
            "python -m agentes_alegacoes analisar --caso <pasta>"
        )
    texto_ro = ro.read_text(encoding="utf-8") if ro.exists() else "(sem prova oral nos autos)"
    texto_rm = rm.read_text(encoding="utf-8") if rm.exists() else "(sem prova técnica nos autos)"

    _titulo("AGENTE 3 — Redator Sênior (alegações finais)")
    resp = agentes.executar_redator(cliente, caso, texto_ro, texto_rm, transmitir=transmitir)
    peca = resp.texto
    caminho = _salvar(caso, relatorio.ARQ_ALEGACOES, peca)
    print(f"\n→ Salvo em: {caminho}")

    _titulo("AGENTE 4 — Advogado do Diabo (crítica adversarial)")
    resp_c = agentes.executar_advogado_do_diabo(cliente, caso, peca, transmitir)
    critica = resp_c.texto
    caminho = _salvar(caso, relatorio.ARQ_CRITICA, critica)
    print(f"\n→ Salvo em: {caminho}")

    if revisar:
        _titulo("AGENTE 3 — Revisão (tapando os buracos da crítica)")
        resp_r = agentes.executar_redator(
            cliente, caso, texto_ro, texto_rm, critica_anterior=critica, transmitir=transmitir
        )
        caminho = _salvar(caso, relatorio.ARQ_REVISADAS, resp_r.texto)
        print(f"\n→ Salvo em: {caminho}")

    destino = relatorio.montar_dossie(caso)
    _titulo("DOSSIÊ COMPLETO")
    print(f"→ Documento consolidado salvo em: {destino}")
    print("\n" + cliente.uso.resumo())


def etapa_tudo(
    cliente: ClienteLLM, caso: Caso, revisar: bool = True, transmitir: bool = True
) -> None:
    """Executa o pipeline completo de ponta a ponta (sem pausa)."""
    etapa_analisar(cliente, caso, transmitir)
    etapa_redigir(cliente, caso, revisar=revisar, transmitir=transmitir)
