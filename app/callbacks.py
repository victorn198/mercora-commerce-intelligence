from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from urllib.parse import parse_qs

import pandas as pd
from dash import Input, Output, State, ctx, dash_table, dcc, html, no_update

from .components import (
    data_table,
    format_currency,
    format_number,
    format_percent,
    graph,
    drill_toolbar,
    kpi_card,
    page_intro,
    panel,
)
from .figures import cohort_heatmap, horizontal_bar, payment_donut, segment_bar, trend_figure
from .i18n import add_english_terms, dropdown_labels, options as localized_options, translate
from .metric_definitions import METRICS
from .repository import AnalyticsRepository, FilterState


NAV_KEYS = ("command", "revenue", "retention", "customers", "trust")
PAGE_META = {
    "command": ("Command Center", "Visão diária de receita, clientes e operação"),
    "revenue": ("Revenue Explorer", "Análise comercial por categoria, região, vendedor e pagamento"),
    "retention": ("Retenção e recompra", "Comportamento, recorrência e experiência de entrega"),
    "customers": ("Customer Explorer", "Investigação individual com identificadores anonimizados"),
    "trust": ("Data Trust", "Qualidade, origem, reconciliação e definição das métricas"),
}


def _localize(component, lang: str):
    if lang != "en" or component is None:
        return component
    if isinstance(component, str):
        return translate(component, lang)
    if isinstance(component, (list, tuple)):
        return [_localize(item, lang) for item in component]
    if hasattr(component, "children"):
        component.children = _localize(component.children, lang)
    if hasattr(component, "placeholder") and isinstance(component.placeholder, str):
        component.placeholder = translate(component.placeholder, lang)
    if hasattr(component, "options") and isinstance(component.options, list):
        component.options = [
            {**option, "label": translate(option.get("label"), lang)} if isinstance(option, dict) else option
            for option in component.options
        ]
    if hasattr(component, "columns") and component.columns:
        component.columns = [{**column, "name": translate(column.get("name"), lang)} for column in component.columns]
    if hasattr(component, "data") and isinstance(component.data, list):
        component.data = [{key: translate(value, lang) for key, value in row.items()} for row in component.data]
    if hasattr(component, "figure") and component.figure:
        figure = component.figure
        for trace in figure.data:
            if getattr(trace, "name", None):
                trace.name = translate(trace.name, lang)
            if getattr(trace, "hovertemplate", None):
                trace.hovertemplate = (trace.hovertemplate.replace("Receita", "Revenue").replace("Pedidos", "Orders").replace("Clientes", "Customers").replace("Participação", "Share").replace("Pagamentos", "Payments").replace("Retenção", "Retention").replace("Coorte", "Cohort"))
            if getattr(trace, "y", None) is not None:
                trace.y = [translate(value, lang) for value in trace.y]
        for annotation in figure.layout.annotations or []:
            annotation.text = translate(annotation.text, lang)
    return component


def _delta(current: float, previous: float) -> float | None:
    if previous in (None, 0) or pd.isna(previous):
        return None
    return (float(current) - float(previous)) / abs(float(previous))


def _state(as_of, window, categories, customer_states, seller_states, payments, statuses) -> FilterState:
    if isinstance(as_of, str):
        as_of = date.fromisoformat(as_of.split("T", 1)[0])
    return FilterState(
        as_of=as_of,
        window_days=int(window or 30),
        categories=tuple(categories or ()),
        customer_states=tuple(customer_states or ()),
        seller_states=tuple(seller_states or ()),
        payment_types=tuple(payments or ()),
        statuses=tuple(statuses or ()),
    )


def _cards(current: dict, previous: dict, lang: str = "pt"):
    specs = [
        ("Receita", "revenue", format_currency, False),
        ("Pedidos", "orders", format_number, False),
        ("Clientes ativos", "active_customers", format_number, False),
        ("Ticket médio", "average_ticket", format_currency, False),
        ("Clientes recorrentes", "repeat_share", format_percent, False),
        ("Entrega no prazo", "on_time_rate", format_percent, False),
    ]
    return html.Div(
        [
            kpi_card(translate(label, lang), formatter(float(current[key]), lang), _delta(current[key], previous[key]), inverse, lang=lang)
            for label, key, formatter, inverse in specs
        ],
        className="kpi-grid",
    )


