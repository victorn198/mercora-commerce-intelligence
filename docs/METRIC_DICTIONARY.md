# Dicionário de métricas

| Métrica | Definição | Granularidade e fonte |
|---|---|---|
| Receita | Soma de `price` dos itens comprados no período. Frete não integra a receita. | Item, `fact_order_items` / `mart_sales_lines` |
| Pedidos | Contagem distinta de `order_id`. | Pedido, `fact_orders` / `mart_orders` |
| Clientes ativos | Clientes anônimos distintos com pedido no período. | Cliente-período, `mart_orders` |
| Ticket médio | Receita dividida pela quantidade de pedidos. | Período filtrado |
| Clientes recorrentes | Participação dos clientes ativos cuja primeira compra ocorreu antes do início da janela. | Cliente-período, `mart_customers` + `mart_orders` |
| Entrega no prazo | Pedidos entregues até a data estimada divididos pelos pedidos com avaliação de prazo válida. | Pedido entregue, `mart_orders` |
| Avaliação média | Média da nota de avaliação associada ao pedido. | Pedido, `fact_reviews` / `mart_orders` |
| Receita por pagamento | Soma de `payment_value`; exibida como mix de cobrança e não como receita contábil. | Pagamento, `fact_payments` |
| Coorte | Mês da primeira compra do cliente. | Cliente, `mart_customers` |
| Retenção da coorte | Clientes da coorte que compraram no mês N divididos pelos clientes do mês zero. | Coorte-mês, `mart_cohorts` |
| Recência | Dias entre o fim analítico fixado e a última compra. | Cliente, `mart_customers` |
| Frequência | Quantidade de pedidos históricos do cliente. | Cliente, `mart_customers` |
| Valor | Receita histórica acumulada do cliente. | Cliente, `mart_customers` |

As métricas respeitam data operacional, janela e filtros aplicáveis. Nenhum percentual exibido no aplicativo é digitado manualmente no layout.
