# Mercora Commerce Intelligence

Aplicação interna de análise diária construída com os dados anonimizados do e-commerce brasileiro Olist. O case demonstra como transformar arquivos operacionais em um produto de decisão governado usando Python, SQL, DuckDB, Dash e Plotly.

**Demo pública:** [Mercora Commerce Intelligence](https://ba9ba428-78e2-4e6e-ac79-8a6dfe44fc99.plotly.app/)

Interface disponível em português e inglês. Links diretos podem usar `?page=revenue&lang=en`.

## Problema de negócio

Líderes comerciais e operacionais precisam acompanhar receita, recompra, qualidade da entrega e os responsáveis por cada desvio em um único lugar. A Mercora usa uma data operacional histórica selecionável, portanto os dados de 2016-2018 nunca são apresentados como atuais.

## Fluxo de dados

`CSV Olist -> ingestão Python -> fatos e dimensões no DuckDB -> marts SQL -> aplicação Dash`

Pedidos, itens e pagamentos permanecem em fatos separados. A receita vem dos itens e é agregada antes dos relacionamentos, impedindo que parcelas ou pedidos com vários itens multipliquem valores.

## Áreas da aplicação

- **Command Center:** situação diária, desvios e fila de ação.
- **Revenue Explorer:** categorias, geografia, vendedores e pagamentos.
- **Retention:** recompra, coortes, RFM e clientes para recuperação.
- **Customer Explorer:** histórico e comportamento por identificador anônimo.
- **Data Trust:** origem, testes, reconciliação e definições das métricas.

![Command Center da Mercora](docs/images/pt/command.png)

Telas verificadas: [Revenue Explorer](docs/images/pt/revenue.png), [Retenção](docs/images/pt/retention.png), [Customer Explorer](docs/images/pt/customers.png) e [Data Trust](docs/images/pt/trust.png).

## Executar localmente

```powershell
copy .env.example .env
run.cmd -m pipeline download
run.cmd -m pipeline build
run.cmd -m pipeline validate
run.cmd -m pipeline capture
run.cmd -m pipeline package
run.cmd app.py
```

Acesse `http://127.0.0.1:8050`.

## Testes

```powershell
run.cmd -m pytest
```

O pipeline possui 14 verificações determinísticas de qualidade, incluindo reconciliação de receita, integridade referencial, limites históricos e ausência de colunas sensíveis. A suíte cobre métricas, filtros, drill-down, internacionalização, empacotamento e inicialização da aplicação.

## Dados e licença

A fonte é o [Olist Brazilian E-Commerce Public Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce), licenciado sob CC BY-NC-SA 4.0. Os CSVs brutos não entram no controle de versão. Os artefatos publicados contêm somente marts analíticos anônimos e continuam sujeitos à licença da fonte. Este portfólio é não comercial e não possui vínculo com a Olist.

Consulte o [dicionário de métricas](docs/METRIC_DICTIONARY.md), o [modelo de dados](docs/DATA_MODEL.md), os [insights](docs/INSIGHTS.md), o [roteiro de demonstração e entrevista](docs/DEMO_GUIDE.md) e o [guia de publicação](docs/DEPLOYMENT.md).