def _table_frame(frame: pd.DataFrame, currency=(), percentages=(), lang: str = "pt") -> pd.DataFrame:
    output = frame.copy()
    for column in currency:
        if column in output:
            output[column] = output[column].map(lambda value: format_currency(float(value), lang) if pd.notna(value) else "—")
    for column in percentages:
        if column in output:
            output[column] = output[column].map(lambda value: format_percent(float(value), lang) if pd.notna(value) else "—")
    return output


def _category_view(repository: AnalyticsRepository, state: FilterState, drill_state: dict | None, limit: int):
    drill_state = drill_state or {}
    level = drill_state.get("level", "category")
    category = drill_state.get("category")
    if level == "product" and category:
        return (
            repository.product_breakdown(state, category, limit),
            f"Produtos em {category.replace('_', ' ').title()}",
            "Granularidade: produto",
            level,
        )
    return repository.breakdown(state, "category", limit), "Categorias que movem o resultado", "Granularidade: categoria", "category"


def _command_page(repository: AnalyticsRepository, state: FilterState, drill_state: dict | None = None, lang: str = "pt"):
    current, previous = repository.current_and_previous_kpis(state)
    trend = repository.trend(state)
    categories, category_title, category_subtitle, category_level = _category_view(repository, state, drill_state, 10)
    states = repository.breakdown(state, "customer_state", 10)
    actions = repository.action_queue(state)
    actions = _table_frame(actions[["dimension", "revenue", "orders", "on_time_rate", "review_score", "signal"]], currency=("revenue",), percentages=("on_time_rate",), lang=lang)
    actions["review_score"] = actions["review_score"].map(lambda value: f"{float(value):.2f}" if pd.notna(value) else "-")
    actions.columns = ["Categoria", "Receita", "Pedidos", "No prazo", "Avaliação", "Sinal"]
    return html.Div(
        [
            page_intro("Visão diária", "Command Center", "Detecte desvios, identifique os responsáveis e priorize a próxima ação."),
            _cards(current, previous, lang),
            html.Div(
                [
                    panel("Ritmo de receita", graph("trend-chart", trend_figure(trend, lang)), "Evolução dentro da janela selecionada", "span-8"),
                    panel("Receita por estado", graph("state-chart", horizontal_bar(states, lang=lang)), "Clique em um estado para filtrar", "span-4"),
                    panel(
                        category_title,
                        graph("category-chart", horizontal_bar(categories, lang=lang)),
                        category_subtitle,
                        "span-6",
                        actions=drill_toolbar(category_level, (drill_state or {}).get("enabled", True), lang),
                    ),
                    panel(
                        "Fila de ação",
                        data_table("action-table", actions, [{"name": column, "id": column} for column in actions.columns], 8, filterable=False),
                        "Combina relevância de receita, atraso e avaliação",
                        "span-6",
                    ),
                ],
                className="content-grid",
            ),
        ]
    )


