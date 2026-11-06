"""Execução de cada um dos quatro agentes."""

from __future__ import annotations

from .config import Caso
from .documentos import Documento, montar_blocos
from .llm import ClienteLLM, Resposta
from . import prompts


def executar_prova_oral(
    cliente: ClienteLLM, caso: Caso, documentos: list[Documento], transmitir: bool = True
) -> Resposta:
    instrucao = (
        "Os documentos acima são as provas ORAIS deste processo (termos de "
        "declaração, interrogatórios e transcrições de audiência). Produza o "
        "relatório da prova oral seguindo rigorosamente a estrutura definida."
    )
    blocos = montar_blocos(documentos, instrucao)
    return cliente.executar(
        system=prompts.prompt_prova_oral(caso),
        blocos=blocos,
        max_tokens=32000,
        transmitir=transmitir,
    )


def executar_materialidade(
    cliente: ClienteLLM, caso: Caso, documentos: list[Documento], transmitir: bool = True
) -> Resposta:
    instrucao = (
        "Os documentos acima são as provas TÉCNICAS deste processo (laudos, "
        "perícias, ERBs, extratos, autos de apreensão). Produza o relatório da "
        "materialidade seguindo rigorosamente a estrutura definida."
    )
    blocos = montar_blocos(documentos, instrucao)
    return cliente.executar(
        system=prompts.prompt_materialidade(caso),
        blocos=blocos,
        max_tokens=32000,
        transmitir=transmitir,
    )


def executar_redator(
    cliente: ClienteLLM,
    caso: Caso,
    relatorio_prova_oral: str,
    relatorio_materialidade: str,
    critica_anterior: str | None = None,
    transmitir: bool = True,
) -> Resposta:
    """Redige a peça a partir dos relatórios 1 e 2.

    Se `critica_anterior` for fornecida (saída do Agente 4), o redator produz
    uma versão revisada que tapa os buracos apontados.
    """
    partes = [
        "# RELATÓRIO DA PROVA ORAL (Agente 1)\n",
        relatorio_prova_oral,
        "\n\n# RELATÓRIO DA MATERIALIDADE (Agente 2)\n",
        relatorio_materialidade,
    ]
    if critica_anterior:
        partes += [
            "\n\n# CRÍTICA DO ADVOGADO DO DIABO (Agente 4) À VERSÃO ANTERIOR\n",
            critica_anterior,
            "\n\nReescreva as alegações finais tapando cada buraco apontado na "
            "crítica acima, sem inventar prova nova. Mantenha a estrutura da peça.",
        ]
    else:
        partes.append(
            "\n\nCom base exclusivamente nos dois relatórios acima, redija as "
            "alegações finais seguindo a estrutura definida."
        )

    blocos = montar_blocos([], "".join(partes))
    # Como não há documentos, montar_blocos devolve só a instrução; marcamos o
    # contexto (relatórios) para cache manualmente.
    blocos[0] = {**blocos[0], "cache_control": {"type": "ephemeral"}}
    return cliente.executar(
        system=prompts.prompt_redator(caso),
        blocos=blocos,
        max_tokens=32000,
        transmitir=transmitir,
    )


def executar_advogado_do_diabo(
    cliente: ClienteLLM, caso: Caso, peca: str, transmitir: bool = True
) -> Resposta:
    instrucao = (
        "# ALEGAÇÕES FINAIS A SEREM ATACADAS\n"
        + peca
        + "\n\nAtaque a peça acima produzindo a crítica adversarial completa."
    )
    blocos = [{"type": "text", "text": instrucao}]
    return cliente.executar(
        system=prompts.prompt_advogado_do_diabo(caso),
        blocos=blocos,
        max_tokens=16000,
        transmitir=transmitir,
    )
