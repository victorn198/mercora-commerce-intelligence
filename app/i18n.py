from __future__ import annotations


def language(value: str | None) -> str:
    return "en" if value == "en" else "pt"


def text(lang: str | None, pt: str, en: str) -> str:
    return en if language(lang) == "en" else pt


VALUE_LABELS = {
    "pt": {"boleto": "Boleto", "credit_card": "Cartão de crédito", "debit_card": "Cartão de débito", "voucher": "Voucher", "not_defined": "Não definido", "delivered": "Entregue", "shipped": "Enviado", "canceled": "Cancelado", "invoiced": "Faturado", "processing": "Em processamento", "approved": "Aprovado", "created": "Criado", "unavailable": "Indisponível"},
    "en": {"boleto": "Bank slip", "credit_card": "Credit card", "debit_card": "Debit card", "voucher": "Voucher", "not_defined": "Not defined", "delivered": "Delivered", "shipped": "Shipped", "canceled": "Canceled", "invoiced": "Invoiced", "processing": "Processing", "approved": "Approved", "created": "Created", "unavailable": "Unavailable"},
}


def options(values, lang: str):
    labels = VALUE_LABELS[language(lang)]
    return [{"label": labels.get(value, str(translate(value, lang)).replace("_", " ").title()), "value": value} for value in values]


def dropdown_labels(lang: str):
    if language(lang) == "en":
        return {"select_all": "Select all", "deselect_all": "Clear selection", "selected_count": "selected", "search": "Search", "clear_search": "Clear search", "clear_selection": "Clear selection", "no_options_found": "No options found"}
    return {"select_all": "Selecionar todos", "deselect_all": "Limpar seleção", "selected_count": "selecionados", "search": "Buscar", "clear_search": "Limpar busca", "clear_selection": "Limpar seleção", "no_options_found": "Nenhuma opção encontrada"}