def _revenue_page(repository: AnalyticsRepository, state: FilterState, drill_state: dict | None = None, lang: str = "pt"):
    current, previous = repository.current_and_previous_kpis(state)
    trend = repository.trend(state)
    categories, category_title, category_subtitle, category_level = _category_view(repository, state, drill_state, 14)
    category_summary = repository.breakdown(state, "category", 14)
    states = repository.breakdown(state, "customer_state", 12)
    sellers = repository.breakdown(state, "seller_state", 12)
    payments = repository.payment_mix(state)
    detail = _table_frame(category_summary[["dimension", "revenue", "orders", "customers", "on_time_rate", "review_score"]], currency=("revenue",), percentages=("on_time_rate",), lang=lang)
    detail["review_score"] = detail["review_score"].map(lambda value: f"{float(value):.2f}" if pd.notna(value) else "-")
    detail.columns = ["Categoria", "Receita", "Pedidos", "Clientes", "No prazo", "Avaliação"]
    cards = html.Div(
        [
            kpi_card("Receita", format_currency(current["revenue"], lang), _delta(current["revenue"], previous["revenue"]), lang=lang),
            kpi_card("Pedidos", format_number(current["orders"], lang), _delta(current["orders"], previous["orders"]), lang=lang),
            kpi_card("Ticket médio", format_currency(current["average_ticket"], lang), _delta(current["average_ticket"], previous["average_ticket"]), lang=lang),
            kpi_card("Cancelamentos", format_percent(current["cancellation_rate"], lang), _delta(current["cancellation_rate"], previous["cancellation_rate"]), inverse=True, lang=lang),
        ],
        className="kpi-grid four",
    )
    return html.Div(
        [
            page_intro("Diagnóstico comercial", "Revenue Explorer", "Atravesse tempo, categoria, geografia, vendedor e pagamento sem perder o recorte."),
            cards,
            html.Div(
                [
                    panel("Receita diária", graph("trend-chart", trend_figure(trend, lang)), class_name="span-8"),
                    panel("Meios de pagamento", graph("payment-chart", payment_donut(payments, lang)), class_name="span-4"),
                    panel(
                        category_title,
                        graph("category-chart", horizontal_bar(categories, lang=lang)),
                        category_subtitle,
                        "span-4",
                        actions=drill_toolbar(category_level, (drill_state or {}).get("enabled", True), lang),
                    ),
                    panel("Estados dos clientes", graph("state-chart", horizontal_bar(states, lang=lang)), "Clique para filtrar", "span-4"),
                    panel("Estados dos vendedores", graph("seller-chart", horizontal_bar(sellers, color="#12315f", lang=lang)), class_name="span-4"),
                    panel("Comparativo por categoria", data_table("revenue-detail", detail, [{"name": c, "id": c} for c in detail.columns], 12), class_name="span-12"),
                ],
                className="content-grid",
            ),
        ]
    )


def _retention_page(repository: AnalyticsRepository, state: FilterState, lang: str = "pt"):
    current, previous = repository.current_and_previous_kpis(state)
    cohorts = repository.cohort_matrix(state.as_of)
    segments = repository.rfm_segments(state)
    customers = repository.customer_table(state, limit=30)
    at_risk = customers[customers["rfm_segment"].isin(["Em risco", "Hibernando"])].head(12)
    at_risk = _table_frame(at_risk[["customer_key", "customer_state", "rfm_segment", "lifetime_orders", "lifetime_revenue", "recency_days"]], currency=("lifetime_revenue",), lang=lang)
    at_risk.columns = ["Cliente", "UF", "Segmento", "Pedidos", "Receita", "Recência"]
    recurring = current["active_customers"] * current["repeat_share"]
    new_customers = current["active_customers"] - recurring
    previous_recurring = previous["active_customers"] * previous["repeat_share"]
    previous_new = previous["active_customers"] - previous_recurring
    cards = html.Div(
        [
            kpi_card("Clientes ativos", format_number(current["active_customers"], lang), _delta(current["active_customers"], previous["active_customers"]), lang=lang),
            kpi_card("Novos na janela", format_number(new_customers, lang), _delta(new_customers, previous_new), lang=lang),
            kpi_card("Recorrentes", format_number(recurring, lang), _delta(recurring, previous_recurring), lang=lang),
            kpi_card("Participação recorrente", format_percent(current["repeat_share"], lang), _delta(current["repeat_share"], previous["repeat_share"]), lang=lang),
            kpi_card("Entrega no prazo", format_percent(current["on_time_rate"], lang), _delta(current["on_time_rate"], previous["on_time_rate"]), lang=lang),
            kpi_card("Avaliação média", f"{current['review_score']:.2f}", _delta(current["review_score"], previous["review_score"]), lang=lang),
        ],
        className="kpi-grid",
    )
    return html.Div(
        [
            page_intro("Comportamento do cliente", "Retenção e recompra", "Separe aquisição de recorrência e conecte fidelidade à experiência de entrega."),
            cards,
            html.Div(
                [
                    panel("Retenção por coorte", graph("cohort-chart", cohort_heatmap(cohorts, lang)), "M0 representa o mês da primeira compra", "span-8"),
                    panel("Segmentos RFM", graph("segment-chart", segment_bar(segments, lang)), class_name="span-4"),
                    panel("Clientes para recuperação", data_table("risk-table", at_risk, [{"name": c, "id": c} for c in at_risk.columns], 12), "Recência e valor histórico orientam a prioridade", "span-12"),
                ],
                className="content-grid",
            ),
        ]
    )


