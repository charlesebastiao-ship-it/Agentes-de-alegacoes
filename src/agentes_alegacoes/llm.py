"""Cliente da API da Claude e contabilização de uso/custo."""

from __future__ import annotations

import sys
from dataclasses import dataclass, field
from typing import Callable

import anthropic

from . import MODELO_PADRAO

# Preço do Claude Opus 4.8 por milhão de tokens (USD), para estimativa de custo.
PRECO_ENTRADA = 5.00
PRECO_SAIDA = 25.00
PRECO_CACHE_ESCRITA = 6.25  # ~1.25x da entrada
PRECO_CACHE_LEITURA = 0.50  # ~0.1x da entrada


@dataclass
class Uso:
    """Acumula tokens e estima custo ao longo de várias chamadas."""

    entrada: int = 0
    saida: int = 0
    cache_escrita: int = 0
    cache_leitura: int = 0

    def somar(self, usage) -> None:
        self.entrada += getattr(usage, "input_tokens", 0) or 0
        self.saida += getattr(usage, "output_tokens", 0) or 0
        self.cache_escrita += getattr(usage, "cache_creation_input_tokens", 0) or 0
        self.cache_leitura += getattr(usage, "cache_read_input_tokens", 0) or 0

    @property
    def custo_usd(self) -> float:
        return (
            self.entrada / 1_000_000 * PRECO_ENTRADA
            + self.saida / 1_000_000 * PRECO_SAIDA
            + self.cache_escrita / 1_000_000 * PRECO_CACHE_ESCRITA
            + self.cache_leitura / 1_000_000 * PRECO_CACHE_LEITURA
        )

    def resumo(self) -> str:
        return (
            f"tokens entrada={self.entrada:,} saída={self.saida:,} "
            f"cache(escrita={self.cache_escrita:,}, leitura={self.cache_leitura:,}) "
            f"| custo estimado ≈ US$ {self.custo_usd:,.2f}"
        )


@dataclass
class Resposta:
    texto: str
    entrada: int = 0
    saida: int = 0
    cache_escrita: int = 0
    cache_leitura: int = 0


class ClienteLLM:
    """Encapsula o cliente da Anthropic com streaming e pensamento adaptativo."""

    def __init__(self, api_key: str | None = None, modelo: str = MODELO_PADRAO):
        self.client = (
            anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()
        )
        self.modelo = modelo
        self.uso = Uso()

    def executar(
        self,
        system: str,
        blocos: list[dict],
        max_tokens: int = 32000,
        effort: str = "high",
        transmitir: bool = True,
    ) -> Resposta:
        """Executa uma chamada única e devolve o texto final.

        Usa streaming (obrigatório para max_tokens alto) e pensamento adaptativo,
        conforme recomendado para o Opus 4.8.
        """
        parametros = dict(
            model=self.modelo,
            max_tokens=max_tokens,
            system=system,
            thinking={"type": "adaptive"},
            output_config={"effort": effort},
            messages=[{"role": "user", "content": blocos}],
        )

        with self.client.messages.stream(**parametros) as stream:
            if transmitir:
                for pedaco in stream.text_stream:
                    sys.stdout.write(pedaco)
                    sys.stdout.flush()
                sys.stdout.write("\n")
            mensagem = stream.get_final_message()

        self.uso.somar(mensagem.usage)
        texto = "".join(b.text for b in mensagem.content if b.type == "text")
        return Resposta(
            texto=texto,
            entrada=mensagem.usage.input_tokens or 0,
            saida=mensagem.usage.output_tokens or 0,
            cache_escrita=mensagem.usage.cache_creation_input_tokens or 0,
            cache_leitura=mensagem.usage.cache_read_input_tokens or 0,
        )
