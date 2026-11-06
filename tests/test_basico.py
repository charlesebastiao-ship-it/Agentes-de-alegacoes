"""Testes que não dependem da API (carregamento, config, montagem de blocos)."""

from pathlib import Path

import pytest

from agentes_alegacoes.config import Caso, carregar_caso
from agentes_alegacoes.documentos import carregar_documentos, montar_blocos
from agentes_alegacoes import prompts, relatorio

RAIZ = Path(__file__).resolve().parents[1]
CASO_EXEMPLO = RAIZ / "casos" / "exemplo"


def test_carregar_caso_exemplo():
    caso = carregar_caso(CASO_EXEMPLO)
    assert caso.tipo_peca == "acusacao"
    assert caso.tese == "condenacao"
    assert caso.reu == "Carlos Pereira"
    assert "condenação" in caso.pedido
    assert "Carlos Pereira" in caso.cabecalho()


def test_caso_valida_campos():
    with pytest.raises(ValueError):
        Caso(raiz=CASO_EXEMPLO, tipo_peca="invalido")
    with pytest.raises(ValueError):
        Caso(raiz=CASO_EXEMPLO, tese="invalida")


def test_carregar_documentos_ordenados():
    docs = carregar_documentos(CASO_EXEMPLO / "prova_oral")
    assert len(docs) == 3
    nomes = [d.nome for d in docs]
    assert nomes == sorted(nomes, key=str.lower)
    assert all(not d.eh_pdf for d in docs)


def test_montar_blocos_marca_cache_e_instrucao():
    docs = carregar_documentos(CASO_EXEMPLO / "prova_tecnica")
    blocos = montar_blocos(docs, "INSTRUÇÃO FINAL")
    # Último bloco é sempre a instrução.
    assert blocos[-1]["text"] == "INSTRUÇÃO FINAL"
    # O bloco anterior (fim do contexto documental) deve ter cache_control.
    assert blocos[-2].get("cache_control") == {"type": "ephemeral"}


def test_prompts_incluem_contexto_do_caso():
    caso = carregar_caso(CASO_EXEMPLO)
    assert "Art. 155" in prompts.prompt_prova_oral(caso)
    assert "MATERIALIDADE" in prompts.prompt_materialidade(caso)
    assert "condenação do réu" in prompts.prompt_redator(caso)
    # O advogado do diabo assume a parte contrária (defesa).
    assert "defesa" in prompts.prompt_advogado_do_diabo(caso)


def test_montar_dossie_com_saida_parcial(tmp_path):
    caso = Caso(raiz=tmp_path, nome="Teste")
    caso.pasta_saida.mkdir(parents=True)
    (caso.pasta_saida / relatorio.ARQ_PROVA_ORAL).write_text("conteudo oral", encoding="utf-8")
    (caso.pasta_saida / relatorio.ARQ_ALEGACOES).write_text("peca final", encoding="utf-8")

    destino = relatorio.montar_dossie(caso)
    texto = destino.read_text(encoding="utf-8")
    assert "DOSSIÊ COMPLETO" in texto
    assert "conteudo oral" in texto
    assert "peca final" in texto