def _customer_page(repository: AnalyticsRepository, state: FilterState, lang: str = "pt"):
    return html.Div(
        [
            page_intro("Investigação individual", "Customer Explorer", "Pesquise o identificador anonimizado e confira comportamento, valor e experiência."),
            html.Div(
                [
                    dcc.Input(id="customer-search", type="search", placeholder="Digite parte do identificador do cliente", debounce=True, className="search-input"),
                    html.Span("Os identificadores são hashes; nenhum nome, e-mail ou telefone é armazenado.", className="privacy-note"),
                ],
                className="customer-search-bar",
            ),
            html.Div([html.Div(id="customer-results", className="span-7"), html.Div(id="customer-detail", className="span-5")], className="content-grid"),
        ]
    )


def _trust_page(repository: AnalyticsRepository, project_root: Path, lang: str = "pt"):
    metadata = repository.metadata()
    counts = repository.table_counts()
    quality_path = project_root / "data" / "processed" / "quality_report.json"
    quality = json.loads(quality_path.read_text(encoding="utf-8")) if quality_path.exists() else {"checks": {}, "status": "unknown"}
    check_labels_pt = {
        "orders_unique": "Pedidos únicos", "items_unique": "Itens únicos", "payments_unique": "Pagamentos únicos",
        "items_have_orders": "Itens possuem pedido", "payments_have_orders": "Pagamentos possuem pedido",
        "order_mart_unique": "Mart de pedidos único", "item_revenue_reconciles": "Receita de itens reconciliada",
        "nonnegative_revenue": "Receita não negativa", "valid_analysis_dates": "Datas de análise válidas",
        "customer_hash_present": "Hash de cliente presente", "customer_hash_unique": "Hash de cliente único",
        "historical_dates_bounded": "Datas históricas limitadas", "critical_fields_present": "Campos críticos presentes",
        "no_sensitive_columns": "Sem colunas sensíveis",
    }
    check_labels_en = {
        "orders_unique": "Unique orders", "items_unique": "Unique items", "payments_unique": "Unique payments",
        "items_have_orders": "Items have valid orders", "payments_have_orders": "Payments have valid orders",
        "order_mart_unique": "Unique order mart", "item_revenue_reconciles": "Item revenue reconciles",
        "nonnegative_revenue": "Nonnegative revenue", "valid_analysis_dates": "Valid analysis dates",
        "customer_hash_present": "Customer hash present", "customer_hash_unique": "Unique customer hash",
        "historical_dates_bounded": "Historical dates bounded", "critical_fields_present": "Critical fields present",
        "no_sensitive_columns": "No sensitive columns",
    }
    check_labels = check_labels_en if lang == "en" else check_labels_pt
    status_passed = "Passed" if lang == "en" else "Aprovado"
    status_failed = "Failed" if lang == "en" else "Falhou"
    checks = pd.DataFrame([{"Teste": check_labels.get(key, key.replace("_", " ").title()), "Status": status_passed if value else status_failed} for key, value in quality.get("checks", {}).items()])
    counts_display = counts.copy()
    counts_display["rows"] = counts_display["rows"].map(lambda value: format_number(value, lang))
    counts_display.columns = ["Tabela", "Registros"]
    return html.Div(
        [
            page_intro("Governança visível", "Data Trust", "Veja a origem, os testes e a definição das métricas antes de confiar na análise."),
            html.Div(
                [
                    kpi_card("Testes aprovados", format_number(sum(quality.get("checks", {}).values()), lang), None, subtitle="validações determinísticas", lang=lang),
                    kpi_card("Pedidos", format_number(quality.get("metrics", {}).get("orders", 0), lang), None, subtitle="grão reconciliado", lang=lang),
                    kpi_card("Clientes anonimizados", format_number(quality.get("metrics", {}).get("customers", 0), lang), None, subtitle="hash de 12 caracteres", lang=lang),
                    kpi_card("Data final da análise", pd.Timestamp(metadata["analysis_end_date"]).strftime("%Y-%m-%d"), None, subtitle="sem datas deslocadas", lang=lang),
                ],
                className="kpi-grid four",
            ),
            html.Div(
                [
                    panel("Qualidade do pipeline", data_table("quality-table", checks, [{"name": c, "id": c} for c in checks.columns], 10), f"Status geral: {quality.get('status', 'unknown')}", "span-4"),
                    panel("Volumes por camada", data_table("count-table", counts_display, [{"name": c, "id": c} for c in counts_display.columns], 10), class_name="span-4"),
                    panel(
                        "Explorador de métricas",
                        html.Div(
                            [
                                dcc.Dropdown(id="metric-select", options=[{"label": value["label"], "value": key} for key, value in METRICS.items()], value="revenue", clearable=False),
                                html.Div(id="metric-definition", className="metric-definition"),
                            ]
                        ),
                        "Definição, fórmula, granularidade e fonte",
                        "span-4",
                    ),
                    panel(
                        "Linhas de confiança",
                        html.Ul(
                            [
                                html.Li("Pedidos, itens e pagamentos permanecem separados até o grão correto."),
                                html.Li("A receita de itens reconcilia integralmente com o fato de itens."),
                                html.Li("Clientes são identificados apenas por hash e dados públicos anonimizados."),
                                html.Li("O período histórico 2016–2018 permanece visível em toda a aplicação."),
                            ],
                            className="trust-list",
                        ),
                        class_name="span-12",
                    ),
                ],
                className="content-grid",
            ),
        ]
    )


