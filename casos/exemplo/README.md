# Caso de exemplo (FICTÍCIO)

Todos os documentos deste caso são **fictícios** e existem apenas para
demonstrar o funcionamento do pipeline. Nomes, números de processo, laudos e
depoimentos são inventados.

O caso foi montado para exercitar o cruzamento típico da análise:

- **Prova oral** (`prova_oral/`): a testemunha João Souza afirma na delegacia
  ter *visto* o réu atirar, mas em juízo recua e diz apenas ter *ouvido* os
  disparos. O réu nega a autoria. → gatilho clássico do Art. 155 do CPP.
- **Prova técnica** (`prova_tecnica/`): a necropsia confirma a materialidade
  (dois PAF), a balística confirma dois disparos da mesma arma mas **sem arma
  apreendida** para confronto, e a ERB coloca o celular do réu na área da cena
  no horário — com as ressalvas técnicas de cobertura.

Isso dá aos agentes contradições reais para mapear e um cotejo prova oral x
prova técnica com pontos fortes e fracos.

## Como rodar

```bash
python -m agentes_alegacoes tudo --caso casos/exemplo
```

Ou, com controle humano entre as etapas:

```bash
python -m agentes_alegacoes analisar --caso casos/exemplo
# revise casos/exemplo/saida/01_prova_oral.md e 02_materialidade.md
python -m agentes_alegacoes redigir --caso casos/exemplo
```

As saídas são gravadas em `casos/exemplo/saida/` (ignorada pelo git).