ENGLISH = {
    "Receita": "Revenue", "Pedidos": "Orders", "Clientes ativos": "Active customers", "Ticket médio": "Average order value",
    "Clientes recorrentes": "Repeat customers", "Entrega no prazo": "On-time delivery", "Cancelamentos": "Cancellations",
    "Retenção e recompra": "Retention & repeat purchases", "Clientes": "Customers", "Categoria": "Category", "Avaliação": "Rating",
    "No prazo": "On time", "Sinal": "Signal", "Receita diária": "Daily revenue", "Meios de pagamento": "Payment mix",
    "Estados dos clientes": "Customer states", "Estados dos vendedores": "Seller states", "Comparativo por categoria": "Category comparison",
    "Ritmo de receita": "Revenue pace", "Receita por estado": "Revenue by state", "Fila de ação": "Action queue",
    "Categorias que movem o resultado": "Categories driving performance", "Granularidade: categoria": "Granularity: category",
    "Granularidade: produto": "Granularity: product", "Retenção por coorte": "Cohort retention", "Segmentos RFM": "RFM segments",
    "Clientes para recuperação": "Customers to recover", "Novos na janela": "New in window", "Recorrentes": "Repeat customers",
    "Participação recorrente": "Repeat customer share", "Avaliação média": "Average rating", "Recência": "Recency",
    "Cliente": "Customer", "Cidade": "City", "Segmento": "Segment", "Dias até 2ª": "Days to 2nd", "Frete": "Freight",
    "Clientes encontrados": "Customers found", "Detalhe": "Details", "Receita histórica": "Lifetime revenue",
    "Histórico de pedidos": "Order history", "Testes aprovados": "Passed tests", "Clientes anonimizados": "Anonymized customers",
    "Data final da análise": "Analysis end date", "Qualidade do pipeline": "Pipeline quality", "Volumes por camada": "Layer volumes",
    "Explorador de métricas": "Metric explorer", "Linhas de confiança": "Trust principles", "Tabela": "Table", "Registros": "Rows",
    "Teste": "Test", "Status": "Status", "Aprovado": "Passed", "Falhou": "Failed", "Fórmula": "Formula",
    "Granularidade": "Granularity", "Fonte": "Source", "Visão diária": "Daily view", "Diagnóstico comercial": "Commercial diagnosis",
    "Comportamento do cliente": "Customer behavior", "Investigação individual": "Individual investigation", "Governança visível": "Visible governance",
    "Em risco": "At risk", "Hibernando": "Hibernating", "Leais": "Loyal", "Novos": "New", "Campeões": "Champions", "Potenciais": "Potential",
    "Atraso": "Delay", "Monitorar": "Monitor", "Sem comparação": "No comparison",
    "Evolução dentro da janela selecionada": "Change within the selected window", "Clique em um estado para filtrar": "Select a state to filter",
    "Clique para filtrar": "Select to filter", "Combina relevância de receita, atraso e avaliação": "Combines revenue relevance, delays, and ratings",
    "M0 representa o mês da primeira compra": "M0 is the first-purchase month", "Recência e valor histórico orientam a prioridade": "Recency and lifetime value determine priority",
    "Definição, fórmula, granularidade e fonte": "Definition, formula, granularity, and source",
    "Nenhum cliente encontrado.": "No customers found.",
    "Visão diária de receita, clientes e operação": "Daily view of revenue, customers, and operations",
    "Análise comercial por categoria, região, vendedor e pagamento": "Commercial analysis by category, region, seller, and payment",
    "Comportamento, recorrência e experiência de entrega": "Behavior, repeat purchases, and delivery experience",
    "Investigação individual com identificadores anonimizados": "Individual analysis using anonymized identifiers",
    "Qualidade, origem, reconciliação e definição das métricas": "Quality, lineage, reconciliation, and metric definitions",
    "Detecte desvios, identifique os responsáveis e priorize a próxima ação.": "Detect deviations, identify owners, and prioritize the next action.",
    "Atravesse tempo, categoria, geografia, vendedor e pagamento sem perder o recorte.": "Explore time, category, geography, seller, and payment without losing context.",
    "Separe aquisição de recorrência e conecte fidelidade à experiência de entrega.": "Separate acquisition from repeat behavior and connect loyalty to delivery experience.",
    "Pesquise o identificador anonimizado e confira comportamento, valor e experiência.": "Search an anonymized identifier and review behavior, value, and experience.",
    "Digite parte do identificador do cliente": "Enter part of the customer identifier",
    "Os identificadores são hashes; nenhum nome, e-mail ou telefone é armazenado.": "Identifiers are hashes; no names, email addresses, or phone numbers are stored.",
    "Veja a origem, os testes e a definição das métricas antes de confiar na análise.": "Review lineage, tests, and metric definitions before trusting the analysis.",
    "validações determinísticas": "deterministic validations", "grão reconciliado": "reconciled grain",
    "hash de 12 caracteres": "12-character hash", "sem datas deslocadas": "original historical dates",
    "Pedidos, itens e pagamentos permanecem separados até o grão correto.": "Orders, items, and payments remain separate until the correct grain.",
    "A receita de itens reconcilia integralmente com o fato de itens.": "Item revenue fully reconciles with the item fact table.",
    "Clientes são identificados apenas por hash e dados públicos anonimizados.": "Customers are identified only by hashes and anonymized public data.",
    "O período histórico 2016–2018 permanece visível em toda a aplicação.": "The 2016–2018 historical period remains visible throughout the application.",
    "Cartão de crédito": "Credit card", "Cartão de débito": "Debit card", "Boleto": "Bank slip", "Não definido": "Not defined",
    "Sim": "Yes", "Não": "No",
    "Receita de itens": "Item revenue", "Taxa de cancelamento": "Cancellation rate",
    "Item do pedido": "Order item", "Pedido": "Order", "Período filtrado": "Filtered period", "Cliente por janela": "Customer by window", "Pedido avaliado": "Reviewed order",
    "Soma do preço dos itens selecionados, sem frete.": "Sum of selected item prices, excluding freight.",
    "Contagem distinta de pedidos com itens no recorte selecionado.": "Distinct count of orders containing items in the selected scope.",
    "Clientes anonimizados com ao menos um pedido no recorte.": "Anonymized customers with at least one order in the selected scope.",
    "Receita de itens dividida pelos pedidos distintos.": "Item revenue divided by distinct orders.",
    "Parcela dos clientes ativos cuja primeira compra ocorreu antes da janela atual.": "Share of active customers whose first purchase occurred before the current window.",
    "Pedidos entregues até a data estimada entre os pedidos com entrega conhecida.": "Orders delivered by the estimated date among orders with a known delivery date.",
    "Pedidos cancelados ou indisponíveis sobre os pedidos do recorte.": "Canceled or unavailable orders divided by orders in the selected scope.",
    "Média das avaliações disponíveis, calculada uma vez por pedido.": "Average available review score, calculated once per order.",
}


def add_english_terms(terms: dict[str, str]) -> None:
    ENGLISH.update({key: value for key, value in terms.items() if key and value})


def translate(value, lang: str):
    if language(lang) != "en" or not isinstance(value, str):
        return value
    if value in ENGLISH:
        return ENGLISH[value]
    prefixes = {
        "Produtos em ": "Products in ", "Janela: ": "Window: ", "Até: ": "Through: ", "Vendedor: ": "Seller: ",
        "Pagamento: ": "Payment: ", "Status geral: ": "Overall status: ", " registros exibidos": " rows shown",
        "Cliente ": "Customer ", " dias": " days",
    }
    for source, target in prefixes.items():
        if value.startswith(source):
            return target + value[len(source):]
        if value.endswith(source):
            return value[:-len(source)] + target
    return value