def register_callbacks(dash_app, repository: AnalyticsRepository, project_root: Path, max_date: date):
    add_english_terms(repository.category_translations())
    filter_options = repository.filter_options()

    @dash_app.callback(
        Output("language-store", "data"),
        Input("language-pt", "n_clicks"),
        Input("language-en", "n_clicks"),
        Input("url", "search"),
    )
    def select_language(_, __, search):
        if ctx.triggered_id == "url":
            requested = parse_qs((search or "").lstrip("?")).get("lang", ["pt"])[0]
            return "en" if requested == "en" else "pt"
        return "en" if ctx.triggered_id == "language-en" else "pt"

    @dash_app.callback(
        Output("language-pt", "className"), Output("language-en", "className"),
        Output("nav-command", "children"), Output("nav-revenue", "children"), Output("nav-retention", "children"), Output("nav-customers", "children"), Output("nav-trust", "children"),
        Output("source-badge-label", "children"), Output("period-label", "children"), Output("period-value", "children"), Output("source-label", "children"), Output("source-value", "children"),
        Output("as-of-label", "children"), Output("as-of", "display_format"), Output("window-label", "children"), Output("window", "options"), Output("category-label", "children"), Output("customer-state-label", "children"), Output("seller-state-label", "children"), Output("payment-label", "children"), Output("status-label", "children"), Output("reset-filters", "children"), Output("reset-filters", "title"), Output("footer-source", "children"),
        Output("category-filter", "options"), Output("customer-state-filter", "options"), Output("seller-state-filter", "options"), Output("payment-filter", "options"), Output("status-filter", "options"),
        Output("category-filter", "placeholder"), Output("customer-state-filter", "placeholder"), Output("seller-state-filter", "placeholder"), Output("payment-filter", "placeholder"), Output("status-filter", "placeholder"),
        Output("category-filter", "labels"), Output("customer-state-filter", "labels"), Output("seller-state-filter", "labels"), Output("payment-filter", "labels"), Output("status-filter", "labels"),
        Input("language-store", "data"),
    )
    def localize_shell(lang):
        en = lang == "en"
        labels = dropdown_labels(lang)
        placeholder_all = "All" if en else "Todas"
        placeholder_any = "All" if en else "Todos"
        return (
            "language-button active" if not en else "language-button", "language-button active" if en else "language-button",
            "Command Center", "Revenue", "Retention", "Customers", "Data Trust",
            "Historical data" if en else "Base histórica", "Period" if en else "Período", f"through {max_date.strftime('%m/%d/%Y')}" if en else f"até {max_date.strftime('%d/%m/%Y')}", "Source" if en else "Fonte", "Olist · historical data" if en else "Olist · dados históricos",
            "Operating date" if en else "Data operacional", "MM/DD/YYYY" if en else "DD/MM/YYYY", "Window" if en else "Janela", [{"label": "Day" if en else "Dia", "value": 1}, {"label": "7 days" if en else "7 dias", "value": 7}, {"label": "30 days" if en else "30 dias", "value": 30}],
            "Category" if en else "Categoria", "Customer state" if en else "Estado cliente", "Seller state" if en else "Estado vendedor", "Payment" if en else "Pagamento", "Status", "Reset" if en else "Limpar", "Reset filters" if en else "Limpar filtros", "Source: Olist Brazilian E-Commerce Public Dataset" if en else "Fonte: Olist Brazilian E-Commerce Public Dataset",
            localized_options(filter_options["categories"], lang), localized_options(filter_options["customer_states"], lang), localized_options(filter_options["seller_states"], lang), localized_options(filter_options["payment_types"], lang), localized_options(filter_options["statuses"], lang),
            placeholder_all, placeholder_any, placeholder_any, placeholder_any, placeholder_any,
            labels, labels, labels, labels, labels,
        )

    @dash_app.callback(
        Output("page-store", "data"),
        Input("url", "search"),
        *[Input(f"nav-{key}", "n_clicks") for key in NAV_KEYS],
    )
    def navigate(search, *_):
        trigger = ctx.triggered_id
        if trigger == "url":
            requested = parse_qs((search or "").lstrip("?")).get("page", ["command"])[0]
            return requested if requested in NAV_KEYS else "command"
        return trigger.removeprefix("nav-") if trigger else "command"

    @dash_app.callback(
        *[Output(f"nav-{key}", "className") for key in NAV_KEYS],
        Input("page-store", "data"),
    )
    def style_navigation(page):
        return tuple("nav-button active" if key == page else "nav-button" for key in NAV_KEYS)

    @dash_app.callback(
        Output("as-of", "date"),
        Output("window", "value"),
        Output("category-filter", "value"),
        Output("customer-state-filter", "value"),
        Output("seller-state-filter", "value"),
        Output("payment-filter", "value"),
        Output("status-filter", "value"),
        Input("reset-filters", "n_clicks"),
        Input("state-chart", "clickData"),
        State("customer-state-filter", "value"),
        prevent_initial_call=True,
    )
    def filter_actions(_, state_click, current_states):
        trigger = ctx.triggered_id
        if trigger == "reset-filters":
            return max_date, 30, [], [], [], [], []
        if trigger == "state-chart" and state_click:
            selected = state_click["points"][0].get("y") or state_click["points"][0].get("customdata", [None])[0]
            return no_update, no_update, no_update, [selected], no_update, no_update, no_update
        return (no_update,) * 7

    @dash_app.callback(
        Output("category-drill-store", "data"),
        Input("category-drill-down", "n_clicks"),
        Input("category-drill-up", "n_clicks"),
        Input("category-drill-reset", "n_clicks"),
        Input("category-chart", "clickData"),
        Input("reset-filters", "n_clicks"),
        State("category-drill-store", "data"),
        prevent_initial_call=True,
    )
    def category_drill(_, __, ___, click_data, ____, current):
        current = current or {"level": "category", "category": None, "enabled": True}
        trigger = ctx.triggered_id
        if trigger in {"category-drill-up", "category-drill-reset", "reset-filters"}:
            return {"level": "category", "category": None, "enabled": True}
        if trigger == "category-drill-down":
            return {**current, "enabled": True}
        if trigger == "category-chart" and click_data and current.get("level", "category") == "category" and current.get("enabled", True):
            point = click_data["points"][0]
            category = point.get("y") or point.get("customdata", [None])[0]
            if category:
                return {"level": "product", "category": category, "enabled": True}
        return no_update

    @dash_app.callback(
        Output("page-content", "children"),
        Output("filter-context", "children"),
        Output("filter-context", "style"),
        Output("workspace-title", "children"),
        Output("workspace-subtitle", "children"),
        *[
            Input("page-store", "data"),
            Input("as-of", "date"),
            Input("window", "value"),
            Input("category-filter", "value"),
            Input("customer-state-filter", "value"),
            Input("seller-state-filter", "value"),
            Input("payment-filter", "value"),
            Input("status-filter", "value"),
            Input("category-drill-store", "data"),
            Input("language-store", "data"),
        ],
    )
    def render_page(page, as_of, window, categories, customer_states, seller_states, payments, statuses, drill_state, lang):
        state = _state(as_of, window, categories, customer_states, seller_states, payments, statuses)
        builders = {
            "command": lambda: _command_page(repository, state, drill_state, lang),
            "revenue": lambda: _revenue_page(repository, state, drill_state, lang),
            "retention": lambda: _retention_page(repository, state, lang),
            "customers": lambda: _customer_page(repository, state, lang),
            "trust": lambda: _trust_page(repository, project_root, lang),
        }
        if lang == "en":
            labels = [f"Window: {state.window_days} day(s)", f"Through: {state.as_of.strftime('%m/%d/%Y')}"]
            filter_names = ("Category", "Customer", "Seller", "Payment", "Status")
        else:
            labels = [f"Janela: {state.window_days} dia(s)", f"Até: {state.as_of.strftime('%d/%m/%Y')}"]
            filter_names = ("Categoria", "Cliente", "Vendedor", "Pagamento", "Status")
        for name, values in zip(filter_names, (categories, customer_states, seller_states, payments, statuses)):
            if values:
                labels.append(f"{name}: {', '.join(str(translate(value, lang)) for value in values)}")
        chips = [html.Span(label, className="filter-chip") for label in labels]
        title, subtitle = PAGE_META.get(page, PAGE_META["command"])
        page_component = _localize(builders.get(page, builders["command"])(), lang)
        return page_component, chips, {"display": "flex"}, translate(title, lang), translate(subtitle, lang)

    @dash_app.callback(
        Output("customer-results", "children"),
        Output("customer-detail", "children"),
        Input("customer-search", "value"),
        Input("language-store", "data"),
        State("as-of", "date"),
        prevent_initial_call=False,
    )
    def customer_lookup(search, lang, as_of):
        normalized_as_of = date.fromisoformat(as_of.split("T", 1)[0]) if isinstance(as_of, str) else as_of
        state = FilterState(as_of=normalized_as_of)
        customers = repository.customer_table(state, search or "", 50)
        display = _table_frame(customers, currency=("lifetime_revenue",), lang=lang)
        display.columns = ["Cliente", "UF", "Cidade", "Segmento", "Pedidos", "Receita", "Recência", "Dias até 2ª", "Avaliação"]
        table = panel("Clientes encontrados", data_table("customer-table", display, [{"name": c, "id": c} for c in display.columns], 12), f"{len(display)} registros exibidos")
        if customers.empty:
            return _localize(table, lang), _localize(panel("Detalhe", html.P("Nenhum cliente encontrado.", className="empty-copy")), lang)
        selected = customers.iloc[0]
        orders = repository.customer_orders(selected["customer_key"])
        order_display = _table_frame(orders, currency=("item_revenue", "freight_value"), lang=lang)
        if not order_display.empty:
            order_display["purchase_date"] = pd.to_datetime(order_display["purchase_date"]).dt.strftime("%Y-%m-%d")
            order_display["order_id"] = order_display["order_id"].astype(str).str.slice(0, 12)
            order_display["is_on_time"] = order_display["is_on_time"].map({True: "Sim", False: "Não"}).fillna("—")
        order_display.columns = ["Data", "Pedido", "Receita", "Frete", "Avaliação", "No prazo"]
        detail = panel(
            f"Cliente {selected['customer_key']}",
            html.Div(
                [
                    html.Div([html.Span("Segmento"), html.Strong(selected["rfm_segment"])], className="detail-row"),
                    html.Div([html.Span("Receita histórica"), html.Strong(format_currency(selected["lifetime_revenue"], lang))], className="detail-row"),
                    html.Div([html.Span("Pedidos"), html.Strong(format_number(selected["lifetime_orders"], lang))], className="detail-row"),
                    html.Div([html.Span("Recência"), html.Strong(f"{selected['recency_days']} dias")], className="detail-row"),
                    html.H4("Histórico de pedidos"),
                    data_table("customer-orders", order_display, [{"name": c, "id": c} for c in order_display.columns], 6),
                ]
            ),
        )
        return _localize(table, lang), _localize(detail, lang)

    @dash_app.callback(Output("metric-definition", "children"), Input("metric-select", "value"), Input("language-store", "data"))
    def metric_definition(metric_key, lang):
        metric = METRICS[metric_key]
        return _localize(html.Div(
            [
                html.H4(metric["label"]),
                html.P(metric["definition"]),
                html.Dl(
                    [
                        html.Dt("Fórmula"), html.Dd(metric["formula"]),
                        html.Dt("Granularidade"), html.Dd(metric["grain"]),
                        html.Dt("Fonte"), html.Dd(metric["source"]),
                    ]
                ),
            ]
        ), lang)
