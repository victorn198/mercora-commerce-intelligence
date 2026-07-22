# Demo and interview guide

## Demonstracao em portugues (90 segundos)

1. **Problema:** a lideranca precisava identificar rapidamente o que movia receita, recompra e qualidade de entrega, sem misturar fatos de pedidos, itens e pagamentos.
2. **Solucao:** construi um pipeline reproduzivel de CSV para Python, DuckDB e marts SQL, consumidos por uma aplicacao Dash bilingue.
3. **Command Center:** comeco pela situacao do periodo e pela fila de prioridades. Todos os valores, comparacoes e alertas sao calculados a partir dos filtros.
4. **Investigacao:** em Revenue Explorer e Retention, uso filtros coordenados e drill-down para localizar categorias, regioes, vendedores e grupos de clientes responsaveis pelo resultado.
5. **Acao e confianca:** Customer Explorer leva ao detalhe anonimizado; Data Trust explica origem, granularidade, definicao das metricas e testes de qualidade.
6. **Decisao tecnica:** pedidos, itens e pagamentos permanecem separados para evitar multiplicacao de receita. A data operacional deixa explicito que a base cobre 2016-2018.

## English demo (90 seconds)

1. **Problem:** leaders needed to identify the drivers of revenue, repeat purchasing, and delivery quality without mixing order, item, and payment facts.
2. **Solution:** I built a reproducible CSV-to-Python-to-DuckDB pipeline, SQL marts, and a bilingual Dash application.
3. **Command Center:** I start with the selected period and the action queue. Values, comparisons, and alerts are calculated from the current filters.
4. **Investigation:** Revenue Explorer and Retention provide coordinated filtering and drill-down across categories, regions, sellers, and customer groups.
5. **Action and trust:** Customer Explorer exposes anonymous customer detail, while Data Trust documents lineage, grain, metric definitions, and quality checks.
6. **Technical decision:** orders, items, and payments remain separate to prevent revenue multiplication. The operating date makes the 2016-2018 coverage explicit.

## Perguntas de entrevista

### Por que DuckDB?

Ele permite uma camada analitica SQL reproduzivel, rapida e portatil, sem exigir infraestrutura de servidor para esta escala de portfolio. Em producao, os mesmos marts poderiam migrar para um warehouse gerenciado.

### Como voce garantiu que a receita nao fosse duplicada?

A receita e calculada no grao de item e agregada antes de qualquer combinacao com pagamentos ou outras relacoes de um-para-muitos. O pipeline inclui reconciliacao automatica entre fatos e marts.

### O que e dado real e o que e simulado?

Os registros vem da base publica anonimizada da Olist. A empresa Mercora e o contexto operacional sao ficticios. Nenhuma data historica e apresentada como atual.

### Qual decisao o dashboard suporta?

Ele ajuda a priorizar desvios de receita, entrega e retencao; identificar categorias, vendedores e localidades responsaveis; e chegar ao detalhe necessario para uma acao operacional.

### Como voce validaria isso em producao?

Alem dos testes existentes, eu definiria donos de metricas, SLAs de atualizacao, alertas de qualidade, controle de acesso, observabilidade do pipeline e validacao periodica com usuarios de negocio.

## Interview questions

### Why DuckDB?

It provides a fast, portable, and reproducible SQL analytics layer without requiring server infrastructure at portfolio scale. The marts could later move to a managed warehouse.

### How did you prevent duplicated revenue?

Revenue is calculated at item grain and aggregated before joining payments or other one-to-many relationships. Automated reconciliation checks compare facts and marts.

### What is real and what is simulated?

Records come from the public anonymized Olist dataset. Mercora and its operating context are fictional. Historical dates are never presented as current.

### What decision does the application support?

It helps prioritize revenue, delivery, and retention deviations; identify the categories, sellers, and locations responsible; and reach actionable operational detail.

### How would you productionize it?

I would add metric ownership, refresh SLAs, data-quality alerts, access control, pipeline observability, and recurring validation with business users.
