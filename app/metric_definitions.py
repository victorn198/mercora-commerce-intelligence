METRICS = {
    "revenue": {
        "label": "Receita de itens",
        "definition": "Soma do preço dos itens selecionados, sem frete.",
        "formula": "SUM(fact_order_items.price)",
        "grain": "Item do pedido",
        "source": "olist_order_items_dataset.csv",
    },
    "orders": {
        "label": "Pedidos",
        "definition": "Contagem distinta de pedidos com itens no recorte selecionado.",
        "formula": "COUNT(DISTINCT order_id)",
        "grain": "Pedido",
        "source": "olist_orders_dataset.csv + olist_order_items_dataset.csv",
    },
    "active_customers": {
        "label": "Clientes ativos",
        "definition": "Clientes anonimizados com ao menos um pedido no recorte.",
        "formula": "COUNT(DISTINCT customer_key)",
        "grain": "Cliente",
        "source": "olist_customers_dataset.csv + olist_orders_dataset.csv",
    },
    "average_ticket": {
        "label": "Ticket médio",
        "definition": "Receita de itens dividida pelos pedidos distintos.",
        "formula": "Receita de itens / Pedidos",
        "grain": "Período filtrado",
        "source": "mart_orders",
    },
    "repeat_share": {
        "label": "Participação recorrente",
        "definition": "Parcela dos clientes ativos cuja primeira compra ocorreu antes da janela atual.",
        "formula": "Clientes recorrentes / Clientes ativos",
        "grain": "Cliente por janela",
        "source": "mart_customer_orders",
    },
    "on_time_rate": {
        "label": "Entrega no prazo",
        "definition": "Pedidos entregues até a data estimada entre os pedidos com entrega conhecida.",
        "formula": "Pedidos no prazo / Pedidos entregues",
        "grain": "Pedido",
        "source": "olist_orders_dataset.csv",
    },
    "cancellation_rate": {
        "label": "Taxa de cancelamento",
        "definition": "Pedidos cancelados ou indisponíveis sobre os pedidos do recorte.",
        "formula": "Pedidos cancelados / Pedidos",
        "grain": "Pedido",
        "source": "olist_orders_dataset.csv",
    },
    "review_score": {
        "label": "Avaliação média",
        "definition": "Média das avaliações disponíveis, calculada uma vez por pedido.",
        "formula": "AVG(review_score por order_id)",
        "grain": "Pedido avaliado",
        "source": "olist_order_reviews_dataset.csv",
    },
}

