from __future__ import annotations

from datetime import date

from dash import dcc, html

from .i18n import dropdown_labels, options as localized_options


NAV_ITEMS = [("command", "Command Center"), ("revenue", "Receita"), ("retention", "Retenção"), ("customers", "Clientes"), ("trust", "Data Trust")]


def _dropdown(component_id: str, values, placeholder: str):
    return dcc.Dropdown(id=component_id, options=localized_options(values, "pt"), multi=True, searchable=True, closeOnSelect=False, optionHeight=34, maxHeight=280, labels=dropdown_labels("pt"), placeholder=placeholder, className="modern-dropdown")


def build_shell(options: dict, min_date: date, max_date: date):
    return html.Div(
        [
            dcc.Location(id="url", refresh=False),
            dcc.Store(id="page-store", data="command"),
            dcc.Store(id="language-store", data="pt", storage_type="local"),
            dcc.Store(id="category-drill-store", data={"level": "category", "category": None, "enabled": True}),
            html.Header(
                [
                    html.Div([html.Img(src="/assets/logo.svg", className="brand-logo"), html.Div([html.Strong("Mercora"), html.Span("Commerce Intelligence")])], className="brand"),
                    html.Nav([html.Button(label, id=f"nav-{key}", className="nav-button", title=f"Abrir {label}") for key, label in NAV_ITEMS], className="top-nav"),
                    html.Div(
                        [
                            html.Div([html.Button("PT", id="language-pt", className="language-button active", title="Português"), html.Button("EN", id="language-en", className="language-button", title="English")], className="language-switch"),
                            html.Div([html.Span("Base histórica", id="source-badge-label"), html.Strong("Olist 2016-2018")], className="source-badge-copy"),
                        ],
                        className="header-tools",
                    ),
                ],
                className="app-header",
            ),
            html.Div(
                [
                    html.Div([html.H1(id="workspace-title", children="Command Center"), html.P(id="workspace-subtitle", children="Visão diária de receita, clientes e operação")], className="workspace-heading-copy"),
                    html.Div([html.Div([html.Span("Período", id="period-label"), html.Strong(f"até {max_date.strftime('%d/%m/%Y')}", id="period-value")], className="heading-meta-item"), html.Div([html.Span("Fonte", id="source-label"), html.Strong("Olist · dados históricos", id="source-value")], className="heading-meta-item")], className="heading-meta"),
                ],
                className="workspace-heading",
            ),
            html.Div(
                [
                    html.Div([html.Label("Data operacional", id="as-of-label"), dcc.DatePickerSingle(id="as-of", min_date_allowed=min_date, max_date_allowed=max_date, date=max_date, display_format="DD/MM/YYYY")], className="filter-item date-filter"),
                    html.Div([html.Label("Janela", id="window-label"), dcc.RadioItems(id="window", options=[{"label": "Dia", "value": 1}, {"label": "7 dias", "value": 7}, {"label": "30 dias", "value": 30}], value=30, inline=True, className="window-control")], className="filter-item window-filter"),
                    html.Div([html.Label("Categoria", id="category-label"), _dropdown("category-filter", options["categories"], "Todas")], className="filter-item"),
                    html.Div([html.Label("Estado cliente", id="customer-state-label"), _dropdown("customer-state-filter", options["customer_states"], "Todos")], className="filter-item"),
                    html.Div([html.Label("Estado vendedor", id="seller-state-label"), _dropdown("seller-state-filter", options["seller_states"], "Todos")], className="filter-item"),
                    html.Div([html.Label("Pagamento", id="payment-label"), _dropdown("payment-filter", options["payment_types"], "Todos")], className="filter-item"),
                    html.Div([html.Label("Status", id="status-label"), _dropdown("status-filter", options["statuses"], "Todos")], className="filter-item"),
                    html.Button("Limpar", id="reset-filters", className="reset-button", title="Limpar filtros"),
                ],
                className="filter-bar",
            ),
            html.Div(id="filter-context", className="filter-context"),
            html.Main(id="page-content", className="page-content"),
            html.Footer([html.Span("Fonte: Olist Brazilian E-Commerce Public Dataset", id="footer-source"), html.Span("CC BY-NC-SA 4.0")], className="app-footer"),
        ],
        className="app-shell",
    )
