"""Configuração de um caso e da execução do pipeline."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


# Pastas esperadas dentro de um caso.
PASTA_PROVA_ORAL = "prova_oral"
PASTA_PROVA_TECNICA = "prova_tecnica"
PASTA_SAIDA = "saida"

TIPOS_PECA = {"acusacao", "defesa"}
TESES = {"condenacao", "absolvicao"}


@dataclass
class Caso:
    """Metadados de um caso, lidos de `caso.yaml` na pasta do caso."""

    raiz: Path
    nome: str = "Processo sem identificação"
    numero: str = ""
    tipo_peca: str = "acusacao"  # acusacao | defesa
    tese: str = "condenacao"  # condenacao | absolvicao
    reu: str = ""
    vitima: str = ""
    resumo: str = ""
    observacoes: str = ""

    def __post_init__(self) -> None:
        self.raiz = Path(self.raiz)
        if self.tipo_peca not in TIPOS_PECA:
            raise ValueError(
                f"tipo_peca inválido: {self.tipo_peca!r}. Use um de {sorted(TIPOS_PECA)}."
            )
        if self.tese not in TESES:
            raise ValueError(
                f"tese inválida: {self.tese!r}. Use uma de {sorted(TESES)}."
            )

    # --- caminhos ---------------------------------------------------------
    @property
    def pasta_prova_oral(self) -> Path:
        return self.raiz / PASTA_PROVA_ORAL

    @property
    def pasta_prova_tecnica(self) -> Path:
        return self.raiz / PASTA_PROVA_TECNICA

    @property
    def pasta_saida(self) -> Path:
        return self.raiz / PASTA_SAIDA

    # --- descrições legíveis para prompts ---------------------------------
    @property
    def parte(self) -> str:
        return "acusação (Ministério Público)" if self.tipo_peca == "acusacao" else "defesa"

    @property
    def pedido(self) -> str:
        if self.tese == "condenacao":
            return "condenação do réu"
        return "absolvição do réu"

    def cabecalho(self) -> str:
        """Bloco de contexto do caso, injetado nos prompts dos agentes."""
        linhas = [f"- Processo: {self.nome}"]
        if self.numero:
            linhas.append(f"- Número: {self.numero}")
        if self.reu:
            linhas.append(f"- Réu: {self.reu}")
        if self.vitima:
            linhas.append(f"- Vítima: {self.vitima}")
        linhas.append(f"- Peça a ser produzida: alegações finais da {self.parte}")
        linhas.append(f"- Tese sustentada: {self.pedido}")
        if self.resumo:
            linhas.append(f"- Resumo dos fatos: {self.resumo}")
        if self.observacoes:
            linhas.append(f"- Observações do operador: {self.observacoes}")
        return "\n".join(linhas)


def carregar_caso(raiz: str | Path) -> Caso:
    """Lê `caso.yaml` (se existir) e devolve um objeto Caso."""
    raiz = Path(raiz)
    if not raiz.exists():
        raise FileNotFoundError(f"Pasta do caso não encontrada: {raiz}")

    dados: dict = {}
    arquivo = raiz / "caso.yaml"
    if arquivo.exists():
        if yaml is None:
            raise RuntimeError(
                "PyYAML não está instalado, mas há um caso.yaml. Rode: pip install pyyaml"
            )
        dados = yaml.safe_load(arquivo.read_text(encoding="utf-8")) or {}

    campos_validos = {
        "nome", "numero", "tipo_peca", "tese", "reu", "vitima", "resumo", "observacoes",
    }
    dados = {k: v for k, v in dados.items() if k in campos_validos and v is not None}
    return Caso(raiz=raiz, **dados)


def obter_api_key() -> str | None:
    """Retorna a chave da API do ambiente, se houver (o SDK também a resolve)."""
    return os.environ.get("ANTHROPIC_API_KEY")
