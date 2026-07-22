# Modelo de dados

```mermaid
erDiagram
    DIM_CUSTOMERS ||--o{ FACT_ORDERS : places
    DIM_DATE ||--o{ FACT_ORDERS : purchase_date
    FACT_ORDERS ||--o{ FACT_ORDER_ITEMS : contains
    FACT_ORDERS ||--o{ FACT_PAYMENTS : receives
    FACT_ORDERS ||--o| FACT_REVIEWS : receives
    DIM_PRODUCTS ||--o{ FACT_ORDER_ITEMS : classifies
    DIM_SELLERS ||--o{ FACT_ORDER_ITEMS : fulfills
    DIM_GEOGRAPHY ||--o{ DIM_CUSTOMERS : locates

    FACT_ORDERS {
      string order_id PK
      string customer_key FK
      date purchase_date
      string order_status
    }
    FACT_ORDER_ITEMS {
      string order_id FK
      int order_item_id
      string product_id FK
      string seller_id FK
      decimal price
      decimal freight_value
    }
    FACT_PAYMENTS {
      string order_id FK
      int payment_sequential
      string payment_type
      decimal payment_value
    }
```

## Regra central de granularidade

`fact_orders`, `fact_order_items` e `fact_payments` não são juntadas diretamente para somar receita. Itens e pagamentos são agregados por pedido antes da construção de `mart_orders`. Essa regra elimina o efeito de multiplicação causado por pedidos com vários itens e várias parcelas.

## Privacidade

O identificador original de cliente é transformado em um hash de 12 caracteres. Nomes, emails, telefones e endereços completos não existem na fonte publicada nem nos marts da aplicação.
