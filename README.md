# Agentes de Alegações

Pipeline de **quatro agentes de IA** (Claude Opus 4.8) que lê um processo penal
bruto, cruza e relaciona toda a prova, e produz **alegações finais**
fundamentadas — terminando em um **dossiê extenso que une e relaciona todos os
dados**.

A ideia central é a **divisão de trabalho**: cada agente faz uma coisa muito
bem, e o operador (advogado/promotor) mantém o controle entre as etapas.

## Os quatro agentes

| # | Agente | Faz | Ignora |
|---|--------|-----|--------|
| 1 | **Prova Oral** (Dinâmica e Autoria) | Cruza o que cada pessoa disse na **delegacia** x na **audiência**, monta linha do tempo evolutiva por pessoa e aponta contradições, omissões e confirmações. Mapeia o Art. 155 do CPP. | Laudos e prova técnica |
| 2 | **Materialidade** (Prova Técnica) | Atesta a materialidade a partir de laudos, necropsia, balística, ERBs, extratos: o crime ocorreu? como? datas, horários e quantidades. | As "histórias" dos depoimentos |
| 3 | **Redator Sênior** (Subsunção e Retórica) | Recebe só o "suco" já mastigado pelos Agentes 1 e 2, faz o **cotejo analítico** (prova oral x prova técnica) e redige a peça com silogismo (premissa maior/menor/conclusão). | O processo bruto e desorganizado |
| 4 | **Advogado do Diabo** (Crítica) | Assume a **parte contrária** e ataca a peça pronta: aponta as 3 maiores falhas lógicas, ausências de prova e brechas — e como blindá-las. | — |

O **controle é seu**: os relatórios dos Agentes 1 e 2 são salvos em Markdown
**editável** antes de o Agente 3 redigir. Se um agente interpretou algo errado,
você corrige o texto e a peça final nasce sobre uma base 100% controlada.

## Instalação

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e .            # instala o pacote e suas dependências
cp .env.example .env        # e preencha ANTHROPIC_API_KEY
```

> A chave também pode ser exportada (`export ANTHROPIC_API_KEY=...`) ou obtida
> via `ant auth login`. Sem chave, o pipeline avisa e não roda os agentes.

## Estrutura de um caso

```
casos/
└── meu_caso/
    ├── caso.yaml          # metadados (opcional): nome, tipo_peca, tese, réu...
    ├── prova_oral/        # depoimentos, termos, interrogatórios, audiências
    │   ├── *.pdf  *.txt  *.md
    └── prova_tecnica/     # laudos, necropsia, balística, ERBs, extratos
        └── *.pdf  *.txt  *.md
```

Formatos aceitos: **PDF, TXT, MD**. Os arquivos são lidos em ordem alfabética
(nomeie com prefixos `01_`, `02_`… para controlar a ordem). PDFs vão direto à
API como documentos.

### `caso.yaml`

```yaml
nome: "Ação Penal nº 000-00"
tipo_peca: acusacao      # acusacao | defesa  → de quem é a peça
tese: condenacao         # condenacao | absolvicao
reu: "Fulano de Tal"
vitima: "Beltrano"
resumo: "Breve relato dos fatos."
```

`tipo_peca` e `tese` orientam o Agente 3 (o que sustentar) e o Agente 4 (quem é
a parte contrária que ataca).

## Uso

Pipeline completo, de ponta a ponta:

```bash
python -m agentes_alegacoes tudo --caso casos/exemplo
```

Com **controle humano** entre as etapas (recomendado):

```bash
# Etapa 1 — Agentes 1 e 2. Gera relatórios editáveis.
python -m agentes_alegacoes analisar --caso casos/exemplo

# ... revise/edite casos/exemplo/saida/01_prova_oral.md e 02_materialidade.md ...

# Etapa 2 — Agentes 3 e 4 + revisão + dossiê.
python -m agentes_alegacoes redigir --caso casos/exemplo
```

Opções úteis: `--sem-revisao` (não reescreve após a crítica), `--silencioso`
(não transmite o texto em tempo real), `--modelo <id>`, `--caso <pasta>`.

Remontar só o dossiê a partir dos arquivos já gerados/editados:

```bash
python -m agentes_alegacoes dossie --caso casos/exemplo
```

## Saídas

Gravadas em `<caso>/saida/`:

| Arquivo | Conteúdo |
|---------|----------|
| `01_prova_oral.md` | Relatório do Agente 1 |
| `02_materialidade.md` | Relatório do Agente 2 |
| `03_alegacoes_finais.md` | Peça do Agente 3 |
| `04_critica_advogado_do_diabo.md` | Crítica do Agente 4 |
| `05_alegacoes_revisadas.md` | Peça reescrita tapando os buracos |
| `00_dossie_completo.md` | **Dossiê extenso unindo e relacionando tudo** |

## Caso de exemplo

O repositório traz um caso **fictício** pronto em `casos/exemplo/` (homicídio,
com contradição entre a fase policial e a judicial). Veja
`casos/exemplo/README.md`.

## Testes

```bash
pip install pytest
pytest          # testes offline (não consomem API)
```

## Avisos

- Ferramenta de **apoio**. As peças e relatórios gerados por IA **devem ser
  revisados por um profissional** antes de qualquer uso processual.
- Nada é enviado além do necessário: os documentos vão à API da Anthropic para
  a análise. Não use com dados sigilosos sem verificar sua política de dados.
- Custo estimado é exibido ao final de cada execução (tokens e US$ aproximados).
