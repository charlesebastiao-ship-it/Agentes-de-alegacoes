"""Carregamento de documentos do processo (PDF, TXT, MD) como blocos da API."""

from __future__ import annotations

import base64
from dataclasses import dataclass
from pathlib import Path

# Extensões suportadas. PDFs vão como blocos "document"; texto vai inline.
EXT_PDF = {".pdf"}
EXT_TEXTO = {".txt", ".md", ".markdown"}
EXT_SUPORTADAS = EXT_PDF | EXT_TEXTO

# A API aceita até ~32 MB por requisição; avisamos bem antes disso.
LIMITE_PDF_MB = 30


@dataclass
class Documento:
    """Um arquivo do processo pronto para virar bloco de conteúdo da API."""

    caminho: Path
    nome: str

    @property
    def extensao(self) -> str:
        return self.caminho.suffix.lower()

    @property
    def eh_pdf(self) -> bool:
        return self.extensao in EXT_PDF

    def blocos(self) -> list[dict]:
        """Devolve os blocos de conteúdo (rótulo + dado) deste documento."""
        rotulo = {
            "type": "text",
            "text": f"\n\n===== DOCUMENTO: {self.nome} =====\n",
        }
        if self.eh_pdf:
            tamanho_mb = self.caminho.stat().st_size / (1024 * 1024)
            if tamanho_mb > LIMITE_PDF_MB:
                raise ValueError(
                    f"PDF muito grande ({tamanho_mb:.1f} MB): {self.nome}. "
                    f"Divida-o em partes menores que {LIMITE_PDF_MB} MB."
                )
            dados = base64.standard_b64encode(self.caminho.read_bytes()).decode("utf-8")
            corpo = {
                "type": "document",
                "source": {
                    "type": "base64",
                    "media_type": "application/pdf",
                    "data": dados,
                },
                "title": self.nome,
            }
        else:
            texto = self.caminho.read_text(encoding="utf-8", errors="replace")
            corpo = {"type": "text", "text": texto}
        return [rotulo, corpo]


def carregar_documentos(pasta: str | Path) -> list[Documento]:
    """Carrega, em ordem alfabética, todos os documentos suportados da pasta.

    A ordenação por nome torna a montagem do prompt determinística — bom para
    reprodutibilidade e para o cache de prompt.
    """
    pasta = Path(pasta)
    if not pasta.exists():
        return []

    documentos: list[Documento] = []
    for caminho in sorted(pasta.iterdir(), key=lambda p: p.name.lower()):
        if caminho.is_dir():
            continue
        if caminho.suffix.lower() not in EXT_SUPORTADAS:
            continue
        documentos.append(Documento(caminho=caminho, nome=caminho.name))
    return documentos


def montar_blocos(
    documentos: list[Documento],
    instrucao_final: str,
    cachear: bool = True,
) -> list[dict]:
    """Monta a lista de blocos do turno do usuário: documentos + instrução.

    Se `cachear`, marca o último bloco de documento com cache_control ephemeral,
    para que chamadas subsequentes que reusem o mesmo contexto paguem menos.
    """
    blocos: list[dict] = []
    for doc in documentos:
        blocos.extend(doc.blocos())

    if cachear and blocos:
        # Marca o fim do contexto documental (antes da instrução variável).
        blocos[-1] = {**blocos[-1], "cache_control": {"type": "ephemeral"}}

    blocos.append({"type": "text", "text": instrucao_final})
    return blocos
