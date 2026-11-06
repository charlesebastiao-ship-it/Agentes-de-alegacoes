"""Interface de linha de comando do pipeline Agentes de Alegações."""

from __future__ import annotations

import argparse
import sys

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:  # dotenv é opcional
    pass

from . import __version__, MODELO_PADRAO, pipeline, relatorio
from .config import carregar_caso, obter_api_key
from .llm import ClienteLLM


def _construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="agentes_alegacoes",
        description=(
            "Pipeline de 4 agentes para analisar um processo penal e produzir "
            "alegações finais fundamentadas."
        ),
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    sub = p.add_subparsers(dest="comando", required=True)

    def comuns(sp: argparse.ArgumentParser) -> None:
        sp.add_argument(
            "--caso", required=True, help="Pasta do caso (contém prova_oral/ e prova_tecnica/)."
        )
        sp.add_argument("--modelo", default=MODELO_PADRAO, help="ID do modelo Claude.")
        sp.add_argument(
            "--silencioso",
            action="store_true",
            help="Não transmitir o texto em tempo real (mostra só ao final).",
        )

    sp = sub.add_parser("analisar", help="Etapa 1: roda os Agentes 1 e 2 (para revisão humana).")
    comuns(sp)

    sp = sub.add_parser("redigir", help="Etapa 2: roda os Agentes 3 e 4 e monta o dossiê.")
    comuns(sp)
    sp.add_argument(
        "--sem-revisao",
        action="store_true",
        help="Não reescrever a peça após a crítica do Advogado do Diabo.",
    )

    sp = sub.add_parser("tudo", help="Roda o pipeline completo de ponta a ponta.")
    comuns(sp)
    sp.add_argument("--sem-revisao", action="store_true", help="Pular a revisão pós-crítica.")

    sp = sub.add_parser("dossie", help="Apenas remonta o dossiê a partir dos arquivos existentes.")
    sp.add_argument("--caso", required=True, help="Pasta do caso.")

    return p


def main(argv: list[str] | None = None) -> int:
    args = _construir_parser().parse_args(argv)
    caso = carregar_caso(args.caso)

    if args.comando == "dossie":
        destino = relatorio.montar_dossie(caso)
        print(f"Dossiê remontado em: {destino}")
        return 0

    if obter_api_key() is None:
        print(
            "ATENÇÃO: ANTHROPIC_API_KEY não encontrada no ambiente.\n"
            "Defina-a (export ANTHROPIC_API_KEY=... ) ou crie um arquivo .env. "
            "O SDK também aceita login via `ant auth login`.",
            file=sys.stderr,
        )

    cliente = ClienteLLM(modelo=args.modelo)
    transmitir = not args.silencioso

    if args.comando == "analisar":
        pipeline.etapa_analisar(cliente, caso, transmitir=transmitir)
    elif args.comando == "redigir":
        pipeline.etapa_redigir(cliente, caso, revisar=not args.sem_revisao, transmitir=transmitir)
    elif args.comando == "tudo":
        pipeline.etapa_tudo(cliente, caso, revisar=not args.sem_revisao, transmitir=transmitir)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
