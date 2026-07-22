from __future__ import annotations

from dash import dash_table, dcc, html


ICON_MAP = {"receita": "revenue.svg", "revenue": "revenue.svg", "pedidos": "orders.svg", "orders": "orders.svg", "clientes": "customers.svg", "customers": "customers.svg", "ticket": "ticket.svg", "recorrentes": "repeat.svg", "recorrente": "repeat.svg", "repeat": "repeat.svg", "entrega": "delivery.svg", "delivery": "delivery.svg", "cancel": "alert.svg", "avalia": "star.svg", "rating": "star.svg"}


def _metric_icon(title: str) -> str:
    normalized = title.casefold()
    filename = next((icon for keyword, icon in ICON_MAP.items() if keyword in normalized), "metric.svg")
    return f"/assets/icons/{filename}"


def format_currency(value: float, lang: str = "pt") -> str:
    formatted = f"{value:,.0f}"
    return f"R$ {formatted if lang == 'en' else formatted.replace(',', '.')}"


def format_number(value: float, lang: str = "pt") -> str:
    formatted = f"{value:,.0f}"
    return formatted if lang == "en" else formatted.replace(",", ".")


def format_percent(value: float, lang: str = "pt") -> str:
    formatted = f"{value:.1%}"
    return formatted if lang == "en" else formatted.replace(".", ",")


def kpi_card(title: str, value: str, delta: float | None, inverse: bool = False, subtitle: str | None = None, lang: str = "pt"):
    subtitle = subtitle or ("vs. previous window" if lang == "en" else "vs. janela anterior")
    if delta is None:
        direction, delta_class = "•", "neutral"
        delta_text = "No comparison" if lang == "en" else "Sem comparação"
    else:
        favorable = delta <= 0 if inverse else delta >= 0
        direction = "▲" if delta > 0 else "▼" if delta < 0 else "•"
        delta_class = "positive" if favorable else "negative"
        delta_text = f"{direction} {abs(delta):.1%}"
        if lang != "en":
            delta_text = delta_text.replace(".", ",")
    return html.Div([html.Div([html.Img(src=_metric_icon(title), className="kpi-icon", alt=""), html.Div(title, className="kpi-label")], className="kpi-heading"), html.Div(value, className="kpi-value"), html.Div([html.Span(delta_text, className=f"delta {delta_class}"), html.Span(subtitle)], className="kpi-context")], className="kpi-card")


def drill_toolbar(level: str = "category", enabled: bool = True, lang: str = "pt"):
    at_root = level == "category"
    return html.Div([
        html.Button("↓", id="category-drill-down", className=f"chart-tool-button{' active' if enabled and at_root else ''}", title="Enable drill down, then select a bar" if lang == "en" else "Ativar drill down e clicar em uma barra", **{"aria-label": "Enable drill down" if lang == "en" else "Ativar drill down"}, disabled=not at_root),
        html.Button("↑", id="category-drill-up", className="chart-tool-button", title="Back to categories" if lang == "en" else "Subir para categorias", **{"aria-label": "Drill up" if lang == "en" else "Subir um nível"}, disabled=at_root),
        html.Button("↺", id="category-drill-reset", className="chart-tool-button", title="Reset hierarchy" if lang == "en" else "Redefinir hierarquia", **{"aria-label": "Reset hierarchy" if lang == "en" else "Redefinir hierarquia"}, disabled=at_root),
    ], className="chart-toolbar", **{"aria-label": "Drill-down controls" if lang == "en" else "Controles de drill down"})


def panel(title: str, content, subtitle: str | None = None, class_name: str = "", actions=None):
    heading = [html.H3(title)]
    if subtitle:
        heading.append(html.P(subtitle))
    content_class = getattr(content, "className", "") or ""
    panel_class = "chart-panel" if "chart" in content_class.split() else ""
    return html.Section(
        [html.Div([html.Div(heading, className="panel-heading-copy"), actions], className="panel-heading"), content],
        className=f"panel {panel_class} {class_name}".strip(),
    )


def graph(graph_id: str, figure):
    return dcc.Graph(id=graph_id, figure=figure, config={"displayModeBar": False, "responsive": True}, className="chart")


def data_table(table_id: str, frame, columns: list[dict], page_size: int = 10, filterable: bool = True):
    return dash_table.DataTable(id=table_id, data=frame.to_dict("records"), columns=columns, page_size=page_size, sort_action="native", filter_action="native" if filterable else "none", style_as_list_view=True, style_table={"overflowX": "auto"}, style_header={"fontWeight": 700, "backgroundColor": "#f7f9fc", "color": "#12346b", "borderBottom": "1px solid #e2e7ef"}, style_cell={"padding": "7px 10px", "fontFamily": "Segoe UI, Inter, sans-serif", "fontSize": 10, "textAlign": "left", "border": "none", "borderBottom": "1px solid #edf0f5", "color": "#344054"}, style_data_conditional=[{"if": {"row_index": "odd"}, "backgroundColor": "#fbfcfe"}])


def page_intro(eyebrow: str, title: str, subtitle: str):
    return html.Div([html.Span(eyebrow, className="eyebrow"), html.H2(title), html.P(subtitle)], className="page-intro")
